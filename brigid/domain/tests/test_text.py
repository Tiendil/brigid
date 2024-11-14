import pytest

from brigid.domain.text import capitalize_first


class TestCapitalizeFirst:

    @pytest.mark.parametrize(
        "text_input,text_expected",
        [
            ["", ""],
            ["tst test", "Tst test"],
            ["?sadasd", "?sadasd"],
            ["ABBR some text ABBR some text ABBR", "ABBR some text ABBR some text ABBR"],
        ],
    )
    def test(self, text_input: str, text_expected: str) -> None:
        assert capitalize_first(text_input) == text_expected
