#!/usr/bin/env python3
"""
Update publications.yml from INSPIREHEP API.

Usage:
  python3 scripts/update_publications_from_inspirehep.py                    # Sync existing entries + check collaboration
  python3 scripts/update_publications_from_inspirehep.py --sync-all         # Refresh all existing arXiv entries from INSPIREHEP
  python3 scripts/update_publications_from_inspirehep.py --arxiv 2409.17127 # Add/update by arXiv ID
  python3 scripts/update_publications_from_inspirehep.py --update-missing-dois  # Fill in missing DOIs
  python3 scripts/update_publications_from_inspirehep.py --dry-run          # Preview changes without writing
"""

import urllib.request
import urllib.parse
import urllib.error
import json
import argparse
import sys
import re
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: 'yaml' module not found. Run with Anaconda Python or install pyyaml: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

YAML_PATH = Path(__file__).parent.parent / "_data" / "publications.yml"
INSPIRE_API = "https://inspirehep.net/api/literature"

def fetch_inspire(query, size=100):
    """Fetch results from INSPIREHEP API using standard library urllib."""
    params = urllib.parse.urlencode({"q": query, "size": size})
    url = f"{INSPIRE_API}?{params}"
    headers = {"User-Agent": "ExTrEMe-Publications-Sync/1.0"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
            hits = data.get("hits", {}).get("hits", [])
            return hits
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError) as e:
        print(f"✗ Error querying INSPIREHEP ({query}): {e}", file=sys.stderr)
        return []

def clean_latex(text):
    """Strip basic XML/HTML tags and normalize spaces."""
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", text)
    return " ".join(text.split())

def parse_inspire_record(record):
    """Extract publication info from INSPIREHEP record."""
    metadata = record.get("metadata", {})

    # Title
    title = None
    if "titles" in metadata and metadata["titles"]:
        title = clean_latex(metadata["titles"][0].get("title", ""))

    # Authors
    authors = ""
    if "authors" in metadata and metadata["authors"]:
        author_names = [a.get("full_name") for a in metadata["authors"] if a.get("full_name")]
        if author_names:
            # Format as First Initial. Last or standard list
            authors = ", ".join(author_names)
            if len(author_names) > 3:
                # E.g. "T. S. Domingues et al."
                first = author_names[0]
                if "," in first:
                    last, first_name = [x.strip() for x in first.split(",", 1)]
                    initials = " ".join([f"{part[0]}." for part in first_name.split() if part])
                    authors = f"{initials} {last} et al."
                else:
                    authors = f"{first} et al."

    # Year
    year = None
    if "publication_info" in metadata and metadata["publication_info"]:
        year = metadata["publication_info"][0].get("year")
    if not year and "earliest_date" in metadata:
        year = metadata["earliest_date"][:4]
    elif not year and "preprint_date" in metadata:
        year = metadata["preprint_date"][:4]

    # DOI
    doi = None
    if "dois" in metadata and metadata["dois"]:
        # Prefer standard DOI (e.g. 10.1103/PhysRevC... over random short tags if available)
        for d in metadata["dois"]:
            val = d.get("value")
            if val and "PhysRev" in val:
                doi = val
                break
        if not doi:
            doi = metadata["dois"][0].get("value")

    # arXiv
    arxiv = None
    if "arxiv_eprints" in metadata and metadata["arxiv_eprints"]:
        arxiv = metadata["arxiv_eprints"][0].get("value")

    # Venue (journal title or conference)
    venue = ""
    if "publication_info" in metadata and metadata["publication_info"]:
        pub_info = metadata["publication_info"][0]
        journal_title = pub_info.get("journal_title")
        if journal_title:
            venue = journal_title
            # Note: Inspire uses 'journal_volume', not 'volume'
            volume = pub_info.get("journal_volume") or pub_info.get("volume")
            if volume:
                venue += f" {volume}"
            artid = pub_info.get("artid") or pub_info.get("page_start")
            if artid:
                venue += f", {artid}"
        elif "conference_record" in pub_info:
            venue = pub_info.get("conference_record", {}).get("name", "")
        elif pub_info.get("pubinfo_freetext"):
            venue = pub_info["pubinfo_freetext"]

    entry = {}
    if year:
        entry["year"] = int(year) if isinstance(year, str) and year.isdigit() else year
    if title:
        entry["title"] = title
    if authors:
        entry["authors"] = authors
    if venue:
        entry["venue"] = venue
    if doi:
        entry["doi"] = doi
    if arxiv:
        entry["arxiv"] = str(arxiv)

    return entry

def load_yaml():
    """Load existing publications.yml."""
    with open(YAML_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or []
    return data

def save_yaml(data):
    """Save updated publications.yml preserving string formatting for arXiv IDs."""
    with open(YAML_PATH, "w", encoding="utf-8") as f:
        yaml.dump(data, f, sort_keys=False, allow_unicode=True, default_flow_style=False)

    # Post-process to quote arXiv IDs so YAML doesn't treat decimal-like IDs as floats
    with open(YAML_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Quote unquoted arXiv numbers: e.g. arxiv: 2311.02210 -> arxiv: '2311.02210'
    content = re.sub(r"(arxiv:\s+)([0-9]{4}\.[0-9]+)(\s|$)", r"\1'\2'\3", content)

    with open(YAML_PATH, "w", encoding="utf-8") as f:
        f.write(content)

def find_entry_by_arxiv(yaml_data, arxiv_id):
    """Find an existing entry by arXiv ID in the YAML structure."""
    target_id = str(arxiv_id).strip()
    for category in yaml_data:
        for item in category.get("items", []):
            item_arxiv = str(item.get("arxiv", "")).strip()
            if item_arxiv == target_id:
                return category, item
    return None, None

def is_provisional_venue(venue):
    """Check if a venue string indicates an unpublished or preprint state."""
    if not venue:
        return True
    v = venue.lower().strip()
    return any(p in v for p in ["under review", "preprint", "submitted", "in preparation", "to be published"])

def merge_entries(existing, new):
    """Merge new fields into existing entry, updating provisional values when published."""
    # If newly found a DOI and existing doesn't have one
    if new.get("doi") and not existing.get("doi"):
        existing["doi"] = new["doi"]

    # If newly found a real journal venue and existing is provisional
    if new.get("venue") and (is_provisional_venue(existing.get("venue")) or not existing.get("venue")):
        existing["venue"] = new["venue"]
        if new.get("year"):
            existing["year"] = new["year"]

    # Fill in any missing fields
    for key, value in new.items():
        if key not in existing or not existing[key]:
            existing[key] = value

    return existing

def update_publications(hits, dry_run=False, category_name="ExTrEMe Collaboration Papers"):
    """Update publications.yml with INSPIREHEP results."""
    yaml_data = load_yaml()

    added = []
    updated = []

    for record in hits:
        entry = parse_inspire_record(record)
        arxiv_id = entry.get("arxiv")
        if not arxiv_id:
            continue

        category, existing = find_entry_by_arxiv(yaml_data, arxiv_id)

        if existing:
            old_entry = dict(existing)
            merge_entries(existing, entry)
            if existing != old_entry:
                updated.append((arxiv_id, old_entry, existing))
        else:
            # Append collaboration tag if adding to ExTrEMe collaboration papers
            if "ExTrEMe" in category_name and "(The ExTrEMe Collaboration)" not in entry.get("authors", ""):
                entry["authors"] = entry.get("authors", "") + " (The ExTrEMe Collaboration)"

            target_cat = None
            for cat in yaml_data:
                if cat.get("category") == category_name:
                    target_cat = cat
                    break
            if not target_cat and yaml_data:
                target_cat = yaml_data[0]

            if target_cat:
                target_cat.setdefault("items", []).append(entry)
                added.append((arxiv_id, entry))

    if added:
        print(f"\n📝 New entries added ({len(added)}):", file=sys.stderr)
        for arxiv_id, entry in added:
            print(f"  + [{arxiv_id}] {entry.get('title', 'No title')}", file=sys.stderr)

    if updated:
        print(f"\n✏️  Entries updated ({len(updated)}):", file=sys.stderr)
        for arxiv_id, old, new in updated:
            changes = [f"{k}: '{old.get(k)}' -> '{new.get(k)}'" for k in new if k not in old or old[k] != new[k]]
            print(f"  * [{arxiv_id}] {', '.join(changes)}", file=sys.stderr)

    if not added and not updated:
        print("\n✓ No new changes needed (all entries in sync)", file=sys.stderr)
        return

    if not dry_run:
        save_yaml(yaml_data)
        print(f"\n✓ Saved updates to {YAML_PATH}", file=sys.stderr)
    else:
        print(f"\n(dry-run: no changes written to disk)", file=sys.stderr)

def sync_all_entries(dry_run=False):
    """Iterate through all entries in publications.yml and refresh metadata from INSPIREHEP."""
    yaml_data = load_yaml()
    updated = []
    total_checked = 0

    print("Checking INSPIREHEP for updates on all existing entries...", file=sys.stderr)

    for cat in yaml_data:
        for item in cat.get("items", []):
            arxiv_id = item.get("arxiv")
            if not arxiv_id:
                continue

            total_checked += 1
            hits = fetch_inspire(f"arxiv:{arxiv_id}", size=1)
            if not hits:
                continue

            record = hits[0]
            new_info = parse_inspire_record(record)
            old_item = dict(item)

            merge_entries(item, new_info)

            if item != old_item:
                updated.append((arxiv_id, old_item, item))
                print(f"  * Updated [{arxiv_id}]: {item.get('title', '')[:50]}...", file=sys.stderr)

    print(f"\nChecked {total_checked} entries. {len(updated)} entries updated.", file=sys.stderr)

    if updated and not dry_run:
        save_yaml(yaml_data)
        print(f"✓ Saved updates to {YAML_PATH}", file=sys.stderr)
    elif dry_run and updated:
        print(f"(dry-run: no changes written)", file=sys.stderr)

def update_missing_dois(dry_run=False):
    """Find all entries with arXiv but missing DOI, and fetch DOI from INSPIREHEP."""
    yaml_data = load_yaml()
    missing_dois = []
    updated = []

    for category in yaml_data:
        for item in category.get("items", []):
            arxiv_id = item.get("arxiv")
            has_doi = item.get("doi")
            if arxiv_id and not has_doi:
                missing_dois.append((str(arxiv_id), item))

    if not missing_dois:
        print(f"\n✓ All entries already have DOIs!", file=sys.stderr)
        return

    print(f"\n🔍 Found {len(missing_dois)} entries with arXiv but missing DOI", file=sys.stderr)

    for arxiv_id, item in missing_dois:
        hits = fetch_inspire(f"arxiv:{arxiv_id}", size=1)
        if hits:
            record = hits[0]
            m = record.get("metadata", {})
            dois = m.get("dois", [])
            if dois:
                doi = dois[0].get("value")
                old_item = dict(item)
                item["doi"] = doi
                updated.append((arxiv_id, old_item, item))
                print(f"  ✓ [{arxiv_id}] Found DOI: {doi}", file=sys.stderr)
            else:
                print(f"  - [{arxiv_id}] No DOI registered yet in INSPIREHEP", file=sys.stderr)
        else:
            print(f"  ✗ [{arxiv_id}] Not found on INSPIREHEP", file=sys.stderr)

    if updated and not dry_run:
        save_yaml(yaml_data)
        print(f"\n✓ Saved {len(updated)} DOIs to {YAML_PATH}", file=sys.stderr)
    elif dry_run and updated:
        print(f"\n(dry-run: {len(updated)} DOIs found, not saved)", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(
        description="Update publications.yml from INSPIREHEP API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Search collaboration:"extreme" and sync
  %(prog)s --sync-all                # Refresh all existing entries from INSPIREHEP
  %(prog)s --arxiv 2409.17127        # Fetch and add/update specific arXiv ID
  %(prog)s --update-missing-dois     # Find and fill missing DOIs
  %(prog)s --dry-run                 # Preview changes without writing
        """
    )
    parser.add_argument("--arxiv", help="Search and add/update by arXiv ID (e.g. 2409.17127)")
    parser.add_argument("--category", default="ExTrEMe Collaboration Papers", help="Category name for new entries")
    parser.add_argument("--sync-all", action="store_true", help="Refresh all existing entries from INSPIREHEP")
    parser.add_argument("--update-missing-dois", action="store_true", help="Update all entries with missing DOI")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")

    args = parser.parse_args()

    if args.sync_all:
        sync_all_entries(dry_run=args.dry_run)
    elif args.update_missing_dois:
        update_missing_dois(dry_run=args.dry_run)
    elif args.arxiv:
        print(f"Searching INSPIREHEP for arXiv:{args.arxiv}...", file=sys.stderr)
        hits = fetch_inspire(f"arxiv:{args.arxiv}", size=1)
        if hits:
            update_publications(hits, dry_run=args.dry_run, category_name=args.category)
        else:
            print("✗ No results found for arXiv ID", file=sys.stderr)
            sys.exit(1)
    else:
        print("Searching INSPIREHEP for collaboration:extreme papers...", file=sys.stderr)
        hits = fetch_inspire('collaboration:"extreme"')
        if hits:
            update_publications(hits, dry_run=args.dry_run, category_name=args.category)
        else:
            print("✗ No results found or API error", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()
