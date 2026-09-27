"""16 Irregular Verbs - the complete list.

Generated from Wiktionary rather than typed by hand. The source is
Appendix:English irregular verbs plus the curated Category:English
irregular_verbs, parsed by tools/irregular-verbs.py into irregular.json.

Why generated: an irregular verb table written from memory is wrong in
exactly the places you cannot check. 415 verbs with all three forms,
verified against a source, is the whole useful inventory. Modals are not
here; they follow their own patterns and live in chapter 05.

Regular verbs are not here either. They are produced by six spelling
rules, which is chapter 24.
"""

import json
from pathlib import Path

from ._base import gap, rule, serie, ex, tabla

D = "16 Irregular Verbs"
T = D + "::Irregular Forms"
P = D + "::Participle Traps"

DATA = Path(__file__).with_name("irregular.json")

VOWELS = "aeiou"

# Verbs whose -ing is not derivable by the spelling rules.
# "see" keeps the e (seeing, not seing) and "be" does not double (being,
# not bing) because b is already preceded by a vowel.
ING_IRREGULAR = {
    "lie": "lying",
    "die": "dying",
    "tie": "tying",
    "vie": "vying",
    "see": "seeing",
    "be": "being",
    "flee": "fleeing",
    "free": "freeing",
    "agree": "agreeing",
    # The CVC rule only fires when the last syllable carries the stress.
    # "open" looks like CVC but the stress is on the first syllable, so no
    # doubling. Verbs where doubling is wrong for the same reason.
    "open": "opening",
    "offer": "offering",
    "order": "ordering",
    "enter": "entering",
    "visit": "visiting",
    "edit": "editing",
    "limit": "limiting",
    "profit": "profiting",
    "benefit": "benefiting",
    "orbit": "orbiting",
    "exhibit": "exhibiting",
}


def ing(v):
    """-ing form, for the continuous tenses.

    The order matters: the -e rule has to be tested before the doubling
    rule, or "like" becomes "liking" and "come" becomes "comming".
    """
    if v in ING_IRREGULAR:
        return ING_IRREGULAR[v]
    if v.endswith("ie"):
        return v[:-2] + "ying"
    if v.endswith("y") and len(v) > 1 and v[-2] not in VOWELS:
        return v[:-1] + "ying"
    if v.endswith("e"):
        # a silent e is dropped: abide -> abiding, come -> coming
        return v[:-1] + "ing"
    if (len(v) > 2 and v[-1] not in VOWELS and v[-1] not in "wxy"
            and v[-2] in VOWELS and v[-3] not in VOWELS):
        # consonant-vowel-consonant: stop -> stopping, begin -> beginning
        return v + v[-1] + "ing"
    return v + "ing"


def load():
    if not DATA.exists():
        raise SystemExit(
            "irregular.json not found. Build it with:\n"
            "  python3 tools/irregular-verbs.py --out anki/content/irregular.json")
    d = json.loads(DATA.read_text(encoding="utf-8"))
    vs = [v for v in d.get("verbs", []) if v.get("past") and v.get("participle")]
    for v in vs:
        v["ing"] = ing(v["base"])
    return sorted(vs, key=lambda x: x["base"])


def third(v):
    if v.endswith(("s", "x", "z", "ch", "sh", "o")):
        return v + "es"
    if v.endswith("y") and len(v) > 1 and v[-2] not in "aeiou":
        return v[:-1] + "ies"
    return v + "s"


def build(verbs):
    # -------------------------------------------- 1. the reference table
    tabla(T, ["base", "3rd sing", "past", "past participle", "-ing"],
          [[v["base"], third(v["base"]), v["past"], v["participle"], v["ing"]] for v in verbs],
          titulo="The complete irregular verb list (%d verbs)" % len(verbs),
          nivel="B1",
          nota="Read it, do not learn it. See the pattern, then drill only "
               "the verbs you actually get wrong.")

    # -------------------------------------------- 2. recognition
    for v in verbs:
        serie(T, [[v["past"], v["base"],
                   "past simple of '%s'" % v["base"],
                   ex("%s - %s - %s - %s" % (v["base"], v["past"], v["participle"], v["ing"])),
                   ""]],
              nivel="B2", tags=("irregular", "verbs"))

    # -------------------------------------------- 3. production, both ways
    for v in verbs:
        triple = "%s / %s / %s" % (v["past"], v["participle"], v["ing"])
        gap(T, "Yesterday I ___ the door. (%s)" % v["base"], v["past"],
            nivel="B2", cue=v["base"], forma=triple,
            regla="Past simple of '%s': %s" % (v["base"], v["past"]),
            tags=("irregular", "verbs", "past"))
        gap(T, "I have already ___ it. (%s)" % v["base"], v["participle"],
            nivel="B2", cue=v["base"], forma=triple,
            regla="Past participle of '%s': %s. The past is '%s'."
                  % (v["base"], v["participle"], v["past"]),
            tags=("irregular", "verbs", "participle"))
        gap(T, "I am ___ right now. (%s)" % v["base"], v["ing"],
            nivel="B2", cue=v["base"], forma=v["ing"],
            regla="-ing form of '%s': %s" % (v["base"], v["ing"]),
            tags=("irregular", "verbs", "continuous"))

    # -------------------------------------------- 4. the participle traps
    traps = [v for v in verbs
             if v["participle"] != v["past"]
             and not v["participle"].startswith(v["past"])]
    for v in traps:
        line = "I have %s it. / I %s yesterday. / I am %s now." % (
            v["participle"], v["past"], v["ing"])
        rule(P, "%s -> participle? (%s)" % (v["past"], v["base"]), v["participle"],
             regla="Past: %s. Participle: %s. They are not the same word."
                   % (v["past"], v["participle"]),
             ejemplos=ex(line),
             notas="I have written, not 'I have wrote'.",
             tags=("irregular", "participle", "traps"))

    # -------------------------------------------- 5. the -ing doubles
    for v in verbs:
        if (len(v["ing"]) > 4 and v["ing"][-1] == v["ing"][-2]
                and v["ing"][-1] not in "aeiouwxy"):
            gap(P, "I am ___ it now. (%s)" % v["base"], v["ing"],
                nivel="B2", cue=v["base"],
                regla="The final consonant doubles before -ing in a short "
                      "stressed syllable ending consonant-vowel-consonant.",
                tags=("irregular", "continuous", "spelling"))


# build.py imports this module, so the generator must run at import
# time; a __main__ guard would never fire.
_verbs = load()
build(_verbs)


if __name__ == "__main__":
    print("16 Irregular Verbs - %d verbs" % len(_verbs))
