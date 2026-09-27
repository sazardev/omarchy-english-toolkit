"""24 Regular Verbs - six suffix rules that conjugate almost everything.

There is no table of all English verbs, and there cannot usefully be one.
Of the roughly 15,000 verbs, about 130 are irregular and the rest follow
six rules of spelling. Those six rules are worth more than every
irregular table combined, because they cover the other 14,800 verbs
without memorising anything.
"""

from ._base import rule, prod, gap, serie_gap, serie_cloze, ex, ul, table, serie

D = "24 Regular Verbs"
R = D + "::The Six Rules"
X = D + "::Exercises"

# ---------------------------------------------------------------- the rules
# (id, name, test, past, participle, -ing, examples)
RULES = [
    ("R1", "Most verbs: add -ed", "anything not covered by R2 to R6",
     "work / worked", "work / worked", "work / working",
     [("call", "called", "called", "calling"),
      ("open", "opened", "opened", "opening"),
      ("help", "helped", "helped", "helping"),
      ("visit", "visited", "visited", "visiting"),
      ("need", "needed", "needed", "needing")]),

    ("R2", "Drop the silent -e, then add -ed", "verb ends in -e",
     "like / liked", "like / liked", "like / liking",
     [("like", "liked", "liked", "liking"),
      ("live", "lived", "lived", "living"),
      ("move", "moved", "moved", "moving"),
      ("close", "closed", "closed", "closing"),
      ("believe", "believed", "believed", "believing")]),

    ("R3", "y becomes ied", "ends in consonant + y",
     "study / studied", "study / studied", "study / studying",
     [("study", "studied", "studied", "studying"),
      ("try", "tried", "tried", "trying"),
      ("carry", "carried", "carried", "carrying"),
      ("worry", "worried", "worried", "worrying"),
      ("hurry", "hurried", "hurried", "hurrying")]),

    ("R4", "y stays y: add -ed", "ends in vowel + y",
     "play / played", "play / played", "play / playing",
     [("play", "played", "played", "playing"),
      ("enjoy", "enjoyed", "enjoyed", "enjoying"),
      ("stay", "stayed", "stayed", "staying"),
      ("buy", "bought", "bought", "buying"),
      ("day", "dayed", "dayed", "daying")]),

    ("R5", "Double the consonant", "consonant-vowel-consonant, stressed last syllable",
     "stop / stopped", "stop / stopped", "stop / stopping",
     [("stop", "stopped", "stopped", "stopping"),
      ("plan", "planned", "planned", "planning"),
      ("travel", "travelled", "travelled", "travelling"),
      ("admit", "admitted", "admitted", "admitting"),
      ("prefer", "preferred", "preferred", "preferring")]),

    ("R6", "Do NOT double before -ed after e", "same shape, but ends in -e",
     "like / liked", "like / liked", "like / liking",
     [("like", "liked", "liked", "liking"),
      ("change", "changed", "changed", "changing"),
      ("use", "used", "used", "using"),
      ("sense", "sensed", "sensed", "sensing"),
      ("dive", "dived", "dived", "diving")]),
]


def build():
    # ---------------------------------------------------------- rule cards
    for rid, name, test, past, pp, ing, examples in RULES:
        ex_html = ex(*[f"{b} - {p} - {ppp} - {i}" for b, p, ppp, i in examples])
        rule(R,
             f"{rid}. {name}",
             f"{past}   {pp}   {ing}",
             regla=f"WHEN: {test}.",
             ejemplos=ex_html,
             notas="Prueba las reglas en este orden: si R6 encaja, no dobles. "
                   "Si R3 encaja, no apliques R5.",
             tags=("regular", "rule", rid))

    # ------------------------------------------- which rule applies? (the
    # actual skill: deciding which rule fires on an unfamiliar verb)
    tests = [
        ("work", "R1", "does not end in -e, consonant+y, or CVC"),
        ("walk", "R1", "final syllable is not stressed, so no doubling"),
        ("watch", "R1", "ends in ch: add -ed, no doubling"),
        ("want", "R1", "plain"),
        ("live", "R2", "ends in -e, drop it"),
        ("dance", "R2", "ends in -e, drop it"),
        ("hate", "R2", "ends in -e, drop it"),
        ("study", "R3", "ends in consonant + y"),
        ("cry", "R3", "ends in consonant + y"),
        ("apply", "R3", "ends in consonant + y"),
        ("enjoy", "R4", "ends in vowel + y, keep the y"),
        ("stay", "R4", "ends in vowel + y, keep the y"),
        ("play", "R4", "ends in vowel + y, keep the y"),
        ("stop", "R5", "CVC and stressed: double the p"),
        ("plan", "R5", "CVC and stressed: double the n"),
        ("admit", "R5", "CVC and stressed: double the t"),
        ("prefer", "R5", "CVC and stressed: double the r"),
        ("travel", "R5", "CVC and stressed, double the l"),
        ("like", "R6", "CVC but ends in -e: no doubling"),
        ("change", "R6", "CVC but ends in -e: no doubling"),
        ("use", "R6", "ends in -e: no doubling"),
        ("dive", "R6", "short vowel, ends in -e: no doubling"),
    ]
    serie(X, [[f"Which rule conjugates '{v}'?", r, why]
              for v, r, why in tests],
          nivel="B1", tags=("regular", "rules"))

    # ------------------------------------------------- produce the forms
    for rid, name, test, past, pp, ing, examples in RULES:
        for b, p, ppp, i in examples:
            triple = "%s / %s / %s" % (p, ppp, i)
            gap(X, "I ___ it every day. (%s)" % b, p,
                nivel="B1", cue=b, forma=triple,
                regla="%s. Past simple of '%s'." % (rid, b),
                tags=("regular", "production", rid))
            gap(X, "I have ___ it. (%s)" % b, ppp,
                nivel="B1", cue=b, forma=triple,
                regla="%s. Past participle of '%s'." % (rid, b),
                tags=("regular", "production", rid))
            gap(X, "I was ___ it. (%s)" % b, i,
                nivel="B1", cue=b, forma=triple,
                regla="%s. -ing form of '%s'." % (rid, b),
                tags=("regular", "production", rid))

    # ------------------------------------------------- spelling traps
    traps = [
        ("stopped", "stoping", "double the p: stopping"),
        ("planned", "planing", "double the n: planning"),
        ("travelled", "traveling", "British doubles the l: travelling"),
        ("studied", "studyd", "y becomes ied, never yd"),
        ("carried", "carryed", "y becomes ied, never yed"),
        ("played", "playd", "keep the y, just add -ed"),
        ("liked", "likedd", "drop the e, add one -ed"),
        ("believed", "believeed", "drop the e, add -ed"),
        ("used", "usedd", "add -ed, one d only"),
        ("dived", "divved", "do not double before -ed after -e"),
    ]
    serie(X, [[f"Which is correct?", f"{good}  (not {bad})", why]
              for good, bad, why in traps],
          nivel="B2", tags=("regular", "spelling", "traps"))

    # ------------------------------------------------- the -s form
    s_forms = [
        ("go", "goes"), ("do", "does"), ("watch", "watches"), ("fix", "fixes"),
        ("pass", "passes"), ("study", "studies"), ("cry", "cries"),
        ("carry", "carries"), ("play", "plays"), ("want", "wants"),
        ("ask", "asks"), ("buzz", "buzzes"), ("wash", "washes"),
    ]
    for base, third_s in s_forms:
        gap(X, "He ___ to work every day. (%s)" % base, third_s,
            nivel="B1", cue=base, forma=third_s,
            regla="Third person singular. -s, or -es after s, x, z, ch, sh, o; "
                  "-ies after consonant + y.",
            tags=("regular", "third-person"))

    # ------------------------------------------------- negative form
    negs = [("work", "does not work", "regular: does + not + base"),
            ("study", "does not study", "base form, never 'studys'"),
            ("go", "does not go", "irregular: do + not, no -es"),
            ("play", "does not play", "base form")]
    serie(X, [[f"___ he speak Spanish?", a, why] for _, a, why in negs],
          nivel="B1", tags=("regular", "negative"))


# build.py imports this module, so the generator must run at import
# time; a __main__ guard would never fire.
build()


if __name__ == "__main__":
    build()
    print("24 Regular Verbs - six rules")
