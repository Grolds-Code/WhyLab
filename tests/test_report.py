from whylab.domain.models import Hypothesis, Investigation, Observation
from whylab.reasoning.investigation import apply_observation_to_investigation
from whylab.reasoning.report import generate_evidence_report


def test_evidence_report_groups_hypotheses_by_state():
    investigation = Investigation(
        id="INV-001",
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
                uncertainties=[
                    "Drainage quality has not yet been measured."
                ],
            ),
        ],
    )

    observation = Observation(
        variable="soil_moisture",
        value=67,
        unit="percent",
    )

    apply_observation_to_investigation(
        investigation,
        observation,
    )

    report = generate_evidence_report(investigation)

    assert report.observation_count == 1
    assert len(report.contradicted) == 1
    assert report.contradicted[0].id == "H1"

    assert len(report.open) == 0

    assert len(report.supported) == 1
    assert report.supported[0].id == "H2"
