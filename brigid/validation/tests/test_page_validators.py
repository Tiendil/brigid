import uuid
from brigid.library.tests import make as library_make
from brigid.validation.page_validators import page_is_rendered, page_has_correct_tags, page_has_correct_series_tags
from brigid.library.storage import storage


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

        allowed_tags = set(storage.get_site().languages[language].tags_translations.keys())

        assert allowed_tags

        page = library_make.page(language=language, body="", tags=list(allowed_tags))
        assert page_has_correct_tags(page) == []

    def test_has_errors(self) -> None:
        language = "en"

        allowed_tags = set(storage.get_site().languages[language].tags_translations.keys())

        assert allowed_tags

        bad_tag_1 = uuid.uuid4().hex
        bad_tag_2 = uuid.uuid4().hex

        allowed_tags.update([bad_tag_1, bad_tag_2])

        page = library_make.page(language=language, body="", tags=list(allowed_tags))

        errors = page_has_correct_tags(page)

        assert len(errors) == 2

        assert ((bad_tag_1 in errors[0].message and bad_tag_2 in errors[1].message) or
                (bad_tag_1 in errors[1].message and bad_tag_2 in errors[0].message))
