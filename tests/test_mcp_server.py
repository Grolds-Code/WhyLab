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
