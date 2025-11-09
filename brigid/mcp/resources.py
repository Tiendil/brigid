
import fastmcp
from pydantic import Field

from typing import Literal, Annotated

from brigid.library.storage import storage
from brigid.markdown_render.markdown_render import render_page


def create_resources(mcp: fastmcp.FastMCP) -> None:

    site = storage.get_site()
    site_i18n = site.languages[site.default_language]

    # TODO: User Elicitation if the post for the language is not found
    # TODO: unify page getting code with the api renderers?
    # TODO: should we render markdown in a special format for MCP? To support backlinks, images as resources, etc.?
    # TODO: should we add an instruction about the markdown format used in the blog?
    # TODO: add mcp url constructors, like with http urls?
    # TODO: maybe we should has on unviersal resource, that returns
    #       all info and representations about the post with meta info?

    Language = Annotated[Literal[*site.allowed_languages], Field(description="Language code of the content")]
    Slug = Annotated[str, Field(description="Slug identifier of the blog post")]

    @mcp.resource(uri="blog://posts/{language}/{slug}.md",
                  name="post_markdown",
                  mime_type="text/markdown")
    def post_markdown(language: Language, slug: Slug) -> str | None:
        """Markdown source of the blog post with the front-matter.
        """

        # TODO: front-matter from the file is generally not full — it doesn't contain default values
        #       maybe we should reconstruct it form the actual page info?

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

    @mcp.resource(uri="blog://posts/{language}/{slug}.html",
                  name="post_html",
                  mime_type="text/html")
    def post_html(language: Language, slug: Slug) -> str | None:
        """HTML-rendered content of the blog post.
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

        render_context = render_page(page)

        return render_context.content
