# `_data/` — the site's content

Every list on the website is generated from these YAML files. Edit them, not the HTML pages.
After editing, run `python3 scripts/check_data.py` (CI runs it on every pull request).

| File | Shown on | Notes |
| --- | --- | --- |
| `talks.yml` | Presentations page, home page | One entry per presentation |
| `publications.yml` | Publications page, home page | Grouped by category; rewritten by the INSPIRE sync script, so **no comments** in this file |
| `members.yml` | Members page; links speakers to their card | Canonical spelling of every name |
| `institutions.yml` | Home page | Grouped by country |
| `navigation.yml` | Header and footer menus | |

## `talks.yml`

| Field | Convention |
| --- | --- |
| `date` | `"YYYY-MM"`, in double quotes. Year and month shown on the site come from here. |
| `speaker` | Exactly a `name` from `members.yml` (current members or alumni). For a non-member presenter, add `external: true`. |
| `type` | `Plenary talk`, `Invited talk`, `Talk` (contributed or unspecified oral), `Flash talk`, `Seminar`, `Colloquium` or `Poster`. |
| `title` | Double-quoted, original language and capitalisation. Inline HTML such as `p<sub>T</sub>` is allowed. Omit only if never recorded. |
| `event` | Official name in its original language, with edition and acronym when common, e.g. `Quark Matter 2025`, `XXXII Reunião de Trabalho sobre Interações Hadrônicas (RETINHA)`. Seminars/colloquia: `<Series>, <Host institution>`. |
| `location` | `[Venue, ]City, [State, ]Country` (e.g. `UFF, Niterói, Brazil`, `Houston, TX, USA`) or `Online`. |
| `url` | *Optional.* Link specific to this presentation: contribution page, slides, abstract. |
| `event_url` | *Optional.* The conference or seminar series as a whole. |
| `video` | *Optional.* Recording. |
| `coauthors` | *Optional.* List, e.g. `[D. D. Chinellato, J. Takahashi]`. |

Leave a link out rather than guessing it, but never delete a link that exists.

## `members.yml`

Four groups (`faculty`, `postdocs`, `students`, `alumni`). Per person: `name`, `position`, `affiliation`, `country`, and optionally `lattes` (`https://lattes.cnpq.br/<16 digits>`), `orcid` (the iD only, e.g. `0000-0002-4091-1779`; the check digit is verified), `inspire` (`https://inspirehep.net/authors/<number>`), `url` (personal page) and `role`.

When someone leaves, move them to the alumni group (e.g. `position: PhD 2026`) instead of deleting them: their presentations stay linked. Renaming a person means updating `talks.yml` too — the check will list every entry that no longer matches.

## `publications.yml`

```yaml
- category: ExTrEMe Collaboration Papers
  items:
  - year: 2024                      # journal year (preprint year while unpublished)
    title: Effect of causality constraints on Bayesian analyses of heavy-ion collisions
    authors: T. S. Domingues et al. (The ExTrEMe Collaboration)
    venue: Phys. Rev. C 110, 064904 (2024)   # or Preprint / Under review
    note: Quark Matter 2025 proceedings      # optional context
    doi: 10.1103/PhysRevC.110.064904         # bare identifier
    arxiv: '2409.17127'                      # always quoted
    url: https://...                         # optional (theses, repositories)
    advisor: J. Takahashi                    # optional (theses)
```

- Authors: initials first (`T. S. Domingues`); up to three in full (`A, B, and C`), otherwise `First Author et al.`, adding `(The ExTrEMe Collaboration)` for collaboration papers.
- `Preprint` / `Under review` venues are replaced automatically by `scripts/update_publications_from_inspirehep.py --sync-all` once INSPIRE has the journal reference.
- Categories are curated: only add papers the collaboration agreed to list.

## `institutions.yml` and `navigation.yml`

`institutions.yml`: `name`, `short` (acronym), `city`, `country`.
`navigation.yml`: `title` and `url` (site path, e.g. `/members/`) of each menu entry.
