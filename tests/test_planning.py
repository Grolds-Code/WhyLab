from whylab.domain.models import Hypothesis, Investigation, Observation
from whylab.reasoning.investigation import apply_observation_to_investigation
from whylab.reasoning.planning import recommend_next_test


def test_recommends_drainage_test_after_wet_soil_weakens_underwatering():
    investigation = Investigation(
        id="INV-003",
        question="Why is my basil wilting even though I'm watering it?",
        domain="gardening",
        hypotheses=[
            Hypothesis(
                id="H1",
                claim="The plant is underwatered",
            ),
            Hypothesis(
                id="H2",
                claim="Excess water is causing root stress",
            ),
            Hypothesis(
                id="H3",
                claim="The plant is receiving insufficient light",
            ),
        ],
    )

    observation = Observation(
        variable="soil_moisture",
        value=67,
        unit="percent",
    )

    apply_observation_to_investigation(investigation, observation)

    experiment = recommend_next_test(investigation)

    assert experiment is not None
    assert experiment.variable_changed == "drainage"
    assert "H2" in experiment.target_hypotheses
    assert "H3" in experiment.target_hypotheses
    assert len(experiment.predicted_results) >= 2


def test_does_not_recommend_drainage_test_before_evidence():
    investigation = Investigation(
        id="INV-004",
        question="Why is my basil wilting even though I'm watering it?",
        domain="gardening",
        hypotheses=[
            Hypothesis(
                id="H1",
                claim="The plant is underwatered",
            ),
            Hypothesis(
                id="H2",
                claim="Excess water is causing root stress",
            ),
            Hypothesis(
                id="H3",
                claim="The plant is receiving insufficient light",
            ),
        ],
    )

    experiment = recommend_next_test(investigation)

    assert experiment is None


def test_generic_planner_selects_discriminating_measurement():
    from whylab.domain.models import (
        ComparisonOperator,
        EvidenceEffect,
        EvidenceRule,
    )

    investigation = Investigation(
        id="INV-BATTERY-PLAN-001",
        question="Why does my laptop battery drain so quickly?",
        domain="consumer_technology",
        hypotheses=[
            Hypothesis(
                id="H1",
                claim="The battery has substantially degraded",
                evidence_rules=[
                    EvidenceRule(
                        variable="battery_health_percent",
                        operator=ComparisonOperator.LTE,
                        value=60,
                        unit="percent",
                        effect=EvidenceEffect.SUPPORTS,
                        reason="Low battery health supports degradation.",
                    ),
                    EvidenceRule(
                        variable="battery_health_percent",
                        operator=ComparisonOperator.GTE,
                        value=90,
                        unit="percent",
                        effect=EvidenceEffect.CONTRADICTS,
                        reason="High battery health weakens degradation.",
                    ),
                ],
            ),
            Hypothesis(
                id="H2",
                claim="The battery itself remains healthy",
                evidence_rules=[
                    EvidenceRule(
                        variable="battery_health_percent",
                        operator=ComparisonOperator.GTE,
                        value=90,
                        unit="percent",
                        effect=EvidenceEffect.SUPPORTS,
                        reason="High battery health supports a healthy battery.",
                    ),
                    EvidenceRule(
                        variable="battery_health_percent",
                        operator=ComparisonOperator.LTE,
                        value=60,
                        unit="percent",
                        effect=EvidenceEffect.CONTRADICTS,
                        reason="Low battery health weakens a healthy-battery explanation.",
                    ),
                ],
            ),
        ],
        variables=["battery_health_percent"],
    )

    experiment = recommend_next_test(investigation)

    assert experiment is not None
    assert experiment.observations_required == [
        "battery_health_percent (percent)"
    ]
    assert set(experiment.target_hypotheses) == {"H1", "H2"}
    assert "H1" in experiment.predicted_results
    assert "H2" in experiment.predicted_results
