import json

import httpx
import pytest

from whylab.application.builder import InvestigationDraft
from whylab.interpreters.llm import (
    LLMInterpreterError,
    LLMQuestionInterpreter,
    _normalize_generated_rule_values,
    _validate_generated_draft,
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



def test_normalizes_stringified_structured_arrays():
    payload = {
        "hypotheses": json.dumps(
            [
                {
                    "claim": "Evening congestion",
                    "evidence_rules": json.dumps(
                        [
                            {
                                "variable": "wifi_speed_mbps",
                                "operator": "<",
                                "value": "20 Mbps",
                                "unit": None,
                                "effect": "supports",
                                "reason": "Low speed supports congestion.",
                                "provenance": "model_generated_assumption",
                                "rationale": "Investigation assumption.",
                            }
                        ]
                    ),
                }
            ]
        )
    }

    normalized = _normalize_generated_rule_values(payload)

    assert isinstance(normalized["hypotheses"], list)
    assert isinstance(
        normalized["hypotheses"][0]["evidence_rules"],
        list,
    )

    rule = normalized["hypotheses"][0]["evidence_rules"][0]

    assert rule["value"] == 20
    assert rule["unit"] == "Mbps"



def test_rejects_conflicting_effects_for_same_predicate():
    draft = InvestigationDraft.model_validate(
        {
            "domain": "home_networking",
            "variables": ["signal"],
            "confounders": [],
            "hypotheses": [
                {
                    "claim": "Hypothesis one",
                    "predictions": [],
                    "falsifiers": [],
                    "confounders": [],
                    "uncertainties": [],
                    "evidence_rules": [
                        {
                            "variable": "signal",
                            "operator": ">=",
                            "value": 1,
                            "unit": None,
                            "effect": "supports",
                            "reason": "Signal supports H1.",
                            "provenance": "model_generated_assumption",
                            "rationale": "Test assumption.",
                        },
                        {
                            "variable": "signal",
                            "operator": ">=",
                            "value": 1,
                            "unit": None,
                            "effect": "contradicts",
                            "reason": "Same signal contradicts H1.",
                            "provenance": "model_generated_assumption",
                            "rationale": "Test assumption.",
                        },
                    ],
                },
                {
                    "claim": "Hypothesis two",
                    "predictions": [],
                    "falsifiers": [],
                    "confounders": [],
                    "uncertainties": [],
                    "evidence_rules": [
                        {
                            "variable": "signal",
                            "operator": ">=",
                            "value": 2,
                            "unit": None,
                            "effect": "supports",
                            "reason": "Higher signal supports H2.",
                            "provenance": "model_generated_assumption",
                            "rationale": "Test assumption.",
                        },
                        {
                            "variable": "signal",
                            "operator": "<",
                            "value": 2,
                            "unit": None,
                            "effect": "contradicts",
                            "reason": "Lower signal contradicts H2.",
                            "provenance": "model_generated_assumption",
                            "rationale": "Test assumption.",
                        },
                    ],
                },
                {
                    "claim": "Hypothesis three",
                    "predictions": [],
                    "falsifiers": [],
                    "confounders": [],
                    "uncertainties": [],
                    "evidence_rules": [
                        {
                            "variable": "signal",
                            "operator": ">=",
                            "value": 3,
                            "unit": None,
                            "effect": "supports",
                            "reason": "Higher signal supports H3.",
                            "provenance": "model_generated_assumption",
                            "rationale": "Test assumption.",
                        },
                        {
                            "variable": "signal",
                            "operator": "<",
                            "value": 3,
                            "unit": None,
                            "effect": "contradicts",
                            "reason": "Lower signal contradicts H3.",
                            "provenance": "model_generated_assumption",
                            "rationale": "Test assumption.",
                        },
                    ],
                },
            ],
        }
    )

    with pytest.raises(
        LLMInterpreterError,
        match="same evidence predicate",
    ):
        _validate_generated_draft(draft)


def test_interpreter_trims_overgenerated_hypotheses_to_four():
    draft_payload = {
        "domain": "home_networking",
        "variables": ["signal"],
        "confounders": [],
        "hypotheses": [
            {
                "claim": f"Hypothesis {index}",
                "predictions": [],
                "falsifiers": [],
                "confounders": [],
                "uncertainties": [],
                "evidence_rules": [
                    {
                        "variable": "signal",
                        "operator": ">=",
                        "value": index,
                        "unit": None,
                        "effect": "supports",
                        "reason": f"Signal supports hypothesis {index}.",
                        "provenance": "model_generated_assumption",
                        "rationale": "Test assumption.",
                    },
                    {
                        "variable": "signal",
                        "operator": "<",
                        "value": index,
                        "unit": None,
                        "effect": "contradicts",
                        "reason": f"Signal contradicts hypothesis {index}.",
                        "provenance": "model_generated_assumption",
                        "rationale": "Test assumption.",
                    },
                ],
            }
            for index in range(1, 7)
        ],
    }

    def handler(request: httpx.Request) -> httpx.Response:
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

    client = httpx.Client(transport=httpx.MockTransport(handler))

    interpreter = LLMQuestionInterpreter(
        api_key="test-key",
        client=client,
    )

    draft = interpreter.interpret(
        "Why does my Wi-Fi slow down every evening?"
    )

    assert len(draft.hypotheses) == 4
    assert [hypothesis.claim for hypothesis in draft.hypotheses] == [
        "Hypothesis 1",
        "Hypothesis 2",
        "Hypothesis 3",
        "Hypothesis 4",
    ]


def test_interpreter_ignores_unknown_hypothesis_fields():
    draft_payload = {
        "domain": "consumer_technology",
        "variables": ["battery_health"],
        "confounders": [],
        "hypotheses": [
            {
                "claim": f"Hypothesis {index}",
                "predictions": [],
                "falsifiers": [],
                "confounders": [],
                "uncertainties": [],
                "contradicts": [
                    {
                        "variable": "battery_health",
                        "note": "Model-added field outside WhyLab's contract.",
                    }
                ],
                "evidence_rules": [
                    {
                        "variable": "battery_health",
                        "operator": "<=",
                        "value": 60 + index,
                        "unit": "percent",
                        "effect": "supports",
                        "reason": f"Supports hypothesis {index}.",
                        "provenance": "model_generated_assumption",
                        "rationale": "Test assumption.",
                    },
                    {
                        "variable": "battery_health",
                        "operator": ">=",
                        "value": 90 + index,
                        "unit": "percent",
                        "effect": "contradicts",
                        "reason": f"Contradicts hypothesis {index}.",
                        "provenance": "model_generated_assumption",
                        "rationale": "Test assumption.",
                    },
                ],
            }
            for index in range(1, 5)
        ],
    }

    def handler(request: httpx.Request) -> httpx.Response:
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

    client = httpx.Client(transport=httpx.MockTransport(handler))

    interpreter = LLMQuestionInterpreter(
        api_key="test-key",
        client=client,
    )

    draft = interpreter.interpret(
        "Why does my laptop battery drain quickly?"
    )

    assert len(draft.hypotheses) == 4
    assert draft.hypotheses[0].claim == "Hypothesis 1"


def test_interpreter_accepts_structured_content_without_tool_calls():
    draft_payload = {
        "domain": "home_networking",
        "variables": ["wifi_speed_mbps"],
        "confounders": [],
        "hypotheses": [
            {
                "claim": f"Hypothesis {index}",
                "predictions": [],
                "falsifiers": [],
                "confounders": [],
                "uncertainties": [],
                "evidence_rules": [
                    {
                        "variable": "wifi_speed_mbps",
                        "operator": "<=",
                        "value": 10 + index,
                        "unit": "Mbps",
                        "effect": "supports",
                        "reason": f"Supports hypothesis {index}.",
                        "provenance": "model_generated_assumption",
                        "rationale": "Test assumption.",
                    },
                    {
                        "variable": "wifi_speed_mbps",
                        "operator": ">=",
                        "value": 90 + index,
                        "unit": "Mbps",
                        "effect": "contradicts",
                        "reason": f"Contradicts hypothesis {index}.",
                        "provenance": "model_generated_assumption",
                        "rationale": "Test assumption.",
                    },
                ],
            }
            for index in range(1, 5)
        ],
    }

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(draft_payload),
                        }
                    }
                ]
            },
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    interpreter = LLMQuestionInterpreter(
        api_key="test-key",
        client=client,
    )

    draft = interpreter.interpret(
        "Why does my Wi-Fi slow down every evening?"
    )

    assert draft.domain == "home_networking"
    assert len(draft.hypotheses) == 4


def test_interpreter_discards_hypothesis_missing_complementary_effect():
    draft_payload = {
        "domain": "home_networking",
        "variables": ["wifi_speed_mbps"],
        "confounders": [],
        "hypotheses": [
            {
                "claim": f"Hypothesis {index}",
                "predictions": [],
                "falsifiers": [],
                "confounders": [],
                "uncertainties": [],
                "evidence_rules": [
                    {
                        "variable": "wifi_speed_mbps",
                        "operator": "<=",
                        "value": 10 + index,
                        "unit": "Mbps",
                        "effect": "supports",
                        "reason": f"Supports hypothesis {index}.",
                        "provenance": "model_generated_assumption",
                        "rationale": "Test assumption.",
                    },
                    {
                        "variable": "wifi_speed_mbps",
                        "operator": ">=",
                        "value": 90 + index,
                        "unit": "Mbps",
                        "effect": (
                            "supports"
                            if index == 4
                            else "contradicts"
                        ),
                        "reason": f"Second rule for hypothesis {index}.",
                        "provenance": "model_generated_assumption",
                        "rationale": "Test assumption.",
                    },
                ],
            }
            for index in range(1, 5)
        ],
    }

    def handler(request: httpx.Request) -> httpx.Response:
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

    client = httpx.Client(transport=httpx.MockTransport(handler))
    interpreter = LLMQuestionInterpreter(
        api_key="test-key",
        client=client,
    )

    draft = interpreter.interpret(
        "Why does my Wi-Fi slow down every evening?"
    )

    assert len(draft.hypotheses) == 3
    assert [hypothesis.claim for hypothesis in draft.hypotheses] == [
        "Hypothesis 1",
        "Hypothesis 2",
        "Hypothesis 3",
    ]
