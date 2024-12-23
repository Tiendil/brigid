# Brigid

A simple blog engine, but not simpler than it should be.

## Demo

- My blog: [tiendil.org](https://tiendil.org/) — look there to see all the features in action.
- Sources of the blog: https://github.com/Tiendil/tiendil-org-content — look there to see how content is organized.

Or run from the root of the repository:

```bash
poetry install

./bin/dev-server.sh
```

## Features

- **Monolithic design** — install and run — no need to look for plugins and themes.
- **Extensive tags support** for navigating and organizing content.
- **Markdown as a source code** for posts.
- **Multi-language support** by design.

### Extensive tags support

- Powerfull tags filtering of the posts. Especially useful if your blog is also your knowledge base.
- Similar posts sugestion by common tags & links (configurable).
- Organize posts in collections. For example, when you want to see on your page an allways actual list of posts with tags `travels` and `best`.
- Organize posts in series. For example, when you want to have always actual content for your series of posts marked by a special tag like `my-cool-experiments-with-chatgpt`.
- Prev/Next post navigation for series of posts.

### Markdown as a source code

- Every page is a Markdown file.
- Every Markdown file has a TOML frontmatter with metadata.

In additional to standard markdown features, Brigid supports custom blocks:

- List of posts in a collection.
- Content of a post serie.
- Image / gallery.
- Youtube video.
- Spoilters / details.
- Info blocks (admonitions).
- Tables.
- Including content from another file (snippets).

### Multi-language support

- Crosslinking between posts/pages in different languages.
- SEO support for multi-language content.
- Configurable translations.
- Configurable per language site menu.
- Auto-detect language by headers and redirect user to the right entry point for your blog: `my-cool-blog.org` -> `my-cool-blog.org/language/`

### Other features

- Mobile-friendly.
- SEO-friendly.
- No default cookies.
- You can add custom headers/footers with JS code.
- Last Essays block on the post page.
- Configurable redirects on the side of the blog content. No need to inject them in configs of your reverse proxy server.

## Design principles

A very subjective list of design principles I follow in this project:

- One solid, stable, simple, up-to-date solution. Just install and run.
- Markdown won => use markdown as the primary source for posts.
- TOML won => use TOML for metadata and frontmatter instead of YAML.
- No unnecessary or unused features.
- Design for not trivial posts: long, multilanguage with images, tables, code, etc.
- Server-side rendering is good. Use it as the primary approach.
- Use minimum JS only when it is really required.
- No CSS experiments, only stable verified solutions.
