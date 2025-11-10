import datetime
import enum
from typing import Annotated

from pydantic import Field

from brigid.core.entities import BaseEntity
from brigid.library.entities import ArticleType


class RenderFormat(enum.StrEnum):
    markdown = "markdown"
    html = "html"


Language = Annotated[str, Field(description="Language code of the content")]
Slug = Annotated[str, Field(description="Slug identifier of the blog post")]
RenderFormatType = Annotated[
    RenderFormat, Field(description="Format of the rendered content", default=RenderFormat.html)
]
PageNumber = Annotated[int, Field(description="Page number for pagination, starts with 1", default=1, ge=1)]
RequiredTags = Annotated[
    set[str], Field(description="Set of required tags for filtering blog posts", default_factory=set)
]
ExcludedTags = Annotated[
    set[str], Field(description="Set of excluded tags for filtering blog posts", default_factory=set)
]
PostTitle = Annotated[str, Field(description="Title of the blog post")]
TagInfos = Annotated[list["TagInfo"], Field(description="List of tags with their counts for filtered posts")]


class DocMixin:
    @classmethod
    def format_specification(cls) -> str:
        from brigid.mcp.utils import model_description

        return model_description(cls)


class PostMeta(BaseEntity, DocMixin):
    """Metadata information about a blog post."""

    published_at: Annotated[datetime.datetime, Field(description="Publication date and time of the blog post")]
    language: Language
    slug: Slug
    seo_description: Annotated[str, Field(description="SEO description of the blog post")]
    seo_image: Annotated[str | None, Field(description="SEO image URL of the blog post")]
    tags: TagInfos
    series: Annotated[str | None, Field(description="Series identifier if the blog post is part of a series")]
    type: Annotated[ArticleType, Field(description="Type of the article, e.g., post or page")]


class PostInfo(BaseEntity, DocMixin):
    meta: PostMeta
    title: PostTitle
    intro_format: RenderFormatType
    intro_body: Annotated[str, Field(description="Introductory content of the blog post")]
    has_more: Annotated[bool, Field(description="Indicates if the blog post has a 'read more' section")]


class Post(BaseEntity, DocMixin):
    meta: PostMeta
    title: PostTitle
    body_format: RenderFormatType
    body: Annotated[str, Field(description="Full content of the blog post")]


class FilteredPosts(BaseEntity, DocMixin):
    total_posts: Annotated[int, Field(description="Total number of posts available after filtering")]
    total_pages: Annotated[int, Field(description="Total number of pages available after filtering")]
    page_number: PageNumber
    posts: Annotated[list[PostInfo], Field(description="List of blog posts")]
    required_tags: RequiredTags
    excluded_tags: ExcludedTags
    tags: TagInfos


class TagInfo(BaseEntity, DocMixin):
    tag: Annotated[str, Field(description="Tag id")]
    name: Annotated[str, Field(description="Human-readable name of the tag")]
    count: Annotated[int, Field(description="Number of posts associated with the tag")]
