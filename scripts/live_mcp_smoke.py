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



def satisfying_value(rule):
    """Return a simple numeric value that satisfies a generated rule."""

    operator = rule["operator"]
    value = rule["value"]

    if operator == ">":
        return value + 1
    if operator == ">=":
        return value
    if operator == "<":
        return value - 1
    if operator == "<=":
        return value
    if operator == "==":
        return value
    if operator == "!=":
        return value + 1

    raise AssertionError(f"Unsupported smoke-test operator: {operator}")


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
                        "My Wi-Fi gets slow every evening even though it works "
                        "well during the day. Help me figure out why."
                    ),
                },
            )
        )

        hypotheses = investigation["hypotheses"]
        assert len(hypotheses) == 4, hypotheses
        assert all(
            hypothesis["state"] == "open"
            for hypothesis in hypotheses
        ), hypotheses
        assert investigation["variables"], investigation
        print("PASS: investigation starts with four open hypotheses")

        target_hypothesis = hypotheses[0]
        support_rule = next(
            rule
            for rule in target_hypothesis["evidence_rules"]
            if rule["effect"] == "supports"
        )

        updated = parse_result(
            await client.call_tool(
                "record_observation",
                {
                    "investigation_id": investigation_id,
                    "variable": support_rule["variable"],
                    "value": satisfying_value(support_rule),
                    "unit": support_rule.get("unit"),
                },
            )
        )

        states = {
            hypothesis["id"]: hypothesis["state"]
            for hypothesis in updated["hypotheses"]
        }
        assert states[target_hypothesis["id"]] == "supported", states
        assert any(
            hypothesis["evidence_for"]
            for hypothesis in updated["hypotheses"]
            if hypothesis["id"] == target_hypothesis["id"]
        ), updated
        print("PASS: deterministic evidence update is correct")

        report = parse_result(
            await client.call_tool(
                "get_evidence_report",
                {"investigation_id": investigation_id},
            )
        )

        supported_ids = {
            item["id"]
            for item in report["supported"]
        }
        assert target_hypothesis["id"] in supported_ids, report
        assert report["observation_count"] == 1, report
        print("PASS: evidence report is correct")

        next_test = parse_result(
            await client.call_tool(
                "get_next_test",
                {"investigation_id": investigation_id},
            )
        )

        assert next_test["target_hypotheses"], next_test
        assert next_test["observations_required"], next_test
        assert next_test["predicted_results"], next_test
        assert all(
            hypothesis_id in {
                hypothesis["id"]
                for hypothesis in updated["hypotheses"]
            }
            for hypothesis_id in next_test["target_hypotheses"]
        ), next_test
        print("PASS: next discriminating experiment is valid")

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
