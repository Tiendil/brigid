
import fastmcp

from brigid.mcp.settings import settings

# TODO: add maximum configuration
# TODO: we may want to create an MCP per language
mcp = fastmcp.FastMCP(name=settings.name)

# ensure that everything will be loaded
from brigid.mcp import tools  # noqa: E402, F401
