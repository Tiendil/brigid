import uuid

from brigid.library.storage import storage
from brigid.library.tests import make as library_make
from brigid.validation.global_validators import required_article


class TestPageIsRendered:

    def test_article_does_not_exists(self) -> None:
        validator = required_article(slug=uuid.uuid4().hex)
        assert validator() != []

    def test_has_article(self) -> None:
        article = library_make.article()

        for language in storage.get_site().allowed_languages:
            library_make.page(article=article, language=language)

        validator = required_article(slug=article.slug)
        assert validator() == []

    def test_has_no_page_in_one_language(self) -> None:

        site = storage.get_site()

        article = library_make.article()

        assert len(site.allowed_languages) > 1

        for language in list(storage.get_site().allowed_languages)[1:]:
            library_make.page(article=article, language=language)

        validator = required_article(slug=article.slug)
        assert validator() != []
