# Website migration: status and open items

Maintained by the website maintainers; tick items off (or add new ones) in the same pull request that does the work.
Last reviewed: November 2026.

## Done

- [x] Site skeleton, routing and custom domain (`www.extreme-collaboration.science`).
- [x] Content migrated from the legacy WordPress site (`sites.ifi.unicamp.br/extreme`): members, simulation chain, the full list of presentations (72), publications and theses (49).
- [x] Structured data in `_data/` with documented conventions (`_data/README.md`) and automatic validation (`scripts/check_data.py`).
- [x] Presentations and publications pages with search and filters (type, speaker, category).
- [x] ORCID iDs and Lattes CVs on the Members page (verified against INSPIRE-HEP, the ORCID registry, the HADREX member list and the members themselves). R. Krupczak's INSPIRE link pointed to another person's profile and was corrected.
- [x] CI: data validation, Jekyll build, internal link check.
- [x] Social-preview metadata, image alt texts, colour contrast checked against WCAG AA, dark mode.
- [x] Contribution guide for non-specialists (top of `README.md`) and maintainer notes in each folder.
- [x] Fork preview workflow for testing changes on GitHub Pages.

## Open — content (needs a decision or information from members)

- [ ] **Missing identifiers.** Lattes and ORCID for Eduardo Oliveira Pinho. ORCID for João Paulo Picchetti: the registry has a record under that name (0000-0003-3273-9726) with no other information, to be confirmed by him. André Vieira da Silva has no ORCID.
- [ ] **Membership audit** (author lists of every paper on the site, November 2026). To decide:
  - Alumni who co-authored no ExTrEMe paper: G. Reis Garcia and D. Silva de Albuquerque (ALICE theses, HADREX only), A. Vieira da Silva (PYTHIA/Angantyr line), G. Rabelo Soares, J. P. Picchetti, V. H. Ribeiro (3C line). Keep, or move off the ExTrEMe page?
  - Their theses on the Publications page, for the same reason.
  - Co-authors of ExTrEMe papers not on the Members page: R. Derradi de Souza (2019 PCA paper; HADREX alumnus) and J.-F. Paquet (2024 Bayesian paper; external).
  - Collaboration paper missing from the site: arXiv:2611.18290, *Are hybrid hydrodynamic models missing soft-pion physics?* (13 current members).
- [ ] **Two presentations without title**: J. Noronha at Initial Stages 2019 and at WWND 2019 (the legacy slide link for the latter is dead).
- [ ] **Slides hosted on the legacy server.** Eight presentation links point to PDFs on `sites.ifi.unicamp.br`. If that server goes away they break: decide whether to copy them into this repository (with the authors' permission) or accept the risk.
- [ ] **Wiki** (`/wiki/`, not linked from the menu): develop, or remove.
- [ ] Ideas from the original plan, not started: current projects / working groups page; software and data resources page; official mailing list; governance and code of conduct; data and software citation policy; media kit (logo, canonical name, citation text).

## Open — maintenance

- [ ] Protect `main` in the collaboration repository: require pull requests and the *Site Checks* status before merging (GitHub Pages publishes `main` regardless of the checks).
- [ ] Decide who reviews contributions, and refresh publications periodically (`scripts/update_publications_from_inspirehep.py --sync-all`, e.g. every few months).

## Deliberately not migrated

- HADREX-only material from `sites.ifi.unicamp.br/hadrex/` (group roster, medical-physics papers, ALICE and other theses outside the ExTrEMe scope).
- Internal links from the legacy home page (analysis logbook folder, analysis code repository).
- FAPESP grant **2017/04616-7** (decided November 2026: left out). The legacy home page named it as the thematic grant, but it appears in no paper indexed by INSPIRE-HEP, whereas the thematic projects 2017/05685-2 and 2023/13749-1 are acknowledged in 111 and 43 papers; it is most likely a typo. A maintainer comment next to the grant numbers in `index.html` records this. Individual grants named on the legacy page (2018/01245-0, 2018/07833-1, 2016/24029-6, CNPq 306397/2016) are not listed on the site either.

## Legacy pages (for reference)

| Legacy page | Now |
| --- | --- |
| `sites.ifi.unicamp.br/extreme/` (description, list of presentations) | Home page, `presentations.html`, `_data/talks.yml` |
| `sites.ifi.unicamp.br/extreme/simulation-chain/` | `simulation-chain.html` |
| `sites.ifi.unicamp.br/extreme/members/` | `members.html`, `_data/members.yml` |
| `sites.ifi.unicamp.br/extreme/contato/` (contact form) | `contact.html` (email and GitHub issues) |
| `sites.ifi.unicamp.br/hadrex/publicacoes/` | `publications.html`, `_data/publications.yml` |
