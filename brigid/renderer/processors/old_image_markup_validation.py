
from brigid.renderer.context import RenderError, render_context
from markdown.inlinepatterns import IMAGE_LINK_RE, IMAGE_REFERENCE_RE, ImageInlineProcessor


class ImageInlineValidator(ImageInlineProcessor):

    def handleMatch(self, m, data):
        context = render_context.get()

        context.add_error(failed_text=data,
                          message='Classic markdown image syntax is not allowed')

        return (None, None, None)
