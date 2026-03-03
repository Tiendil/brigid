
### Migration

- Replace `brigid.application.application:app` with `brigid.asgi:app` in your ASGI server configuration (e.g. `uvicorn` command or `Procfile`).

### Changes

- gh-129 — Support for base URL prefixes such as `/blog` for hosting Brigid behind reverse proxies without stripping the prefix.
