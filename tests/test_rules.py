from whylab.domain.models import Hypothesis, Observation
from whylab.reasoning.evidence import apply_rule_result
from whylab.reasoning.rules import evaluate_soil_moisture_for_underwatering


def test_high_soil_moisture_automatically_contradicts_underwatering():
    hypothesis = Hypothesis(
        id="H1",
        claim="The plant is underwatered",
    )

    observation = Observation(
        variable="soil_moisture",
        value=67,
        unit="percent",
    )

    result = evaluate_soil_moisture_for_underwatering(observation)

    apply_rule_result(
        hypothesis=hypothesis,
        observation=observation,
        direction=result.direction,
        reason=result.reason,
    )

    assert hypothesis.state.value == "contradicted"
    assert len(hypothesis.evidence_against) == 1
    assert len(hypothesis.evidence_for) == 0
    assert "soil_moisture=67 percent" in hypothesis.evidence_against[0]
