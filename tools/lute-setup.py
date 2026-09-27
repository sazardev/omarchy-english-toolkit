#!/usr/bin/env python3
"""Finish the Lute setup: languages, demo cleanup, corpus import.

Run inside the lute3 tool environment, with Lute stopped:

    lute-remote --stop
    ~/.local/share/uv/tools/lute3/bin/python lute-setup.py corpus <clean-dir>
    ~/.local/share/uv/tools/lute3/bin/python lute-setup.py setup
    lute-remote

subcommands
    setup     set L1=Spanish, L2=English, clear the bundled demo books
    corpus    import every "LEVEL - Title.txt" in <dir>, tagged by level
    status    show what is in the database
"""
import csv
import io
import os
import sys
from pathlib import Path

csv.field_size_limit(sys.maxsize)  # books are way over the 128 KB default

B = "\033[1m"; D = "\033[2m"; G = "\033[1;32m"; Y = "\033[1;33m"; R = "\033[1;31m"; O = "\033[0m"
L1, L2 = "Spanish", "English"

# The 15 books Lute ships with, in several languages, to demo the UI.
DEMO_TITLES = {
    "Examples", "Tutorial", "Tutorial follow-up",
    "Aladino y la lámpara maravillosa", "Büyük ağaç",
    "Hrad Cimburk – Jak vzal vítr pasáčkovi čepici", "逍遙遊",
    "Boucles d'or et les trois ours", "Die Bremer Stadtmusikanten",
    "Γεια σου, Νίκη. Ο Πέτρος είμαι.", "медведь",
    "बुद्धिमान् शिष्यः", "Bhagavad Ghita (Devanagari)",
    "Bhagavad Ghita (Latin)", "Universal Declaration of Human Rights",
}


def app_ctx():
    from lute.app_factory import create_app
    return create_app(None, output_func=lambda *a: None)


def importable():
    """Fail early with a clear message if Lute is running."""
    # pgrep is useless here: the `timeout …/bin/python lute-setup.py`
    # wrapper this script runs under has the same substring in its command
    # line, so pgrep always reports a false positive. Ask the port instead.
    import socket
    with socket.socket() as s_:
        s_.settimeout(1.5)
        listening = s_.connect_ex(("127.0.0.1", 5001)) == 0
    if listening:
        print(f"  {R}error:{O} Lute is running and holding the database.",
              file=sys.stderr)
        print(f"         Stop it with:  lute-remote --stop", file=sys.stderr)
        sys.exit(1)


def cmd_setup() -> int:
    importable()
    from lute.book.model import Repository
    from lute.models.repositories import LanguageRepository
    from lute.models.repositories import UserSettingRepository

    app = app_ctx()
    with app.app_context():
        from lute.db import db
        us = UserSettingRepository(db.session)
        lang = LanguageRepository(db.session)

        l1 = lang.find_by_name(L1)
        l2 = lang.find_by_name(L2)
        if not l1 or not l2:
            # Lute only knows the languages it has data for; English is
            # there, Spanish may not be until it is used once in the UI.
            print(f"  {Y}note:{O} {L1} not in Lute's language list yet. "
                  f"Set it once in the UI (Settings) and rerun this.")
            if l2:
                us.set_value("m2", l2.id)
                us.set_value("current_language_id", l2.id)
                db.session.commit()
                print(f"  {G}ok{O}   L2={L2} set (L1 pending)")
                return 0
            print(f"  {R}error:{O} {L2} not found either", file=sys.stderr)
            return 1

        # m1/m2 are created lazily by the UI, and set_value refuses keys it
        # has not seen, so create the rows first with Lute's own model.
        from lute.models.setting import UserSetting
        for key in ("m1", "m2"):
            if not us.key_exists(key):
                row = UserSetting()
                row.key = key
                row.value = ""
                db.session.add(row)
        db.session.commit()

        us.set_value("m1", l1.id)
        us.set_value("m2", l2.id)
        us.set_value("current_language_id", l2.id)
        if us.key_exists("IsDemoData"):
            us.set_value("IsDemoData", 0)
        db.session.commit()
        print(f"  {G}ok{O}   L1={L1}  L2={L2}  (translations show in your language)")

        from lute.models.book import Book as DBBook
        removed = 0
        for b in db.session.query(DBBook).all():
            tags = [t.text for t in b.book_tags]
            is_demo = b.title in DEMO_TITLES or (
                # anything left that is neither English nor tagged is
                # leftover sample data from the first run
                "gutenberg" not in tags
                and b.language.name != L2
            )
            if is_demo:
                db.session.delete(b)
                removed += 1
        db.session.commit()
        print(f"  {G}ok{O}   removed {removed} demo book(s)" if removed
              else f"  {D}no demo books left to remove{O}")
        left = db.session.query(DBBook).count()
        print(f"  {D}books in the database: {left}{O}")
    return 0


def cmd_corpus(cleandir: Path) -> int:
    importable()
    files = sorted(cleandir.glob("*.txt"))
    if not files:
        print(f"  {R}error:{O} no .txt in {cleandir}", file=sys.stderr)
        return 1

    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=["title", "text", "language", "tags", "url"],
                       lineterminator="\n")
    w.writeheader()
    for f in files:
        # filenames are "LEVEL kind - Title", so the level and the form
        # both survive into the tags
        stem = f.stem
        head, sep, title = stem.partition(" - ")
        if not sep:
            head, title = "", stem
        bits = head.split() if head else []
        level = next((b.upper() for b in bits if b.upper() in ("B1", "B2", "C1", "C2")), "B2")
        kind = next((b for b in bits if b.upper() != level), "general")
        nice = " ".join(title.replace("-", " ").split())
        w.writerow({
            "title": nice,
            "text": f.read_text(encoding="utf-8", errors="replace"),
            "language": L2,
            "tags": f"gutenberg,graded,{level},{kind}",
            "url": "https://www.gutenberg.org/",
        })

    app = app_ctx()
    with app.app_context():
        from lute.cli.import_books import import_books_from_csv
        tmp = Path("/tmp/lute-corpus.csv")
        tmp.write_text(buf.getvalue(), encoding="utf-8")
        import_books_from_csv(str(tmp), L2, ["gutenberg", "graded"], True)
    return 0


def cmd_status() -> int:
    from lute.book.model import Repository
    app = app_ctx()
    with app.app_context():
        from lute.db import db
        us = UserSettingRepository(db.session)
        print(f"  L1={us.get_value('m1')}  L2={us.get_value('m2')}  "
              f"current_language={us.get_value('current_language_id')}")
        from lute.models.book import Book as DBBook
        books = db.session.query(DBBook).all()
        print(f"  {len(books)} books")
        bytag = {}
        for b in books:
            for t in b.book_tags:
                bytag.setdefault(t.text, []).append(b.title)
        for tag in sorted(bytag):
            if tag in ("gutenberg", "graded"):
                continue
            print(f"    {tag}: {len(bytag[tag])} books")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    cmd = sys.argv[1]
    if cmd == "setup":
        sys.exit(cmd_setup())
    elif cmd == "corpus":
        sys.exit(cmd_corpus(Path(sys.argv[2])))
    elif cmd == "status":
        sys.exit(cmd_status())
    else:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
