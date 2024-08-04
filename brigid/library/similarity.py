from brigid.library.connectivity import connectivity
from brigid.library.entities import Page, PageSimilarityScore
from brigid.library.storage import storage


# TODO: collect data to explain similarity
# TODO: add similarity by vector embedings?
def get_similar_pages(language: str, original_page: Page, number: int) -> list[PageSimilarityScore]:  # noqa: CCR001

    site = storage.get_site()

    scores = []

    # initialize scores
    for page in storage.get_posts(language=language):
        if original_page.id == page.id:
            continue

        scores.append(PageSimilarityScore(page_id=page.id, score=0))

    # add points for common tags
    for page_score in scores:
        page = storage.get_page(id=page_score.page_id)

        for tag in original_page.tags:
            if tag in site.similarity.ignore_similar_tags:
                continue

            if tag in page.tags:
                page_score.add_score(site.similarity.common_tag_score, f'common tag "{tag}"')

    # add points for special tags
    for page_score in scores:
        page = storage.get_page(id=page_score.page_id)

        for tag in page.tags:
            if tag in site.similarity.bonus_for_tags:
                page_score.add_score(site.similarity.bonus_for_tags[tag], f'special tag "{tag}"')

    # add points for linked articles

    for page_score in scores:
        references_number = len(connectivity.get_referenced_from(page_id=page_score.page_id))
        page_score.add_score(
            references_number * site.similarity.bonus_per_reference,
            f"bonus for {references_number} references",
        )

    for referenced_to_id in connectivity.get_referenced_to(page_id=original_page.id):
        # TODO: optimize to map
        for page_score in scores:
            if page_score.page_id == referenced_to_id:
                page_score.add_score(
                    site.similarity.referenced_to_score,
                    f"referenced to {referenced_to_id}",
                )

    for referenced_from_id in connectivity.get_referenced_from(page_id=original_page.id):
        # TODO: optimize to map
        for page_score in scores:
            if page_score.page_id == referenced_from_id:
                page_score.add_score(
                    site.similarity.referenced_from_score,
                    f"referenced from {referenced_from_id}",
                )

    # selecting top pages
    scores.sort(key=lambda x: x.score, reverse=True)

    return scores[:number]
