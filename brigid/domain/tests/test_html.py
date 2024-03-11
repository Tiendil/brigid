import pytest

from brigid.domain.html import strip_html


class TestStripHtml:

    @pytest.mark.parametrize(
        "text_input,text_expected",
        [
            ["<b>test</b>", "test"],
            ["", ""],
            ["tst test", "tst test"],
            ["complex <p>test</p> bla-bla <<<", "complex test bla-bla <<<"],
            ['complex with "quotes" test', 'complex with "quotes" test'],
        ],
    )
    def test_strip(self, text_input: str, text_expected: str) -> None:
        assert strip_html(text_input) == text_expected
