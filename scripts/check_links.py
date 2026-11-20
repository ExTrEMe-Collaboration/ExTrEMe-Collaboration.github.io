#!/usr/bin/env python3
"""
Check internal links in the built site (no network access needed).

    python3 scripts/check_links.py _site [--baseurl /repo-name]

Every href/src that points inside the site must resolve to a generated file,
and every #fragment must match an id on the target page. External links are
not fetched. Standard library only.
"""

import argparse
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

SITE_HOSTS = {"www.extreme-collaboration.science", "extreme-collaboration.science"}


class Collector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag == "a" and attrs.get("name"):
            self.ids.add(attrs["name"])
        for key in ("href", "src"):
            if attrs.get(key) and not (tag == "link" and attrs.get("rel") in ("preconnect", "alternate")):
                self.links.append(attrs[key])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("site", type=Path)
    ap.add_argument("--baseurl", default="")
    args = ap.parse_args()
    site = args.site.resolve()
    base = args.baseurl.rstrip("/")

    pages = {}
    for path in site.rglob("*.html"):
        c = Collector()
        c.feed(path.read_text(encoding="utf-8", errors="replace"))
        pages[path] = c

    def resolve(target):
        if target.is_dir():
            target = target / "index.html"
        elif not target.exists() and target.with_suffix(".html").exists():
            target = target.with_suffix(".html")
        return target if target.exists() else None

    errors = []
    checked = 0
    for page, info in pages.items():
        rel = page.relative_to(site)
        for link in info.links:
            parts = urlsplit(link)
            if parts.scheme in ("mailto", "tel", "javascript", "data"):
                continue
            if parts.scheme in ("http", "https"):
                if parts.hostname not in SITE_HOSTS:
                    continue  # external link: not checked here
            elif parts.netloc:
                continue  # protocol-relative external
            path = unquote(parts.path)
            if parts.scheme or path.startswith("/"):
                if base and path.startswith(base):
                    path = path[len(base):] or "/"
                elif base and not parts.scheme:
                    errors.append(f"{rel}: '{link}' is missing the baseurl '{base}'")
                    continue
                target = site / path.lstrip("/")
            elif path:
                target = page.parent / path
            else:
                target = page  # same-page fragment
            checked += 1
            resolved = resolve(target)
            if resolved is None:
                errors.append(f"{rel}: broken link '{link}'")
                continue
            if parts.fragment and resolved.suffix == ".html":
                ids = pages.get(resolved.resolve(), Collector()).ids
                if unquote(parts.fragment) not in ids:
                    errors.append(f"{rel}: '{link}' points to a missing anchor")

    if errors:
        print(f"✗ {len(errors)} broken internal link(s):")
        for e in sorted(set(errors)):
            print("  -", e)
        sys.exit(1)
    print(f"✓ {checked} internal links OK across {len(pages)} pages")


if __name__ == "__main__":
    main()
