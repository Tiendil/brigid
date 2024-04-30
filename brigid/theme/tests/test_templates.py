import warnings
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from brigid.domain.urls import UrlsFeedsAtom, UrlsPost, UrlsTags
from brigid.library.storage import storage
from brigid.library.tests import make as library_make
from brigid.renderer.markdown_render import render_page
from brigid.renderer.processors.images_block import Image, ImageModel, ImagesBlock, ImagesModel
from brigid.theme.entities import MetaInfo, Template
from brigid.theme.templates import render
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
from html5lib import HTMLParser


def assert_correct_html(text: str) -> None:
    parser = HTMLParser(strict=True)

    try:
        parser.parse(text)
    except Exception as e:
        pytest.fail(f"Malformed HTML: {e}")


def test_assert_correct_html() -> None:
    from _pytest.outcomes import Failed

    assert_correct_html("<!DOCTYPE html><html></html>")

    with pytest.raises(Failed):
        assert_correct_html("<html>")


class TestPageRender:

    def test_page_rendered_without_errors(self) -> None:
        article = library_make.article()
        page = library_make.page(article, body="bla-bla-text")

        # TODO: make real meta_info
        #       maybe move code of constructing meta_info (from renderers.py) to separate function
        meta_info = MetaInfo(
            site_title='title',  # TODO: get real site title
            language=page.language,
            allowed_languages=[page.language],
            title=page.title,
            description=page.description,
            author='author',
            # TODO: add some tags
            tags=[],
            published_at=page.published_at,
            seo_image_url="",
        )

        post_url = UrlsPost(language=page.language, slug=article.slug)

        content = render(
            str(Template.article_page),
            {
                "language": page.language,
                "meta_info": meta_info,
                "site": storage.get_site(),
                "article": article,
                # TODO: add similar pages
                "similar_pages": [],
                "page": page,
                # TODO: add post_url
                "current_url": post_url,
            },
        )

        assert content is not None

        assert_correct_html(content)


class TestIndexRender:

    def test_page_rendered_without_errors(self) -> None:

        language = "en"

        pages = []

        for i in range(10):
            article = library_make.article()
            page = library_make.page(article, body="bla-bla-text", language=language)
            pages.append(page)

        # TODO: make real meta_info
        #       maybe move code of constructing meta_info (from renderers.py) to separate function
        meta_info = MetaInfo(
            site_title='title',  # TODO: get real site title
            language=language,
            allowed_languages=[],
            title='seo title',
            description='seo description',
            author='author',
            tags=[],  # TODO: add tags
            published_at=None,
            seo_image_url=None,
        )

        # TODO: test complex filter_state
        filter_state = UrlsTags(
            language=language,
            page=1,
            required_tags=[],
            excluded_tags=[],
        )

        content = render(
            "./blog_index.html.j2",
            {
                "language": language,
                "meta_info": meta_info,
                "site": storage.get_site(),
                "pages": pages,
                "current_url": filter_state,
                "article": None,
                "pages_found": len(pages),  # TODO: add more hidden pages
                # TODO: add tags_count
                "tags_count": {},
            },
        )

        assert content is not None

        assert_correct_html(content)