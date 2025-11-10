
import fastmcp
from collections import Counter

from brigid.mcp.entities import PageInfo, Language, Slug, PageNumber, FilteredPosts, RequiredTags, ExcludedTags
from brigid.library.storage import storage
from brigid.mcp import utils, domain


def create_tools(mcp: fastmcp.FastMCP) -> None:
    site = storage.get_site()

    get_posts_description = "\n".join([
        "Returns a filtered list of blog posts from new to old.",
        f"Returns up to {site.posts_per_page} posts. Request the next page to get more posts.",
        "Always start requesting from page 1.",
        "",
        "- required_tags: A set of tags that the blog posts must have.",
        "- excluded_tags: A set of tags that the blog posts must not have.",
        "",
        "Recomendations:",
        "",
        "- Filter posts by tags gradually — add one tag at a time — in response you'll find tag counts for the tags in the filtered posts.",
        ""
        "Response specification:",
        "",
        FilteredPosts.format_specification(),
        "",
        "PostInfo specification:",
        "",
        PageInfo.format_specification()
    ])

    # TODO: unify with api.renderes.py:render_index
    # TODO: add annotations
    @mcp.tool(name="get_posts",
              description=get_posts_description)
    def get_posts(language: Language,
                  page_number: PageNumber,
                  required_tags: RequiredTags,
                  excluded_tags: ExcludedTags) -> FilteredPosts:
        all_posts = storage.get_posts(language=language,
                                      require_tags=required_tags,
                                      exclude_tags=excluded_tags)

        tags_count: Counter[str] = Counter()

        for post in all_posts:
            tags_count.update(post.tags)

        posts = all_posts[site.posts_per_page * (page_number - 1) : site.posts_per_page * page_number]

        total_pages = (len(all_posts) + site.posts_per_page - 1) // site.posts_per_page

        return FilteredPosts(
            total_pages=total_pages,
            page_number=page_number,
            posts=[domain.page_info(post) for post in posts],
            required_tags=required_tags,
            excluded_tags=excluded_tags,
            tags=dict(tags_count)
        )
