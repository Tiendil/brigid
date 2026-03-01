# Brigid architecture

```toml donna
kind = "donna.lib.specification"
```

Top-level description of the Brigid architecture and code structure.

## Core architecture

Brigid is a monolithic Python application with these main runtime stages:

1. Load site/content into in-memory storage.
2. Build rendering environment (Markdown + Jinja2 + plugins).
3. Serve HTTP pages/feeds/static assets through FastAPI.
4. Optionally serve MCP tools for LLM access to blog content.

The primary design is request-time rendering from in-memory content models, without a database.

## Modules

All backend code is placed in the `./brigid` directory, which is a Python package. The main modules are:

- `brigid.application` — FastAPI app construction, lifespan, Sentry, startup orchestration.
- `brigid.api` — HTTP routers, renderers, middleware, sitemap and static cache.
- `brigid.cli` — Typer CLI commands (validate, static list, templates list/copy, configs).
- `brigid.core` — core/framework code — base classes and utilities.
- `brigid.domain` — domain logic — base logic related to the whole domain / used by the whole domain — base classes and building blocks for the domain logic.
- `brigid.jinja2_render` — Jinja environment setup, core globals/filters, template rendering.
- `brigid.library` — content loading/discovery, storage, series/connectivity/similarity logic.
- `brigid.markdown_render` — Markdown renderer and custom processors/extensions.
- `brigid.mcp` — MCP server initialization and tools.
- `brigid.plugins` — plugin interfaces, loading, and built-in plugins.
- `brigid.validation` — global and per-page validators used by CLI and checks.

## Data structures

- Do not use `dataclass` for data structures. Use `brigid.core.entities.BaseEntity` (subclass of the `pydantic.BaseModel`) instead.

Key storage and context components:

- `Storage` (singleton `brigid.library.storage.storage`) is the canonical in-memory source.
- `request_context` (contextvars) carries `storage`, `language`, and current URL for rendering and URL generation.

## Important architectural constraints

- Content is loaded at startup into memory; runtime writes are not part of normal request handling.
- Request context must be initialized before URL generation and most rendering operations.
