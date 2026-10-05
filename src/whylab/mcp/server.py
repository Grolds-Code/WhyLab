from pathlib import Path

from mcp.server import MCPServer

from whylab.application.builder import InvestigationBuilder
from whylab.application.service import WhyLabService
from whylab.interpreters.basil import BasilQuestionInterpreter
from whylab.storage.sqlite import InvestigationStore
from whylab.tools.facade import WhyLabTools


def create_mcp_server(
    database_path: str | Path,
) -> MCPServer:
    """Create the WhyLab MCP server."""

    store = InvestigationStore(database_path)

    builder = InvestigationBuilder(
        interpreter=BasilQuestionInterpreter(),
    )

    service = WhyLabService(
        store,
        builder=builder,
    )

    tools = WhyLabTools(service)

    server = MCPServer(
        name="whylab",
        title="WhyLab",
        description=(
            "Persistent scientific reasoning tools for falsifiable "
            "real-world investigations."
        ),
        version="0.1.0",
    )

    @server.tool(
        name="start_investigation",
        description=(
            "Start a persistent scientific investigation from a natural-language "
            "why question."
        ),
    )
    def start_investigation(
        investigation_id: str,
        question: str,
    ):
        return tools.start_investigation(
            investigation_id=investigation_id,
            question=question,
        )

    @server.tool(
        name="record_observation",
        description=(
            "Record real-world evidence and update competing hypotheses."
        ),
    )
    def record_observation(
        investigation_id: str,
        variable: str,
        value: str | int | float | bool,
        unit: str | None = None,
    ):
        return tools.record_observation(
            investigation_id=investigation_id,
            variable=variable,
            value=value,
            unit=unit,
        )

    @server.tool(
        name="get_evidence_report",
        description=(
            "Summarize what the current evidence supports, contradicts, "
            "or leaves open."
        ),
    )
    def get_evidence_report(
        investigation_id: str,
    ):
        return tools.get_evidence_report(
            investigation_id,
        )

    @server.tool(
        name="get_next_test",
        description=(
            "Recommend the next discriminating test for the investigation."
        ),
    )
    def get_next_test(
        investigation_id: str,
    ):
        return tools.get_next_test(
            investigation_id,
        )

    return server


def main() -> None:
    """Run WhyLab as a standalone MCP server over stdio."""

    import os

    database_path = os.environ.get(
        "WHYLAB_DB_PATH",
        "whylab.db",
    )

    server = create_mcp_server(database_path)
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
