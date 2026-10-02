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


def test_soil_moisture_rule_respects_explicit_configuration():
    from whylab.reasoning.config import SoilMoistureRuleConfig

    observation = Observation(
        variable="soil_moisture",
        value=67,
        unit="percent",
    )

    default_result = evaluate_soil_moisture_for_underwatering(observation)

    custom_config = SoilMoistureRuleConfig(
        supports_underwatering_at_or_below=20,
        contradicts_underwatering_at_or_above=80,
        provenance="Custom test configuration",
    )

    custom_result = evaluate_soil_moisture_for_underwatering(
        observation,
        config=custom_config,
    )

    assert default_result.direction.value == "contradicts"
    assert custom_result.direction.value == "neutral"
    assert custom_config.provenance == "Custom test configuration"
