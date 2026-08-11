# Application search

`ApplicationSearch` is intended for command palettes, settings, products, contacts, help pages and general UI result search.

Documents have stable ID, title, body, tags, structured fields and payload. `search_results` returns scoring metadata; `search` returns application-oriented values; `suggest` powers search boxes; `facet` counts a structured field.

Use `update`/`remove` rather than editing internal index state so all indexes remain synchronized.
