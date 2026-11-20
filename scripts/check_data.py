#!/usr/bin/env python3
"""
Validate the site's data files against the conventions documented in README.md.

    python3 scripts/check_data.py

Exits with status 1 and a list of problems if anything is off, so it can run in CI.
Requires PyYAML (`pip install pyyaml`).
"""

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

TALK_TYPES = ["Plenary talk", "Invited talk", "Talk", "Flash talk", "Seminar", "Colloquium", "Poster"]
TALK_KEYS = {"date", "speaker", "external", "type", "title", "event", "location",
             "url", "event_url", "video", "coauthors"}
TALK_REQUIRED = ["date", "speaker", "type", "event"]
MEMBER_KEYS = {"name", "position", "affiliation", "country", "url", "role"}
PUB_KEYS = {"year", "title", "authors", "venue", "note", "advisor", "doi", "arxiv", "url"}

errors = []


def err(where, msg):
    errors.append(f"{where}: {msg}")


def load(name):
    path = DATA / name
    try:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        err(name, f"invalid YAML: {e}")
        return None


def check_strings(where, entry):
    """No leading/trailing whitespace or doubled spaces in any string value."""
    for key, value in entry.items():
        values = value if isinstance(value, list) else [value]
        for v in values:
            if isinstance(v, str) and (v != v.strip() or "  " in v):
                err(where, f"stray whitespace in '{key}': {v!r}")


def is_url(v):
    return isinstance(v, str) and re.match(r"^https?://\S+$", v) is not None


# ---------------------------------------------------------------- members
members = load("members.yml") or []
member_names = []
for g_idx, group in enumerate(members):
    gwhere = f"members.yml[{group.get('group', g_idx)}]"
    for key in ("group", "id", "people"):
        if key not in group:
            err(gwhere, f"missing '{key}'")
    for person in group.get("people", []):
        where = f"{gwhere} {person.get('name', '?')}"
        for key in ("name", "position", "affiliation", "country"):
            if not person.get(key):
                err(where, f"missing '{key}'")
        for key in set(person) - MEMBER_KEYS:
            err(where, f"unknown field '{key}'")
        if "url" in person and not is_url(person["url"]):
            err(where, f"url is not an http(s) link: {person['url']!r}")
        check_strings(where, person)
        member_names.append(person.get("name"))
for name, n in Counter(member_names).items():
    if n > 1:
        err("members.yml", f"'{name}' listed {n} times")
member_set = set(member_names)

# ---------------------------------------------------------------- talks
talks = load("talks.yml") or []
seen = Counter()
for i, t in enumerate(talks):
    where = f"talks.yml #{i + 1} ({t.get('date', '?')}, {t.get('speaker', '?')})"
    for key in TALK_REQUIRED:
        if not t.get(key):
            err(where, f"missing '{key}'")
    for key in set(t) - TALK_KEYS:
        err(where, f"unknown field '{key}'")
    date = t.get("date")
    if not isinstance(date, str) or not re.match(r"^\d{4}-(0[1-9]|1[0-2])$", date):
        err(where, f"date must be a quoted \"YYYY-MM\" string, got {date!r}")
    if t.get("type") not in TALK_TYPES:
        err(where, f"type {t.get('type')!r} is not one of: {', '.join(TALK_TYPES)}")
    speaker = t.get("speaker")
    if t.get("external"):
        if speaker in member_set:
            err(where, f"'{speaker}' is a member; remove 'external: true'")
    elif speaker not in member_set:
        err(where, f"speaker {speaker!r} does not match a name in members.yml "
                   "(fix the spelling, or add 'external: true' for non-members)")
    if "title" in t and not isinstance(t["title"], str):
        err(where, "title must be a string")
    for key in ("url", "event_url", "video"):
        if key in t and not is_url(t[key]):
            err(where, f"{key} is not an http(s) link: {t[key]!r}")
    if "coauthors" in t and not (isinstance(t["coauthors"], list) and all(isinstance(c, str) for c in t["coauthors"])):
        err(where, "coauthors must be a list of names")
    loc = t.get("location")
    if loc is not None and loc != "Online" and "," not in loc and loc not in ("Brazil",):
        err(where, f"location should look like 'City, Country' (or 'Online'), got {loc!r}")
    check_strings(where, t)
    seen[(date, speaker, t.get("title"), t.get("event"))] += 1
for key, n in seen.items():
    if n > 1:
        err("talks.yml", f"duplicate entry: {key}")

# ---------------------------------------------------------------- publications
pubs = load("publications.yml") or []
arxiv_seen = Counter()
for group in pubs:
    gwhere = f"publications.yml[{group.get('category', '?')}]"
    if not group.get("items"):
        err(gwhere, "category has no items")
    for p in group.get("items", []):
        where = f"{gwhere} {str(p.get('title', '?'))[:50]}"
        for key in ("year", "title", "authors"):
            if not p.get(key):
                err(where, f"missing '{key}'")
        for key in set(p) - PUB_KEYS:
            err(where, f"unknown field '{key}'")
        if not isinstance(p.get("year"), int):
            err(where, f"year must be a number, got {p.get('year')!r}")
        if "arxiv" in p:
            if not isinstance(p["arxiv"], str):
                err(where, f"arxiv must be a quoted string (YAML turned {p['arxiv']!r} into a number)")
            else:
                arxiv_seen[p["arxiv"]] += 1
        if "doi" in p and (not isinstance(p["doi"], str) or not p["doi"].startswith("10.")):
            err(where, f"doi must be the bare identifier (10.xxxx/...), got {p['doi']!r}")
        if "url" in p and not is_url(p["url"]):
            err(where, f"url is not an http(s) link: {p['url']!r}")
        check_strings(where, p)
for arxiv, n in arxiv_seen.items():
    if n > 1:
        err("publications.yml", f"arXiv:{arxiv} appears {n} times")

# ---------------------------------------------------------------- institutions
for inst in load("institutions.yml") or []:
    where = f"institutions.yml {inst.get('short', '?')}"
    for key in ("name", "short", "city", "country"):
        if not inst.get(key):
            err(where, f"missing '{key}'")

# ---------------------------------------------------------------- report
if errors:
    print(f"✗ {len(errors)} problem(s) in _data/:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

n_pubs = sum(len(g.get("items", [])) for g in pubs)
print(f"✓ Data OK: {len(member_names)} people, {len(talks)} talks, {n_pubs} publications")
