#!/usr/bin/env python3
"""
Validate the site's data files (_data/*.yml) against the conventions in README.md.

    python3 scripts/check_data.py

Every problem is reported with its file and line number. Inside GitHub Actions
the problems are also emitted as annotations, so they show up directly on the
lines of the pull request. Exits with status 1 if anything must be fixed.
Requires PyYAML (`pip install pyyaml`).
"""

import datetime
import difflib
import os
import re
import sys
from collections import Counter
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "_data"
IN_ACTIONS = os.environ.get("GITHUB_ACTIONS") == "true"
THIS_YEAR = datetime.date.today().year

TALK_TYPES = ["Plenary talk", "Invited talk", "Talk", "Flash talk", "Seminar", "Colloquium", "Poster"]
# Common legacy or informal spellings, mapped to the type to suggest.
TYPE_ALIASES = {"oral": "Talk", "contributed": "Talk", "contributed talk": "Talk", "invited": "Invited talk",
                "plenary": "Plenary talk", "invited plenary": "Plenary talk", "flash": "Flash talk",
                "poster": "Poster", "seminar": "Seminar", "colloquium": "Colloquium"}
TALK_KEYS = ["date", "speaker", "external", "type", "title", "event", "location",
             "url", "event_url", "video", "coauthors"]
TALK_REQUIRED = ["date", "speaker", "type", "event"]
MEMBER_KEYS = ["name", "position", "affiliation", "country", "lattes", "orcid", "inspire", "url", "role"]
GROUP_KEYS = ["group", "id", "people", "alumni"]
PUB_KEYS = ["year", "title", "authors", "venue", "note", "advisor", "doi", "arxiv", "url"]
CATEGORY_KEYS = ["category", "description", "items"]
INSTITUTION_KEYS = ["name", "short", "city", "country"]

YAML_HINT = ("Common causes: indentation with tabs or an inconsistent number of spaces; "
             "a new entry that does not start with '- '; or a value containing ': ' "
             "(e.g. a title) that is not wrapped in double quotes.")

problems = []   # (level, file, line, message)


def report(level, file, line, msg):
    problems.append((level, file, line, msg))


def error(file, line, msg):
    report("error", file, line, msg)


def warning(file, line, msg):
    report("warning", file, line, msg)


def suggest(value, options):
    match = difflib.get_close_matches(str(value), options, n=1, cutoff=0.6)
    return f" Did you mean {match[0]!r}?" if match else ""


# ----------------------------------------------------------------- YAML loading
class Mapping(dict):
    """A dict that remembers the line it started on (1-based)."""
    line = 0


class Loader(yaml.SafeLoader):
    pass


def construct_mapping(loader, node):
    loader.flatten_mapping(node)
    result = Mapping()
    result.line = node.start_mark.line + 1
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=True)
        if key in result:
            raise yaml.constructor.ConstructorError(
                None, None,
                f"the field '{key}' appears twice in the entry that starts on line {result.line}. "
                "If you are adding a new entry, it must start with '- '.",
                key_node.start_mark)
        result[key] = loader.construct_object(value_node, deep=True)
    return result


Loader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping)


def load(name):
    path = DATA / name
    rel = f"_data/{name}"
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        error(rel, 1, "file is not valid UTF-8 text (save it with UTF-8 encoding)")
        return None
    for i, line in enumerate(text.splitlines(), 1):
        if "\t" in line:
            error(rel, i, "contains a tab character; indent with spaces only")
    try:
        return yaml.load(text, Loader=Loader)
    except yaml.MarkedYAMLError as e:
        mark = e.problem_mark or e.context_mark
        line = mark.line + 1 if mark else 1
        error(rel, line, f"YAML syntax error: {e.problem or e}. {YAML_HINT}")
    except yaml.YAMLError as e:
        error(rel, 1, f"YAML syntax error: {e}. {YAML_HINT}")
    return None


# ----------------------------------------------------------------- helpers
def line_of(entry):
    return getattr(entry, "line", 0)


def check_keys(file, entry, allowed, what):
    for key in entry:
        if key not in allowed:
            error(file, line_of(entry), f"{what}: unknown field '{key}'.{suggest(key, allowed)}")


def check_strings(file, entry, what):
    for key, value in entry.items():
        for v in (value if isinstance(value, list) else [value]):
            if isinstance(v, str) and (v != v.strip() or "  " in v):
                error(file, line_of(entry), f"{what}: stray spaces in '{key}': {v!r}")


def is_url(v):
    return isinstance(v, str) and re.match(r"^https?://\S+$", v) is not None


def orcid_ok(value):
    """ORCID format and ISO 7064 mod 11-2 check digit."""
    if not isinstance(value, str) or not re.match(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$", value):
        return False
    digits = value.replace("-", "")
    total = 0
    for ch in digits[:-1]:
        total = (total + int(ch)) * 2
    check = (12 - total % 11) % 11
    return digits[-1] == ("X" if check == 10 else str(check))


def must_be_list(file, data, what):
    if data is None:
        return []
    if not isinstance(data, list):
        error(file, 1, f"{what} must be a list of entries, each starting with '- '")
        return []
    good = []
    for item in data:
        if isinstance(item, dict):
            good.append(item)
        else:
            error(file, line_of(data), f"found {item!r} where an entry was expected (entries start with '- ' "
                                       "followed by indented 'field: value' lines)")
    return good


# ----------------------------------------------------------------- members
F = "_data/members.yml"
members = must_be_list(F, load("members.yml"), "members.yml")
member_names = []
group_ids = Counter()
for group in members:
    gname = group.get("group", "?")
    check_keys(F, group, GROUP_KEYS, f"group '{gname}'")
    for key in ("group", "id", "people"):
        if key not in group:
            error(F, line_of(group), f"group '{gname}': missing '{key}'")
    group_ids[group.get("id")] += 1
    for person in must_be_list(F, group.get("people"), f"group '{gname}' people"):
        who = person.get("name", "?")
        for key in ("name", "position", "affiliation", "country"):
            if not person.get(key):
                error(F, line_of(person), f"{who}: missing '{key}'")
        check_keys(F, person, MEMBER_KEYS, who)
        check_strings(F, person, who)
        if "lattes" in person and not re.match(r"^https://lattes\.cnpq\.br/\d{16}$", str(person["lattes"])):
            error(F, line_of(person), f"{who}: lattes must look like https://lattes.cnpq.br/1234567890123456, got {person['lattes']!r}")
        if "orcid" in person and not orcid_ok(person["orcid"]):
            error(F, line_of(person), f"{who}: orcid {person['orcid']!r} is not a valid ORCID iD (write only the iD, e.g. 0000-0002-4091-1779)")
        if "inspire" in person and not re.match(r"^https://inspirehep\.net/authors/\d+$", str(person["inspire"])):
            error(F, line_of(person), f"{who}: inspire must look like https://inspirehep.net/authors/1234567, got {person['inspire']!r}")
        if "url" in person and not is_url(person["url"]):
            error(F, line_of(person), f"{who}: url is not an http(s) link: {person['url']!r}")
        member_names.append(who)
for gid, n in group_ids.items():
    if n > 1:
        error(F, 1, f"group id '{gid}' is used {n} times")
for name, n in Counter(member_names).items():
    if n > 1:
        error(F, 1, f"'{name}' is listed {n} times")
member_set = set(member_names)

# ----------------------------------------------------------------- talks
F = "_data/talks.yml"
talks = must_be_list(F, load("talks.yml"), "talks.yml")
seen = {}
for t in talks:
    where = f"talk ({t.get('date', '?')}, {t.get('speaker', '?')})"
    ln = line_of(t)
    for key in TALK_REQUIRED:
        if not t.get(key):
            error(F, ln, f"{where}: missing '{key}'")
    check_keys(F, t, TALK_KEYS, where)
    check_strings(F, t, where)

    date = t.get("date")
    m = re.match(r"^(\d{4})-(0[1-9]|1[0-2])$", date) if isinstance(date, str) else None
    if not m:
        shown = date if isinstance(date, str) else str(date)
        error(F, ln, f"{where}: date must be year and month in double quotes, e.g. \"2025-11\" (got {shown})")
    elif not 1990 <= int(m.group(1)) <= THIS_YEAR + 2:
        error(F, ln, f"{where}: the year in date {date!r} looks wrong")

    ttype = t.get("type")
    if ttype not in TALK_TYPES:
        alias = TYPE_ALIASES.get(str(ttype).strip().lower())
        hint = f" Did you mean {alias!r}?" if alias else suggest(ttype, TALK_TYPES)
        error(F, ln, f"{where}: type {ttype!r} is not one of {', '.join(TALK_TYPES)}.{hint}")

    speaker = t.get("speaker")
    if t.get("external") not in (None, True):
        error(F, ln, f"{where}: 'external' can only be 'true'")
    if t.get("external"):
        if speaker in member_set:
            error(F, ln, f"{where}: '{speaker}' is in members.yml; remove 'external: true'")
    elif speaker not in member_set:
        error(F, ln, f"{where}: speaker {speaker!r} is not in _data/members.yml.{suggest(speaker, sorted(member_set))} "
                     "Use the exact name from members.yml, add the person there, or add 'external: true' for a non-member.")

    for key in ("title", "event", "location"):
        if key in t and not isinstance(t[key], str):
            error(F, ln, f"{where}: {key} must be text; wrap it in double quotes")
    for key in ("url", "event_url", "video"):
        if key in t and not is_url(t[key]):
            error(F, ln, f"{where}: {key} must be a full link starting with https://, got {t[key]!r}")
    if "coauthors" in t and not (isinstance(t["coauthors"], list) and all(isinstance(c, str) for c in t["coauthors"])):
        error(F, ln, f"{where}: coauthors must be a list, e.g. [A. B. Name, C. Other]")
    loc = t.get("location")
    if isinstance(loc, str) and loc != "Online" and "," not in loc and loc != "Brazil":
        warning(F, ln, f"{where}: location should look like 'City, Country' (or 'Online'), got {loc!r}")
    if not t.get("title"):
        warning(F, ln, f"{where}: no title (shown as 'Title not recorded')")

    key = (date, speaker)
    title = str(t.get("title", "")).lower()
    for other_title, other_line in seen.get(key, []):
        if title and difflib.SequenceMatcher(None, title, other_title).ratio() > 0.85:
            error(F, ln, f"{where}: looks like a duplicate of the entry on line {other_line}")
    seen.setdefault(key, []).append((title, ln))

# ----------------------------------------------------------------- publications
F = "_data/publications.yml"
pubs = must_be_list(F, load("publications.yml"), "publications.yml")
arxiv_seen = {}
categories = Counter()
for group in pubs:
    cname = group.get("category", "?")
    categories[cname] += 1
    check_keys(F, group, CATEGORY_KEYS, f"category '{cname}'")
    items = must_be_list(F, group.get("items"), f"category '{cname}' items")
    if not items:
        error(F, line_of(group), f"category '{cname}' has no items")
    for p in items:
        where = f"publication '{str(p.get('title', '?'))[:50]}'"
        ln = line_of(p)
        for key in ("year", "title", "authors"):
            if not p.get(key):
                error(F, ln, f"{where}: missing '{key}'")
        check_keys(F, p, PUB_KEYS, where)
        check_strings(F, p, where)
        year = p.get("year")
        if not isinstance(year, int) or not 1990 <= year <= THIS_YEAR + 1:
            error(F, ln, f"{where}: year must be a number like 2024 (no quotes), got {year!r}")
        for key in ("title", "authors", "venue", "note", "advisor"):
            if key in p and not isinstance(p[key], str):
                error(F, ln, f"{where}: {key} must be text; wrap it in double quotes")
        if "arxiv" in p:
            a = p["arxiv"]
            if not isinstance(a, str):
                error(F, ln, f"{where}: arxiv must be in quotes, e.g. arxiv: '2409.17127' (without quotes YAML reads it as a number and may drop digits)")
            elif not re.match(r"^(\d{4}\.\d{4,5}|[a-z\-]+(\.[A-Z]{2})?/\d{7})$", a):
                error(F, ln, f"{where}: arxiv {a!r} is not an arXiv identifier like '2409.17127'")
            elif a in arxiv_seen:
                error(F, ln, f"{where}: arXiv:{a} is already listed on line {arxiv_seen[a]}")
            else:
                arxiv_seen[a] = ln
        if "doi" in p and (not isinstance(p["doi"], str) or not re.match(r"^10\.\d{4,9}/\S+$", p["doi"])):
            error(F, ln, f"{where}: doi must be the bare identifier, e.g. 10.1103/PhysRevC.110.064904 (no https://doi.org/), got {p['doi']!r}")
        if "url" in p and not is_url(p["url"]):
            error(F, ln, f"{where}: url must be a full link starting with https://, got {p['url']!r}")
for cname, n in categories.items():
    if n > 1:
        error(F, 1, f"category '{cname}' appears {n} times; put all its items under one category")

# ----------------------------------------------------------------- institutions
F = "_data/institutions.yml"
for inst in must_be_list(F, load("institutions.yml"), "institutions.yml"):
    check_keys(F, inst, INSTITUTION_KEYS, f"institution {inst.get('short', '?')}")
    for key in INSTITUTION_KEYS:
        if not inst.get(key):
            error(F, line_of(inst), f"institution {inst.get('short', '?')}: missing '{key}'")

# ----------------------------------------------------------------- navigation
F = "_data/navigation.yml"
for item in must_be_list(F, load("navigation.yml"), "navigation.yml"):
    if not item.get("title") or not str(item.get("url", "")).startswith("/"):
        error(F, line_of(item), "each menu item needs a 'title' and a 'url' starting with '/'")

# ----------------------------------------------------------------- report
errors = [p for p in problems if p[0] == "error"]
warnings = [p for p in problems if p[0] == "warning"]
for level, file, line, msg in sorted(problems, key=lambda p: (p[1], p[2])):
    if IN_ACTIONS:
        clean = msg.replace("%", "%25").replace("\r", "").replace("\n", " ")
        print(f"::{level} file={file},line={max(line, 1)}::{clean}")
    print(f"{'✗' if level == 'error' else '!'} {file}:{line}: {msg}")

if errors:
    print(f"\n✗ {len(errors)} problem(s) must be fixed before the site can be published"
          + (f" ({len(warnings)} warning(s) can be ignored)" if warnings else "") + ".")
    sys.exit(1)

n_pubs = sum(len(g.get("items") or []) for g in pubs)
print(f"✓ Data OK: {len(member_names)} people, {len(talks)} presentations, {n_pubs} publications"
      + (f" ({len(warnings)} warning(s))" if warnings else ""))
