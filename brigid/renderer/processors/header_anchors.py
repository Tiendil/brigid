import re
import xml.etree.ElementTree as etree  # noqa: S405

from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor

from brigid.domain.urls import UrlsPost
from brigid.renderer.context import render_context

DISALLOWED_CHARS_PATTERN = re.compile(r"[^-a-zA-Z0-9]+")


class AnchorCounter:

    def __init__(self):
        self.counts = [0, 0, 0, 0, 0]

    def count(self, tag: str) -> None:
        if "h1" == tag:
            raise NotImplementedError("We do not expect h1 here")

        index = int(tag[1]) - 2

        self.counts[index] += 1

        for i in range(index + 1, len(self.counts)):
            self.counts[i] = 0

    def anchor(self) -> str:
        counts = list(self.counts)

        while counts[-1] == 0:
            counts.pop()

        return f'h-{"-".join(str(c) for c in counts)}'


class HeaderAnchorsProcessor(Treeprocessor):

    def run(self, root: etree.Element) -> None:
        context = render_context.get()

        counter = AnchorCounter()

        headers = [tag for tag in root.iter() if tag.tag in ("h1", "h2", "h3", "h4", "h5", "h6")]

        for header in headers:

            if header.tag == "h1":
                context.add_error(
                    failed_text=str(header),
                    message="H1 headers are not allowed in articles, they are for titles only",
                )
                continue

            counter.count(header.tag)

            if header.text is None:
                text = None
            else:
                text = header.text.strip()

            id = counter.anchor()

            post_url = UrlsPost(language=context.page.language, slug=context.article.slug)

            url = f"{post_url.url()}#{id}"

            header.set("id", id)

            anchor = etree.Element("a")
            anchor.set("href", url)
            anchor.text = text

            header.text = None
            header.insert(0, anchor)


class HeaderAnchorsExtension(Extension):

    def extendMarkdown(self, md):
        # TODO: which priority to set?
        md.treeprocessors.register(HeaderAnchorsProcessor(), "brigid_header_anchors", 175)
