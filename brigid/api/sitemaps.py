import datetime
import xml.etree.ElementTree as ET  # noqa: S405

from brigid.domain.urls import UrlsPost, UrlsRoot, UrlsTags
from brigid.library.storage import storage


def get_last_published_at(language) -> datetime.datetime | None:
    last_published_at = None

    # TODO: here we look at all posts, but we should look at all sources of blog
    #       including configs & static files
    for page in storage.last_pages(language=language, only_posts=True):
        if last_published_at is None or page.published_at > last_published_at:
            last_published_at = page.published_at

    return last_published_at


def build_sitemap_xml() -> str:

    site = storage.get_site()

    attributes = {
        "xmlns": "http://www.sitemaps.org/schemas/sitemap/0.9",
        "xmlns:xhtml": "http://www.w3.org/1999/xhtml",
    }

    sitemap = ET.Element("urlset", **attributes)  # type: ignore[arg-type]

    for language in site.allowed_languages:
        for page in storage.last_pages(language=language, only_posts=False):
            add_page_url(sitemap, page)

    for language in site.allowed_languages:
        add_index_url(sitemap, language)

    for language in site.allowed_languages:
        add_pagination_urls(sitemap, language)

    return ET.tostring(sitemap, encoding="unicode")


def add_index_url(sitemap, language) -> None:

    site = storage.get_site()

    url = ET.SubElement(sitemap, "url")

    root_url = UrlsRoot(language=language)

    loc = ET.SubElement(url, "loc")
    loc.text = root_url.url()

    last_published_at = get_last_published_at(language)

    # could be none for a new blog
    if last_published_at is not None:
        lastmod = ET.SubElement(url, "lastmod")
        lastmod.text = last_published_at.isoformat()

    priority = ET.SubElement(url, "priority")
    priority.text = "1.0"

    if len(site.allowed_languages) > 1:
        add_language_variants(url, root_url, site.allowed_languages)


def add_pagination_urls(sitemap, language) -> None:

    # add only index with no tags filter
    pagination_urls = UrlsTags(language=language, page=1, required_tags=[], excluded_tags=[])

    if pagination_urls.total_pages == 1:
        return

    last_published_at = get_last_published_at(language)

    while pagination_urls.page <= pagination_urls.total_pages:
        pagination_urls = pagination_urls.move_page(+1)

        url = ET.SubElement(sitemap, "url")

        loc = ET.SubElement(url, "loc")
        loc.text = pagination_urls.url()

        if last_published_at is not None:
            lastmod = ET.SubElement(url, "lastmod")
            lastmod.text = last_published_at.isoformat()

        priority = ET.SubElement(url, "priority")
        priority.text = "1.0"

        # do not add language variants for pagination urls
        # because sets of posts for each language will differ
        # => pages will differ


def add_page_url(sitemap, page) -> None:

    article = storage.get_article(id=page.article_id)

    url = ET.SubElement(sitemap, "url")

    page_url = UrlsPost(language=page.language, slug=article.slug)

    loc = ET.SubElement(url, "loc")
    loc.text = page_url.url()

    lastmod = ET.SubElement(url, "lastmod")
    lastmod.text = page.published_at.isoformat()

    priority = ET.SubElement(url, "priority")
    priority.text = "1.0"

    site = storage.get_site()

    if len(article.pages) > 1:
        languages = [language for language in site.allowed_languages if language in article.pages]
        add_language_variants(url, page_url, languages)


def add_language_variants(url, page_url, languages) -> None:
    for language in languages:
        ET.SubElement(
            url,
            "xhtml:link",
            rel="alternate",
            hreflang=language,
            href=page_url.to_language(language).url(),
        )
