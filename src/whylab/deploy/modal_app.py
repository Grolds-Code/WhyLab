from collections.abc import Callable
from pathlib import Path

import modal

from whylab.mcp.server import create_mcp_server


APP_NAME = "whylab-mcp"
VOLUME_NAME = "whylab-data"
VOLUME_MOUNT_PATH = "/data"
DATABASE_PATH = Path(VOLUME_MOUNT_PATH) / "whylab.db"


def build_mcp_asgi_app(
    database_path: str | Path,
    after_save: Callable[[], None] | None = None,
):
    """Build WhyLab's stateless Streamable HTTP MCP ASGI app."""

    server = create_mcp_server(
        database_path,
        after_save=after_save,
    )

    return server.streamable_http_app(
        streamable_http_path="/mcp",
        stateless_http=True,
    )


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

    return build_mcp_asgi_app(
        DATABASE_PATH,
        after_save=volume.commit,
    )
