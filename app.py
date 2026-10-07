from starlette.requests import Request
from starlette.responses import JSONResponse

from mcp.server.transport_security import TransportSecuritySettings
from mcp_server import mcp


@mcp.custom_route("/health", methods=["GET"])
async def health(_: Request):
    return JSONResponse({"status": "ok", "service": "SchemeSetu MCP"})


app = mcp.streamable_http_app(
    streamable_http_path="/mcp",
    stateless_http=True,
    json_response=True,
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=False
    ),
)