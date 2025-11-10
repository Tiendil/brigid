
import fastmcp

from brigid.mcp.entities import PageInfo, Language, Slug


def create_tools(mcp: fastmcp.FastMCP) -> None:

    get_posts_description = "\n".join([
        "Returns a filtered list of blog posts from new to old",
        "",
        "- required_tags: A set of tags that the blog posts must have.",
        "- excluded_tags: A set of tags that the blog posts must not have.",
        "",
        "Post info specification:",
        "",
        PageInfo.format_specification()
    ])

    @mcp.tool(name="get_posts",
              description=get_posts_description)
    def get_posts(language: Language,
                  required_tags: set[str] | None = None,
                  excluded_tags: set[str] | None = None) -> list[PageInfo]:
        return "pong"
