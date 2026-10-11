import json

import httpx
from pydantic import ValidationError

from whylab.application.builder import InvestigationDraft


SYSTEM_PROMPT = """
You are WhyLab's investigation planner.

Convert a new causal or investigable question into a rigorous scientific
investigation draft.

Requirements:
- Produce 3 to 5 genuinely competing, falsifiable hypotheses.
- Use concise machine-readable variable names in snake_case.
- Give each hypothesis predictions, falsifiers, confounders, and uncertainties.
- Add evidence_rules only when an observation can be evaluated by an explicit
  comparison against a value.
- Never present generated thresholds as universal facts.
- For model-proposed thresholds or criteria, use
  provenance="model_generated_assumption" and explain the assumption in rationale.
- Evidence rules may SUPPORT or CONTRADICT hypotheses, but must never mark a
  hypothesis KNOWN.
- Prefer observations a normal user can realistically obtain.
- Do not smuggle epistemic conclusions into the hypothesis text.
- The output must conform exactly to the supplied JSON schema.
""".strip()


class LLMInterpreterError(RuntimeError):
    """Raised when the external interpreter cannot produce a valid draft."""


class LLMQuestionInterpreter:
    """Generate structured WhyLab investigations through an OpenAI-compatible API."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str = "openrouter/free",
        base_url: str = "https://openrouter.ai/api/v1",
        client: httpx.Client | None = None,
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.client = client

    def interpret(self, question: str) -> InvestigationDraft:
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": question,
                },
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "investigation_draft",
                    "strict": True,
                    "schema": InvestigationDraft.model_json_schema(),
                },
            },
            "temperature": 0.2,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            if self.client is not None:
                response = self.client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )
            else:
                response = httpx.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=45.0,
                )

            response.raise_for_status()
            body = response.json()
            content = body["choices"][0]["message"]["content"]

            if not isinstance(content, str):
                raise LLMInterpreterError(
                    "Interpreter returned an unexpected response format."
                )

            parsed = json.loads(content)
            return InvestigationDraft.model_validate(parsed)

        except (
            httpx.HTTPError,
            KeyError,
            IndexError,
            TypeError,
            json.JSONDecodeError,
            ValidationError,
        ) as exc:
            raise LLMInterpreterError(
                "The investigation interpreter could not produce a valid draft."
            ) from exc
