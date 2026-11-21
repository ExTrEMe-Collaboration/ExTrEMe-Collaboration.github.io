# `_includes/` — reusable pieces

| File | Renders | Parameters |
| --- | --- | --- |
| `head.html` | `<meta>` tags, fonts, CSS, favicon, SEO tags | — |
| `header.html` | Logo and main menu (from `_data/navigation.yml`) | — |
| `footer.html` | Footer | — |
| `logo.html` | The collaboration mark (SVG) | `id` — unique per page when used twice |
| `icon.html` | Small inline SVG icons | `name`: `github`, `external`, `arrow`, `play`, `search`, `mail`, `orcid`, `chevron`, `check`, `pin` |
| `talk.html` | One presentation from `_data/talks.yml` | `talk`, `show_year` |
| `publication.html` | One paper from `_data/publications.yml` | `pub`, `category` |
| `member-links.html` | Lattes / ORCID / INSPIRE / website / presentations links of one person | `person` |

Use them as `{% include talk.html talk=t %}`. Changing `talk.html` or `publication.html` changes every list on the site at once.
