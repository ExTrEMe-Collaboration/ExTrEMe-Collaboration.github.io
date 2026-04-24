#!/usr/bin/env python3
"""
Update publications.yml from INSPIREHEP API.

Usage:
  python update_publications_from_inspirehep.py                    # Search by collaboration:"extreme"
  python update_publications_from_inspirehep.py --arxiv 2311.02210  # Search by arXiv ID
  python update_publications_from_inspirehep.py --dry-run           # Preview changes without writing
"""

import requests
import yaml
import argparse
import sys
from pathlib import Path

YAML_PATH = Path(__file__).parent.parent / "_data" / "publications.yml"
INSPIRE_API = "https://inspirehep.net/api/literature"

def fetch_inspire(query):
    """Fetch results from INSPIREHEP API."""
    params = {"q": query, "size": 100}  # Fetch up to 100 results
    try:
        r = requests.get(INSPIRE_API, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        hits = data.get("hits", {}).get("hits", [])
        print(f"✓ Found {len(hits)} results from INSPIREHEP", file=sys.stderr)
        return hits
    except requests.RequestException as e:
        print(f"✗ Error querying INSPIREHEP: {e}", file=sys.stderr)
        return []

def parse_inspire_record(record):
    """Extract publication info from INSPIREHEP record."""
    metadata = record.get("metadata", {})
    
    # Title
    title = None
    if "titles" in metadata and metadata["titles"]:
        title = metadata["titles"][0].get("title")
    
    # Authors
    authors = ""
    if "authors" in metadata and metadata["authors"]:
        author_names = [a.get("full_name") for a in metadata["authors"]]
        author_names = [a for a in author_names if a]  # Filter None
        if author_names:
            authors = ", ".join(author_names)
            # Add "et al." if many authors
            if len(author_names) > 3:
                authors = author_names[0] + " et al."
    
    # Year
    year = None
    if "publication_info" in metadata and metadata["publication_info"]:
        year = metadata["publication_info"][0].get("year")
    if not year and "preprint_date" in metadata:
        year = metadata["preprint_date"][:4]
    
    # DOI
    doi = None
    if "dois" in metadata and metadata["dois"]:
        doi = metadata["dois"][0].get("value")
    
    # arXiv
    arxiv = None
    if "arxiv_eprints" in metadata and metadata["arxiv_eprints"]:
        arxiv = metadata["arxiv_eprints"][0].get("value")
    
    # Venue (journal title or conference)
    venue = ""
    if "publication_info" in metadata and metadata["publication_info"]:
        pub_info = metadata["publication_info"][0]
        if "journal_title" in pub_info:
            venue = pub_info["journal_title"]
            if "volume" in pub_info:
                venue += f" {pub_info['volume']}"
            if "artid" in pub_info:
                venue += f", {pub_info['artid']}"
        elif "conference_record" in pub_info:
            venue = pub_info.get("conference_record", {}).get("name", "")
    
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
        entry["arxiv"] = arxiv
    
    return entry

def load_yaml():
    """Load existing publications.yml."""
    with open(YAML_PATH, "r") as f:
        data = yaml.safe_load(f) or []
    return data

def save_yaml(data):
    """Save updated publications.yml."""
    with open(YAML_PATH, "w") as f:
        yaml.dump(data, f, sort_keys=False, allow_unicode=True, default_flow_style=False)

def find_entry_by_arxiv(yaml_data, arxiv_id):
    """Find an existing entry by arXiv ID in the YAML structure."""
    for category in yaml_data:
        for item in category.get("items", []):
            # Handle both string and numeric arXiv IDs (YAML may parse as float)
            item_arxiv = str(item.get("arxiv", ""))
            if item_arxiv == str(arxiv_id):
                return category, item
    return None, None

def merge_entries(existing, new):
    """Merge new fields into existing entry, keeping existing values if present."""
    for key, value in new.items():
        if key not in existing or not existing[key]:
            existing[key] = value
    return existing

def update_publications(hits, dry_run=False):
    """Update publications.yml with INSPIREHEP results."""
    yaml_data = load_yaml()
    
    added = []
    updated = []
    
    for record in hits:
        entry = parse_inspire_record(record)
        if not entry.get("arxiv"):
            # Skip if no arXiv ID (we use it as unique identifier)
            continue
        
        arxiv_id = entry["arxiv"]
        category, existing = find_entry_by_arxiv(yaml_data, arxiv_id)
        
        if existing:
            # Merge new fields into existing entry
            old_entry = dict(existing)
            existing = merge_entries(existing, entry)
            
            # Check if anything changed
            if existing != old_entry:
                updated.append((arxiv_id, old_entry, existing))
        else:
            # Add as new entry to first category (ExTrEMe Collaboration Papers)
            if yaml_data:
                yaml_data[0]["items"].append(entry)
                added.append((arxiv_id, entry))
    
    # Report changes
    if added:
        print(f"\n📝 New entries to add ({len(added)}):", file=sys.stderr)
        for arxiv_id, entry in added:
            print(f"  - {arxiv_id}: {entry.get('title', 'No title')}", file=sys.stderr)
    
    if updated:
        print(f"\n✏️  Entries to update ({len(updated)}):", file=sys.stderr)
        for arxiv_id, old, new in updated:
            changes = [k for k in new if k not in old or old[k] != new[k]]
            print(f"  - {arxiv_id}: {', '.join(changes)}", file=sys.stderr)
    
    if not added and not updated:
        print("\n✓ All entries already in sync!", file=sys.stderr)
        return
    
    # Write back
    if not dry_run:
        save_yaml(yaml_data)
        print(f"\n✓ Updated {YAML_PATH}", file=sys.stderr)
    else:
        print(f"\n(dry-run: no changes written)", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(
        description="Update publications.yml from INSPIREHEP API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Search collaboration:"extreme"
  %(prog)s --arxiv 2311.02210        # Search by arXiv ID
  %(prog)s --dry-run                 # Preview without writing
        """
    )
    parser.add_argument("--arxiv", help="Search by arXiv ID (e.g., 2311.02210)")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    
    args = parser.parse_args()
    
    if args.arxiv:
        query = f"arxiv:{args.arxiv}"
        print(f"Searching INSPIREHEP for arXiv:{args.arxiv}...", file=sys.stderr)
    else:
        query = 'collaboration:"extreme"'
        print(f"Searching INSPIREHEP for all ExTrEMe collaboration papers...", file=sys.stderr)
    
    hits = fetch_inspire(query)
    if hits:
        update_publications(hits, dry_run=args.dry_run)
    else:
        print("✗ No results found or API error", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
