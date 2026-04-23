# ExTrEMe Collaboration

The EXperiment and TheoRy in Extreme MattEr collaboration is a group of researchers focused on phenomenology of high-energy heavy-ion collisions, with special interest in connecting theory with experiments.

This repository hosts the collaboration website and wiki for GitHub Pages.

## Site Structure

- Home: `index.md`
- Members: `members.md`
- Publications: `publications.md`
- Simulation Chain: `simulation-chain.md`
- Presentations: `presentations.md`
- Wiki: `wiki.md`
- Contact: `contact.md`
- Migration plan: `MIGRATION_PLAN.md`

## Structured Content Data

- Publications dataset: `/_data/publications.yml`
- Talks dataset: `/_data/talks.yml`

The `publications.md` and `presentations.md` pages are rendered from these data files.

## Legacy Source Pages

- https://sites.ifi.unicamp.br/extreme/
- https://sites.ifi.unicamp.br/extreme/simulation-chain/
- https://sites.ifi.unicamp.br/extreme/members/
- https://sites.ifi.unicamp.br/extreme/contato/
- https://sites.ifi.unicamp.br/hadrex/publicacoes/

## Publishing

1. Push changes to the default branch.
2. In repository settings, enable GitHub Pages from the default branch root.
3. Confirm the site URL in GitHub Pages settings.

## Contribution Workflow

1. Open a branch for content updates.
2. Submit a pull request with a short summary and source links.
3. After merge, verify the rendered page and external links.

## Automated Checks

GitHub Actions workflow `site-checks.yml` runs on pushes and pull requests:

1. Jekyll build validation
2. Markdown link validation
