import json
import re

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
- Every hypothesis must include 2 to 3 evidence_rules that a user could
  realistically evaluate.
- Every hypothesis must have at least one rule with effect="supports" and at
  least one rule with effect="contradicts". This is required for falsification.
- Evidence rules must use variables listed in the investigation's variables.
- Prefer numeric comparisons when a measurable quantity exists.
- When numeric thresholds are not appropriate, use boolean or categorical
  equality comparisons.
- If you introduce a threshold or criterion rather than retrieving an
  established one, mark it explicitly as an investigation assumption.
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


_ORDERED_OPERATORS = {"<", "<=", ">", ">="}
_NUMERIC_RULE_VALUE = re.compile(
    r"^\s*(-?(?:\d+(?:\.\d+)?|\.\d+))\s*"
    r"([^\d\s].*|[A-Za-z°%][A-Za-z0-9°%_./ -]*)?\s*$"
)


def _normalize_generated_rule_values(payload: dict) -> dict:
    """Normalize unambiguous numeric tool output without guessing meaning."""

    hypotheses = payload.get("hypotheses")

    if not isinstance(hypotheses, list):
        return payload

    for hypothesis in hypotheses:
        if not isinstance(hypothesis, dict):
            continue

        rules = hypothesis.get("evidence_rules")

        if not isinstance(rules, list):
            continue

        for rule in rules:
            if not isinstance(rule, dict):
                continue

            if rule.get("operator") not in _ORDERED_OPERATORS:
                continue

            value = rule.get("value")

            if not isinstance(value, str):
                continue

            match = _NUMERIC_RULE_VALUE.fullmatch(value)

            if match is None:
                continue

            numeric_text = match.group(1)
            numeric_value = float(numeric_text)

            rule["value"] = (
                int(numeric_value)
                if numeric_value.is_integer()
                else numeric_value
            )

            suffix = (match.group(2) or "").strip()

            if suffix and not rule.get("unit"):
                rule["unit"] = (
                    "percent"
                    if suffix == "%"
                    else suffix
                )

    return payload


def _validate_generated_draft(draft: InvestigationDraft) -> None:
    """Reject structurally valid but scientifically unusable generated drafts."""

    if not 3 <= len(draft.hypotheses) <= 5:
        raise LLMInterpreterError(
            "Generated investigation must contain 3 to 5 hypotheses."
        )

    if not draft.variables:
        raise LLMInterpreterError(
            "Generated investigation must contain measurable variables."
        )

    allowed_variables = set(draft.variables)

    for hypothesis in draft.hypotheses:
        if not 2 <= len(hypothesis.evidence_rules) <= 3:
            raise LLMInterpreterError(
                "Each generated hypothesis must contain 2 to 3 evidence rules."
            )

        effects = {rule.effect.value for rule in hypothesis.evidence_rules}

        if "supports" not in effects or "contradicts" not in effects:
            raise LLMInterpreterError(
                "Each generated hypothesis must include at least one supporting "
                "rule and at least one contradicting rule."
            )

        for rule in hypothesis.evidence_rules:
            if rule.variable not in allowed_variables:
                raise LLMInterpreterError(
                    f"Evidence rule variable {rule.variable!r} is not declared "
                    "in the investigation variables."
                )


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
        schema = InvestigationDraft.model_json_schema()

        schema["properties"]["hypotheses"]["minItems"] = 4
        schema["properties"]["hypotheses"]["maxItems"] = 4
        schema["properties"]["variables"]["minItems"] = 1

        hypothesis_schema = schema["$defs"]["HypothesisDraft"]
        hypothesis_schema["properties"]["evidence_rules"]["minItems"] = 2
        hypothesis_schema["properties"]["evidence_rules"]["maxItems"] = 3

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": question,
            },
        ]

        tool = {
            "type": "function",
            "function": {
                "name": "create_investigation_draft",
                "description": (
                    "Create the structured scientific investigation for WhyLab."
                ),
                "parameters": schema,
            },
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        for attempt in range(2):
            payload = {
                "model": self.model,
                "provider": {
                    "require_parameters": True,
                },
                "messages": messages,
                "tools": [tool],
                "tool_choice": {
                    "type": "function",
                    "function": {
                        "name": "create_investigation_draft",
                    },
                },
                "temperature": 0.2,
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

                arguments = (
                    body["choices"][0]["message"]["tool_calls"][0]
                    ["function"]["arguments"]
                )

                if isinstance(arguments, str):
                    parsed = json.loads(arguments)
                elif isinstance(arguments, dict):
                    parsed = arguments
                else:
                    raise LLMInterpreterError(
                        "Interpreter returned invalid tool arguments."
                    )

                parsed = _normalize_generated_rule_values(parsed)
                draft = InvestigationDraft.model_validate(parsed)
                _validate_generated_draft(draft)
                return draft

            except httpx.HTTPError as exc:
                raise LLMInterpreterError(
                    "The investigation interpreter request failed."
                ) from exc

            except (
                LLMInterpreterError,
                KeyError,
                IndexError,
                TypeError,
                json.JSONDecodeError,
                ValidationError,
            ) as exc:
                if isinstance(exc, LLMInterpreterError):
                    failure = exc
                else:
                    failure = LLMInterpreterError(
                        f"Generated tool output failed validation: "
                        f"{type(exc).__name__}: {exc}"
                    )

                if attempt == 1:
                    raise failure from exc

                messages.append(
                    {
                        "role": "user",
                        "content": (
                            f"Your previous investigation was rejected: {failure}. "
                            "Call create_investigation_draft again. It MUST contain "
                            "exactly 4 competing hypotheses, at least one measurable "
                            "top-level variable, and 2 to 3 evidence_rules for every "
                            "hypothesis. Every rule variable must exactly match a "
                            "top-level variable. For <, <=, >, or >= comparisons, "
                            "value MUST be a bare JSON number; put units only in "
                            "the unit field."
                        ),
                    }
                )

        raise LLMInterpreterError(
            "The investigation interpreter exhausted its retry limit."
        )
