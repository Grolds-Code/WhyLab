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


def test_asgi_factory_configures_transport_security(monkeypatch, tmp_path):
    calls = {}

    class FakeServer:
        def streamable_http_app(self, **kwargs):
            calls["http_kwargs"] = kwargs
            return "fake-asgi-app"

    def fake_create_mcp_server(path, after_save=None):
        return FakeServer()

    monkeypatch.setattr(
        modal_app,
        "create_mcp_server",
        fake_create_mcp_server,
    )

    host = "example.modal.run"
    origin = "https://example.modal.run"

    app = modal_app.build_mcp_asgi_app(
        tmp_path / "whylab.db",
        allowed_hosts=[host],
        allowed_origins=[origin],
    )

    assert app == "fake-asgi-app"

    security = calls["http_kwargs"]["transport_security"]

    assert security.enable_dns_rebinding_protection is True
    assert security.allowed_hosts == [host]
    assert security.allowed_origins == [origin]


def test_modal_http_api_factory_uses_persistent_store(monkeypatch, tmp_path):
    calls = {}
    database_path = tmp_path / "whylab.db"

    def fake_create_api_app(path, after_save=None):
        calls["database_path"] = Path(path)
        calls["after_save"] = after_save
        return "fake-http-api"

    monkeypatch.setattr(
        modal_app,
        "create_api_app",
        fake_create_api_app,
    )

    def after_save():
        pass

    app = modal_app.build_http_api_app(
        database_path,
        after_save=after_save,
    )

    assert app == "fake-http-api"
    assert calls["database_path"] == database_path
    assert calls["after_save"] is after_save


def test_combined_asgi_app_mounts_mcp_on_http_api(monkeypatch, tmp_path):
    calls = {}
    database_path = tmp_path / "whylab.db"

    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def noop_lifespan(app):
        yield

    class FakeRouter:
        def __init__(self):
            self.lifespan_context = noop_lifespan

    class FakeHttpApi:
        def __init__(self):
            self.router = FakeRouter()

        def mount(self, path, app):
            calls["mount_path"] = path
            calls["mounted_app"] = app

    class FakeMcpApi:
        def __init__(self):
            self.router = FakeRouter()

    fake_http_api = FakeHttpApi()
    fake_mcp_app = FakeMcpApi()

    def fake_build_http_api_app(path, after_save=None):
        calls["http_database_path"] = Path(path)
        calls["http_after_save"] = after_save
        return fake_http_api

    def fake_build_mcp_asgi_app(
        path,
        after_save=None,
        allowed_hosts=None,
        allowed_origins=None,
    ):
        calls["mcp_database_path"] = Path(path)
        calls["mcp_after_save"] = after_save
        calls["allowed_hosts"] = allowed_hosts
        calls["allowed_origins"] = allowed_origins
        return fake_mcp_app

    monkeypatch.setattr(
        modal_app,
        "build_http_api_app",
        fake_build_http_api_app,
    )
    monkeypatch.setattr(
        modal_app,
        "build_mcp_asgi_app",
        fake_build_mcp_asgi_app,
    )

    def after_save():
        pass

    app = modal_app.build_combined_asgi_app(
        database_path,
        after_save=after_save,
        allowed_hosts=["example.modal.run"],
        allowed_origins=["https://example.modal.run"],
    )

    assert app is fake_http_api
    assert calls["http_database_path"] == database_path
    assert calls["mcp_database_path"] == database_path
    assert calls["http_after_save"] is after_save
    assert calls["mcp_after_save"] is after_save
    assert calls["mount_path"] == "/"
    assert calls["mounted_app"] is fake_mcp_app
    assert calls["allowed_hosts"] == ["example.modal.run"]
    assert calls["allowed_origins"] == ["https://example.modal.run"]


def test_combined_asgi_app_runs_http_and_mcp_lifespans(monkeypatch, tmp_path):
    import asyncio
    from contextlib import asynccontextmanager

    events = []

    @asynccontextmanager
    async def http_lifespan(app):
        events.append("http-start")
        yield
        events.append("http-stop")

    @asynccontextmanager
    async def mcp_lifespan(app):
        events.append("mcp-start")
        yield
        events.append("mcp-stop")

    class FakeRouter:
        def __init__(self, lifespan_context):
            self.lifespan_context = lifespan_context

    class FakeHttpApi:
        def __init__(self):
            self.router = FakeRouter(http_lifespan)

        def mount(self, path, app):
            pass

    class FakeMcpApi:
        def __init__(self):
            self.router = FakeRouter(mcp_lifespan)

    fake_http_api = FakeHttpApi()
    fake_mcp_api = FakeMcpApi()

    monkeypatch.setattr(
        modal_app,
        "build_http_api_app",
        lambda path, after_save=None: fake_http_api,
    )

    monkeypatch.setattr(
        modal_app,
        "build_mcp_asgi_app",
        lambda path, after_save=None, allowed_hosts=None, allowed_origins=None: fake_mcp_api,
    )

    app = modal_app.build_combined_asgi_app(
        tmp_path / "whylab.db",
    )

    async def exercise_lifespan():
        async with app.router.lifespan_context(app):
            events.append("running")

    asyncio.run(exercise_lifespan())

    assert events == [
        "http-start",
        "mcp-start",
        "running",
        "mcp-stop",
        "http-stop",
    ]
