# Introduction to the Brigid development

```toml donna
kind = "donna.lib.specification"
```

This document provides an introduction to the Brigid project for agents and developers who need to understand how to work with the Brigid codebase.

## Project overview

Brigid is a self-hosted blog engine focused on server-side rendering of Markdown content.

- Content source is a directory with `site/*.toml` configs, `article.toml` article descriptors, and per-language Markdown pages.
- The application serves HTML pages, feeds, sitemap, static assets, and plugin assets via FastAPI.
- The project includes a plugin system for templates, static files, and Jinja globals/filters.
- The project includes an MCP server that exposes blog content to LLM clients.

## Technology stack

### Backend

- Python 3.12
- FastAPI
- Pydantic / pydantic-settings
- Structlog

### Rendering

- Markdown (`markdown`, `pymdown-extensions`, custom processors)
- Jinja2 templates
- Pillow (image metadata)

### Tooling

- Poetry
- Pytest
- mypy
- flake8
- black / isort / autoflake
- codespell

## Infrastructure

- Docker Compose development environment (`brigid`, `mcp-inspector`, `ngrok`).
- Environment variables are read from `.env` via settings classes in multiple modules.
- Content and cache directories are mounted/configured via environment variables.

## Dictionary

- `Site` — global site configuration loaded from `<content-dir>/site/*.toml`.
- `Article` — language-independent article descriptor loaded from `article.toml`.
- `Page` — language-specific Markdown page with metadata/frontmatter.
- `Collection` — saved tag filter defined in `<content-dir>/collections/*.toml`.
- `Storage` — in-memory singleton with all loaded site entities.
- `Request context` — contextvar storage for current language/url/storage during rendering and request handling.

## Points of interest

- `./docker` — dockerfiles and related artifacts.
- `./brigid` — source code of the Brigid backend application.
- `./test-content` — example content fixtures used in tests.

## Specifications of interest

Check the next specifications:

- `{{ donna.lib.view("project:core:architecture") }}` when you need to understand or change the main architecture and module responsibilities.
