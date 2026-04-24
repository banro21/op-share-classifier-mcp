import json
import logging

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from starlette.responses import JSONResponse
from starlette.routing import Route

from .classify import classify

logger = logging.getLogger(__name__)

mcp = FastMCP(
    name="op-share-classifier",
    streamable_http_path="/mcp",
    stateless_http=True,
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=False,
    ),
)


@mcp.tool()
async def classify_share_link(url: str) -> str:
    """Classify a 1Password share link as public or email-restricted
    without opening it in a browser. Uses the share-service API with a
    retrieval token derived from the URL fragment. WARNING: a `public`
    classification consumes one view on the share link. Callers MUST
    dedup by hash before invoking."""
    result = await classify(url)
    return json.dumps(result)


def create_app():
    """Return FastMCP's ASGI app as top-level so its lifespan runs
    (mounting under another Starlette would drop the lifespan and
    break the session manager). Append /healthz onto its router."""
    app = mcp.streamable_http_app()

    async def healthz(request):
        return JSONResponse({"ok": True})

    app.router.routes.append(Route("/healthz", healthz, methods=["GET"]))
    return app
