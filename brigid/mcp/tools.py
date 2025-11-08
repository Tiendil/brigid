
import fastmcp


def create_tools(mcp: fastmcp.FastMCP) -> None:

    @mcp.tool()
    def ping() -> str:
        return "pong"
