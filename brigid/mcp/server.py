
import fastapi
import fastmcp

from brigid.core import utils
from brigid.mcp.settings import settings
from brigid.mcp.tools import create_tools


# We create MCP instance dymanically because:
# - we need site configs that are loaded at runtime
# - we may need to construct multiple MCPs (per language) in the future
def create_mcp(app: fastapi.FastAPI) -> fastapi.FastAPI:

    instructions = """
    Do smth
    """

    # TODO: add maximum configuration
    # TODO: we may want to create an MCP per language
    # TODO: website_url, icons (fastmcp 2.14.0+)
    mcp = fastmcp.FastMCP(name=settings.name,
                          instructions=instructions,
                          version=utils.version(),
                          auth=None,
                          strict_input_validation=False,  # allow Pydantic to be flexible
                          )

    create_tools(mcp)

    mcp_app = mcp.http_app(path="/")
    app.mount("/mcp", mcp_app)

    return mcp_app
