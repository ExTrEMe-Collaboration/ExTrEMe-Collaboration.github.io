# Website migration: status and open items

Maintained by the website maintainers; tick items off (or add new ones) in the same pull request that does the work.
Last reviewed: November 2026.

## Done

- [x] Site skeleton, routing and custom domain (`www.extreme-collaboration.science`).
- [x] Content migrated from the legacy WordPress site (`sites.ifi.unicamp.br/extreme`): members, simulation chain, the full list of presentations (72), publications and theses (21 after the membership audit and the category review below).
- [x] Structured data in `_data/` with documented conventions (`_data/README.md`) and automatic validation (`scripts/check_data.py`).
- [x] Presentations and publications pages with search and filters (type, speaker, category).
- [x] Lattes, ORCID and INSPIRE-HEP links on the Members page. ORCID iDs verified in the ORCID registry; INSPIRE profiles matched by ORCID (on the profile, or on the author entries of the person's papers), not by name. R. Krupczak's INSPIRE link pointed to another person's profile and was corrected. G. Dias has no INSPIRE profile yet.
- [x] CI: data validation, Jekyll build, internal link check.
- [x] Monthly INSPIRE-HEP sync (`.github/workflows/inspire-sync.yml`): proposes updated journal references and new collaboration papers as a pull request.
- [x] Social-preview metadata, image alt texts, colour contrast checked against WCAG AA, dark mode.
- [x] Contribution guide for non-specialists (top of `README.md`) and maintainer notes in each folder.
- [x] Fork preview workflow for testing changes on GitHub Pages.
- [x] **Membership audit** (November 2026): every person on the Members page was checked against the author lists of every paper on the site and against the legacy ExTrEMe members page. Six people listed as alumni, and their theses, were removed: they were never ExTrEMe members. They had been added because, when the legacy site was scraped, the ExTrEMe pages and the pages of the HADREX group (same server, overlapping people) were read together and their member and thesis lists merged by mistake. Co-authors of collaboration papers who were never members are not listed either. The collaboration paper arXiv:2611.18290 was added.
- [x] **Presentations**: every presentation listed on the legacy ExTrEMe page is kept, including three given by non-members (marked `external: true` in `_data/talks.yml`).
- [x] **Publication categories** (November 2026): the publications list came from the HADREX publications page, which the legacy ExTrEMe site linked as its own. Kept: *ExTrEMe Collaboration Papers*, *Selected Related Theory Papers* (M. Luzum's selection) and members' *Theses*. Removed as not ExTrEMe work: *Pythia and Angantyr Studies*, *3C Collaboration and Vorticity* (another collaboration) and *NeXSPheRIO Legacy Papers*.
- [x] **Slides on the legacy server**: eight presentation links point to PDFs on `sites.ifi.unicamp.br` (all reachable in November 2026). They stay linked there rather than copied into this repository (87 MB, mostly two files).

## Open — to check or decide

- [ ] **Verify FAPESP grant 2017/04616-7.** The legacy home page lists it as "FAPESP temático grant 2017/04616-7", so it is shown on the home page, but no paper indexed by INSPIRE-HEP acknowledges that number (2017/05685-2 and 2023/13749-1 appear in 111 and 43 papers). FAPESP's online library could not be searched automatically. Confirm with the coordinators, then correct or remove it in `index.html` (a maintainer comment marks the spot).
- [ ] **Protect `main`** in the collaboration repository (to discuss with M. Luzum): require pull requests and the *Site Checks* status before merging. GitHub Pages publishes `main` regardless of the checks.
- [ ] **Enable the monthly INSPIRE sync** in the collaboration repository: *Settings → Actions → General → Workflow permissions → Allow GitHub Actions to create and approve pull requests*. Decide who reviews its pull requests (and contributions in general).
- [ ] **One presentation without title**: J. Noronha at WWND 2019 (not on BNL's Indico; the legacy slide link is dead; ask him). His Initial Stages 2019 title was recovered from the conference Indico.
- [ ] **One title to confirm**: M. Hippert's Initial Stages 2019 flash talk shows the title of his slides (*Understanding p<sub>T</sub>-dependent flow fluctuations from initial geometry*); the conference programme lists it as *Linear and non-linear response of two-particle correlations to initial-geometry fluctuations*.
- [ ] **Which list of theory papers to keep.** *Selected Related Theory Papers* shows M. Luzum's selection (5 papers). The legacy HADREX publications page had a longer list, "Papers by members of the project supported by the FAPESP temático grant 2017/05685-2"; the 12 papers from it that are not shown are arXiv 1708.06255, 1709.03131, 1802.09011, 1804.04771, 1804.05210, 1805.00882, 1807.06191, 1808.06436, 1906.10768, 1907.12695, 2002.12735 and 2003.00181. Keep the selection, or add some of these back (`scripts/update_publications_from_inspirehep.py --arxiv <id> --category "Selected Related Theory Papers"`).
- [ ] **Hero animation: make it less distracting** (M. Luzum's concern: a repeating animation may become annoying). For now it plays one collision about every 16 s (`T_REST` in `assets/js/collision.js`). Options being designed: play once and settle on a still frame with a replay control; tie the collision to scrolling; a slower, dimmer ambient loop. Decide, then implement.
- [ ] **Wiki** (`/wiki/`, not linked from the menu): kept for now; develop or remove later.

## Next steps (later)

Current projects / working groups page; official mailing list; governance and code of conduct; data and software citation policy; media kit (logo, canonical name, citation text). The collaboration's code repositories are expected to stay private, so no public software page is planned.

## Rules of thumb for maintainers

- **Who is a member.** The coordinator decides; when in doubt, ask. Useful evidence: the legacy ExTrEMe members page, kept current until about 2023 (people in the group at that time but not on that list were most likely not members), and authorship of papers signed by the ExTrEMe Collaboration. Being in the HADREX group does not by itself make someone a member, and neither does co-authoring a paper with the collaboration. People who leave move to *Alumni & Former Members*.
- **What is published.** Only theses by ExTrEMe members appear on the Publications page; other HADREX material belongs on the HADREX site. Everything that was on `sites.ifi.unicamp.br/extreme/` itself is considered correct.
- **Identifiers.** Match INSPIRE profiles by ORCID, never by name alone: several members have namesakes in physics (e.g. another Jun Takahashi on INSPIRE).

## Deliberately not migrated

- HADREX-only material from `sites.ifi.unicamp.br/hadrex/` (group roster, medical-physics papers, ALICE and other theses outside the ExTrEMe scope).
- Internal links from the legacy home page (analysis logbook folder, analysis code repository).
- Papers from the HADREX publications page that are not ExTrEMe work: PYTHIA/Angantyr studies, 3C collaboration (vorticity) papers and NeXSPheRIO papers.
- Individual grants named on the legacy home page (2018/01245-0, 2018/07833-1, 2016/24029-6, CNPq 306397/2016); the home page lists the thematic projects and "subsequent research grants".

## Legacy pages (for reference)

| Legacy page | Now |
| --- | --- |
| `sites.ifi.unicamp.br/extreme/` (description, list of presentations) | Home page, `presentations.html`, `_data/talks.yml` |
| `sites.ifi.unicamp.br/extreme/simulation-chain/` | `simulation-chain.html` |
| `sites.ifi.unicamp.br/extreme/members/` | `members.html`, `_data/members.yml` |
| `sites.ifi.unicamp.br/extreme/contato/` (contact form) | `contact.html` (email and GitHub issues) |
| `sites.ifi.unicamp.br/hadrex/publicacoes/` | `publications.html`, `_data/publications.yml` |
