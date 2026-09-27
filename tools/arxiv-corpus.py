#!/usr/bin/env python3
"""Fetch Computer Science papers from arXiv as clean plain text for Lute.

Papers are read on arXiv, which is free to read, but the page is HTML full
of MathML and layout markup. ar5iv renders the LaTeX source to clean
semantic HTML, which strips down to readable prose.

Math is reduced to a [formula] marker: it is not learnable as prose and
Lute would otherwise index thousands of fragments of LaTeX as words.

usage: arxiv-corpus.py <list.tsv> <out-dir> [--only ID,ID]
"""
import re
import sys
import time
import urllib.request
from pathlib import Path

AR5IV = "https://ar5iv.labs.arxiv.org/html/{id}"
UA = {"User-Agent": "omarchy-english-toolkit/1.0 (local corpus builder)"}

B = "\033[1m"; G = "\033[1;32m"; Y = "\033[1;33m"; R = "\033[1;31m"; D = "\033[2m"; O = "\033[0m"

RE_DROP_BLOCKS = re.compile(
    r"<(script|style|noscript|svg|math)\b[^>]*>.*?</\1>", re.S | re.I)
RE_MATH_SELF = re.compile(r"<math\b[^>]*/>", re.I)
RE_TAG = re.compile(r"<[^>]+>")
RE_NBSP = re.compile(r"&nbsp;?", re.I)
RE_ENTITIES = {"&amp;": "&", "&lt;": "<", "&gt;": ">", "&quot;": '"',
               "&apos;": "'", "&ndash;": "-", "&mdash;": " - ", "&hellip;": "...",
               "&times;": "x", "&minus;": "-", "&deg;": " degrees "}


def fetch(url: str, tries: int = 3) -> str:
    last = ""
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read().decode("utf-8", errors="replace")
        except Exception as e:  # noqa: BLE001
            last = type(e).__name__
            time.sleep(3 * (i + 1))
    raise RuntimeError(last)


def page_title(html: str) -> str:
    """The paper's real title, from the rendered page.

    arXiv IDs get reused in the wrong list the same way Gutenberg ones do:
    1502.01852 is not Batch Normalization. Checking the title, not the word
    count, is what catches it.
    """
    # prefer the rendered heading: ar5iv often puts "[id] Untitled Document"
    # in <title> when the LaTeX title macro was not used
    m = re.search(r'<h1[^>]*class="ltx_title[^"]*"[^>]*>(.*?)</h1>', html, re.S | re.I)
    if not m:
        m = re.search(r"<h1[^>]*ltx_title[^>]*>(.*?)</h1>", html, re.S | re.I)
    if m:
        t = RE_TAG.sub(" ", m.group(1))
        t = RE_NBSP.sub(" ", t)
        t = re.sub(r"\[\[a-z ]+\]\]", " ", t)
        return re.sub(r"\s+", " ", t).strip(" -|:")
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
    if m:
        t = RE_TAG.sub("", m.group(1))
        t = RE_NBSP.sub(" ", t)
        t = re.split(r"\s*-\s*arXiv:", t)[0]
        t = re.sub(r"^\[[\d.]+\]\s*", "", t)
        if t.strip().lower() not in ("untitled document", "untitled"):
            return t.strip(" -|:")
    return ""


def agree(actual: str, expected: str) -> bool:
    import unicodedata
    def norm(s):
        s = unicodedata.normalize("NFKD", s).lower()
        s = re.sub(r"[^a-z0-9 ]+", " ", s)
        return set(re.sub(r"\s+", " ", s).split()) - {
            "the", "a", "an", "of", "and", "or", "to", "in", "on", "for", "with"}
    a, e = norm(actual), norm(expected)
    if not a or not e:
        return False
    return len(a & e) >= max(1, min(len(a), len(e)) * 0.4)


def to_text(html: str) -> str:
    h = RE_DROP_BLOCKS.sub(" ", html)
    h = RE_MATH_SELF.sub(" [formula] ", h)
    # the article body, if the renderer wrapped it
    m = re.search(r"<article\b.*?</article>", h, re.S | re.I)
    if m:
        h = m.group(0)
    h = RE_TAG.sub("\n", h)
    for k, v in RE_ENTITIES.items():
        h = h.replace(k, v)
    h = RE_NBSP.sub(" ", h)
    h = re.sub(r"[ \t]+", " ", h)
    h = re.sub(r"\n\s*\n\s*\n+", "\n\n", h)
    lines = [ln.strip() for ln in h.split("\n")]
    # ar5iv emits one fragment per line; rejoin fragments into sentences
    out, buf = [], ""
    for ln in lines:
        if not ln:
            if buf:
                out.append(buf)
                buf = ""
            out.append("")
            continue
        if buf:
            # a line starting a new sentence means the previous one ended
            if re.match(r"^[A-Z(\[]", ln) and re.search(r"[.!?:;]$", buf):
                out.append(buf)
                buf = ln
            else:
                buf += " " + ln
        else:
            buf = ln
    if buf:
        out.append(buf)
    text = "\n".join(out)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    # collapse runs of the formula marker
    text = re.sub(r"(?:\s*\[formula\]\s*){2,}", " [formula] ", text)
    return text


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__, file=sys.stderr)
        return 2
    listfile, outdir = Path(sys.argv[1]), Path(sys.argv[2])
    only = None
    if "--only" in sys.argv:
        only = set(sys.argv[sys.argv.index("--only") + 1].split(","))

    outdir.mkdir(parents=True, exist_ok=True)
    rows = []
    for line in listfile.read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        parts = [x.strip() for x in line.split("\t")]
        if len(parts) >= 4:
            rows.append(parts[:4])

    if only:
        rows = [r for r in rows if r[0] in only]

    print(f"{B}Fetching {len(rows)} papers from arXiv via ar5iv{O}\n")
    ok = bad = 0
    for aid, level, kind, title in rows:
        if (outdir / f"{aid}.txt").exists():
            print(f"  {D}cached{O} {aid}")
            ok += 1
            continue
        try:
            html = fetch(AR5IV.format(id=aid))
        except Exception as e:  # noqa: BLE001
            print(f"  {R}FAIL{O}     {aid}  {title[:44]}  ({e})")
            bad += 1
            continue
        actual = page_title(html)
        if actual and not agree(actual, title):
            print(f"  {R}MISMATCH{O} {aid}  wanted '{title}' but the paper is '{actual}'")
            bad += 1
            continue
        if not actual:
            # ar5iv sometimes renders no title at all. That is an extraction
            # failure, not proof of a wrong paper, so keep it but say so.
            print(f"  {Y}no title{O}   {aid}  keeping '{title}' unverified, check it yourself")
        text = to_text(html)
        words = len(text.split())
        if words < 1200:
            print(f"  {Y}THIN{O}     {aid}  {title[:44]}  ({words} words)")
            bad += 1
            continue
        safe = re.sub(r"[^A-Za-z0-9]+", "-", title).strip("-")[:70]
        (outdir / f"{level} {kind} - {safe} - {aid}.txt").write_text(text, encoding="utf-8")
        print(f"  {G}OK{O}       {aid}  [{level} {kind:9}] {title[:40]:42} {words:>6,} words")
        ok += 1
        time.sleep(1.5)  # be polite to ar5iv

    print(f"\n  {ok} papers in {outdir}, {bad} failed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
