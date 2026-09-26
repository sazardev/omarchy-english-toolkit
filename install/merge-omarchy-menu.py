#!/usr/bin/env python3
"""Merge the English section into an Omarchy menu extension.

Never replaces the file. Any sections the user already has are preserved,
and comments are stripped because jsonc is not valid json.

usage: merge-omarchy-menu.py <menu.jsonc> <english-section.jsonc>
"""
import json
import re
import sys


def load_jsonc(path):
    raw = open(path, encoding="utf-8").read()
    clean = re.sub(r"/\*.*?\*/", "", raw, flags=re.S)
    clean = re.sub(r"(?m)^\s*//.*$", "", clean)
    return json.loads(clean)


def main():
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2

    target, fragment = sys.argv[1], sys.argv[2]

    data = load_jsonc(target) if _exists(target) else {}
    add = load_jsonc(fragment)

    before = len(data)
    data.update(add)
    after = len(data)

    with open(target, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    print("    merged %d entries (%d -> %d)" % (len(add), before, after))
    return 0


def _exists(path):
    import os
    return os.path.isfile(path)


if __name__ == "__main__":
    sys.exit(main())
