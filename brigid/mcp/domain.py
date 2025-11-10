from brigid.domain.urls import UrlsPost
from brigid.library.entities import Page
from brigid.library.storage import storage
from brigid.markdown_render.markdown_render import render_page, render_page_intro
from brigid.mcp.entities import Language, Post, PostInfo, PostMeta, RenderFormat, TagInfo


def create_post_meta(post: Page) -> PostMeta:
    article = storage.get_article(id=post.article_id)

    post_url = UrlsPost(language=post.language, slug=article.slug)

    return PostMeta(
        published_at=post.published_at,
        language=post.language,
        translated_into=set(article.pages.keys()),
        slug=article.slug,
        seo_description=post.seo_description,
        seo_image=post.seo_image,
        tags=create_tag_infos(post.language, {tag: 1 for tag in post.tags}),
        series=post.series,
        type=storage.get_article(id=post.article_id).type,
        http_url=post_url.url(),
    )


def create_post_info(post: Page, render_format: RenderFormat) -> PostInfo:
    meta = create_post_meta(post)

    match render_format:
        case RenderFormat.markdown:
            intro_body = post.intro
        case RenderFormat.html:
            render_context = render_page_intro(post)
            assert render_context.content
            intro_body = render_context.content
        case _:
            raise ValueError(f"Unsupported render format: {render_format}")

    return PostInfo(
        meta=meta, title=post.title, intro_format=render_format, intro_body=intro_body, has_more=post.has_more
    )


def create_post(post: Page, render_format: RenderFormat) -> Post:
    meta = create_post_meta(post)

    match render_format:
        case RenderFormat.markdown:
            body = post.body
        case RenderFormat.html:
            render_context = render_page(post)
            assert render_context.content
            body = render_context.content
        case _:
            raise ValueError(f"Unsupported render format: {render_format}")

    return Post(meta=meta, title=post.title, body_format=render_format, body=body)


def create_tag_infos(language: Language, tag_count: dict[str, int]) -> list[TagInfo]:
    site = storage.get_site()

    return [
        TagInfo(tag=tag, name=site.languages[language].tags_translations[tag], count=count)
        for tag, count in tag_count.items()
    ]
