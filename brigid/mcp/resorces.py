
import fastmcp

from brigid.library.storage import storage


def create_resources(mcp: fastmcp.FastMCP) -> None:

    site = storage.get_site()
    site_i18n = site.languages[site.default_language]

    # TODO: improve
    domain = site.url.replace("https://", "").replace("http://", "")

    prefix = f"blog://{domain}"

    # TODO: User Elicitation if the post for the language is not found
    # TODO: unify page getting code with the api renderers?

# from typing import Annotated
# from pydantic import Field

# @mcp.tool
# def process_image(
#     image_url: Annotated[str, Field(description="URL of the image to process")],
#     resize: Annotated[bool, Field(description="Whether to resize the image")] = False,
#     width: Annotated[int, Field(description="Target width in pixels", ge=1, le=2000)] = 800,
#     format: Annotated[
#         Literal["jpeg", "png", "webp"],
#         Field(description="Output image format")
#     ] = "jpeg"
# ) -> dict:
#     """Process an image with optional resizing."""
#     # Implementation...

    # fallback: none, closest
    @mcp.resource(uri=prefix + "blog://posts/{language}/{slug}.md{?fallback}",
                  name="post_markdown",
                  mime_type="text/markdown")
    def post_markdown(language: str, slug: str, fallback: str | None = None) -> str | None:
        """
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
