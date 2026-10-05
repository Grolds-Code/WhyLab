from pathlib import Path

import whylab.mcp.server as server_module


def test_mcp_cli_starts_stdio_server_with_configured_database(
    monkeypatch,
    tmp_path,
):
    database_path = tmp_path / "whylab.db"
    calls = {}

    class FakeServer:
        def run(self, transport="stdio", **kwargs):
            calls["transport"] = transport
            calls["kwargs"] = kwargs

    def fake_create_mcp_server(path):
        calls["database_path"] = Path(path)
        return FakeServer()

    monkeypatch.setenv(
        "WHYLAB_DB_PATH",
        str(database_path),
    )
    monkeypatch.setattr(
        server_module,
        "create_mcp_server",
        fake_create_mcp_server,
    )

    server_module.main()

    assert calls["database_path"] == database_path
    assert calls["transport"] == "stdio"
