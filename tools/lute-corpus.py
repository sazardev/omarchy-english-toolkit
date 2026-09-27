#!/usr/bin/env python3
"""Build a graded English corpus from Project Gutenberg for Lute.

Public domain, no accounts, no DRM, plain text. Every download is
verified against the Title: header in the file, because a Gutenberg ID
is a number and numbers get misremembered: 164 is Twenty Thousand Leagues
under the Sea, not Aesop, and 2701 is Moby Dick, not Dracula.

usage: lute-corpus.py fetch   <list.tsv> <raw-dir>
       lute-corpus.py clean   <list.tsv> <raw-dir> <out-dir>
       lute-corpus.py all     <list.tsv> <work-dir>
"""
import re
import sys
import time
import unicodedata
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

PG = "https://www.gutenberg.org/cache/epub/{i}/pg{i}.txt"
UA = {"User-Agent": "omarchy-english-toolkit/1.0 (local corpus builder)"}

B = "\033[1m"; D = "\033[2m"; G = "\033[1;32m"; Y = "\033[1;33m"; R = "\033[1;31m"; O = "\033[0m"


def read_list(path: Path):
    rows = []
    for line in path.read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        # id, level, kind, title, author - this order must match list.tsv
        parts = [x.strip() for x in line.split("\t")]
        if len(parts) >= 4:
            gid, level, kind, title = parts[0], parts[1], parts[2], parts[3]
            author = parts[4] if len(parts) > 4 else ""
            rows.append((gid, level, kind, title, author))
    return rows


def gutenberg_title(raw: str) -> str:
    m = re.search(r"^Title:\s*(.+)$", raw, re.M | re.I)
    return m.group(1).strip() if m else ""


def normalise(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = s.replace("’", "'").replace("‘", "'")
    s = re.sub(r"[^a-z0-9 ]+", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


def titles_agree(actual: str, expected: str) -> bool:
    """Loose match: enough significant words in common."""
    a = set(normalise(actual).split())
    e = set(normalise(expected).split())
    # drop very common words that carry no identity
    a -= {"the", "a", "an", "of", "and", "or", "to", "in", "on", "for", "with"}
    e -= {"the", "a", "an", "of", "and", "or", "to", "in", "on", "for", "with"}
    if not a or not e:
        return False
    hits = len(a & e)
    return hits >= max(1, min(len(a), len(e)) * 0.4)


def fetch(gid: str, level: str, kind: str, title: str, author: str, rawdir: Path):
    dst = rawdir / f"{gid}.txt"
    if dst.exists() and dst.stat().st_size > 10000:
        return dict(id=gid, level=level, title=title, author=author, kind=kind,
                    status="cached", actual=gutenberg_title(dst.read_text(errors="replace")))
    try:
        req = urllib.request.Request(PG.format(i=gid), headers=UA)
        with urllib.request.urlopen(req, timeout=90) as r:
            data = r.read().decode("utf-8", errors="replace")
        dst.write_text(data, encoding="utf-8")
        return gid, level, title, "ok", gutenberg_title(data)
    except Exception as e:
        return gid, level, title, f"fail: {type(e).__name__}", ""


# ------------------------------------------------------------------ cleaning
RE_START = re.compile(r"\*\*\*\s*START OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*", re.I | re.S)
RE_END = re.compile(r"\*\*\*\s*END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*", re.I | re.S)
RE_START_OLD = re.compile(r"\*\*\*\s*START OF TH(E|IS) PROJECT GUTENBERG.*?\*\*\*", re.I | re.S)
RE_END_OLD = re.compile(r"\*\*\*\s*END OF TH(E|IS) PROJECT GUTENBERG.*?\*\*\*", re.I | re.S)
RE_ILLUST = re.compile(r"\[Illustration[^\]]*\]", re.I)
RE_ASCII_ART = re.compile(r"^[ \t]*[|/\\\-_*#=~^]{6,}[ \t]*$", re.M)
RE_MULTI_NL = re.compile(r"\n{3,}")
RE_SB_PUNCT = re.compile(r"[ \t]+([,.;:!?])")
RE_SA_OPEN = re.compile(r"([(\[])[ \t]+")
RE_TRAIL = re.compile(r"[ \t]+$", re.M)

TOC_WORDS = r"^(contents|table of contents|index|chapter|part|book|act|scene|appendix|volume|epilogue|prologue|preface|introduction)\b"


def is_toc_entry(s: str) -> bool:
    if len(s) < 2 or len(s) > 90:
        return False
    if s.endswith((".", "!", "?", ",", ";", ":")):
        return False
    if re.search(r"[.·_]{3,}\s*\d*\s*$", s):
        return True
    if re.match(TOC_WORDS, s, re.I):
        return True
    letters = [c for c in s if c.isalpha()]
    if letters and sum(c.isupper() for c in letters) / len(letters) > 0.7:
        return True
    return False


def drop_toc(text: str) -> str:
    """Remove a leading contents block, conservatively.

    Only starts scanning if a contents-looking line appears within the
    first 40 lines, and stops at the first prose-looking line, so a
    chapter heading or the opening paragraph can never be eaten.
    """
    lines = text.split("\n")
    limit = min(40, len(lines))

    start = None
    for i in range(limit):
        s = lines[i].strip()
        if re.match(TOC_WORDS, s, re.I) and is_toc_entry(s):
            start = i
            break
    if start is None:
        return text

    i, removed = start + 1, 0
    while i < len(lines) and i < start + 400:
        s = lines[i].strip()
        if not s:
            i += 1
            continue
        if not is_toc_entry(s):
            break
        i += 1
        removed += 1

    if removed < 4:
        return text
    return "\n".join(lines[i:])


def extract_body(raw: str) -> str:
    m = RE_START.search(raw) or RE_START_OLD.search(raw)
    if m:
        raw = raw[m.end():]
    m = RE_END.search(raw) or RE_END_OLD.search(raw)
    if m:
        raw = raw[:m.start()]
    return raw


def clean(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = RE_ASCII_ART.sub("", text)
    text = RE_ILLUST.sub("", text)
    text = drop_toc(text)
    text = unicodedata.normalize("NFC", text)
    for a, b in (("’", "'"), ("‘", "'"), ("“", '"'),
                 ("”", '"'), ("—", " - "), ("–", "-")):
        text = text.replace(a, b)
    text = text.replace("_", "")
    text = RE_SB_PUNCT.sub(r"\1", text)
    text = RE_SA_OPEN.sub(r"\1", text)
    text = RE_TRAIL.sub("", text)
    text = RE_MULTI_NL.sub("\n\n", text)
    return text.strip()


# ---------------------------------------------------------------------- main
def cmd_fetch(listfile, rawdir):
    rawdir.mkdir(parents=True, exist_ok=True)
    rows = read_list(listfile)
    print(f"{B}Fetching {len(rows)} books from Project Gutenberg{O}\n")
    with ThreadPoolExecutor(max_workers=6) as ex:
        results = list(ex.map(lambda r: fetch(*r, rawdir), rows))

    good, bad = [], []
    for r in results:
        gid, title, actual = r["id"], r["title"], r["actual"]
        if r["status"].startswith("fail"):
            print(f"  {R}FAIL{O}     {gid:>6}  {title}  ({r['status']})")
            bad.append((gid, title, actual, r["status"]))
            continue
        if not titles_agree(actual, title):
            print(f"  {R}MISMATCH{O} {gid:>6}  wanted '{title}' but the file is '{actual}'")
            bad.append((gid, title, actual, "title mismatch"))
            continue
        words = len(extract_body(rawdir.joinpath(f"{gid}.txt")
                                 .read_text(errors="replace")).split())
        print(f"  {G}OK{O}       {gid:>6}  [{r['level']} {r['kind']:10}] {title:38} {words:>7,}")
        good.append(r)
    return good, bad


def cmd_clean(listfile, rawdir, outdir):
    outdir.mkdir(parents=True, exist_ok=True)
    print(f"{B}Cleaning into {outdir}{O}\n")
    ok = 0
    for gid, level, title, author, kind in read_list(listfile):
        src = rawdir / f"{gid}.txt"
        if not src.exists():
            print(f"  {R}MISS{O} {gid} {title}")
            continue
        body = clean(extract_body(src.read_text(errors="replace")))
        words = len(body.split())
        if words < 2000:
            print(f"  {Y}THIN{O} {gid} {title} ({words} words)")
            continue
        safe = re.sub(r"[^A-Za-z0-9]+", "-", title).strip("-")
        prefix = f"{level} {kind}".strip()
        (outdir / f"{prefix} - {safe}.txt").write_text(body, encoding="utf-8")
        print(f"  {G}OK{O} [{prefix:14}] {title:38} {words:>7,} words")
        ok += 1
    print(f"\n{ok} books in {outdir}")
    return 0


def cmd_all(listfile, workdir):
    workdir = Path(workdir)
    raw, out = workdir / "raw", workdir / "clean"
    good, bad = cmd_fetch(listfile, raw)
    if bad:
        print(f"\n{R}{len(bad)} book(s) rejected; not cleaning those{O}")
        for gid, want, got, why in bad:
            print(f"  {gid}: wanted '{want}', got '{got}' ({why})")
    # clean only the verified set
    verified = workdir / "verified.tsv"
    verified.write_text("".join(
        f"{r['id']}\t{r['level']}\t{r['actual']}\t{r['author']}\t{r['kind']}\n"
        for r in good))
    cmd_clean(verified, raw, out)
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    cmd = sys.argv[1]
    if cmd == "fetch":
        cmd_fetch(Path(sys.argv[2]), Path(sys.argv[3]))
    elif cmd == "clean":
        cmd_clean(Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]))
    elif cmd == "all":
        cmd_all(Path(sys.argv[2]), sys.argv[3])
    else:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
