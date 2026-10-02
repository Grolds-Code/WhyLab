from whylab.domain.models import Hypothesis, Observation
from whylab.reasoning.falsification import check_underwatering_falsifier


def test_high_soil_moisture_triggers_underwatering_falsifier():
    hypothesis = Hypothesis(
        id="H1",
        claim="The plant is underwatered",
    )

    observation = Observation(
        variable="soil_moisture",
        value=67,
        unit="percent",
    )

    result = check_underwatering_falsifier(
        hypothesis,
        observation,
    )

    assert result.triggered is True
    assert "inconsistent" in result.reason.lower()


def test_low_soil_moisture_does_not_trigger_underwatering_falsifier():
    hypothesis = Hypothesis(
        id="H1",
        claim="The plant is underwatered",
    )

    observation = Observation(
        variable="soil_moisture",
        value=20,
        unit="percent",
    )

    result = check_underwatering_falsifier(
        hypothesis,
        observation,
    )

    assert result.triggered is False


def test_underwatering_falsifier_ignores_other_hypotheses():
    hypothesis = Hypothesis(
        id="H2",
        claim="Excess water is causing root stress",
    )

    observation = Observation(
        variable="soil_moisture",
        value=67,
        unit="percent",
    )

    result = check_underwatering_falsifier(
        hypothesis,
        observation,
    )

    assert result.triggered is False
