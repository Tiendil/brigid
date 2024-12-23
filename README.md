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

Here are main features of Brigid:

- **Monolithic design** — install and run. No need to look for plugins and themes.
- **Self-hosted dynamic service** (not a static site generator), that gives some advantages over static site generators.
- **Extensive tags support** for navigation and organizing content.
- **Markdown as a source code** for articles.
- **Multi-language support** by design.

### Monolithic design

???

### Self-hosted dynamic service

Running Brigid as a service gives some advantages that static site generators can not provide easily:

- Configurable redirects on the side of the blog content. No need to inject them in configs of your reverse proxy server.

### Extensive tags support

- Powerfull tags filtering of the posts.
- Suggesting similar posts by common tags & links (configurable).
- Collections of posts by tags. For example, you can display on the page allways actual list of posts with tags `travels` and `best`.
- Series of posts by tags. For example, you have always actual content for your series of posts marked by the selected tag like `my-cool-experiments-with-chatgpt`.

### Markdown as a source code

- Every post/page is a markdown file.
- Every Markdown file has a TOML frontmatter with metadata.
- A lot of custom blocks for markdown to make your content more interactive and informative.

In additional to standard markdown features, Brigid supports custom blocks:

- List posts in a collection.
- Image / gallery.
- Youtube video.
- Content of a post series.
- Include content from another files (snippets).
- Info blocks (admonitions).
- Tables.
- Spoilters / details.

### Multi-language support

- Crosslinking between posts/pages in different languages.
- SEO support for multi-language content.
- Auto-detect language by headers and redirect user to the right entry point for your blog.
- Configurable translations.
- Configurable site menu per language.

### Other features

- Mobile-friendly.
- SEO-friendly.
- No cookies (you can add custom headers/footers with JS code).

## Design principles

A very subjective list of design principles I follow in this project:

- One solid, stable, simple, up-to-date solution. Just install and run.
- Markdown won => use markdown as the primary source for posts.
- TOML won => use TOML for metadata and frontmatter instead of YAML.
- No unnecessary or unused features.
- Design for not trivial posts: long, multilanguage, images, code, etc.
- Server-side rendering is good. Use it as the primary approach.
- Use minimum JS only when it is really required.
- No CSS experiments, only stable verified solutions.
