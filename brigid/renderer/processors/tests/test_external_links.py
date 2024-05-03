from brigid.library.storage import storage
from brigid.library.tests import make as library_make
from brigid.renderer.markdown_render import render_page


class TestExternalLink:

    def test_target_blank(self) -> None:

        text = """
[xxx](http://example.com) + [yyy](http://example.org)
        """

        article = library_make.article()
        page = library_make.page(article, body=text)

        result = render_page(page)

        assert (
            result.content
            == '<p><a href="http://example.com" target="_blank">xxx</a> + <a href="http://example.org" target="_blank">yyy</a></p>'  # noqa: E501
        )

    def test_no_schema(self) -> None:

        text = """
[xxx](example.com)
        """

        article = library_make.article()
        page = library_make.page(article, body=text)

        result = render_page(page)

        assert len(result.errors) == 1
        assert result.errors[0].message == "Specify schema/protocol for external links"

    def test_used_for_internal_links(self) -> None:

        site = storage.get_site()

        text = f"""
[xxx]({site.url})
        """

        article = library_make.article()
        page = library_make.page(article, body=text)

        result = render_page(page)

        assert len(result.errors) == 1
        assert result.errors[0].message == "Use internal links syntax to specify links to the same domain"
