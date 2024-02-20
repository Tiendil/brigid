import re

from markdown.inlinepatterns import LINK_RE as INTERNAL_LINK_RE
from markdown.inlinepatterns import LinkInlineProcessor

from brigid.domain.urls import UrlsFeedsAtom, UrlsPost, UrlsTags, normalize_url
from brigid.library.storage import storage
from brigid.renderer.context import render_context


class InternalLinkInlineProcessor(LinkInlineProcessor):
    RE_LINK = re.compile(r"\{\s*(.*?)\s*\}", re.DOTALL | re.UNICODE)

    # TODO: return errors instead of result
    def handleMatch(self, m, data):  # noqa # pylint: disable=all
        from brigid.library.connectivity import connectivity

        result = super().handleMatch(m, data)

        if result[0] is None:
            return result

        href = result[0].get("href")

        if href is None:
            return result

        site = storage.get_site()

        context = render_context.get()

        parts = href.split(":")

        new_href = None

        # TODO: support specifying language to easier give cross-language links

        if parts[0] == "post":
            slug = parts[1]

            if not storage.has_article(slug=slug):
                context = render_context.get()

                context.add_error(
                    failed_text=data,
                    message="Non-existing page slug specified for local link",
                )
                return result

            article = storage.get_article(slug=slug)

            if context.page.language not in article.pages:
                context.add_error(
                    failed_text=data,
                    message="Article does not have page in the current language",
                )
                return result

            connectivity.add_connection(
                target_page_id=article.pages[context.page.language],
                reference_page_id=context.page.id,
            )

            new_href = UrlsPost(language=context.page.language, slug=slug).url()

        elif parts[0] == "tags":

            required = set()
            excluded = set()

            for tag in parts[1:]:
                normalized_tag = tag[1:] if tag[0] == "-" else tag

                if normalized_tag not in site.languages[context.page.language].tags_translations:
                    context.add_error(failed_text=data, message="One of tags does not exist")
                    return result

                if tag[0] != "-":
                    required.add(normalized_tag)
                else:
                    excluded.add(normalized_tag)

            new_href = UrlsTags(
                page=1,
                required_tags=required,
                excluded_tags=excluded,
                language=context.page.language,
            ).url()

        elif parts[0] == "absolute":

            if parts[1][0] != "/":
                context.add_error(failed_text=data, message="Absolute link should start with /")
                return result

            new_href = normalize_url(f"{site.url}/{parts[1]}")

        elif parts[0] == "feed":
            new_href = UrlsFeedsAtom(language=context.page.language).url()

        elif parts[0] == "static":
            post_url = UrlsPost(language=context.page.language, slug=context.article.slug)

            new_href = post_url.file_url(parts[1])

        else:
            context.add_error(failed_text=data, message="Unknown local link format")
            return result

        # set full url for rendering in feeds and other places
        result[0].set("href", new_href)

        return result

    def getLink(self, data: str, index: int) -> tuple[str, str | None, int, bool]:
        match = self.RE_LINK.match(data, index)

        if match is None:
            return "", None, -1, False

        href = match.group(1)

        return href, None, match.end(), True


__all__ = ["InternalLinkInlineProcessor", "INTERNAL_LINK_RE"]
