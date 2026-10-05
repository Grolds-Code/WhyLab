import asyncio

from whylab.mcp.server import create_mcp_server


def test_mcp_server_exposes_core_whylab_tools(tmp_path):
    server = create_mcp_server(tmp_path / "whylab.db")

    tools = asyncio.run(server.list_tools())

    tool_names = {
        tool.name
        for tool in tools
    }

    assert tool_names == {
        "start_investigation",
        "record_observation",
        "get_evidence_report",
        "get_next_test",
    }


def test_mcp_tools_run_complete_investigation_flow(tmp_path):
    import json

    async def run_flow():
        server = create_mcp_server(tmp_path / "whylab.db")

        start_result = await server.call_tool(
            "start_investigation",
            {
                "investigation_id": "INV-MCP-FLOW-001",
                "question": (
                    "My basil keeps wilting even though I'm watering it. "
                    "Help me figure out why."
                ),
            },
        )

        assert start_result.is_error is False

        investigation = json.loads(
            start_result.content[0].text
        )

        assert investigation["id"] == "INV-MCP-FLOW-001"
        assert len(investigation["hypotheses"]) == 3

        observation_result = await server.call_tool(
            "record_observation",
            {
                "investigation_id": "INV-MCP-FLOW-001",
                "variable": "soil_moisture",
                "value": 67,
                "unit": "percent",
            },
        )

        assert observation_result.is_error is False

        updated = json.loads(
            observation_result.content[0].text
        )

        assert updated["hypotheses"][0]["state"] == "contradicted"
        assert updated["hypotheses"][1]["state"] == "supported"
        assert updated["hypotheses"][2]["state"] == "open"

        report_result = await server.call_tool(
            "get_evidence_report",
            {
                "investigation_id": "INV-MCP-FLOW-001",
            },
        )

        assert report_result.is_error is False

        report = json.loads(
            report_result.content[0].text
        )

        assert report["contradicted"][0]["id"] == "H1"
        assert report["supported"][0]["id"] == "H2"
        assert report["open"][0]["id"] == "H3"

        next_test_result = await server.call_tool(
            "get_next_test",
            {
                "investigation_id": "INV-MCP-FLOW-001",
            },
        )

        assert next_test_result.is_error is False

        next_test = json.loads(
            next_test_result.content[0].text
        )

        assert next_test["variable_changed"] == "drainage"
        assert "H2" in next_test["target_hypotheses"]
        assert "H3" in next_test["target_hypotheses"]

    asyncio.run(run_flow())


def test_mcp_server_calls_persistence_hook_after_save(tmp_path):
    calls = []

    server = create_mcp_server(
        tmp_path / "whylab.db",
        after_save=lambda: calls.append("committed"),
    )

    async def run_flow():
        await server.call_tool(
            "start_investigation",
            {
                "investigation_id": "INV-PERSIST-MCP-001",
                "question": (
                    "My basil keeps wilting even though I'm watering it."
                ),
            },
        )

    asyncio.run(run_flow())

    assert calls == ["committed"]
