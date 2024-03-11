from brigid.library.tests import make as library_make
from brigid.validation.page_validators import page_is_rendered


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
