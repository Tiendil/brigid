import os

import fastapi
import fastmcp
from fastmcp.server.http import StarletteWithLifespan

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
        (
            f"The blog is multi-lingual and supports the following languages: {', '.join(site.allowed_languages)}."
            if is_multi_lingual
            else None
        ),
        "Each piece of content in the blog can be available in multiple languages." if is_multi_lingual else None,
        f"The default language of the blog is {site.default_language}." if len(site.allowed_languages) > 1 else None,
        (
            f"The content of the blog is stored in the repository: {site.content_repository}."
            if site.content_repository
            else None
        ),
        "The posts in this blog is organized by tags. Use them to find content related to specific topics.",
        "The posts in this blog connected to similar posts, like in a graph. Use this to find related content.",
        (
            "Some posts in this blog are organized into series. "
            "Use them to explore complex topics step by step and to read posts in order."
        ),
        (
            "Some posts in this blog are ogranized into collections. "
            "Use them to explore posts highlighted by the author by specific properties."
        ),
        (
            "Besides posts, the blog contains static pages. "
            "You can look on them as on the important sections/collections of the blog."
        ),
    ]

    source = [instruction for instruction in source if instruction]

    return "\n".join(source)  # type: ignore


# We create MCP instance dymanically because:
# - we need site configs that are loaded at runtime
# - we may need to construct multiple MCPs (per language) in the future
def create_mcp(app: fastapi.FastAPI) -> StarletteWithLifespan:

    site = storage.get_site()
    site_i18n = site.languages[site.default_language]

    # There are issues with continuing session after server restart
    # For example, OpenAI does not handle it well
    # TODO: try to rollback to stateful sessions in the future
    if "FASTMCP_STATELESS_HTTP" not in os.environ:
        os.environ["FASTMCP_STATELESS_HTTP"] = "1"

    # TODO: website_url, icons (fastmcp 2.14.0+)
    mcp = fastmcp.FastMCP(
        name=site_i18n.title,
        instructions=construct_instructions(),
        version=utils.version(),
        auth=None,
        strict_input_validation=False,  # allow Pydantic to be flexible
    )

    create_tools(mcp)

    mcp_app = mcp.http_app(path="/")
    app.mount("/mcp", mcp_app)

    return mcp_app
