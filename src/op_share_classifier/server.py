import hmac
import json
import logging
import os

from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

from .classify import classify

logger = logging.getLogger(__name__)


class BearerAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, token: str):
        super().__init__(app)
        self.token = token

    async def dispatch(self, request, call_next):
        if request.url.path == "/healthz":
            return await call_next(request)
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return JSONResponse({"error": "unauthorized"}, status_code=401)
        provided = auth[7:]
        if not hmac.compare_digest(provided, self.token):
            return JSONResponse({"error": "unauthorized"}, status_code=401)
        return await call_next(request)


async def healthz(request):
    return JSONResponse({"ok": True})


def create_app() -> Starlette:
    auth_token = os.environ.get("MCP_AUTH_TOKEN")
    if not auth_token:
        raise RuntimeError("MCP_AUTH_TOKEN environment variable must be set")

    mcp = FastMCP("op-share-classifier")

    @mcp.tool()
    async def classify_share_link(url: str) -> str:
        """Classify a 1Password share link as public or email-restricted
        without opening it in a browser. Uses the share-service API
        with a retrieval token derived from the URL fragment.
        WARNING: a `public` classification consumes one view on the
        share link. Callers MUST dedup by hash before invoking."""
        result = await classify(url)
        return json.dumps(result)

    mcp_app = mcp.streamable_http_app()

    app = Starlette(
        routes=[
            Route("/healthz", healthz),
            Mount("/", app=mcp_app),
        ],
        middleware=[Middleware(BearerAuthMiddleware, token=auth_token)],
    )
    return app
