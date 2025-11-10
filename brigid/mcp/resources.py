
import fastmcp
from pydantic import Field

from typing import Literal, Annotated

from brigid.library.entities import Page
from brigid.library.storage import storage
from brigid.markdown_render.markdown_render import render_page
from brigid.mcp.entities import PageInfo, Language, Slug
from brigid.mcp import utils, domain


# TODO: we may want to switch resource for tools, since tools provide data sceme
def create_resources(mcp: fastmcp.FastMCP) -> None:

    site = storage.get_site()
    # site_i18n = site.languages[site.default_language]

    # TODO: User Elicitation if the post for the language is not found
    # TODO: unify page getting code with the api renderers?
    # TODO: should we render markdown in a special format for MCP? To support backlinks, images as resources, etc.?
    # TODO: should we add an instruction about the markdown format used in the blog?
    # TODO: add mcp url constructors, like with http urls?
    # TODO: maybe we should has on unviersal resource, that returns
    #       all info and representations about the post with meta info?

    def get_page(language: str, slug: str) -> Page | None:
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

        return storage.get_page(id=article.pages[language])

    @mcp.resource(uri="blog://posts/{language}/{slug}.md",
                  name="post_markdown",
                  mime_type="text/markdown")
    def post_markdown(language: Language, slug: Slug) -> str | None:
        """Markdown source of the blog post with the front-matter.
        """

        # TODO: front-matter from the file is generally not full — it doesn't contain default values
        #       maybe we should reconstruct it form the actual page info?

        if (page := get_page(language=language, slug=slug)) is None:
            return None

        return page.path.read_text(encoding="utf-8")

    @mcp.resource(uri="blog://posts/{language}/{slug}.html",
                  name="post_html",
                  mime_type="text/html")
    def post_html(language: Language, slug: Slug) -> str | None:
        """HTML-rendered content of the blog post.
        """

        if (page := get_page(language=language, slug=slug)) is None:
            return None

        render_context = render_page(page)

        return render_context.content

    post_meta_description = '\n'.join([
        "JSON metadata of the blog post.",
        "",
        "Return data description:",
        "",
        PageInfo.format_specification()
    ])

    @mcp.resource(uri="blog://posts/{language}/{slug}/meta.json",
                  name="post_meta",
                  description=post_meta_description,
                  mime_type="application/json")
    def post_meta(language: Language, slug: Slug) -> PageInfo:
        if (page := get_page(language=language, slug=slug)) is None:
            return None

        return domain.page_info(page)

    @mcp.resource(uri="blog://tags/{language}/meta.json",
                  name="tags_list",
                  description="JSON dict of all tags used in the blog with verbose names. Keys are tag identifiers, values are translated tag names.",
                  mime_type="application/json")
    def tags_list(language: Language) -> dict[str, str]:
        return site.languages[language].tags_translations
