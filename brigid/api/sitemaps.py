import datetime
import xml.etree.ElementTree as ET  # noqa: S405

from brigid.domain.urls import UrlsPost, UrlsRoot, UrlsTags
from brigid.library.storage import storage

# Google does not like too old dates like 0001-01-01
# => we do not create lastmod for pages with date less than MIN_DATE
MIN_DATE = datetime.datetime(1980, 1, 1, tzinfo=datetime.timezone.utc)


def get_last_published_at(language) -> datetime.datetime | None:
    last_published_at = None

    # TODO: here we look at all posts, but we should look at all sources of blog
    #       including configs & static files
    for page in storage.get_posts(language=language):
        if last_published_at is None or page.published_at > last_published_at:
            last_published_at = page.published_at

    return last_published_at


def add_lastmod(url: ET.Element, date: datetime.datetime | None) -> None:
    if date is None:
        return

    if date < MIN_DATE:
        return

    lastmod = ET.SubElement(url, "lastmod")
    lastmod.text = date.isoformat()


def build_sitemap_xml() -> str:

    site = storage.get_site()

    attributes = {
        "xmlns": "http://www.sitemaps.org/schemas/sitemap/0.9",
        "xmlns:xhtml": "http://www.w3.org/1999/xhtml",
    }

    sitemap = ET.Element("urlset", **attributes)  # type: ignore[arg-type]

    for page in storage.all_entities():
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

    add_lastmod(url, last_published_at)

    priority = ET.SubElement(url, "priority")
    priority.text = "1.0"

    if len(site.allowed_languages) > 1:
        add_language_variants(url, root_url, site.allowed_languages)


def add_pagination_urls(sitemap, language) -> None:

    # add only index with no tags filter
    pagination_urls = UrlsTags(language=language, page=1, required_tags=[], excluded_tags=[])

    last_published_at = get_last_published_at(language)

    while pagination_urls.page < pagination_urls.total_pages:
        # do not add the first page, because it is already added
        pagination_urls = pagination_urls.move_page(+1)

        url = ET.SubElement(sitemap, "url")

        loc = ET.SubElement(url, "loc")
        loc.text = pagination_urls.url()

        add_lastmod(url, last_published_at)

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

    add_lastmod(url, page.published_at)

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
