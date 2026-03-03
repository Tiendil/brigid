from urllib.parse import urlparse

from markdown.inlinepatterns import LINK_RE as EXTERNAL_LINK_RE
from markdown.inlinepatterns import LinkInlineProcessor

from brigid.markdown_render.context import render_context


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

        context = render_context.get()

        # validate external links

        if parsed_url.scheme == "":
            context.add_error(failed_text=data, message="Specify schema/protocol for external links")
            return result

        # all external links must be with target="_blank"
        result[0].set("target", "_blank")

        return result


__all__ = ["ExternalLinkInlineProcessor", "EXTERNAL_LINK_RE"]
