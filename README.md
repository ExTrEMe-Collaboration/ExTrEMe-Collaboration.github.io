# ExTrEMe Collaboration Website

Website and resources for the **ExTrEMe** (**Ex**periment and **T**heo**r**y in **E**xtreme **M**att**e**r) Collaboration, hosted on GitHub Pages: [https://extreme-collaboration.github.io](https://extreme-collaboration.github.io).

## Site Structure

- **Home**: `index.md` — Overview, research scope, participating institutions, quick navigation
- **Members**: `members.md` — Faculty coordinators, postdocs, students, and alumni
- **Simulation Chain**: `simulation-chain.md` — End-to-end multi-stage hydrodynamic simulation framework and architecture
- **Publications**: `publications.md` — Dynamic listing generated from `_data/publications.yml`
- **Presentations & Talks**: `presentations.md` — Dynamic listing generated from `_data/talks.yml`
- **Contact**: `contact.md` — Coordination, inquiries, student/postdoc opportunities
- **Internal Wiki**: `wiki.md` — Internal guidelines and onboarding notes

## Maintaining Structured Data

### Publications (`_data/publications.yml`)

The publications page is generated automatically from `_data/publications.yml`.

#### Updating via the INSPIREHEP Synchronization Script

We provide a Python script in `scripts/update_publications_from_inspirehep.py` to synchronize publications with INSPIREHEP:

```bash
# Refresh and sync all existing entries (updates published journal venues, DOIs, years)
python3 scripts/update_publications_from_inspirehep.py --sync-all

# Fetch and add a new paper by arXiv ID
python3 scripts/update_publications_from_inspirehep.py --arxiv 2409.17127

# Search and fill in missing DOIs
python3 scripts/update_publications_from_inspirehep.py --update-missing-dois

# Preview changes without modifying files
python3 scripts/update_publications_from_inspirehep.py --dry-run
```

*Prerequisites*: Uses standard library modules (`urllib`, `json`, `argparse`). Requires `pyyaml` (pre-installed in Anaconda/Miniconda or `pip install pyyaml`).

#### Manual Publication Entries

Entries follow this format in `_data/publications.yml`:

```yaml
- year: 2024
  title: Effect of causality constraints on Bayesian analyses of heavy-ion collisions
  authors: T. S. Domingues et al. (The ExTrEMe Collaboration)
  venue: Phys. Rev. C 110, 064904 (2024)
  doi: 10.1103/PhysRevC.110.064904
  arxiv: '2409.17127'
  url: https://... # (optional, for theses or non-DOI links)
```

- Always quote numeric-looking arXiv IDs (e.g. `'2409.17127'`) so YAML does not interpret them as floats.
- `doi`: store only the identifier (e.g., `10.1103/PhysRevC.110.064904`); the link is constructed automatically in Jekyll.

### Presentations and Talks (`_data/talks.yml`)

Talks are sorted chronologically by the `date_sort` field (`YYYY-MM`):

```yaml
- date_sort: 2025-12
  year: 2025
  month: December
  speaker: Matthew Luzum
  type: Oral
  event: UIUC Nuclear Seminar
  location: Urbana, IL, USA
  title: "Exploring the shape of the transverse momentum spectra in relativistic heavy-ion collisions"
  url: https://... # (optional link to slides or event page)
```

- If a title contains colons, quote the full title string to avoid YAML parsing syntax errors.

## Automated Checks (CI)

A GitHub Actions workflow (`.github/workflows/site-checks.yml`) validates every push and pull request:

1. **YAML Data Validation**: Verifies that `_data/publications.yml` and `_data/talks.yml` are syntactically valid YAML.
2. **Jekyll Build**: Builds the complete site to ensure layouts and Liquid templates render cleanly.
3. **Markdown Link Check**: Scans markdown pages for dead local links or malformed references using `lychee`.

## Legacy Archive References

Migrated from earlier WordPress web resources:
- Legacy Home: `https://sites.ifi.unicamp.br/extreme/`
- Legacy Simulation Chain: `https://sites.ifi.unicamp.br/extreme/simulation-chain/`
- Legacy Members: `https://sites.ifi.unicamp.br/extreme/members/`
- Legacy Publications & Theses: `https://sites.ifi.unicamp.br/hadrex/publicacoes/`
