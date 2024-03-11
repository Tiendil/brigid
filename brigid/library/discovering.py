import functools
import pathlib
import re

import frontmatter
import toml

from brigid.core import logging
from brigid.library.entities import Article, Collection, Page, Redirects, Site, SiteLanguage
from brigid.library.storage import storage

logger = logging.get_module_logger()


def log_error(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            logger.error(f"error_while_{func.__name__}", args=args, kwargs=kwargs)
            raise

    return wrapper


class FrontmatterTOMLHandler(frontmatter.TOMLHandler):
    FM_BOUNDARY = re.compile(r"^\-{3,}\s*$", re.MULTILINE)
    START_DELIMITER = END_DELIMITER = "---"


@log_error
def find_page_paths(directory: pathlib.Path) -> list[pathlib.Path]:  # noqa: CCR001

    site = storage.get_site()

    page_paths = []

    for root, _, files in directory.walk(follow_symlinks=True):
        for filename in files:
            if not filename.endswith(".md"):
                continue

            if filename[:-3] not in site.allowed_languages:
                continue

            page_paths.append((root / filename).resolve().absolute())

    logger.info("found_pages", count=len(page_paths))

    return page_paths


@log_error
def find_article_paths(directory: pathlib.Path) -> list[pathlib.Path]:
    article_paths = []

    for root, _, files in directory.walk(follow_symlinks=True):
        for filename in files:
            if filename == "article.toml":
                article_paths.append((root / filename).resolve().absolute())

    logger.info("found_articles", count=len(article_paths))

    return article_paths


@log_error
def load_page(path: pathlib.Path) -> Page:

    path = path.resolve().absolute()

    article_path = path.parent / "article.toml"

    if storage.has_article(path=article_path):
        article = storage.get_article(path=article_path)

    elif not article_path.exists():
        raise NotImplementedError(f"article configs has not found at {article_path}")

    else:
        raise NotImplementedError(f"article has not found for {article_path}")

    with path.open() as f:
        page_data, page_content = frontmatter.parse(f.read(), handler=FrontmatterTOMLHandler())

    if "tags" not in page_data:
        page_data["tags"] = article.tags

    if page_data["seo_image"] == "":
        page_data["seo_image"] = None

    page = Page(
        article_id=article.id,
        path=path,
        language=path.stem,
        body=page_content,
        **page_data,
    )

    return page


@log_error
def load_pages(directory: pathlib.Path) -> None:
    page_paths = find_page_paths(directory=directory)

    for page_path in page_paths:
        page = load_page(page_path)
        storage.add_page(page)


@log_error
def load_article(path: pathlib.Path) -> Article:
    path = path.resolve().absolute()

    article_content = path.read_text()

    article_data = toml.loads(article_content)
    article = Article(path=path, **article_data)

    return article


@log_error
def load_articles(directory: pathlib.Path) -> None:
    article_paths = find_article_paths(directory=directory)

    for article_path in article_paths:
        article = load_article(article_path)
        storage.add_article(article)


# TODO: exclude 'site' directory from pages search
#       or freeze all highl-level directories?
@log_error
def load_site(directory: pathlib.Path) -> None:  # noqa: CCR001
    languages = {}
    site = None
    redirects = Redirects()

    for file_path in (directory / "site").glob("*.toml"):
        data = toml.loads(file_path.read_text())

        if file_path.name == "meta.toml":
            site = Site(**data, path=file_path.resolve().absolute())
            continue

        if file_path.name == "redirects.toml":
            redirects = Redirects(**data)
            continue

        languages[file_path.stem] = SiteLanguage(**data)

        for menu in languages[file_path.stem].menu:
            menu.language = file_path.stem

    if site is None:
        raise NotImplementedError("meta.toml has not found")

    if (directory / "site" / "footer.html").exists():
        site.footer_html = (directory / "site" / "footer.html").read_text()

    if (directory / "site" / "header.html").exists():
        site.header_html = (directory / "site" / "header.html").read_text()

    site.languages.update(languages)

    storage.set_site(site)

    storage.set_redirects(redirects)


@log_error
def load_collections(directory: pathlib.Path) -> None:
    for file_path in (directory / "collections").glob("*.toml"):
        data = toml.loads(file_path.read_text())

        path = file_path.resolve().absolute()

        collection = Collection(**data, path=path)

        storage.add_collection(collection)


@log_error
def load(directory: pathlib.Path) -> None:
    from brigid.library.connectivity import connectivity

    # goes fiest, because other loaders depend on it
    load_site(directory=directory)

    load_articles(directory=directory)
    load_pages(directory=directory)
    load_collections(directory=directory)

    connectivity.initialize()
