# Brigid

A simple blog engine—but not simpler than it should be.

## **Demo**

- My blog: [tiendil.org](https://tiendil.org/) — see it in action with all features.
- Sources of the blog: [tiendil-org-content](https://github.com/Tiendil/tiendil-org-content) — see how the content is organized.

Or run the project from the root of this repository:

```bash
poetry install

./bin/dev-server.sh
```

## Features

- **Monolithic design** — install and run. No need to look for plugins or themes.
- **Extensive tag support** for navigating and organizing content.
- **Markdown as a source code** for posts.
- **Multi-language support** by design.
- **Plugins** — allow using custom CSS, scripts, and HTML templates.
- **[Experimental] MCP server** — allows LLMs to access your blog content.

### Extensive tag support

- Powerful tag filtering for posts. Especially useful if your blog is also your knowledge base.
- Similar post suggestions based on common tags & links (configurable).
- Post collections: for instance, if you want an always-up-to-date list of posts tagged `travels` and `best`.
- Post series: for example, if you want a dedicated set of posts marked by a special tag like `my-cool-experiments-with-chatgpt`.
- Prev/Next post navigation for series of posts.

### Markdown as a source

- Every page is a Markdown file.
- Each Markdown file has a TOML frontmatter with metadata.
- In addition to standard Markdown features, Brigid supports custom blocks:
    - Lists of posts in a collection.
    - Contents of a post series.
    - Image / gallery.
    - YouTube video.
    - Spoilers / details.
    - Info blocks (admonitions).
    - Tables.
    - Including content from other files (snippets).

### Multi-language support

- Cross-linking between posts/pages in different languages.
- SEO support for multi-language content.
- Configurable translations.
- Configurable per-language site menu.
- Auto-detect language by headers and redirect users to the right entry point, e.g. `my-cool-blog.org` -> `my-cool-blog.org/<language>/`
- Auto-marking links to posts that are not translated yet. For example, if you have a post in German and want to link to your English post that currently lacks a German translation (but might have one later).

### Plugins

For examples check [brigid.plugins](./brigid/plugins) directory.

### Other features

- Mobile-friendly.
- SEO-friendly.
- No default cookies.
- Custom headers/footers with JS code.
- Last posts block on the post page.
- Configurable redirects on the content side—no need to inject them in your reverse proxy configs.

## How to run

Set environment variables:

```bash
BRIGID_ENVIRONMENT="prod"

# Path to your content directory.
# You can find examples here:
# - ./test-content
# - https://github.com/Tiendil/tiendil-org-content/tree/main/content
BRIGID_LIBRARY_DIRECTORY="<path-to-your-content-dir>"

# Optional: Brigid will store files here for your reverse proxy to serve.
BRIGID_API_CACHE_DIRECTORY="<path-to-your-cache-dir>"

# Python list of allowed origins for CORS:
BRIGID_ORIGINS="[\"https://my-site.org\"]"

```

Install and run the server:

```bash
pip install brigid uvicorn

uvicorn brigid.application.application:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4
```

That’s it! You’ll have a server running on port 8000.

Consider the following for production deployment:

- Process Management: Use a process manager like systemd, supervisord, or Docker to ensure reliable, long-term operation.
- Reverse Proxy: Set up a reverse proxy such as Nginx or Caddy to enhance performance and security.

### Design principles

A subjective list of design principles I follow in this project:

- One solid, stable, simple, up-to-date solution. Just install and run.
- Markdown won ⇒ use Markdown as the primary source for posts.
- TOML won ⇒ use TOML for metadata and frontmatter instead of YAML.
- No unnecessary or unused features.
- Designed for non-trivial posts: long, multi-language, with images, tables, code, etc.
- Server-side rendering is good — use it as the primary approach.
- Use minimal JS only when truly required.
- No CSS experiments—only stable, verified solutions.
