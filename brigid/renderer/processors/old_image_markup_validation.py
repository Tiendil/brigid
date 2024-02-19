from markdown.inlinepatterns import ImageInlineProcessor

from brigid.renderer.context import render_context


class ImageInlineValidator(ImageInlineProcessor):

    def handleMatch(self, m, data):
        context = render_context.get()

        context.add_error(failed_text=data, message="Classic markdown image syntax is not allowed")

        return (None, None, None)
