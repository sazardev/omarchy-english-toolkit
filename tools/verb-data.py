#!/usr/bin/env python3
"""Build the master verb dataset: forms, meanings and usage scenarios.

Forms come from the generated irregular.json (Wiktionary appendix).
Meanings come from WordNet, which is open, offline once downloaded and
does not invent a gloss: it returns Princeton's own definitions, so the
text is trustworthy and offline-capable.

Scenarios are hand-written, because which verb fits a situation is a
judgement, not a fact anyone has tabulated. They are the part a
dictionary cannot give you.

usage: verb-data.py --irregular anki/content/irregular.json --out web/data/verbs.json
"""
import argparse
import json
import re
import sys
from pathlib import Path

VOWELS = "aeiou"

ING_IRREGULAR = {
    "lie": "lying", "die": "dying", "tie": "tying", "vie": "vying",
    "see": "seeing", "be": "being", "flee": "fleeing", "free": "freeing",
    "agree": "agreeing", "open": "opening", "offer": "offering",
    "order": "ordering", "enter": "entering", "visit": "visiting",
    "edit": "editing", "limit": "limiting", "profit": "profiting",
    "benefit": "benefiting", "orbit": "orbiting", "exhibit": "exhibiting",
}

# the six rules, each with the test and worked examples
RULES = [
    {"id": "R1", "name": "Add -ed",
     "test": "anything not covered by R2 to R6",
     "how": "work / worked / worked / working",
     "note": "The default. If nothing else applies, just add -ed.",
     "examples": [
         {"base": "call", "third": "calls", "past": "called",
          "participle": "called", "ing": "calling"},
         {"base": "open", "third": "opens", "past": "opened",
          "participle": "opened", "ing": "opening"},
         {"base": "help", "third": "helps", "past": "helped",
          "participle": "helped", "ing": "helping"},
         {"base": "visit", "third": "visits", "past": "visited",
          "participle": "visited", "ing": "visiting"},
         {"base": "need", "third": "needs", "past": "needed",
          "participle": "needed", "ing": "needing"}]},
    {"id": "R2", "name": "Drop the silent -e, then add -ed",
     "test": "the verb ends in -e",
     "how": "like / liked / liked / liking",
     "note": "Only one -ed. 'likedd' is wrong.",
     "examples": [
         {"base": "like", "third": "likes", "past": "liked",
          "participle": "liked", "ing": "liking"},
         {"base": "live", "third": "lives", "past": "lived",
          "participle": "lived", "ing": "living"},
         {"base": "move", "third": "moves", "past": "moved",
          "participle": "moved", "ing": "moving"},
         {"base": "close", "third": "closes", "past": "closed",
          "participle": "closed", "ing": "closing"},
         {"base": "believe", "third": "believes", "past": "believed",
          "participle": "believed", "ing": "believing"}]},
    {"id": "R3", "name": "y becomes ied",
     "test": "ends in consonant + y",
     "how": "study / studied / studied / studying",
     "note": "Never 'studyd'. The y turns into i before -ed.",
     "examples": [
         {"base": "study", "third": "studies", "past": "studied",
          "participle": "studied", "ing": "studying"},
         {"base": "try", "third": "tries", "past": "tried",
          "participle": "tried", "ing": "trying"},
         {"base": "carry", "third": "carries", "past": "carried",
          "participle": "carried", "ing": "carrying"},
         {"base": "worry", "third": "worries", "past": "worried",
          "participle": "worried", "ing": "worrying"},
         {"base": "hurry", "third": "hurries", "past": "hurried",
          "participle": "hurried", "ing": "hurrying"}]},
    {"id": "R4", "name": "Keep the y: add -ed",
     "test": "ends in vowel + y",
     "how": "play / played / played / playing",
     "note": "'Playd' is wrong. The y stays.",
     "examples": [
         {"base": "play", "third": "plays", "past": "played",
          "participle": "played", "ing": "playing"},
         {"base": "enjoy", "third": "enjoys", "past": "enjoyed",
          "participle": "enjoyed", "ing": "enjoying"},
         {"base": "stay", "third": "stays", "past": "stayed",
          "participle": "stayed", "ing": "staying"},
         {"base": "day", "third": "days", "past": "dayed",
          "participle": "dayed", "ing": "daying"}]},
    {"id": "R5", "name": "Double the consonant",
     "test": "consonant-vowel-consonant, stress on the last syllable",
     "how": "stop / stopped / stopped / stopping",
     "note": "Travel doubles too: travelled, travelling. US accepts traveled.",
     "examples": [
         {"base": "stop", "third": "stops", "past": "stopped",
          "participle": "stopped", "ing": "stopping"},
         {"base": "plan", "third": "plans", "past": "planned",
          "participle": "planned", "ing": "planning"},
         {"base": "travel", "third": "travels", "past": "travelled",
          "participle": "travelled", "ing": "travelling"},
         {"base": "admit", "third": "admits", "past": "admitted",
          "participle": "admitted", "ing": "admitting"},
         {"base": "prefer", "third": "prefers", "past": "preferred",
          "participle": "preferred", "ing": "preferring"}]},
    {"id": "R6", "name": "Do NOT double before -ed after -e",
     "test": "CVC shape, but the verb already ends in -e",
     "how": "like / liked / liked / liking",
     "note": "This is why like is liked and not likked.",
     "examples": [
         {"base": "change", "third": "changes", "past": "changed",
          "participle": "changed", "ing": "changing"},
         {"base": "use", "third": "uses", "past": "used",
          "participle": "used", "ing": "using"},
         {"base": "dive", "third": "dives", "past": "dived",
          "participle": "dived", "ing": "diving"},
         {"base": "sense", "third": "senses", "past": "sensed",
          "participle": "sensed", "ing": "sensing"}]},
]

# which rule fires: the decision is the actual skill
DECISIONS = [
    ("work", "R1", "plain"), ("want", "R1", "plain"), ("open", "R1", "plain"),
    ("watch", "R1", "ends in ch, so the third person is watches"),
    ("live", "R2", "ends in -e"), ("dance", "R2", "ends in -e"),
    ("hate", "R2", "ends in -e"),
    ("study", "R3", "consonant + y"), ("cry", "R3", "consonant + y"),
    ("apply", "R3", "consonant + y"),
    ("enjoy", "R4", "vowel + y, keep the y"), ("stay", "R4", "vowel + y"),
    ("play", "R4", "vowel + y"),
    ("stop", "R5", "stressed CVC, double the p"),
    ("plan", "R5", "stressed CVC, double the n"),
    ("admit", "R5", "stressed CVC, double the t"),
    ("prefer", "R5", "stressed CVC, double the r"),
    ("travel", "R5", "stressed CVC, double the l"),
    ("like", "R6", "CVC but ends in -e, no doubling"),
    ("change", "R6", "CVC but ends in -e, no doubling"),
    ("use", "R6", "ends in -e, no doubling"),
    ("dive", "R6", "short vowel and -e, no doubling"),
]


def ing(v):
    if v in ING_IRREGULAR:
        return ING_IRREGULAR[v]
    if v.endswith("ie"):
        return v[:-2] + "ying"
    if v.endswith("y") and len(v) > 1 and v[-2] not in VOWELS:
        return v[:-1] + "ying"
    if v.endswith("e"):
        return v[:-1] + "ing"
    if (len(v) > 2 and v[-1] not in VOWELS and v[-1] not in "wxy"
            and v[-2] in VOWELS and v[-3] not in VOWELS):
        return v + v[-1] + "ing"
    return v + "ing"


def third(v):
    if v.endswith(("s", "x", "z", "ch", "sh", "o")):
        return v + "es"
    if v.endswith("y") and len(v) > 1 and v[-2] not in VOWELS:
        return v[:-1] + "ies"
    return v + "s"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--irregular", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--extra", help="JSON file of hand-written entries to merge")
    a = ap.parse_args()

    src = json.loads(Path(a.irregular).read_text(encoding="utf-8"))
    verbs = src.get("verbs", [])

    extra = {}
    if a.extra and Path(a.extra).exists():
        extra = json.loads(Path(a.extra).read_text(encoding="utf-8")).get("extra", {})

    # WordNet definitions
    definitions = {}
    try:
        import nltk
        try:
            nltk.data.find("corpora/wordnet")
        except LookupError:
            nltk.download("wordnet", quiet=True)
            nltk.download("omw-1.4", quiet=True)
        from nltk.corpus import wordnet as wn
        for v in verbs:
            base = v["base"]
            syn = wn.synsets(base, pos=wn.VERB)
            glosses = []
            for s in syn[:2]:
                d = s.definition()
                if d and d not in glosses:
                    glosses.append(d)
            if glosses:
                definitions[base] = glosses
    except ImportError:
        print("  warn: nltk not available, no definitions", file=sys.stderr)

    out = []
    for v in sorted(verbs, key=lambda x: x["base"]):
        b = v["base"]
        e = dict(
            base=b,
            third=third(b),
            past=v["past"],
            participle=v["participle"],
            ing=ing(b),
            irregular=True,
        )
        if b in definitions:
            e["meaning"] = definitions[b][0]
            if len(definitions[b]) > 1:
                e["alt"] = definitions[b][1]
        if b in extra:
            e.update(extra[b])
        out.append(e)

    payload = {
        "source": {
            "forms": "Wiktionary: Appendix:English irregular verbs",
            "meanings": "Princeton WordNet via NLTK",
            "scenarios": "hand-written",
        },
        "count": len(out),
        "rules": RULES,
        "decisions": [{"base": b, "rule": r, "why": w} for b, r, w in DECISIONS],
        "verbs": out,
    }
    if a.extra and Path(a.extra).exists():
        payload.update(json.loads(Path(a.extra).read_text(encoding="utf-8")))

    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf-8")
    have = sum(1 for v in out if v.get("meaning"))
    print(f"  {len(out)} verbs -> {a.out}")
    print(f"  {have} with a definition, {len(out)-have} without")
    return 0


if __name__ == "__main__":
    sys.exit(main())
