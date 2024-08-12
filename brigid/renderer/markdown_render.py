import markdown

from brigid.core import logging
from brigid.library.entities import Page
from brigid.library.storage import storage
from brigid.renderer.context import RenderContext, markdown_context, render_context
from brigid.renderer.processors.collection_block import CollectionBlockExtension
from brigid.renderer.processors.external_links import EXTERNAL_LINK_RE, ExternalLinkInlineProcessor
from brigid.renderer.processors.header_anchors import HeaderAnchorsExtension
from brigid.renderer.processors.images_block import ImagesBlockExtension
from brigid.renderer.processors.internal_links import INTERNAL_LINK_RE, InternalLinkInlineProcessor
from brigid.renderer.processors.old_image_markup_validation import IMAGE_LINK_RE, ImageInlineValidator
from brigid.renderer.processors.snippets import SnippetExtension
from brigid.renderer.processors.youtube_block import YouTubeBlockExtension

logger = logging.get_module_logger()

_renderers: list[markdown.Markdown] = []


def _construct() -> markdown.Markdown:

    configs = {
        "pymdownx.tilde": {"smart_delete": True, "subscript": True},
    }

    renderer = markdown.Markdown(
        extensions=[
            ImagesBlockExtension(),
            YouTubeBlockExtension(),
            HeaderAnchorsExtension(),
            CollectionBlockExtension(),
            SnippetExtension(dedent_subsections=True),
            "md_in_html",
            "pymdownx.betterem",
            "pymdownx.superfences",
            "pymdownx.saneheaders",
            "pymdownx.tilde",
            "pymdownx.blocks.details",
            "pymdownx.blocks.admonition",
            "markdown.extensions.tables",
        ],
        extension_configs=configs,
    )

    # all images must be processed by ImagesBlockExtension
    # because it gives more control over the output and more validation
    renderer.inlinePatterns.deregister("image_link")
    renderer.inlinePatterns.deregister("image_reference")
    renderer.inlinePatterns.deregister("short_image_ref")

    # remove classic links processor
    renderer.inlinePatterns.deregister("link")

    # add modified processors
    renderer.inlinePatterns.register(ImageInlineValidator(IMAGE_LINK_RE, renderer), "image_link_validator", 160)
    renderer.inlinePatterns.register(ExternalLinkInlineProcessor(EXTERNAL_LINK_RE, renderer), "external_link", 160)
    renderer.inlinePatterns.register(InternalLinkInlineProcessor(INTERNAL_LINK_RE, renderer), "internal_link", 160)

    return renderer


def renderer(index: int) -> markdown.Markdown:
    while len(_renderers) <= index:
        _renderers.append(_construct())

    return _renderers[index]


def render(text: str) -> str:
    context = render_context.get()

    content = renderer(context.renderer).convert(text)

    if not context.errors:
        return content

    logger.warning("markdown_render_errors", errors_number=len(context.errors))

    return repr(context.errors[0])


def render_page(page: Page) -> RenderContext:
    # TODO: reload only optionally

    context = RenderContext(page=page, article=storage.get_article(id=page.article_id), renderer=0)

    with markdown_context(context):
        context.content = render(page.body)

    return context


def render_page_intro(page: Page) -> RenderContext:
    # TODO: reload only optionally

    context = RenderContext(page=page, article=storage.get_article(id=page.article_id), renderer=0)

    with markdown_context(context):
        context.content = render(page.intro)

    return context


def render_text(text: str) -> RenderContext:
    prev_context = render_context.get()

    if prev_context is None:
        raise NotImplementedError("render_text must be called within render context")

    context = RenderContext(
        page=prev_context.page,
        article=prev_context.article,
        renderer=prev_context.renderer + 1,
    )

    with markdown_context(context):
        context.content = render(text)

    return context
