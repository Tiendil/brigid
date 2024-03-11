import warnings

from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning


def strip_html(html: str) -> str:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=MarkupResemblesLocatorWarning)
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text()
