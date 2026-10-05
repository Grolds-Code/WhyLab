from collections.abc import Callable
from contextlib import asynccontextmanager
from pathlib import Path

import modal
from mcp.server.transport_security import TransportSecuritySettings

from whylab.api.app import create_app as create_api_app
from whylab.mcp.server import create_mcp_server


APP_NAME = "whylab-mcp"
VOLUME_NAME = "whylab-data"
VOLUME_MOUNT_PATH = "/data"
DATABASE_PATH = Path(VOLUME_MOUNT_PATH) / "whylab.db"


def build_http_api_app(
    database_path: str | Path,
    after_save: Callable[[], None] | None = None,
):
    """Build WhyLab's persistent HTTP API ASGI app."""

    return create_api_app(
        database_path,
        after_save=after_save,
    )


def build_mcp_asgi_app(
    database_path: str | Path,
    after_save: Callable[[], None] | None = None,
    allowed_hosts: list[str] | None = None,
    allowed_origins: list[str] | None = None,
):
    """Build WhyLab's stateless Streamable HTTP MCP ASGI app."""

    server = create_mcp_server(
        database_path,
        after_save=after_save,
    )

    transport_security = TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=allowed_hosts or [],
        allowed_origins=allowed_origins or [],
    )

    return server.streamable_http_app(
        streamable_http_path="/mcp",
        stateless_http=True,
        transport_security=transport_security,
    )


def build_combined_asgi_app(
    database_path: str | Path,
    after_save: Callable[[], None] | None = None,
    allowed_hosts: list[str] | None = None,
    allowed_origins: list[str] | None = None,
):
    """Build one ASGI app exposing both WhyLab HTTP and MCP surfaces."""

    http_api = build_http_api_app(
        database_path,
        after_save=after_save,
    )

    mcp_api = build_mcp_asgi_app(
        database_path,
        after_save=after_save,
        allowed_hosts=allowed_hosts,
        allowed_origins=allowed_origins,
    )

    http_lifespan = http_api.router.lifespan_context
    mcp_lifespan = mcp_api.router.lifespan_context

    @asynccontextmanager
    async def combined_lifespan(app):
        async with http_lifespan(http_api):
            async with mcp_lifespan(mcp_api):
                yield

    http_api.router.lifespan_context = combined_lifespan
    http_api.mount("/", mcp_api)

    return http_api


image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install_from_pyproject("pyproject.toml")
    .add_local_python_source("whylab")
)

volume = modal.Volume.from_name(
    VOLUME_NAME,
    create_if_missing=True,
)

app = modal.App(APP_NAME)


@app.function(
    image=image,
    volumes={
        VOLUME_MOUNT_PATH: volume,
    },
    max_containers=1,
)
@modal.concurrent(max_inputs=1)
@modal.asgi_app()
def mcp_app():
    """Expose WhyLab's MCP server as a persistent Modal web endpoint."""

    volume.reload()

    return build_combined_asgi_app(
        DATABASE_PATH,
        after_save=volume.commit,
        allowed_hosts=[
            "groldotieno97--whylab-mcp-mcp-app.modal.run",
        ],
        allowed_origins=[
            "https://groldotieno97--whylab-mcp-mcp-app.modal.run",
        ],
    )
