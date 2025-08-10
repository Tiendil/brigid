
**Migration**:

- The plain default configuration should work as before.
- If you had configured `footer_html` or `header_html`, set `BRIGID_PLUGINS_INCLUDE_TEMPLATES` to the path with `*.html.j2` instead. You can find examples here: `./test-content/plugins/include/`

**Changes**:

- gh-120 — Added plugins. Monolithic rendering is partially split into default plugins. The work will continue in the future.
