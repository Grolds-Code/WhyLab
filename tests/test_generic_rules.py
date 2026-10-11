from whylab.domain.models import (
    ComparisonOperator,
    EvidenceEffect,
    EvidenceRule,
    Observation,
)
from whylab.reasoning.generic_rules import evaluate_evidence_rule
from whylab.reasoning.rules import EvidenceDirection


def test_numeric_rule_supports_hypothesis():
    rule = EvidenceRule(
        variable="battery_health",
        operator=ComparisonOperator.LTE,
        value=60,
        unit="percent",
        effect=EvidenceEffect.SUPPORTS,
        reason="Low battery health supports battery degradation.",
    )
    observation = Observation(
        variable="battery_health",
        value=54,
        unit="percent",
    )

    result = evaluate_evidence_rule(rule, observation)

    assert result.direction == EvidenceDirection.SUPPORTS
    assert result.reason == rule.reason


def test_numeric_rule_can_contradict_hypothesis():
    rule = EvidenceRule(
        variable="soil_moisture",
        operator=ComparisonOperator.GTE,
        value=60,
        unit="percent",
        effect=EvidenceEffect.CONTRADICTS,
        reason="Moist soil weakens the underwatering explanation.",
    )
    observation = Observation(
        variable="soil_moisture",
        value=67,
        unit="percent",
    )

    result = evaluate_evidence_rule(rule, observation)

    assert result.direction == EvidenceDirection.CONTRADICTS


def test_equality_rule_handles_boolean_observation():
    rule = EvidenceRule(
        variable="charger_detected",
        operator=ComparisonOperator.EQ,
        value=False,
        effect=EvidenceEffect.SUPPORTS,
        reason="Failure to detect the charger supports a charging-path problem.",
    )
    observation = Observation(
        variable="charger_detected",
        value=False,
    )

    result = evaluate_evidence_rule(rule, observation)

    assert result.direction == EvidenceDirection.SUPPORTS


def test_nonmatching_variable_is_neutral():
    rule = EvidenceRule(
        variable="packet_loss",
        operator=ComparisonOperator.GTE,
        value=10,
        unit="percent",
        effect=EvidenceEffect.SUPPORTS,
        reason="High packet loss supports network instability.",
    )
    observation = Observation(
        variable="latency",
        value=200,
        unit="ms",
    )

    result = evaluate_evidence_rule(rule, observation)

    assert result.direction == EvidenceDirection.NEUTRAL


def test_unit_mismatch_is_neutral():
    rule = EvidenceRule(
        variable="temperature",
        operator=ComparisonOperator.GTE,
        value=90,
        unit="celsius",
        effect=EvidenceEffect.SUPPORTS,
        reason="High temperature supports thermal throttling.",
    )
    observation = Observation(
        variable="temperature",
        value=194,
        unit="fahrenheit",
    )

    result = evaluate_evidence_rule(rule, observation)

    assert result.direction == EvidenceDirection.NEUTRAL
