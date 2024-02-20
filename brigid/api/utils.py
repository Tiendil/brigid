from typing import Iterable

import fastapi

from brigid.api.default_translations import translations


def parse_accept_language(accept_language):
    languages = accept_language.split(",")

    parsed_languages = []

    for language in languages:
        parts = language.split(";q=")

        if len(parts) == 1:
            parsed_languages.append((parts[0].strip(), 1.0))

        else:
            parsed_languages.append((parts[0].strip(), float(parts[1])))

    parsed_languages.sort(key=lambda x: x[1], reverse=True)

    return [lang.lower() for lang, _ in parsed_languages]


def select_language(accepted_languages, available_languages):
    for lang in accepted_languages:
        if lang in available_languages:
            return lang

        if "-" not in lang:
            continue

        lang = lang.split("-")[0]

        if lang in available_languages:
            return lang

    return None


def to_integer(text: str) -> int | None:
    try:
        return int(text)
    except ValueError:
        return None


def choose_language(request: fastapi.Request) -> str:
    from brigid.library.storage import storage

    path = request.url.path

    for language in storage.get_site().allowed_languages:
        if path.startswith(f"/{language}/") or path == f"/{language}":
            return language

    accept_language = request.headers.get("accept-language", "")
    languages = parse_accept_language(accept_language)

    site = storage.get_site()

    if language := select_language(languages, site.allowed_languages):
        return language

    return site.default_language


def translate_seo(language: str, text_id: str) -> str:
    from brigid.library.storage import storage

    site = storage.get_site()

    if text_id in site.languages[language].seo_translations:
        return site.languages[language].seo_translations[text_id]

    if language not in translations:
        language = site.default_language

    if language not in translations:
        language = "en"

    if text_id in translations[language]:
        return translations[language][text_id]

    return text_id


def construct_index_title(  # noqa: CCR001
    language: str,
    title: str,
    page: int,
    tags_required: Iterable[str],
    tags_excluded: Iterable[str],
) -> str:

    if page == 1 and not tags_required and not tags_excluded:
        return title

    title_parts = []

    tags_required = list(tags_required)
    tags_excluded = list(tags_excluded)
    category = None

    if tags_required:
        category = tags_required[0]
        tags_required = tags_required[1:]

    if category:
        title_parts.append(category.capitalize())

    if page > 1:
        if category:
            title_parts.append(", ")
            title_parts.append(translate_seo(language, "page"))
        else:
            title_parts.append(translate_seo(language, "page").capitalize())

        title_parts.append(" ")
        title_parts.append(str(page))

    if tags_required:
        title_parts.append(" ")
        title_parts.append(translate_seo(language, "with_tags"))
        title_parts.append(" ")
        title_parts.append(", ".join([f"[{tag}]" for tag in tags_required]))

    if tags_excluded:
        title_parts.append(" ")
        title_parts.append(translate_seo(language, "without_tags"))
        title_parts.append(" ")
        title_parts.append(", ".join([f"[{tag}]" for tag in tags_excluded]))

    title_parts.append(" | ")
    title_parts.append(title)

    return "".join(title_parts)


def construct_index_description(  # noqa: CCR001
    language: str,
    subtitle: str,
    page: int,
    tags_required: Iterable[str],
    tags_excluded: Iterable[str],
) -> str:

    if page == 1 and not tags_required and not tags_excluded:
        return subtitle

    title_parts = []

    tags_required = list(tags_required)
    tags_excluded = list(tags_excluded)
    category = None

    if tags_required:
        category = tags_required[0]
        tags_required = tags_required[1:]

    if category:
        title_parts.append(category.capitalize())

    if page > 1:
        if category:
            title_parts.append(", ")
            title_parts.append(translate_seo(language, "page"))
        else:
            title_parts.append(translate_seo(language, "page").capitalize())

        title_parts.append(" ")
        title_parts.append(str(page))

    if tags_required:
        title_parts.append(" ")
        title_parts.append(translate_seo(language, "with_tags"))
        title_parts.append(" ")
        title_parts.append(", ".join([f"[{tag}]" for tag in tags_required]))

    if tags_excluded:
        title_parts.append(" ")
        title_parts.append(translate_seo(language, "without_tags"))
        title_parts.append(" ")
        title_parts.append(", ".join([f"[{tag}]" for tag in tags_excluded]))

    title_parts.append(". ")
    title_parts.append(subtitle.capitalize())
    title_parts.append(".")

    return "".join(title_parts)
