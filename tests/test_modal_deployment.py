from pathlib import Path

import whylab.deploy.modal_app as modal_app


def test_modal_asgi_factory_configures_stateless_mcp(monkeypatch, tmp_path):
    calls = {}
    database_path = tmp_path / "whylab.db"

    class FakeServer:
        def streamable_http_app(self, **kwargs):
            calls["http_kwargs"] = kwargs
            return "fake-asgi-app"

    def fake_create_mcp_server(path, after_save=None):
        calls["database_path"] = Path(path)
        calls["after_save"] = after_save
        return FakeServer()

    monkeypatch.setattr(
        modal_app,
        "create_mcp_server",
        fake_create_mcp_server,
    )

    def after_save():
        pass

    app = modal_app.build_mcp_asgi_app(
        database_path,
        after_save=after_save,
    )

    assert app == "fake-asgi-app"
    assert calls["database_path"] == database_path
    assert calls["after_save"] is after_save

    assert calls["http_kwargs"]["streamable_http_path"] == "/mcp"
    assert calls["http_kwargs"]["stateless_http"] is True
