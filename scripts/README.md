# `scripts/` — maintenance tools

The Python scripts need Python 3; `check_data.py` and the INSPIRE script also need PyYAML (`pip install pyyaml`). `make_og_image.js` needs Node.js and Playwright. This folder is excluded from the published site (`exclude` in `_config.yml`).

## `check_data.py`

```bash
python3 scripts/check_data.py
```

Validates everything in `_data/` and reports each problem with file and line (in CI also as annotations on the pull request). It catches, among others: YAML syntax errors (with hints), tabs, a field written twice in one entry (usually a missing `- `), unknown or misspelled fields, presentation types outside the list, speakers that are not in `members.yml` (with a "did you mean" suggestion), malformed dates and years, links without `https://`, unquoted arXiv numbers, DOIs written as links, invalid ORCID iDs, malformed Lattes/INSPIRE links, and duplicate presentations or papers. Warnings (e.g. a presentation without title) do not fail the check.

## `check_links.py`

```bash
python3 scripts/check_links.py _site                    # after `bundle exec jekyll build`
python3 scripts/check_links.py _site --baseurl /my-fork  # site built under a sub-path
```

Checks that every internal link and `#anchor` in the built site resolves. External links are not fetched.

## `update_publications_from_inspirehep.py`

```bash
python3 scripts/update_publications_from_inspirehep.py --arxiv 2409.17127                       # add/update one paper
python3 scripts/update_publications_from_inspirehep.py --arxiv 2409.17127 --category "Theses"
python3 scripts/update_publications_from_inspirehep.py --sync-all                                # refresh venues, DOIs, years
python3 scripts/update_publications_from_inspirehep.py --update-missing-dois
python3 scripts/update_publications_from_inspirehep.py --sync-all --dry-run                      # preview only
```

Keeps `_data/publications.yml` in sync with INSPIRE-HEP and writes new entries in the site's format (venue `Journal Vol, Page (Year)`, author initials). It only fills in missing information and replaces `Preprint`/`Under review` venues; existing fields are never removed. It rewrites the whole file, so keep comments out of `publications.yml`, and review the diff before committing.

## `make_og_image.js`

```bash
bundle exec jekyll serve                                   # in one terminal
node scripts/make_og_image.js                              # writes assets/images/og-image.jpg
node scripts/make_og_image.js http://127.0.0.1:4000/ /tmp/preview.jpg   # custom URL / output
```

Regenerates the 1200×630 preview image used when the site is shared, by capturing the home-page hero at the fireball moment: fixed viewport, seeded `Math.random` (the same collision every run), a wait of about 1.75 s after load, saved as JPEG. Needs Playwright with Chromium (`npm install playwright && npx playwright install chromium`). Look at the result before committing it; to try a different collision, change `SEED` at the top of the script.
