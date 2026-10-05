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
