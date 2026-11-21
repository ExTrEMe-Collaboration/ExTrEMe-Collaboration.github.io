# ExTrEMe Collaboration Website

Source of [www.extreme-collaboration.science](https://www.extreme-collaboration.science).

## Add a presentation or a paper (no installation needed)

Everything can be done on GitHub, in the browser.

1. Open the file:
   - presentations → [`_data/talks.yml`](_data/talks.yml)
   - papers → [`_data/publications.yml`](_data/publications.yml)
2. Click the pencil icon (**Edit this file**). If GitHub asks to fork the repository, accept.
3. Copy an example below, paste it **at the top of the list** (papers: under the right category) and fill it in.
4. Click **Commit changes…**, then **Propose changes** / **Create pull request**.
5. Wait about a minute for the automatic check. A green ✓ means it is fine and a maintainer will publish it. A red ✗ shows which line to fix: click **Details**, then edit the file again in your pull request.

**A presentation**

```yaml
- date: "2026-03"                    # year-month, in quotes
  speaker: Matthew Luzum             # exactly as written on the Members page
  type: Talk                         # Plenary talk, Invited talk, Talk, Flash talk, Seminar, Colloquium or Poster
  title: "Title of the presentation" # in double quotes
  event: Quark Matter 2026
  location: Kraków, Poland           # City, Country — or Online
  url: https://indico.cern.ch/...    # optional: slides or contribution page
```

**A paper**

```yaml
  - year: 2026
    title: "Title of the paper"
    authors: A. B. Author et al. (The ExTrEMe Collaboration)
    venue: Phys. Rev. C 113, 012345 (2026)   # or: Preprint
    doi: 10.1103/PhysRevC.113.012345         # optional, without https://doi.org/
    arxiv: '2601.01234'                      # in single quotes
```

Three rules prevent almost every error:

- indent with **spaces** (never tabs), aligned with the entries around yours;
- every entry starts with **`- `**;
- put titles in **"double quotes"** and arXiv numbers in **'single quotes'**.

Not comfortable with GitHub? Send the details to [admin@extreme-collaboration.science](mailto:admin@extreme-collaboration.science).

---

## For maintainers

The site is plain [Jekyll](https://jekyllrb.com/) built by GitHub Pages: content lives in YAML files in `_data/`, pages are Liquid/HTML templates, styling is one CSS file. No theme gem, no build step.

| Path | What it is |
| --- | --- |
| `index.html`, `members.html`, `presentations.html`, `publications.html`, `simulation-chain.html`, `contact.html`, `404.html`, `wiki.md` | The pages |
| [`_data/`](_data/README.md) | All lists shown on the site, and their conventions |
| [`_layouts/`](_layouts/README.md) | Page skeletons |
| [`_includes/`](_includes/README.md) | Reusable pieces (header, footer, one talk, one paper, …) |
| [`assets/`](assets/README.md) | CSS, JavaScript, images |
| [`scripts/`](scripts/README.md) | Data checks, link checker, INSPIRE-HEP sync |
| `.github/workflows/` | CI (`site-checks.yml`), the monthly INSPIRE-HEP sync (`inspire-sync.yml`) and the optional fork preview (`fork-preview.yml`) |
| `MIGRATION_PLAN.md` | What is done and what is still open |

Each folder's README explains its contents; none of them is published on the website.

### Checks (CI)

Every pull request (and every push to `main`) runs `site-checks.yml`:

1. `scripts/check_data.py` — validates `_data/` and annotates the offending lines in the pull request;
2. a Jekyll build with the same builder as GitHub Pages;
3. `scripts/check_links.py` — every internal link and `#anchor` in the built site must resolve.

### Automatic publication updates

On the 2nd of every month, `inspire-sync.yml` runs the INSPIRE-HEP sync script: it fills in journal references, DOIs and years (e.g. for papers still marked `Preprint`) and adds new papers that INSPIRE tags with the ExTrEMe collaboration. If anything changed, it opens a pull request (or updates the one already open) for a maintainer to review; nothing is merged automatically. It can also be started by hand from the *Actions* tab.

- One-time setting in the repository: *Settings → Actions → General → Workflow permissions → Allow GitHub Actions to create and approve pull requests*.
- Cost: GitHub Actions is free for public repositories; a run takes about a minute.
- GitHub pauses scheduled workflows in repositories with no activity for 60 days; re-enable it from the *Actions* tab if that happens.
- Pull requests opened by the workflow do not start *Site Checks* by themselves; close and reopen the pull request to run them.

### Publishing

The site itself is deployed by GitHub Pages from `main`, independently of these checks. To make sure nothing broken is published, protect `main` (*Settings → Branches*): require pull requests and the *Site Checks* status.

### Previewing

Locally:

```bash
bundle install
bundle exec jekyll serve --livereload    # http://localhost:4000
```

From a personal fork, at `https://<user>.github.io/<fork-name>/` (the collaboration's domain is never touched):

1. *Settings → Pages → Source*: **GitHub Actions**;
2. *Settings → Secrets and variables → Actions → Variables*: `PAGES_PREVIEW` = `true`;
3. push to any branch. To deploy a branch other than the default one, allow it under *Settings → Environments → github-pages*.

The workflow (`fork-preview.yml`) never runs in the ExTrEMe-Collaboration organization.

### Legacy site

Content was migrated from `https://sites.ifi.unicamp.br/extreme/` (home with the list of talks, members, simulation chain) and `https://sites.ifi.unicamp.br/hadrex/publicacoes/` (publications and theses). See `MIGRATION_PLAN.md` for what was and was not carried over.
