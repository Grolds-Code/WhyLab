from whylab.domain.models import Hypothesis, Observation
from whylab.reasoning.evidence import (
    add_contradicting_evidence,
    add_supporting_evidence,
    update_epistemic_state,
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


def test_epistemic_state_becomes_supported_with_support_only():
    observation = Observation(
        variable="soil_moisture",
        value=67,
        unit="percent",
    )

    hypothesis = Hypothesis(
        id="H1",
        claim="Excess water is causing root stress",
    )

    add_supporting_evidence(
        hypothesis,
        observation,
        "Persistently moist soil supports excess water.",
    )

    update_epistemic_state(hypothesis)

    assert hypothesis.state.value == "supported"


def test_epistemic_state_becomes_contradicted_with_contradiction_only():
    observation = Observation(
        variable="soil_moisture",
        value=67,
        unit="percent",
    )

    hypothesis = Hypothesis(
        id="H2",
        claim="The plant is underwatered",
    )

    add_contradicting_evidence(
        hypothesis,
        observation,
        "Moist soil weakens underwatering.",
    )

    update_epistemic_state(hypothesis)

    assert hypothesis.state.value == "contradicted"


def test_epistemic_state_remains_open_with_mixed_evidence():
    observation = Observation(
        variable="soil_moisture",
        value=67,
        unit="percent",
    )

    hypothesis = Hypothesis(
        id="H3",
        claim="Insufficient light is reducing plant health",
    )

    add_supporting_evidence(
        hypothesis,
        observation,
        "This observation is somewhat consistent with the hypothesis.",
    )

    add_contradicting_evidence(
        hypothesis,
        observation,
        "The observation does not uniquely support this hypothesis.",
    )

    update_epistemic_state(hypothesis)

    assert hypothesis.state.value == "open"
