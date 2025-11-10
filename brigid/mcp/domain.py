from brigid.library.entities import Page
from brigid.library.storage import storage
from brigid.mcp.entities import PageInfo


def page_info(page: Page) -> PageInfo:
    article = storage.get_article(id=page.article_id)

    # TODO: similar posts
    # TODO: series info

    return PageInfo(
        published_at=page.published_at,
        language=page.language,
        slug=article.slug,
        title=page.title,
        seo_description=page.seo_description,
        seo_image=page.seo_image,
        tags=page.tags,
        series=page.series,
        type=article.type,
        intro=page.intro,
        has_more=page.has_more,
    )
