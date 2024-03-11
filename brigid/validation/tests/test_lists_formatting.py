import pytest

from brigid.library.tests import make as library_make
from brigid.validation.lists_formatting import is_line_empty, is_list_line, page_has_correct_list_formatting


@pytest.mark.parametrize(
    "line,is_list",
    [
        ["- item 1", True],
        ["    - item 2", True],
        ["* item 3", True],
        ["+ item 4", True],
        ["1. item 5", True],
        ["    1. item 6", True],
        ["", False],
        ["**bold text**", False],
        ["text", False],
        ["    text", False],
        ["-sddssd", False],
        ["    -sddssd", False],
        ["*sddssd", False],
        ["+sddssd", False],
        ["1.sddssd", False],
        ["    1.sddssd", False],
    ],
)
def test_is_list_line(line: str, is_list: bool) -> None:
    assert is_list_line(line) == is_list


@pytest.mark.parametrize(
    "line,is_empty",
    [
        ["", True],
        [" ", True],
        ["    ", True],
        ["text", False],
        ["    text", False],
        ["    - item 1", False],
        ["    * item 2", False],
        ["    + item 3", False],
        ["    1. item 4", False],
    ],
)
def test_is_line_empty(line: str, is_empty: bool) -> None:
    assert is_line_empty(line) == is_empty


class TestPageHasCorrectListFormatting:

    def test_empty_body(self) -> None:
        page = library_make.page(body="")
        assert page_has_correct_list_formatting(page) == []

    def test_complext_list_are_ok(self) -> None:
        body = """
text in paragraphs

- item 1
- item 2
    - item 3
    - item 4
- item 5
    * item 6
    * item 7
        - item 8
        - item 9
- item 10

text in paragraphs

1. item 1
2. item 2
    1. item 3
    2. item 4

text in paragraphs
        """

        page = library_make.page(body=body)
        assert page_has_correct_list_formatting(page) == []

    @pytest.mark.parametrize("prefix", ["-", "*", "+"])
    def test_item_elemsts_are_separated_by_newlines__unordered(self, prefix: str) -> None:
        body = f"""
{prefix} item 1
{prefix} item 2

{prefix} item 3
{prefix} item 4
        """

        page = library_make.page(body=body)
        assert page_has_correct_list_formatting(page) != []

    def test_item_elemsts_are_separated_by_newlines__ordered(self) -> None:
        body = """
1. item 1
2. item 2

1. item 3
2. item 4
        """

        page = library_make.page(body=body)
        assert page_has_correct_list_formatting(page) != []

    def test_item_elemsts_are_separated_by_newline__nested(self) -> None:
        body = """
- item 1
    - item 2
    - item 3
- item 4
    - item 5
    - item 6

    - item 7
    - item 8
- item 9
        """

        page = library_make.page(body=body)
        assert page_has_correct_list_formatting(page) != []
