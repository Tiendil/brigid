from collections import Counter

import fastmcp

from brigid.library.entities import Page
from brigid.library.storage import storage
from brigid.mcp import domain
from brigid.mcp.entities import ExcludedTags, FilteredPosts, Language, PageInfo, PageNumber, RequiredTags, RenderFormat, Slug, Post, RenderFormat, TagInfo


# TODO: User Elicitation if the post for the language is not found
# TODO: unify page getting code with the api renderers?
# TODO: should we render markdown in a special format for MCP? To support backlinks, images as resources, etc.?
# TODO: should we add an instruction about the markdown format used in the blog?
# TODO: add mcp url constructors, like with http urls?
# TODO: maybe we should has on unviersal resource, that returns
#       all info and representations about the post with meta info?

def create_tools(mcp: fastmcp.FastMCP) -> None:
    site = storage.get_site()

    get_posts_description = "\n".join(
        [
            "Returns a filtered list of blog posts from new to old.",
            f"Returns up to {site.posts_per_page} posts. Request the next page to get more posts.",
            "Always start requesting from page 1.",
            "",
            "- required_tags: A set of tags that the blog posts must have.",
            "- excluded_tags: A set of tags that the blog posts must not have.",
            "",
            "Recomendations:",
            "",
            "- Filter posts by tags gradually — add one tag at a time — in response you'll find tag counts for the tags in the filtered posts."
        ]
    )

    # TODO: unify with api.renderes.py:render_index
    # TODO: add annotations
    @mcp.tool(name="get_posts", description=get_posts_description)
    def get_posts(
            language: Language, page_number: PageNumber, required_tags: RequiredTags, excluded_tags: ExcludedTags, render_format: RenderFormat
    ) -> FilteredPosts:
        all_posts = storage.get_posts(language=language, require_tags=required_tags, exclude_tags=excluded_tags)

        tags_count: Counter[str] = Counter()

        for post in all_posts:
            tags_count.update(post.tags)

        posts = all_posts[site.posts_per_page * (page_number - 1) : site.posts_per_page * page_number]

        total_pages = (len(all_posts) + site.posts_per_page - 1) // site.posts_per_page

        return FilteredPosts(
            total_posts=len(all_posts),
            total_pages=total_pages,
            page_number=page_number,
            posts=[domain.create_post_info(post, render_format) for post in posts],
            required_tags=required_tags,
            excluded_tags=excluded_tags,
            tags=domain.create_tag_infos(language, tags_count),
        )

    # TODO: description
    get_post_description = "\n".join([
        "Returns the full content of a blog post identified by its slug in the specified language.",
        "",
        "Recommendations:",
        "",
        "- Prefer `html` as the render format for the content that will be displayed to the user.",
    ])

    @mcp.tool(name="get_post", description=get_post_description)
    def get_post(language: Language, slug: Slug, render_format: RenderFormat) -> Post | None:
        if language not in site.allowed_languages:
            # TODO: send notification or error?
            return None

        if not storage.has_article(slug=slug):
            # TODO: send notification or error?
            return None

        article = storage.get_article(slug=slug)

        if language not in article.pages:
            # TODO: send notification or error?
            return None

        post = storage.get_page(id=article.pages[language])

        return domain.create_post(post, render_format)

    get_tags_description = "\n".join([
        "Returns a list of all tags used in blog posts for the specified language, along with the count of posts associated with each tag.",
        "",
        "Recommendations:",
        "",
        "- Use this tool when the user requested information about specific topics: get all tags -> choose relevant tags -> get posts with these tags.",
    ])

    @mcp.tool(name="get_tags", description=get_tags_description)
    def get_tags(language: Language) -> list[TagInfo]:
        all_posts = storage.get_posts(language=language, require_tags=(), exclude_tags=())

        tags_count: Counter[str] = Counter()

        for post in all_posts:
            tags_count.update(post.tags)

        return domain.create_tag_infos(language, tags_count)
