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
