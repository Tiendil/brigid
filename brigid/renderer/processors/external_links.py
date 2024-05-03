from urllib.parse import urlparse

from markdown.inlinepatterns import LINK_RE as EXTERNAL_LINK_RE
from markdown.inlinepatterns import LinkInlineProcessor

from brigid.library.storage import storage
from brigid.renderer.context import render_context


class ExternalLinkInlineProcessor(LinkInlineProcessor):

    # TODO: return errors instead of result
    def handleMatch(self, m, data):  # noqa # pylint: disable=all
        result = super().handleMatch(m, data)

        if result[0] is None:
            return result

        href = result[0].get("href")

        if href is None:
            return result

        parsed_url = urlparse(href)

        site = storage.get_site()

        context = render_context.get()

        parsed_site = urlparse(site.url)

        # validate external links

        # TODO: compare taking into account the default ports, aka example.com:90 = example.com
        # TODO: is this required, link could be to the same domain but in different project
        if parsed_site.netloc == parsed_url.netloc:
            context.add_error(
                failed_text=data, message="Use internal links syntax to specify links to the same domain"
            )
            return result

        if parsed_url.scheme == "":
            context.add_error(failed_text=data, message="Specify schema/protocol for external links")
            return result

        # all external links must be with target="_blank"
        result[0].set("target", "_blank")

        return result


__all__ = ["ExternalLinkInlineProcessor", "EXTERNAL_LINK_RE"]
