from whylab.domain.models import Hypothesis, Investigation, Observation
from whylab.storage.sqlite import InvestigationStore


def test_investigation_survives_save_and_reload(tmp_path):
    database_path = tmp_path / "whylab.db"
    store = InvestigationStore(database_path)

    investigation = Investigation(
        id="INV-PERSIST-001",
        question="Why is my basil wilting?",
        domain="gardening",
        hypotheses=[
            Hypothesis(
                id="H1",
                claim="The plant is underwatered",
            )
        ],
        observations=[
            Observation(
                variable="soil_moisture",
                value=67,
                unit="percent",
            )
        ],
    )

    store.save(investigation)

    restored = store.get("INV-PERSIST-001")

    assert restored is not None
    assert restored.id == investigation.id
    assert restored.question == investigation.question
    assert len(restored.hypotheses) == 1
    assert len(restored.observations) == 1
    assert restored.observations[0].value == 67
