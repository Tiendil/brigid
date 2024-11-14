from collections import Counter
from itertools import chain

from fastapi.responses import HTMLResponse
from feedgenerator import Atom1Feed

from brigid.api.utils import construct_index_description, construct_index_title, to_integer
from brigid.core import errors
from brigid.domain import request_context
from brigid.domain.urls import UrlsFeedsAtom, UrlsPost, UrlsTags
from brigid.library import utils as l_utils
from brigid.library.similarity import get_similar_pages
from brigid.library.storage import storage
from brigid.theme.entities import MetaInfo, Template
from brigid.theme.jinjaglobals import render_page_intro
from brigid.theme.templates import render


def render_index(language: str, raw_tags: str) -> HTMLResponse:  # noqa: CCR001, CFQ001
    site = storage.get_site()

    if language not in site.allowed_languages:
        raise errors.PageNotFound()

    request_context.set("language", language)

    required = set()
    excluded = set()
    page_number = 1

    parsed_tags = raw_tags.split("/")

    parsed_tags = [tag for tag in parsed_tags if tag]

    if parsed_tags:
        parsed_page_number = to_integer(parsed_tags[-1])

        if parsed_page_number is not None and parsed_page_number > 0:
            page_number = parsed_page_number
            parsed_tags.pop()

    for tag in parsed_tags:
        if tag.startswith("-"):
            excluded.add(tag[1:])
        else:
            required.add(tag)

    for tag in chain(required, excluded):
        if tag not in site.languages[language].tags_translations:
            # TODO: maybe, in the future it is better to make smart redirect and message user about it
            raise errors.PageNotFound()

    site = storage.get_site()

    all_pages = storage.get_posts(language=language, require_tags=required, exclude_tags=excluded)

    tags_count: Counter[str] = Counter()

    for page in all_pages:
        tags_count.update(page.tags)

    pages = all_pages[site.posts_per_page * (page_number - 1) : site.posts_per_page * page_number]

    filter_state = UrlsTags(
        language=language,
        page=page_number,
        required_tags=required,
        excluded_tags=excluded,
    )

    request_context.set("url", filter_state)

    translated_tags_required = [site.languages[language].tags_translations[tag] for tag in required]
    translated_tags_required.sort()

    translated_tags_excluded = [site.languages[language].tags_translations[tag] for tag in excluded]
    translated_tags_excluded.sort()

    seo_title = construct_index_title(
        language=language,
        title=site.languages[language].title,
        page=page_number,
        tags_required=translated_tags_required,
        tags_excluded=translated_tags_excluded,
    )

    seo_description = construct_index_description(
        language=language,
        subtitle=site.languages[language].subtitle,
        page=page_number,
        tags_required=translated_tags_required,
        tags_excluded=translated_tags_excluded,
    )

    meta_info = MetaInfo(
        site_title=site.languages[language].title,
        language=language,
        # TODO: construct language urls for filters
        #       it is complicated, because
        #       - we need to reset page number to 1 when changing language
        #       - we need to reapply filters to pages to calculate total pages
        allowed_languages=[],
        title=seo_title,
        seo_description=seo_description,
        author=site.languages[language].author,
        tags=translated_tags_required,
        published_at=None,
        seo_image_url=None,
    )

    content = render(
        str(Template.index_page),
        {
            "language": language,
            "meta_info": meta_info,
            "site": site,
            "pages": pages,
            "current_url": filter_state,
            "article": None,
            "pages_found": len(all_pages),
            "tags_count": tags_count,
        },
    )

    return HTMLResponse(content=content)


def render_page(language: str, article_slug: str, status_code: int = 200) -> HTMLResponse:

    site = storage.get_site()

    if language not in site.allowed_languages:
        raise errors.PageNotFound()

    if not storage.has_article(slug=article_slug):
        raise errors.PageNotFound()

    article = storage.get_article(slug=article_slug)

    if language not in article.pages:
        raise errors.PageNotFound()

    request_context.set("language", language)

    page = storage.get_page(id=article.pages[language])

    similar_pages = get_similar_pages(language=language, original_page=page, number=site.posts_in_similar)

    # TODO: default template for each page type
    template = page.template or Template.article_page

    post_url = UrlsPost(language=page.language, slug=article.slug)

    request_context.set("url", post_url)

    seo_image_url = None

    if page.seo_image:
        seo_image_url = post_url.file_url(page.seo_image)

    meta_info = MetaInfo(
        site_title=site.languages[language].title,
        language=language,
        allowed_languages=[language for language in site.allowed_languages if language in article.pages],
        title=l_utils.page_title(page, short=False),
        seo_description=page.seo_description,
        author=site.languages[language].author,
        tags=[site.languages[language].tags_translations[tag] for tag in page.tags],
        published_at=page.published_at,
        seo_image_url=seo_image_url,
    )

    content = render(
        str(template),
        {
            "language": language,
            "meta_info": meta_info,
            "site": storage.get_site(),
            "article": article,
            "similar_pages": similar_pages,
            "page": page,
            "current_url": post_url,
        },
    )

    return HTMLResponse(content=content, status_code=status_code)


# TODO: cache?
def render_atom_feed(language: str) -> HTMLResponse:
    site = storage.get_site()

    if language not in site.allowed_languages:
        raise errors.PageNotFound()

    author = site.languages[language].author

    feed = Atom1Feed(
        title=site.languages[language].title,
        # TODO: what is to use: subtitle or description?
        subtitle=site.languages[language].subtitle,
        description=site.languages[language].subtitle,
        link=site.url,
        language=language,
        feed_url=UrlsFeedsAtom(language=language).url(),
        author_name=author,
        # 'image' TODO: favicon?
        # 'author_email': to_unicode(author_email),  # noqa: E800
        # 'author_link': iri_to_uri(author_link),    # noqa: E800
    )

    all_pages = storage.get_posts(language=language)

    for page in all_pages[: site.posts_in_feed]:
        article = storage.get_article(id=page.article_id)

        post_url = UrlsPost(language=language, slug=article.slug)

        # Note: str() converts Markup strings into normal strings
        #       preventing double escaping in the feed
        feed.add_item(
            # TODO: do we need to render title as markdown?
            title=str(l_utils.page_title(page, short=False)),
            link=post_url.url(),
            description=str(render_page_intro(page)),
            author_name=author,
            pubdate=page.published_at,
            # TODO: now unique_id is constructed automatically like tag URI, which is expected by ATOM spec
            #       check if it is ok
        )

    xml = feed.writeString("utf-8")

    return HTMLResponse(content=xml, media_type=feed.mime_type)
