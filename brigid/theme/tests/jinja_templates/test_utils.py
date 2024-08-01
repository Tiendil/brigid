from typing import Any
from unittest import mock
from xml.dom import minidom  # noqa: S408

from brigid.domain import request_context
from brigid.domain.urls import UrlsTags
from brigid.theme.templates import env


def assert_compare_html(a: str, b: str):
    assert minidom.parseString(a).toprettyxml() == minidom.parseString(b).toprettyxml()  # noqa: S318


class TestTagsUrl:

    template = """
{% from "utils.html.j2" import tags_url %}
{{tags_url("xxx", current_url, "") }}
"""

    url = UrlsTags(language="en", page=13, required_tags=("a", "d"), excluded_tags=("c", "b", "e"))

    def render(self, context: dict[str, Any], template: str | None = None) -> str:
        if template is None:
            template = self.template

        return env().from_string(template).render(context)

    def test(self) -> None:
        context = {"current_url": self.url}

        request_context.set("language", "en")
        request_context.set("url", self.url)

        result = self.render(context)

        expected_result = """
  <a class=""
     href="http://0.0.0.0:8000/en/tags/a/-b/-c/d/-e/13">
    xxx
  </a>
 """

        assert_compare_html(result, expected_result)

    def test_render_class(self) -> None:
        template = """
{% from "utils.html.j2" import tags_url %}
{{tags_url("xxx", current_url, "aaa bbb") }}
"""

        context = {"current_url": self.url}

        request_context.set("language", "en")
        request_context.set("url", self.url)

        result = self.render(context, template=template)

        expected_result = """
  <a class="aaa bbb"
     href="http://0.0.0.0:8000/en/tags/a/-b/-c/d/-e/13">
    xxx
  </a>
 """

        assert_compare_html(result, expected_result)

    @mock.patch("brigid.domain.urls.UrlsTags.total_pages", 100500)
    def test_prev(self) -> None:
        context = {"current_url": self.url}

        page_url = self.url.move_page(1)

        assert self.url.is_prev_to(page_url)

        request_context.set("language", "en")
        request_context.set("url", page_url)

        result = self.render(context)

        expected_result = """
  <a class="" rel="prev" href="http://0.0.0.0:8000/en/tags/a/-b/-c/d/-e/13">
    xxx
  </a>
 """
        assert_compare_html(result, expected_result)

    @mock.patch("brigid.domain.urls.UrlsTags.total_pages", 100500)
    def test_next(self) -> None:
        context = {"current_url": self.url}

        page_url = self.url.move_page(-1)

        assert self.url.is_next_to(page_url)

        request_context.set("language", "en")
        request_context.set("url", page_url)

        result = self.render(context)

        expected_result = """
  <a class=""
     rel="next"
     href="http://0.0.0.0:8000/en/tags/a/-b/-c/d/-e/13">
    xxx
  </a>
 """

        assert_compare_html(result, expected_result)
