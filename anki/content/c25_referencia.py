"""25 Reference - the twelve tenses on one page, and the cheat sheet.

One verb per column, one tense per row, so the structure of the tense
system is visible at a glance. This is a page to look things up on, not a
page to memorise.
"""

from ._base import rule, gap, ex, tabla, serie

D = "25 Reference"
T = D + "::The Twelve Tenses"
S = D + "::Cheat Sheet"

TENSES = [
    "Presente simple",
    "Presente continuo",
    "Pasado simple",
    "Pasado continuo",
    "Pasado perfecto",
    "Pasado perfecto continuo",
    "Futuro",
    "Futuro continuo",
    "Presente perfecto",
    "Presente perfecto continuo",
    "Futuro perfecto",
    "Futuro perfecto continuo",
]

# one row per tense: to be, and a regular verb
BE = [
    "am/is/are", "am/is/are eating", "was/were", "was/were eating",
    "had been", "had been eating", "will be", "will be eating",
    "have/has been", "have/has been eating", "will have been",
    "will have been eating",
]
EAT = [
    "eat", "eat / am eating", "ate", "ate / was eating",
    "had eaten", "had been eating", "will eat", "will be eating",
    "have/has eaten", "have/has been eating", "will have eaten",
    "will have been eating",
]


def build():
    tabla(T, ["tense", "to be", "to eat (regular)"],
          [[TENSES[i], BE[i], EAT[i]] for i in range(len(TENSES))],
          titulo="All twelve tenses, side by side",
          nivel="B2",
          nota="The tense system never changes. Only the verb does. Read "
               "across to see the three forms build on each other.")

    # the same twelve tenses across five verb shapes: this is the table
    # that makes the pattern obvious
    shapes = [
        ("to be", "am/is/are", "was/were", "been", "being"),
        ("to eat", "eats", "ate", "eaten", "eating"),
        ("to go", "goes", "went", "gone", "going"),
        ("to have", "has", "had", "had", "having"),
        ("to write", "writes", "wrote", "written", "writing"),
        ("to see", "sees", "saw", "seen", "seeing"),
    ]
    tabla(T + "::Across Verb Shapes",
          ["verb", "3rd sing", "past", "participle", "-ing"],
          [list(s) for s in shapes],
          titulo="Five verb shapes, the same five columns",
          nivel="B2",
          nota="Written / wrote / written is the shape to memorise. The "
               "others fall out of the pattern.")

    # ---------------------------------------------------- the cheat sheet
    sheet = [
        ("Add -ed", "work -> worked", "R1. Nothing special.",
         "call / called, open / opened, visit / visited, need / needed",
         "regular-1"),
        ("Drop the silent -e", "like -> liked", "R2. Ends in -e.",
         "live / lived, move / moved, close / closed, believe / believed",
         "regular-2"),
        ("y becomes ied", "study -> studied", "R3. Consonant + y.",
         "try / tried, carry / carried, worry / worried, hurry / hurried",
         "regular-3"),
        ("Keep the y", "play -> played", "R4. Vowel + y. 'Playd' is wrong.",
         "enjoy / enjoyed, stay / stayed, buy / bought",
         "regular-4"),
        ("Double the consonant", "stop -> stopped",
         "R5. Stressed consonant-vowel-consonant.",
         "plan / planned, travel / travelled, admit / admitted, prefer / preferred",
         "regular-5"),
        ("No doubling after -e", "like -> liked",
         "R6. CVC but already ends in -e.",
         "change / changed, use / used, dive / dived, sense / sensed",
         "regular-6"),
    ]
    for name, change, why, examples, rid in sheet:
        change_verb = change.split(" -> ")[0]
        change_past = change.split(" -> ")[1]
        gap(S, "___ (change '%s' to the past simple)" % change_verb, change_past,
            nivel="B1", cue=change_verb, forma=name,
            regla="%s. %s" % (rid, why),
            ejemplos=ex(examples),
            tags=("reference", "regular", rid))

    # -------------------------------------------- the order to test in
    rule(S,
         "In which order do I test a verb against the six rules?",
         "R6, then R3, then R5, then R2, then R1",
         regla="Test in this order, because the earlier rules are the "
               "exceptions to the later ones.\n"
               "1. R6: ends in -e? Then no doubling at all, R2 applies.\n"
               "2. R3: ends in consonant + y? Then ied, and R5 never applies.\n"
               "3. R5: stressed CVC? Then double the consonant.\n"
               "4. R2: any other -e ending? Drop the e.\n"
               "5. R1: everything else, just add -ed.",
         ejemplos=ex("travel / travelled / travelling - CVC, stressed, no -e, so R5.",
                     "study / studied / studying - consonant + y, so R3 beats R5.",
                     "like / liked / liking - ends in -e, so R6 beats R5."),
         notas="Travelled versus traveled is the whole point: both are "
               "correct, they differ by dialect.",
         tags=("reference", "regular", "strategy"))

    # -------------------------------------------- the two -ed sounds
    rule(S,
         "Why is 'worked' pronounced 'workt' but 'wanted' 'wanted'?",
         "After t and d, -ed is /id/. Otherwise /t/ or /d/.",
         regla="The spelling is always -ed, but the sound is one of three.\n"
               "- /id/ after t or d: wanted, needed, decided\n"
               "- /t/ after a voiceless sound: worked, walked, laughed\n"
               "- /d/ after everything else: played, called, cleaned",
         ejemplos=ex("worked /wɜːkt/", "wanted /ˈwɒntɪd/",
                     "called /kɔːld/", "walked /wɔːkt/"),
         notas="Spelling does not change. Only the sound does.",
         tags=("reference", "pronunciation"))

    # -------------------------------------------- how many are irregular
    rule(S,
         "How many English verbs are irregular?",
         "About 130 out of roughly 15,000.",
         regla="The irregular ones must be memorised, and they are few. The "
               "other 14,800 come from six spelling rules. So the efficient "
               "order is: learn the six rules first, then drill the "
               "irregulars. Chapter 24 has the rules, chapter 16 has the list.",
         ejemplos=ex("Irregular, must be learned: be, do, have, go, come, "
                     "get, give, make, take, see, write, speak.",
                     "Regular, produced by the rules: work, play, study, "
                     "call, walk, need, want, open."),
         notas="A table of all 15,000 verbs would be useless, because you do "
               "not read it. You apply six rules.",
         tags=("reference", "irregular", "strategy"))

    # -------------------------------------------- which rule, drills
    which = [
        ("work", "R1", "plain"),
        ("watch", "R1", "ends in ch, add -es not -s, no doubling"),
        ("want", "R1", "plain"),
        ("live", "R2", "ends in -e, drop it"),
        ("dance", "R2", "ends in -e, drop it"),
        ("hate", "R2", "ends in -e, drop it"),
        ("study", "R3", "consonant + y"),
        ("cry", "R3", "consonant + y"),
        ("apply", "R3", "consonant + y"),
        ("enjoy", "R4", "vowel + y, keep the y"),
        ("stay", "R4", "vowel + y, keep the y"),
        ("play", "R4", "vowel + y, keep the y"),
        ("stop", "R5", "stressed CVC, double the p"),
        ("plan", "R5", "stressed CVC, double the n"),
        ("admit", "R5", "stressed CVC, double the t"),
        ("prefer", "R5", "stressed CVC, double the r"),
        ("travel", "R5", "stressed CVC, double the l"),
        ("like", "R6", "CVC but ends in -e, no doubling"),
        ("change", "R6", "CVC but ends in -e, no doubling"),
        ("use", "R6", "ends in -e, no doubling"),
        ("dive", "R6", "short vowel and -e, no doubling"),
        ("open", "R1", "plain"),
    ]
    serie(T + "::Which Rule", [[f"Which rule conjugates '{v}'?", r, why]
                               for v, r, why in which],
          nivel="B1", tags=("reference", "regular", "rules"))


# build.py imports this module, so the generator must run at import
# time; a __main__ guard would never fire.
build()


if __name__ == "__main__":
    build()
    print("25 Reference - twelve tenses and cheat sheet")
