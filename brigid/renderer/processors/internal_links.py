import enum
import re
import xml.etree.ElementTree as etree  # noqa: S405
from typing import Any

from markdown.inlinepatterns import LINK_RE as INTERNAL_LINK_RE
from markdown.inlinepatterns import LinkInlineProcessor

from brigid.domain.urls import UrlsFeedsAtom, UrlsPost, UrlsTags, normalize_url
from brigid.library.storage import storage
from brigid.renderer.context import render_context


class Option(enum.StrEnum):
    choose_nearest_language = "choose-nearest-language"


def extract_options(parts: list[str]) -> tuple[str, list[str], dict[Option, Any]]:
    options = {}

    tail = []

    for part in parts[1:]:
        if not part.startswith("@"):
            tail.append(part)
            continue

        if part[1:] == Option.choose_nearest_language:
            options[Option.choose_nearest_language] = True
            continue

        raise ValueError(f"Unknown option in local link: {part}")

    return parts[0], tail, options


class InternalLinkInlineProcessor(LinkInlineProcessor):
    RE_LINK = re.compile(r"\{\s*(.*?)\s*\}", re.DOTALL | re.UNICODE)

    # TODO: return errors instead of result
    def handleMatch(  # type: ignore  # noqa  # pylint: disable=all
        self, m: re.Match[str], data: str
    ) -> tuple[etree.Element | None, int | None, int | None]:
        from brigid.library.connectivity import connectivity

        result = super().handleMatch(m, data)

        if result[0] is None:
            return result  # type: ignore

        assert not isinstance(result[0], str)

        href = result[0].get("href")

        if href is None:
            return result  # type: ignore

        site = storage.get_site()

        context = render_context.get()

        parts = href.split(":")

        if len(parts) < 2:
            context.add_error(failed_text=data, message="Invalid local link format")
            return result  # type: ignore

        try:
            # TODO: move here all parsing?
            link_type, link_tail, options = extract_options(parts)
        except ValueError as e:
            context.add_error(failed_text=data, message=str(e))
            return result  # type: ignore

        new_href = None

        # TODO: support specifying language to easier give cross-language links

        if link_type == "post":
            slug = link_tail[0]

            if not storage.has_article(slug=slug):
                context = render_context.get()

                context.add_error(
                    failed_text=data,
                    message="Non-existing page slug specified for local link",
                )
                return result  # type: ignore

            article = storage.get_article(slug=slug)

            if options.get(Option.choose_nearest_language, False):
                link_language = article.first_language(
                    context.page.language, site.default_language, *site.allowed_languages
                )
            else:
                link_language = context.page.language

            if link_language is None:
                context.add_error(
                    failed_text=data,
                    message="Article does not have page in the current language",
                )
                return result  # type: ignore

            if link_language == context.page.language:
                # we track connection only for the same language
                # otherwise the "similar" section will be a mess
                connectivity.add_connection(
                    target_page_id=article.pages[link_language],
                    reference_page_id=context.page.id,
                )

            new_href = UrlsPost(language=link_language, slug=slug).url()

            if link_language != context.page.language:
                # add `[language]` to the text in link
                language_element = etree.Element("span")
                language_element.text = f" [{link_language}]"
                language_element.set("class", "brigid-link-language")
                result[0].insert(0, language_element)

        elif link_type == "tags":

            required = set()
            excluded = set()

            for tag in link_tail:
                normalized_tag = tag[1:] if tag[0] == "-" else tag

                if normalized_tag not in site.languages[context.page.language].tags_translations:
                    context.add_error(failed_text=data, message="One of tags does not exist")
                    return result  # type: ignore

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

        elif link_type == "absolute":

            if link_tail[0][0] != "/":
                context.add_error(failed_text=data, message="Absolute link should start with /")
                return result  # type: ignore

            new_href = normalize_url(f"{site.url}/{link_tail[0]}")

        elif link_type == "feed":
            new_href = UrlsFeedsAtom(language=context.page.language).url()

        elif link_type == "static":
            post_url = UrlsPost(language=context.page.language, slug=context.article.slug)

            new_href = post_url.file_url(link_tail[0])

        else:
            context.add_error(failed_text=data, message="Unknown local link format")
            return result  # type: ignore

        # set full url for rendering in feeds and other places
        result[0].set("href", new_href)

        return result  # type: ignore

    def getLink(self, data: str, index: int) -> tuple[str, str | None, int, bool]:
        match = self.RE_LINK.match(data, index)

        if match is None:
            return "", None, -1, False

        href = match.group(1)

        return href, None, match.end(), True


__all__ = ["InternalLinkInlineProcessor", "INTERNAL_LINK_RE"]
