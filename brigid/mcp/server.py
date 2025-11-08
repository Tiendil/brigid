
import fastapi
import fastmcp

from brigid.core import utils
from brigid.library.storage import storage
from brigid.mcp.tools import create_tools


def construct_instructions() -> str:
    site = storage.get_site()
    site_i18n = site.languages[site.default_language]

    is_multi_lingual = len(site.allowed_languages) > 1

    source = [
        f"This is a personal assistant for readers of the blog {site.url}.",
        f"The blog title '{site_i18n.title}'.",
        f"The blog description is: '{site_i18n.subtitle}'",
        f"The blog author is '{site_i18n.author}'.",
        f"The license of the blog content is {site_i18n.license}." if site_i18n.license else None,
        f"The blog is multi-lingual and supports the following languages: {', '.join(site.allowed_languages)}." if is_multi_lingual else None,
        "Each piece of content in the blog can be available in multiple languages." if is_multi_lingual else None,
        f"The default language of the blog is {site.default_language}." if len(site.allowed_languages) > 1 else None,
        f"The content of the blog is stored in the repository: {site.content_repository}." if site.content_repository else None,
    ]

    source = [instruction for instruction in source if instruction]

    return '\n'.join(source)


# We create MCP instance dymanically because:
# - we need site configs that are loaded at runtime
# - we may need to construct multiple MCPs (per language) in the future
def create_mcp(app: fastapi.FastAPI) -> fastapi.FastAPI:

    site = storage.get_site()
    site_i18n = site.languages[site.default_language]

    # TODO: website_url, icons (fastmcp 2.14.0+)
    mcp = fastmcp.FastMCP(name=site_i18n.title,
                          instructions=construct_instructions(),
                          version=utils.version(),
                          auth=None,
                          strict_input_validation=False,  # allow Pydantic to be flexible
                          )

    create_tools(mcp)

    mcp_app = mcp.http_app(path="/")
    app.mount("/mcp", mcp_app)

    return mcp_app
