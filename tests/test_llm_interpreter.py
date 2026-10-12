import json

import httpx

from whylab.interpreters.llm import (
    LLMQuestionInterpreter,
    _normalize_generated_rule_values,
)


def test_llm_interpreter_builds_unseen_investigation():
    draft_payload = {
        "domain": "consumer_technology",
        "variables": [
            "battery_health",
            "background_power_usage",
            "screen_brightness_percent",
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
                    },
                    {
                        "variable": "battery_health",
                        "operator": ">=",
                        "value": 90,
                        "unit": "percent",
                        "effect": "contradicts",
                        "reason": (
                            "High measured battery health weakens substantial "
                            "battery degradation."
                        ),
                        "provenance": "model_generated_assumption",
                        "rationale": (
                            "This threshold is an investigation assumption."
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
                "evidence_rules": [
                    {
                        "variable": "background_power_usage",
                        "operator": ">=",
                        "value": 5,
                        "unit": "watts",
                        "effect": "supports",
                        "reason": (
                            "Elevated background power usage supports excessive "
                            "background software activity."
                        ),
                        "provenance": "model_generated_assumption",
                        "rationale": (
                            "This threshold is an investigation assumption."
                        ),
                    },
                    {
                        "variable": "background_power_usage",
                        "operator": "<=",
                        "value": 1,
                        "unit": "watts",
                        "effect": "contradicts",
                        "reason": (
                            "Low background power usage weakens the background "
                            "software explanation."
                        ),
                        "provenance": "model_generated_assumption",
                        "rationale": (
                            "This threshold is an investigation assumption."
                        ),
                    }
                ],
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
                "evidence_rules": [
                    {
                        "variable": "screen_brightness_percent",
                        "operator": ">=",
                        "value": 80,
                        "unit": "percent",
                        "effect": "supports",
                        "reason": (
                            "High screen brightness supports elevated display "
                            "power draw."
                        ),
                        "provenance": "model_generated_assumption",
                        "rationale": (
                            "This threshold is an investigation assumption."
                        ),
                    },
                    {
                        "variable": "screen_brightness_percent",
                        "operator": "<=",
                        "value": 30,
                        "unit": "percent",
                        "effect": "contradicts",
                        "reason": (
                            "Low screen brightness weakens elevated display "
                            "power draw as the primary explanation."
                        ),
                        "provenance": "model_generated_assumption",
                        "rationale": (
                            "This threshold is an investigation assumption."
                        ),
                    }
                ],
            },
        ],
    }

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)

        assert body["model"] == "openrouter/free"
        assert body["messages"][-1]["content"] == (
            "Why does my laptop battery drain so quickly?"
        )
        assert body["tools"][0]["function"]["name"] == (
            "create_investigation_draft"
        )
        assert body["tool_choice"]["function"]["name"] == (
            "create_investigation_draft"
        )
        assert request.headers["Authorization"] == "Bearer test-key"

        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "tool_calls": [
                                {
                                    "function": {
                                        "name": "create_investigation_draft",
                                        "arguments": json.dumps(draft_payload),
                                    }
                                }
                            ]
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



def test_normalizes_unambiguous_numeric_rule_values():
    payload = {
        "hypotheses": [
            {
                "evidence_rules": [
                    {
                        "operator": "<",
                        "value": "20 Mbps",
                        "unit": None,
                    },
                    {
                        "operator": ">=",
                        "value": "70%",
                        "unit": None,
                    },
                    {
                        "operator": "<",
                        "value": "about 20 Mbps",
                        "unit": None,
                    },
                ]
            }
        ]
    }

    normalized = _normalize_generated_rule_values(payload)
    rules = normalized["hypotheses"][0]["evidence_rules"]

    assert rules[0]["value"] == 20
    assert rules[0]["unit"] == "Mbps"

    assert rules[1]["value"] == 70
    assert rules[1]["unit"] == "percent"

    # Ambiguous prose must not be guessed or silently coerced.
    assert rules[2]["value"] == "about 20 Mbps"
    assert rules[2]["unit"] is None
