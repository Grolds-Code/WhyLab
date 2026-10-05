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
