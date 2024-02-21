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

- Markdown as a source code for articles.
- Multi-language support by design.
- Mobile-friendly.
- SEO-friendly.
- No cookies.
- Monolithic design: install and run. No need to look for plugins and themes.

### Some specific features

Brigid is not a static site generator, i.e. you should run brigid process to access the site. It gives some advantages over classic static site generators.

- Redirects.
- Nice tags filtering (for wide pages only, for now).
- Detect language by headers.
- Sentry reporting.
- More features are coming.

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
