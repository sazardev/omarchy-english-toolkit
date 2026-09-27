#!/usr/bin/env python3
"""Build the English irregular verb list from Wiktionary.

Two Wiktionary sources, because neither alone is enough:

  * Category:English_irregular_verbs and its four subcategories give the
    authoritative list of WHICH verbs are irregular. It is curated, so it
    does not include typos or coinages from random quizzes.
  * Appendix:English irregular verbs gives the forms, and also the
    prefixed variants: forbear/forbore/forborne, foresee/foreseen and so
    on. Those are real English verbs and belong in a reference.

The appendix is wikitext, so it is parsed with a small state machine
rather than a regex: the italic markup spans the whole cell, and comments
inside the cell contain apostrophes that break naive matching.

usage: irregular-verbs.py --out irreg.json [--wikitext file] [--categories]
"""
import argparse
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

UA = {"User-Agent": "omarchy-english-toolkit/1.0 (irregular verb table)"}
API = "https://en.wiktionary.org/w/api.php"

B = "\033[1m"; G = "\033[1;32m"; Y = "\033[1;33m"; R = "\033[1;31m"; D = "\033[2m"; O = "\033[0m"

CATEGORIES = [
    "Category:English_irregular_verbs",
    "Category:English_defective_verbs",
    "Category:English_strong_verbs",
    "Category:English_suppletive_verbs",
    "Category:English_verbs_with_weak_preterite_but_strong_past_participle",
]

# A table cell is italic-wrapped: apostrophes, the linked base, the two
# forms, apostrophes, then a line break. Requiring four apostrophes at the
# opening does not match anything; the opening marker is a pair.
RE_CELL = re.compile(
    r"'{2,}\[\[([a-z][a-z \-']*?)\]\](?P<rest>.*?)'{2,}\s*(?:\n|\||$)", re.S)
RE_DERIVED = re.compile(r"^:\s*'{2,}\[\[([a-z][a-z \-']*?)\]\](.*?)'{2,}\s*$", re.S | re.M)


def api(**params) -> str:
    params.setdefault("format", "json")
    url = f"{API}?{urllib.parse.urlencode(params)}"
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read().decode("utf-8", "replace")
        except Exception:  # noqa: BLE001
            time.sleep(3 * (attempt + 1))
    return "{}"


def clean_forms(s: str):
    """Strip the wikitext noise out of a forms cell."""
    s = re.sub(r"<!--.*?-->", " ", s, flags=re.S)
    s = re.sub(r"<ref[^>]*>.*?</ref>", " ", s, flags=re.S)
    s = re.sub(r"<sup>.*?</sup>", "", s, flags=re.S)
    s = re.sub(r"\{\{[^{}]*\}\}", " ", s)
    s = s.replace("''", "").replace("[[", "").replace("]]", "")
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def split_forms(text: str):
    """Return (past, participle).

    Cells look like "bore/*bare born/borne" or "bent/bended bent/bended":
    the first group is the preterite, the second the participle, and a
    slash inside a group means an accepted variant.
    """
    text = text.strip().rstrip("|").strip()
    parts = [p.strip() for p in text.split() if p.strip()]
    if not parts:
        return "", ""
    past = parts[0]
    part = parts[1] if len(parts) > 1 else parts[0]
    # a slash before a space separates the two groups, not a variant
    if "/" in past and " " in past:
        head, _, tail = past.partition(" ")
        past, part = head, (tail + " " + part).strip()
    return past.strip("/"), part.strip("/")


def normalise_form(f: str) -> str:
    """Keep the first listed variant: "born(e)" -> "born", "bore/*bare" -> "bore"."""
    f = f.split("/")[0]
    f = f.replace("(", "").replace(")", "")
    f = re.sub(r"[^a-z\- ]", "", f.lower())
    return f.strip()


def parse_appendix(wikitext: str):
    """Yield (base, past, participle) from the appendix table."""
    text = wikitext
    # drop code examples at the top and the notes at the bottom
    out = []
    # each table row starts at a line beginning with |-
    rows = re.split(r"(?m)^\|-", text)
    for row in rows:
        m = RE_CELL.search(row)
        if not m:
            continue
        base = m.group(1).strip()
        if not base or " " in base:
            continue
        past, part = split_forms(clean_forms(m.group("rest")))
        if not past:
            continue
        out.append((base, normalise_form(past), normalise_form(part)))
        # prefixed forms live on ":" continuation lines
        for dm in RE_DERIVED.finditer(row):
            dbase = dm.group(1).strip()
            dpast, dpart = split_forms(clean_forms(dm.group(2)))
            if dbase and " " not in dbase and dpast:
                out.append((dbase, normalise_form(dpast), normalise_form(dpart)))
    return out


def category_members() -> list:
    found = set()
    for cat in CATEGORIES:
        cont = None
        while True:
            params = {"action": "query", "list": "categorymembers",
                      "cmtitle": cat, "cmlimit": "500", "cmtype": "page"}
            if cont:
                params["cmcontinue"] = cont
            d = json.loads(api(**params))
            for m in d.get("query", {}).get("categorymembers", []):
                t = m["title"].strip()
                if t and ":" not in t and " " not in t and "/" not in t:
                    found.add(t.lower())
            cont = d.get("continue", {}).get("cmcontinue")
            if not cont:
                break
            time.sleep(0.4)
    return sorted(found)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="irregular.json")
    ap.add_argument("--wikitext", help="use a saved Appendix wikitext dump")
    ap.add_argument("--categories", action="store_true",
                    help="also fetch the curated category list")
    a = ap.parse_args()

    if a.wikitext:
        w = Path(a.wikitext).read_text(encoding="utf-8")
    else:
        print(f"{B}Fetching the Wiktionary appendix{O}")
        d = json.loads(api(action="parse", page="Appendix:English irregular verbs",
                           prop="wikitext"))
        w = d.get("parse", {}).get("wikitext", {}).get("*", "")
        if not w:
            print(f"  {R}could not read the appendix{O}", file=sys.stderr)
            return 1
        Path(a.wikitext or "appendix.wikitext").write_text(w, encoding="utf-8")
        print(f"  {G}appendix{O} {len(w):,} bytes")

    rows = parse_appendix(w)
    print(f"  {G}parsed{O} {len(rows)} verb forms from the appendix")

    # de-duplicate, keep the first occurrence
    verbs = {}
    for base, past, part in rows:
        base = base.lower()
        if base not in verbs:
            verbs[base] = {"base": base, "past": past, "participle": part}

    if a.categories:
        print(f"{B}Fetching the curated category lists{O}")
        members = category_members()
        print(f"  {G}category{O} {len(members)} verbs flagged irregular")
        missing = [m for m in members if m not in verbs]
        print(f"  {Y}{len(missing)} in the category but not in the appendix{O}")
        for m in missing[:15]:
            print(f"     {m}")
        verbs_meta = {"_category_only": sorted(missing)}

    payload = {"source": "Wiktionary: Appendix:English irregular verbs + Category:English_irregular_verbs",
               "verbs": sorted(verbs.values(), key=lambda x: x["base"])}
    if a.categories:
        payload["category_only"] = verbs_meta["_category_only"]

    Path(a.out).write_text(json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"\n  {D}wrote {len(verbs)} verbs to {a.out}{O}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
