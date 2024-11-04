import uuid

from brigid.library.storage import storage
from brigid.library.tests import make as library_make
from brigid.validation.page_validators import page_has_correct_series_tags, page_has_correct_tags, page_is_rendered


def test_some_tags_are_in_configs() -> None:
    """To not test in every test that tags are in configs"""
    for language in storage.get_site().languages.keys():
        allowed_tags = list(storage.get_site().languages[language].tags_translations.keys())
    assert allowed_tags


class TestPageIsRendered:

    def test_empty_body(self) -> None:
        page = library_make.page(body="")
        assert page_is_rendered(page) == []

    def test_no_errors(self) -> None:
        page = library_make.page(body="some text")
        assert page_is_rendered(page) == []

    def test_has_errors(self) -> None:
        body = """
/// brigid-images
x = "y"
///
"""

        page = library_make.page(body=body)
        assert page_is_rendered(page) != []


class TestPageHasCorrectTags:

    def test_empty_tags(self) -> None:
        page = library_make.page(body="", tags=[])
        assert page_has_correct_tags(page) == []

    def test_no_errors(self) -> None:
        language = "en"

        allowed_tags = list(storage.get_site().languages[language].tags_translations.keys())

        page = library_make.page(language=language, body="", tags=allowed_tags)
        assert page_has_correct_tags(page) == []

    def test_has_errors(self) -> None:
        language = "en"

        allowed_tags = list(storage.get_site().languages[language].tags_translations.keys())

        bad_tag_1 = uuid.uuid4().hex
        bad_tag_2 = uuid.uuid4().hex

        allowed_tags.extend([bad_tag_1, bad_tag_2])

        page = library_make.page(language=language, body="", tags=allowed_tags)

        errors = page_has_correct_tags(page)

        assert len(errors) == 2

        assert (bad_tag_1 in errors[0].message and bad_tag_2 in errors[1].message) or (
            bad_tag_1 in errors[1].message and bad_tag_2 in errors[0].message
        )


class TestPageHasCorrectSeriesTags:

    def test_empty_series(self) -> None:
        language = "en"

        allowed_tags = list(storage.get_site().languages[language].tags_translations.keys())

        page = library_make.page(body="", tags=allowed_tags, series=None)

        assert page_has_correct_series_tags(page) == []

    def test_ok_series(self) -> None:
        language = "en"

        allowed_tags = list(storage.get_site().languages[language].tags_translations.keys())

        page = library_make.page(body="", tags=allowed_tags, series=allowed_tags[0])

        assert page_has_correct_series_tags(page) == []

    def test_wrong_series(self) -> None:
        language = "en"

        allowed_tags = list(storage.get_site().languages[language].tags_translations.keys())

        bad_tag = uuid.uuid4().hex

        page = library_make.page(body="", tags=allowed_tags + [bad_tag], series=bad_tag)

        errors = page_has_correct_series_tags(page)

        assert len(errors) == 1

        assert bad_tag in errors[0].message

    def test_series_not_in_page_tags(self) -> None:
        language = "en"

        allowed_tags = list(storage.get_site().languages[language].tags_translations.keys())

        page = library_make.page(body="", tags=allowed_tags[1:], series=allowed_tags[0])

        errors = page_has_correct_series_tags(page)

        assert len(errors) == 1

        assert allowed_tags[0] in errors[0].message
