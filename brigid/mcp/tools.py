
from brigid.mcp.server import mcp


@mcp.tool()
def ping() -> str:
    return "pong"
