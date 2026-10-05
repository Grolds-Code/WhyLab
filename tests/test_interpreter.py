import pytest

from whylab.interpreters.basil import (
    BasilQuestionInterpreter,
    UnsupportedQuestionError,
)


def test_basil_interpreter_builds_falsifiable_competing_hypotheses():
    interpreter = BasilQuestionInterpreter()

    draft = interpreter.interpret(
        "My basil keeps wilting even though I'm watering it."
    )

    assert draft.domain == "gardening"
    assert len(draft.hypotheses) == 3

    claims = [
        hypothesis.claim
        for hypothesis in draft.hypotheses
    ]

    assert claims == [
        "The plant is underwatered",
        "Excess water is causing root stress",
        "The plant is receiving insufficient light",
    ]

    assert "soil_moisture" in draft.variables
    assert "drainage" in draft.variables
    assert "light_exposure" in draft.variables

    assert all(
        hypothesis.predictions
        for hypothesis in draft.hypotheses
    )

    assert all(
        hypothesis.falsifiers
        for hypothesis in draft.hypotheses
    )


def test_basil_interpreter_rejects_unsupported_question():
    interpreter = BasilQuestionInterpreter()

    with pytest.raises(UnsupportedQuestionError):
        interpreter.interpret(
            "Why does my car make a knocking sound?"
        )
