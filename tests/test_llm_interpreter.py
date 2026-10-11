import json

import httpx

from whylab.interpreters.llm import LLMQuestionInterpreter


def test_llm_interpreter_builds_unseen_investigation():
    draft_payload = {
        "domain": "consumer_technology",
        "variables": [
            "battery_health",
            "background_power_usage",
        ],
        "confounders": [
            "screen_brightness",
            "device_age",
        ],
        "hypotheses": [
            {
                "claim": "The battery has substantially degraded",
                "predictions": [
                    "Measured battery health should be relatively low."
                ],
                "falsifiers": [
                    "Battery health remains high despite rapid discharge."
                ],
                "confounders": [
                    "device_age"
                ],
                "uncertainties": [
                    "Battery-health estimates may be imperfect."
                ],
                "evidence_rules": [
                    {
                        "variable": "battery_health",
                        "operator": "<=",
                        "value": 60,
                        "unit": "percent",
                        "effect": "supports",
                        "reason": (
                            "Low measured battery health supports substantial "
                            "battery degradation."
                        ),
                        "provenance": "model_generated_assumption",
                        "rationale": (
                            "This threshold is an investigation assumption, "
                            "not a universal battery-health boundary."
                        ),
                    }
                ],
            },
            {
                "claim": "Background software is consuming excessive power",
                "predictions": [
                    "Background power usage should be elevated."
                ],
                "falsifiers": [
                    "Background activity remains low during rapid discharge."
                ],
                "confounders": [
                    "screen_brightness"
                ],
                "uncertainties": [],
                "evidence_rules": [],
            },
            {
                "claim": "Display power draw is unusually high",
                "predictions": [
                    "Battery drain should decrease when display demand is reduced."
                ],
                "falsifiers": [
                    "Reducing display demand does not change discharge rate."
                ],
                "confounders": [
                    "background_power_usage"
                ],
                "uncertainties": [],
                "evidence_rules": [],
            },
        ],
    }

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)

        assert body["model"] == "openrouter/free"
        assert body["messages"][-1]["content"] == (
            "Why does my laptop battery drain so quickly?"
        )
        assert body["response_format"]["type"] == "json_schema"
        assert request.headers["Authorization"] == "Bearer test-key"

        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(draft_payload)
                        }
                    }
                ]
            },
        )

    client = httpx.Client(
        transport=httpx.MockTransport(handler)
    )

    interpreter = LLMQuestionInterpreter(
        api_key="test-key",
        client=client,
    )

    draft = interpreter.interpret(
        "Why does my laptop battery drain so quickly?"
    )

    assert draft.domain == "consumer_technology"
    assert len(draft.hypotheses) == 3
    assert draft.hypotheses[0].evidence_rules[0].variable == "battery_health"
    assert draft.hypotheses[0].evidence_rules[0].effect.value == "supports"
