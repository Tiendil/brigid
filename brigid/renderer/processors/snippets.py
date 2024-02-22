from pymdownx import snippets

from brigid.renderer.context import render_context


class BrigidSnippetPreprocessor(snippets.SnippetPreprocessor):

    @property
    def base_path(self):
        context = render_context.get()
        return [str(context.article.path.parent)]

    @base_path.setter
    def base_path(self, value):
        # do not allow to change base_path
        pass


class SnippetExtension(snippets.SnippetExtension):

    def extendMarkdown(self, md):
        self.md = md
        md.registerExtension(self)
        config = self.getConfigs()
        snippet = BrigidSnippetPreprocessor(config, md)
        md.preprocessors.register(snippet, "snippet", 32)
