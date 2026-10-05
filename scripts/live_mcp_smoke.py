"""Smoke-test the deployed WhyLab MCP scientific reasoning loop."""

import argparse
import asyncio
import json

from mcp import Client


def parse_result(result):
    if result.is_error:
        raise RuntimeError(f"MCP tool returned an error: {result}")

    for item in result.content:
        text = getattr(item, "text", None)
        if text:
            return json.loads(text)

    raise RuntimeError("MCP tool returned no JSON text content")


async def run_smoke_test(url: str) -> None:
    investigation_id = "whylab-live-smoke"

    async with Client(url) as client:
        tools = await client.list_tools()
        tool_names = {tool.name for tool in tools.tools}

        expected_tools = {
            "start_investigation",
            "record_observation",
            "get_evidence_report",
            "get_next_test",
        }
        assert tool_names == expected_tools, tool_names
        print("PASS: live server exposes the four WhyLab tools")

        investigation = parse_result(
            await client.call_tool(
                "start_investigation",
                {
                    "investigation_id": investigation_id,
                    "question": (
                        "My basil keeps wilting even though I'm watering it. "
                        "Help me figure out why."
                    ),
                },
            )
        )

        states = {
            hypothesis["id"]: hypothesis["state"]
            for hypothesis in investigation["hypotheses"]
        }
        assert states == {
            "H1": "open",
            "H2": "open",
            "H3": "open",
        }, states
        print("PASS: investigation starts with all hypotheses open")

        updated = parse_result(
            await client.call_tool(
                "record_observation",
                {
                    "investigation_id": investigation_id,
                    "variable": "soil_moisture",
                    "value": 67,
                    "unit": "percent",
                },
            )
        )

        states = {
            hypothesis["id"]: hypothesis["state"]
            for hypothesis in updated["hypotheses"]
        }
        assert states == {
            "H1": "contradicted",
            "H2": "supported",
            "H3": "open",
        }, states
        print("PASS: deterministic evidence update is correct")

        report = parse_result(
            await client.call_tool(
                "get_evidence_report",
                {"investigation_id": investigation_id},
            )
        )

        assert [item["id"] for item in report["supported"]] == ["H2"]
        assert [item["id"] for item in report["contradicted"]] == ["H1"]
        assert [item["id"] for item in report["open"]] == ["H3"]
        assert report["observation_count"] == 1
        print("PASS: evidence report is correct")

        next_test = parse_result(
            await client.call_tool(
                "get_next_test",
                {"investigation_id": investigation_id},
            )
        )

        assert next_test["target_hypotheses"] == ["H2", "H3"]
        assert next_test["variable_changed"] == "drainage"
        assert next_test["duration_days"] == 3
        print("PASS: next discriminating experiment is correct")

    print("\nWhyLab live MCP smoke test PASSED")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--url",
        required=True,
        help="Full Streamable HTTP MCP endpoint, including /mcp",
    )
    args = parser.parse_args()

    asyncio.run(run_smoke_test(args.url))


if __name__ == "__main__":
    main()
