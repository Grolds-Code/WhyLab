from whylab.domain.models import Hypothesis, Observation
from whylab.reasoning.evidence import (
    add_contradicting_evidence,
    add_supporting_evidence,
)


def test_observation_can_support_one_hypothesis_and_contradict_another():
    observation = Observation(
        variable="soil_moisture",
        value=67,
        unit="percent",
    )

    underwatering = Hypothesis(
        id="H1",
        claim="The plant is underwatered",
    )

    root_stress = Hypothesis(
        id="H2",
        claim="Excess water is causing root stress",
    )

    add_contradicting_evidence(
        underwatering,
        observation,
        "Moist soil weakens the underwatering explanation.",
    )

    add_supporting_evidence(
        root_stress,
        observation,
        "Persistently moist soil is consistent with excess water.",
    )

    assert len(underwatering.evidence_against) == 1
    assert len(underwatering.evidence_for) == 0

    assert len(root_stress.evidence_for) == 1
    assert len(root_stress.evidence_against) == 0

    assert "soil_moisture=67 percent" in underwatering.evidence_against[0]
    assert "soil_moisture=67 percent" in root_stress.evidence_for[0]
