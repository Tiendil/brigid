import pathlib
from typing import Callable

from brigid.core.entities import BaseEntity
from brigid.library.entities import Article, Page
from brigid.library.storage import storage
from brigid.renderer.markdown_render import render_page
from brigid.validation.entities import Error
from brigid.validation.lists_formatting import page_has_correct_list_formatting


def required_article(slug: str) -> Callable[[], list[Error]]:
    def validator() -> list[Error]:

        if not storage.has_article(slug=slug):
            return [Error(filepath=None, message=f"{slug} article not found")]

        article = storage.get_article(slug=slug)

        site = storage.get_site()

        allowed_languages = set(site.allowed_languages)
        article_languages = set(article.pages)

        missing_languages = allowed_languages - article_languages

        if missing_languages:
            return [Error(filepath=article.path, message=f"Missing languages for article: {missing_languages}")]

        return []

    return validator
