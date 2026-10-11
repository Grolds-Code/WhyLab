from whylab.domain.models import (
    ComparisonOperator,
    EvidenceEffect,
    EvidenceRule,
    EpistemicState,
    Hypothesis,
    Investigation,
    Observation,
)
from whylab.reasoning.investigation import apply_observation_to_investigation


def test_generic_rule_updates_unseen_battery_hypothesis():
    investigation = Investigation(
        id="battery-1",
        question="Why does my laptop battery drain so quickly?",
        domain="consumer_technology",
        hypotheses=[
            Hypothesis(
                id="H1",
                claim="The battery has substantially degraded",
                evidence_rules=[
                    EvidenceRule(
                        variable="battery_health",
                        operator=ComparisonOperator.LTE,
                        value=60,
                        unit="percent",
                        effect=EvidenceEffect.SUPPORTS,
                        reason=(
                            "Low measured battery health supports substantial "
                            "battery degradation."
                        ),
                        provenance="test_assumption",
                    )
                ],
            ),
            Hypothesis(
                id="H2",
                claim="Background software is consuming excessive power",
            ),
        ],
        variables=["battery_health"],
    )

    observation = Observation(
        variable="battery_health",
        value=54,
        unit="percent",
    )

    updated = apply_observation_to_investigation(
        investigation,
        observation,
    )

    assert updated.hypotheses[0].state == EpistemicState.SUPPORTED
    assert len(updated.hypotheses[0].evidence_for) == 1
    assert updated.hypotheses[1].state == EpistemicState.OPEN
