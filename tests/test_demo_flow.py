from fastapi.testclient import TestClient

from whylab.api.app import create_app


def test_complete_basil_investigation_demo_flow(tmp_path):
    app = create_app(tmp_path / "whylab.db")
    client = TestClient(app)

    # 1. User starts with only a natural-language "why" question.
    create_response = client.post(
        "/investigations/from-question",
        json={
            "investigation_id": "INV-DEMO-001",
            "question": (
                "My basil keeps wilting even though I'm watering it. "
                "Help me figure out why."
            ),
        },
    )

    assert create_response.status_code == 201

    investigation = create_response.json()

    assert len(investigation["hypotheses"]) == 3
    assert [
        hypothesis["state"]
        for hypothesis in investigation["hypotheses"]
    ] == [
        "open",
        "open",
        "open",
    ]

    # 2. User returns with a real-world observation.
    observation_response = client.post(
        "/investigations/INV-DEMO-001/observations",
        json={
            "variable": "soil_moisture",
            "value": 67,
            "unit": "percent",
        },
    )

    assert observation_response.status_code == 200

    updated = observation_response.json()

    assert updated["hypotheses"][0]["state"] == "contradicted"
    assert updated["hypotheses"][1]["state"] == "supported"
    assert updated["hypotheses"][2]["state"] == "open"

    # 3. WhyLab explains what the evidence currently supports.
    report_response = client.get(
        "/investigations/INV-DEMO-001/report",
    )

    assert report_response.status_code == 200

    report = report_response.json()

    assert report["observation_count"] == 1
    assert report["contradicted"][0]["id"] == "H1"
    assert report["supported"][0]["id"] == "H2"
    assert report["open"][0]["id"] == "H3"

    # 4. WhyLab chooses the next discriminating test.
    next_test_response = client.get(
        "/investigations/INV-DEMO-001/next-test",
    )

    assert next_test_response.status_code == 200

    next_test = next_test_response.json()

    assert next_test["variable_changed"] == "drainage"
    assert "H2" in next_test["target_hypotheses"]
    assert "H3" in next_test["target_hypotheses"]

    # 5. The investigation remains persisted for a later session.
    persisted_response = client.get(
        "/investigations/INV-DEMO-001",
    )

    assert persisted_response.status_code == 200
    assert len(persisted_response.json()["observations"]) == 1
