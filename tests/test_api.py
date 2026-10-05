from fastapi.testclient import TestClient

from whylab.api.app import create_app


def test_create_and_retrieve_investigation_through_api(tmp_path):
    app = create_app(tmp_path / "whylab.db")
    client = TestClient(app)

    payload = {
        "id": "INV-API-001",
        "question": "Why is my basil wilting even though I'm watering it?",
        "domain": "gardening",
        "hypotheses": [
            {
                "id": "H1",
                "claim": "The plant is underwatered",
            },
            {
                "id": "H2",
                "claim": "Excess water is causing root stress",
            },
            {
                "id": "H3",
                "claim": "The plant is receiving insufficient light",
            },
        ],
    }

    create_response = client.post(
        "/investigations",
        json=payload,
    )

    assert create_response.status_code == 201
    assert create_response.json()["id"] == "INV-API-001"

    get_response = client.get(
        "/investigations/INV-API-001",
    )

    assert get_response.status_code == 200

    restored = get_response.json()

    assert restored["id"] == "INV-API-001"
    assert restored["question"] == payload["question"]
    assert len(restored["hypotheses"]) == 3
    assert restored["hypotheses"][0]["state"] == "open"


def test_record_observation_updates_and_persists_hypotheses(tmp_path):
    app = create_app(tmp_path / "whylab.db")
    client = TestClient(app)

    investigation_payload = {
        "id": "INV-API-002",
        "question": "Why is my basil wilting even though I'm watering it?",
        "domain": "gardening",
        "hypotheses": [
            {
                "id": "H1",
                "claim": "The plant is underwatered",
            },
            {
                "id": "H2",
                "claim": "Excess water is causing root stress",
            },
            {
                "id": "H3",
                "claim": "The plant is receiving insufficient light",
            },
        ],
    }

    client.post(
        "/investigations",
        json=investigation_payload,
    )

    observation_response = client.post(
        "/investigations/INV-API-002/observations",
        json={
            "variable": "soil_moisture",
            "value": 67,
            "unit": "percent",
        },
    )

    assert observation_response.status_code == 200

    updated = observation_response.json()

    assert len(updated["observations"]) == 1
    assert updated["hypotheses"][0]["state"] == "contradicted"
    assert updated["hypotheses"][1]["state"] == "supported"
    assert updated["hypotheses"][2]["state"] == "open"

    persisted_response = client.get(
        "/investigations/INV-API-002",
    )

    persisted = persisted_response.json()

    assert len(persisted["observations"]) == 1
    assert persisted["hypotheses"][0]["state"] == "contradicted"
    assert persisted["hypotheses"][1]["state"] == "supported"


def test_api_returns_evidence_report_and_next_test(tmp_path):
    app = create_app(tmp_path / "whylab.db")
    client = TestClient(app)

    investigation_payload = {
        "id": "INV-API-003",
        "question": "Why is my basil wilting even though I'm watering it?",
        "domain": "gardening",
        "hypotheses": [
            {
                "id": "H1",
                "claim": "The plant is underwatered",
            },
            {
                "id": "H2",
                "claim": "Excess water is causing root stress",
            },
            {
                "id": "H3",
                "claim": "The plant is receiving insufficient light",
            },
        ],
    }

    client.post(
        "/investigations",
        json=investigation_payload,
    )

    client.post(
        "/investigations/INV-API-003/observations",
        json={
            "variable": "soil_moisture",
            "value": 67,
            "unit": "percent",
        },
    )

    report_response = client.get(
        "/investigations/INV-API-003/report",
    )

    assert report_response.status_code == 200

    report = report_response.json()

    assert len(report["contradicted"]) == 1
    assert report["contradicted"][0]["id"] == "H1"
    assert len(report["supported"]) == 1
    assert report["supported"][0]["id"] == "H2"
    assert len(report["open"]) == 1
    assert report["open"][0]["id"] == "H3"

    next_test_response = client.get(
        "/investigations/INV-API-003/next-test",
    )

    assert next_test_response.status_code == 200

    next_test = next_test_response.json()

    assert next_test["variable_changed"] == "drainage"
    assert "H2" in next_test["target_hypotheses"]
    assert "H3" in next_test["target_hypotheses"]


def test_create_investigation_from_natural_language_question(tmp_path):
    from whylab.application.builder import (
        HypothesisDraft,
        InvestigationBuilder,
        InvestigationDraft,
    )

    class FakeQuestionInterpreter:
        def interpret(self, question: str) -> InvestigationDraft:
            return InvestigationDraft(
                domain="gardening",
                variables=[
                    "soil_moisture",
                    "drainage",
                    "light_exposure",
                ],
                hypotheses=[
                    HypothesisDraft(
                        claim="The plant is underwatered",
                    ),
                    HypothesisDraft(
                        claim="Excess water is causing root stress",
                    ),
                    HypothesisDraft(
                        claim="The plant is receiving insufficient light",
                    ),
                ],
            )

    builder = InvestigationBuilder(
        interpreter=FakeQuestionInterpreter(),
    )

    app = create_app(
        tmp_path / "whylab.db",
        builder=builder,
    )
    client = TestClient(app)

    response = client.post(
        "/investigations/from-question",
        json={
            "investigation_id": "INV-API-NL-001",
            "question": (
                "My basil keeps wilting even though I'm watering it."
            ),
        },
    )

    assert response.status_code == 201

    investigation = response.json()

    assert investigation["id"] == "INV-API-NL-001"
    assert investigation["domain"] == "gardening"
    assert len(investigation["hypotheses"]) == 3

    assert [
        hypothesis["state"]
        for hypothesis in investigation["hypotheses"]
    ] == [
        "open",
        "open",
        "open",
    ]

    persisted = client.get(
        "/investigations/INV-API-NL-001",
    )

    assert persisted.status_code == 200
    assert persisted.json()["question"] == (
        "My basil keeps wilting even though I'm watering it."
    )


def test_default_api_configuration_handles_basil_question(tmp_path):
    app = create_app(tmp_path / "whylab.db")
    client = TestClient(app)

    response = client.post(
        "/investigations/from-question",
        json={
            "investigation_id": "INV-DEFAULT-001",
            "question": (
                "My basil keeps wilting even though I'm watering it."
            ),
        },
    )

    assert response.status_code == 201

    investigation = response.json()

    assert investigation["id"] == "INV-DEFAULT-001"
    assert investigation["domain"] == "gardening"
    assert len(investigation["hypotheses"]) == 3

    assert [
        hypothesis["state"]
        for hypothesis in investigation["hypotheses"]
    ] == [
        "open",
        "open",
        "open",
    ]


def test_default_api_rejects_unsupported_question_cleanly(tmp_path):
    app = create_app(tmp_path / "whylab.db")
    client = TestClient(app)

    response = client.post(
        "/investigations/from-question",
        json={
            "investigation_id": "INV-UNSUPPORTED-001",
            "question": "Why does my car make a knocking sound?",
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "WhyLab v0.1 currently supports basil-wilting investigations only."
    )


def test_api_invokes_after_save_hook_for_persistent_write(tmp_path):
    calls = []

    def after_save():
        calls.append("saved")

    app = create_app(
        tmp_path / "whylab.db",
        after_save=after_save,
    )
    client = TestClient(app)

    response = client.post(
        "/investigations/from-question",
        json={
            "investigation_id": "INV-HOOK-001",
            "question": (
                "My basil keeps wilting even though I'm watering it."
            ),
        },
    )

    assert response.status_code == 201
    assert calls == ["saved"]
