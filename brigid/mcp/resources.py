
import fastmcp
from pydantic import Field

from typing import Literal, Annotated

from brigid.library.storage import storage


def create_resources(mcp: fastmcp.FastMCP) -> None:

    site = storage.get_site()
    site_i18n = site.languages[site.default_language]

    # TODO: improve
    domain = site.url.replace("https://", "").replace("http://", "")

    # TODO: User Elicitation if the post for the language is not found
    # TODO: unify page getting code with the api renderers?
    # TODO: should we render markdown in a special format for MCP? To support backlinks, images as resources, etc.?
    # TODO: should we add an instruction about the markdown format used in the blog?

    Language = Annotated[Literal[*site.allowed_languages], Field(description="Language code of the content")]
    Slug = Annotated[str, Field(description="Slug identifier of the blog post")]

    @mcp.resource(uri="blog://posts/{language}/{slug}.md",
                  name="post_markdown",
                  mime_type="text/markdown")
    def post_markdown(language: Language, slug: Slug) -> str | None:
        """Markdown source of the blog post with the front-matter.
        """

        if language not in site.allowed_languages:
            # TODO: send notification or error?
            return None

        if not storage.has_article(slug=slug):
            # TODO: send notification or error?
            return None

        article = storage.get_article(slug=slug)

        if language not in article.pages:
            # TODO: send notification or error?
            return None

        page = storage.get_page(id=article.pages[language])

        return page.path.read_text(encoding="utf-8")
