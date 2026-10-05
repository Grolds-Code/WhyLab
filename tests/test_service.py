from whylab.application.service import WhyLabService
from whylab.domain.models import Hypothesis, Investigation, Observation
from whylab.storage.sqlite import InvestigationStore


def test_service_runs_persistent_investigation_workflow(tmp_path):
    store = InvestigationStore(tmp_path / "whylab.db")
    service = WhyLabService(store)

    investigation = Investigation(
        id="INV-SERVICE-001",
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

    service.create_investigation(investigation)

    service.record_observation(
        investigation.id,
        Observation(
            variable="soil_moisture",
            value=67,
            unit="percent",
        ),
    )

    restored = service.get_investigation(investigation.id)

    assert restored is not None
    assert len(restored.observations) == 1
    assert restored.hypotheses[0].state.value == "contradicted"
    assert restored.hypotheses[1].state.value == "supported"
    assert restored.hypotheses[2].state.value == "open"

    report = service.get_evidence_report(investigation.id)

    assert report is not None
    assert len(report.contradicted) == 1
    assert len(report.supported) == 1
    assert len(report.open) == 1

    next_test = service.recommend_next_test(investigation.id)

    assert next_test is not None
    assert next_test.variable_changed == "drainage"
