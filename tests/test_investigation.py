from whylab.domain.models import Hypothesis, Investigation, Observation
from whylab.reasoning.investigation import apply_observation_to_investigation


def test_duplicate_observation_is_not_recorded_twice():
    investigation = Investigation(
        id="INV-001",
        question="Why is my basil wilting even though I'm watering it?",
        domain="gardening",
        hypotheses=[
            Hypothesis(
                id="H1",
                claim="The plant is underwatered",
            )
        ],
    )

    observation = Observation(
        variable="soil_moisture",
        value=67,
        unit="percent",
    )

    apply_observation_to_investigation(investigation, observation)
    apply_observation_to_investigation(investigation, observation)

    hypothesis = investigation.hypotheses[0]

    assert len(investigation.observations) == 1
    assert hypothesis.state.value == "contradicted"
    assert len(hypothesis.evidence_against) == 1


def test_one_observation_updates_competing_hypotheses_differently():
    investigation = Investigation(
        id="INV-002",
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
        ],
    )

    observation = Observation(
        variable="soil_moisture",
        value=67,
        unit="percent",
    )

    apply_observation_to_investigation(investigation, observation)

    underwatering = investigation.hypotheses[0]
    root_stress = investigation.hypotheses[1]

    assert underwatering.state.value == "contradicted"
    assert len(underwatering.evidence_against) == 1

    assert root_stress.state.value == "supported"
    assert len(root_stress.evidence_for) == 1

    assert len(investigation.observations) == 1
