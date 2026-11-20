# ExTrEMe Collaboration Website

Website of the **ExTrEMe** (**Ex**periment and **T**heo**r**y in **E**xtreme **M**att**e**r) Collaboration, hosted on GitHub Pages: [https://www.extreme-collaboration.science](https://www.extreme-collaboration.science).

The site is plain Jekyll (built by GitHub Pages, no theme gem, no build step): content lives in YAML data files, pages are Liquid templates, and styling is a single CSS file.

## Site structure

| Page | Source | Content |
| --- | --- | --- |
| Home | `index.html` | Hero, research scope, latest papers and talks, institutions, funding |
| Members | `members.html` | Generated from `_data/members.yml` |
| Simulation chain | `simulation-chain.html` | The multi-stage hybrid simulation pipeline |
| Publications | `publications.html` | Generated from `_data/publications.yml` (search + category filter) |
| Talks | `presentations.html` | Generated from `_data/talks.yml` (search + type/speaker filters) |
| Contact | `contact.html` | Coordination, website issues, opportunities |
| Wiki | `wiki.md` | Internal notes (not linked from the navigation) |

Shared pieces:

- `_layouts/default.html`, `_layouts/page.html` — page skeleton and inner-page header (`title`, optional `eyebrow` and `lead` front matter).
- `_includes/` — `header.html`, `footer.html`, `head.html`, `talk.html`, `publication.html`, `logo.html`, `icon.html`.
- `_data/navigation.yml` — main menu; `_data/institutions.yml` — institutions on the home page.
- `assets/css/site.css` — all styles. Colours, fonts and spacing are CSS variables at the top (light and dark themes).
- `assets/js/site.js` — mobile menu and list filters; `assets/js/collision.js` — the animated collision in the home-page hero (respects *reduce motion*).

Always build internal links with `relative_url` (e.g. `{{ '/members/' | relative_url }}`) so the site also works under a sub-path such as a fork preview.

## Editing content

All lists on the site are generated from `_data/`. After editing, run `python3 scripts/check_data.py` (CI runs it too): it enforces the conventions below and points at the offending entry.

### Talks — `_data/talks.yml`

One entry per presentation, newest first:

```yaml
- date: "2025-11"                 # "YYYY-MM", quoted
  speaker: Thiago S. Domingues    # exactly as in _data/members.yml
  type: Talk                      # see list below
  title: "Universal Scaled Spectra: Bayesian Constraints on QGP Transport from Heavy-Ion Collisions"
  event: Advances in QCD at the LHC and the EIC
  location: CBPF, Rio de Janeiro, Brazil
  url: https://indico.cern.ch/event/1450037/contributions/6728882/   # optional
```

| Field | Convention |
| --- | --- |
| `date` | `"YYYY-MM"`, quoted. The year and month shown on the site are derived from it. |
| `speaker` | Canonical name from `_data/members.yml` (current members or alumni) — the site links it to the member card. For a non-member presenter add `external: true`. |
| `type` | One of `Plenary talk`, `Invited talk`, `Talk` (contributed or unspecified oral), `Flash talk`, `Seminar`, `Colloquium`, `Poster`. |
| `title` | Double-quoted, in the original language. Omit only if it was never recorded (shown as "Title not recorded"). Inline HTML such as `p<sub>T</sub>` is allowed. |
| `event` | Official name in the original language, with edition/year and acronym when common, e.g. `Quark Matter 2025`, `XXXII Reunião de Trabalho sobre Interações Hadrônicas (RETINHA)`. Seminars/colloquia: `<Series>, <Host institution>`. |
| `location` | `[Venue, ]City, [State, ]Country`, e.g. `UFF, Niterói, Brazil`, `Houston, TX, USA`, or `Online`. |
| `url` | *Optional.* Link specific to this talk: contribution page, slides or abstract. |
| `event_url` | *Optional.* Link to the conference or seminar series as a whole. |
| `video` | *Optional.* Recording. |
| `coauthors` | *Optional.* List of co-authors as `F. M. Lastname`. |

Not every event provides slides or contribution pages — leave the link fields out rather than inventing them, but never drop a link that exists.

### Members — `_data/members.yml`

Groups (`Faculty & Coordinators`, `Postdoctoral Researchers`, `Graduate Students`, `Alumni & Former Members`) with `name`, `position`, `affiliation`, `country`, and optional `url` (Lattes, INSPIRE or personal page) and `role`. The `name` is the canonical spelling used across the site. When someone leaves, move them to the alumni group (e.g. `position: PhD 2026`) rather than deleting them, so their talks stay linked.

### Publications — `_data/publications.yml`

Categories with an optional `description` and a list of `items`:

```yaml
- year: 2024
  title: Effect of causality constraints on Bayesian analyses of heavy-ion collisions
  authors: T. S. Domingues et al. (The ExTrEMe Collaboration)
  venue: Phys. Rev. C 110, 064904 (2024)
  note: Quark Matter 2025 proceedings        # optional context
  doi: 10.1103/PhysRevC.110.064904            # bare identifier
  arxiv: '2409.17127'                         # always quoted
  url: https://...                            # optional (theses, repositories)
  advisor: J. Takahashi                       # optional (theses)
```

- `venue`: `Journal Vol, Page (Year)`; `Preprint` / `Under review` while unpublished (the sync script then fills it in automatically once INSPIRE has the journal reference).
- `year`: year of the journal publication (preprint year while unpublished).
- `authors`: initials first (`T. S. Domingues`); up to three authors in full (`A, B, and C`), otherwise `First Author et al.`, adding `(The ExTrEMe Collaboration)` for collaboration papers.

#### Syncing with INSPIRE-HEP

`scripts/update_publications_from_inspirehep.py` keeps entries in sync with INSPIRE and writes new ones in the format above:

```bash
python3 scripts/update_publications_from_inspirehep.py --sync-all              # refresh venues, DOIs, years
python3 scripts/update_publications_from_inspirehep.py --arxiv 2409.17127      # add or update one paper
python3 scripts/update_publications_from_inspirehep.py --arxiv 2409.17127 --category "Theses"
python3 scripts/update_publications_from_inspirehep.py --update-missing-dois
python3 scripts/update_publications_from_inspirehep.py --dry-run               # preview only
```

Requires `pyyaml`. The script rewrites the whole file, so keep comments out of `publications.yml`.

## Previewing

### Locally

```bash
bundle install
bundle exec jekyll serve --livereload      # http://localhost:4000
```

### On GitHub Pages from a personal fork

The workflow `.github/workflows/fork-preview.yml` publishes a fork to `https://<user>.github.io/<fork-name>/` without claiming the collaboration's custom domain: it rewrites `url`/`baseurl` for the preview and drops `CNAME` before building. It is opt-in and never runs in repositories of the ExTrEMe-Collaboration organization. In your fork:

1. **Settings → Pages → Build and deployment → Source:** *GitHub Actions*.
2. **Settings → Secrets and variables → Actions → Variables:** add `PAGES_PREVIEW` = `true`.
3. Push to any branch (or run *Fork preview* from the Actions tab).
4. To deploy from a branch other than the default one, allow it under **Settings → Environments → github-pages → Deployment branches and tags**.

## Automated checks (CI)

`.github/workflows/site-checks.yml` runs on every pull request and on pushes to `main`:

1. **Data validation** — `scripts/check_data.py` (YAML syntax, required fields, talk types, canonical speaker names, date and identifier formats, duplicates).
2. **Jekyll build** — the same builder GitHub Pages uses.
3. **Internal link check** — `scripts/check_links.py _site` verifies every internal link and `#anchor` in the built site.

## Legacy archive references

Content was migrated from the earlier WordPress pages:

- Legacy home (talks list): `https://sites.ifi.unicamp.br/extreme/`
- Legacy simulation chain: `https://sites.ifi.unicamp.br/extreme/simulation-chain/`
- Legacy members: `https://sites.ifi.unicamp.br/extreme/members/`
- Legacy publications & theses: `https://sites.ifi.unicamp.br/hadrex/publicacoes/`
