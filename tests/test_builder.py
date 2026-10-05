from whylab.application.builder import (
    InvestigationBuilder,
    InvestigationDraft,
    HypothesisDraft,
)


class FakeQuestionInterpreter:
    def interpret(self, question: str) -> InvestigationDraft:
        return InvestigationDraft(
            domain="gardening",
            variables=[
                "soil_moisture",
                "drainage",
                "light_exposure",
            ],
            confounders=[
                "temperature",
            ],
            hypotheses=[
                HypothesisDraft(
                    claim="The plant is underwatered",
                    predictions=[
                        "Soil moisture should be low.",
                    ],
                    falsifiers=[
                        "Soil remains persistently moist while wilting continues.",
                    ],
                ),
                HypothesisDraft(
                    claim="Excess water is causing root stress",
                    predictions=[
                        "Soil should remain persistently wet.",
                    ],
                    falsifiers=[
                        "The root zone dries normally while wilting continues.",
                    ],
                ),
                HypothesisDraft(
                    claim="The plant is receiving insufficient light",
                    predictions=[
                        "The plant receives limited useful light exposure.",
                    ],
                    falsifiers=[
                        "Adequate light exposure does not improve the condition.",
                    ],
                ),
            ],
        )


def test_builder_creates_open_structured_investigation_from_question():
    builder = InvestigationBuilder(
        interpreter=FakeQuestionInterpreter(),
    )

    investigation = builder.build(
        question="My basil keeps wilting even though I'm watering it.",
        investigation_id="INV-BUILD-001",
    )

    assert investigation.id == "INV-BUILD-001"
    assert investigation.domain == "gardening"
    assert len(investigation.hypotheses) == 3
    assert investigation.variables == [
        "soil_moisture",
        "drainage",
        "light_exposure",
    ]

    assert [hypothesis.id for hypothesis in investigation.hypotheses] == [
        "H1",
        "H2",
        "H3",
    ]

    assert all(
        hypothesis.state.value == "open"
        for hypothesis in investigation.hypotheses
    )

    assert investigation.hypotheses[0].falsifiers


def test_hypothesis_draft_rejects_epistemic_state_from_interpreter():
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        HypothesisDraft.model_validate(
            {
                "claim": "The plant is underwatered",
                "state": "known",
            }
        )
