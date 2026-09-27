#!/usr/bin/env python3
"""Look up arXiv IDs by title using the arXiv API."""
import re, sys, urllib.request, urllib.parse
UA = {"User-Agent": "omarchy-english-toolkit/1.0"}
API = "https://export.arxiv.org/api/query?search_query=ti:%22{}%22&max_results=3"

def search(title):
    url = API.format(urllib.parse.quote(title))
    try:
        req = urllib.request.Request(url, headers=UA)
        x = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")
    except Exception as e:
        return f"ERR {type(e).__name__}"
    out = []
    for entry in re.findall(r"<entry>(.*?)</entry>", x, re.S):
        aid = re.search(r"<id>http[s]?://arxiv\.org/abs/([^<]+)</id>", entry)
        ti = re.search(r"<title>(.*?)</title>", entry, re.S)
        if aid and ti:
            t = " ".join(ti.group(1).split())
            out.append((aid.group(1), t))
    return out or "not found"

for t in sys.argv[1:]:
    r = search(t)
    if isinstance(r, str):
        print(f"  {t[:48]:50} {r}")
    else:
        for i, (aid, tt) in enumerate(r[:2]):
            mark = ">>" if i == 0 else "  "
            print(f"{mark} {aid:12} {tt[:56]:58} <- '{t[:30]}'")
