
import datetime
from typing import Literal, Annotated
from pydantic import Field
from brigid.core.entities import BaseEntity
from brigid.library.entities import ArticleType


Language = Annotated[str, Field(description="Language code of the content")]
Slug = Annotated[str, Field(description="Slug identifier of the blog post")]
PageNumber = Annotated[int, Field(description="Page number for pagination, starts with 1",
                                  default=1, ge=1)]
RequiredTags = Annotated[set[str], Field(description="Set of required tags for filtering blog posts",
                                         default_factory=set)]
ExcludedTags = Annotated[set[str], Field(description="Set of excluded tags for filtering blog posts",
                                         default_factory=set)]


class DocMixin:
    @classmethod
    def format_specification(cls) -> str:
        from brigid.mcp.utils import model_description
        return model_description(cls)


# TODO: add resource uri
class PageInfo(BaseEntity, DocMixin):
    published_at: Annotated[datetime.datetime,
                            Field(description="Publication date and time of the blog post")]
    language: Language
    slug: Slug
    title: Annotated[str,
                     Field(description="Title of the blog post")]
    seo_description: Annotated[str,
                               Field(description="SEO description of the blog post")]
    seo_image: Annotated[str | None,
                         Field(description="SEO image URL of the blog post")]
    tags: Annotated[set[str],
                    Field(description="Set of tags associated with the blog post")]
    series: Annotated[str | None,
                      Field(description="Series identifier if the blog post is part of a series")]
    type: Annotated[ArticleType,
                    Field(description="Type of the article, e.g., post or page")]
    intro: Annotated[str,
                     Field(description="Introductory content of the blog post")]
    has_more: Annotated[bool,
                        Field(description="Indicates if the blog post has a 'read more' section")]


class FilteredPosts(BaseEntity, DocMixin):
    total_pages: Annotated[int,
                           Field(description="Total number of pages available after filtering")]
    page_number: PageNumber
    posts: Annotated[list[PageInfo],
                     Field(description="List of blog posts")]
    required_tags: RequiredTags
    excluded_tags: ExcludedTags
    tags: Annotated[dict[str, int],
                    Field(description="Tag counts of the filtered posts")]
