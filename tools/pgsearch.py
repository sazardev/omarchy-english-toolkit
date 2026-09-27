#!/usr/bin/env python3
"""Search the Project Gutenberg catalog, locally.

Looking IDs up by guessing does not work: 164 is Twenty Thousand Leagues
under the Sea, not Aesop, and 2701 is Moby Dick, not Dracula. Download the
catalog once, then search it offline.

    curl -L -o pg_catalog.csv.gz \
      https://www.gutenberg.org/cache/epub/feeds/pg_catalog.csv.gz
    gunzip pg_catalog.csv.gz

    python3 pgsearch.py author "doyle"      # by author
    python3 pgsearch.py title  "raven" 10   # by title, 10 results
    python3 pgsearch.py lang   "en" 5
"""
import csv, re, sys

def rows():
    with open("pg_catalog.csv", newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            r["Type"] = r.get("Type", "")
            yield r

def num(r):
    try: return int(r["Text#"])
    except Exception: return None

def main():
    mode = sys.argv[1]           # title | author | lang
    needle = sys.argv[2].lower()
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    field = {"title": "Title", "author": "Authors", "lang": "Language"}[mode]
    hits = []
    for r in rows():
        if needle not in (r.get(field) or "").lower():
            continue
        if r["Language"] not in ("en", "en-US", "en-GB", ""):
            continue
        n = num(r)
        if n is None:
            continue
        hits.append((n, r["Title"], (r.get("Authors") or "")[:30], r["Type"]))
    hits.sort()
    for n, t, a, ty in hits[:limit]:
        print(f"{n:>6}  {t[:52]:54} {a:32} {ty}")

if __name__ == "__main__":
    main()
