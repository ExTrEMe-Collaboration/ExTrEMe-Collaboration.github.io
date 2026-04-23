# ExTrEMe Website Migration Plan

## Goal

Migrate legacy content from WordPress pages into a maintainable GitHub Pages site, while improving structure, discoverability, and long-term maintainability.

## Legacy Content Inventory

- Home: https://sites.ifi.unicamp.br/extreme/
- Simulation Chain: https://sites.ifi.unicamp.br/extreme/simulation-chain/
- Members: https://sites.ifi.unicamp.br/extreme/members/
- Contact: https://sites.ifi.unicamp.br/extreme/contato/
- Publications and theses: https://sites.ifi.unicamp.br/hadrex/publicacoes/

## Migration Mapping

- Legacy home -> index.md + presentations.md
- Legacy simulation chain -> simulation-chain.md
- Legacy members -> members.md
- Legacy contact form -> contact.md (email + GitHub issue workflow)
- Legacy publications page -> publications.md

## Phased Execution

1. Foundation phase (done)
- Build site skeleton and page routing
- Create migration tracker and content ownership checklist

2. Content phase
- Import full member roster with status labels (faculty, postdoc, student, alumni)
- Import publication entries into structured data files
- Import talks and presentations in year-based format
- Rehost critical static assets (figures, PDFs with permission)

3. Quality phase
- Add link checker in CI
- Add metadata and social preview cards
- Add accessibility checks (alt text, heading order, contrast)

4. Sustainability phase
- Add contribution guidelines and content update ownership
- Add release cadence (for example: quarterly site refresh)

## Suggested Improvements Over Legacy Site

- Separate public-facing content from internal wiki docs
- Convert long mixed lists into searchable structured sections
- Add short collaboration overview with current projects
- Add software and data resources page
- Add talks and events page with filters by year/topic
- Add funding and acknowledgements page with current grant numbers
- Add media kit (logo, citation text, canonical collaboration name)

## Important Missing Information to Add

- Official domain and canonical URL
- Official contact email and mailing list
- Current active projects and working groups
- Contribution policy for website and wiki
- Collaboration governance and code of conduct
- Data and software citation policy

## Ownership Checklist

Before importing binary assets and full text from the legacy site:

- Confirm permission to copy slide PDFs and external hosted files
- Confirm whether to mirror files in this repository or link externally
- Confirm which content is public vs internal only

## Next Step

Use a structured data source for publications and talks (YAML, JSON, or BibTeX) to avoid manually editing long Markdown lists.
