# `_layouts/` — page skeletons

| Layout | Used by | What it adds |
| --- | --- | --- |
| `default.html` | every page | `<head>`, header, footer, scripts |
| `page.html` | every page except the home page (it is the default in `_config.yml`) | the dark page header with title, eyebrow and lead |

Front matter understood by the layouts:

| Key | Effect |
| --- | --- |
| `title` | Page title (header and browser tab) |
| `eyebrow` | Small label above the title |
| `lead` | Introductory sentence under the title |
| `wide: true` | Use the full content width (Members page) |
| `scripts` | Extra JavaScript files for this page only (home page: the collision animation) |
| `body_class` | Extra CSS class on `<body>` |
| `permalink` | URL of the page |

Internal links must use `relative_url` (e.g. `{{ '/members/' | relative_url }}`) so the site also works in a fork preview under a sub-path.
