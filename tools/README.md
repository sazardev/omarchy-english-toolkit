# tools

Helper scripts for the Lute side of the stack. They need Lute's own Python
environment, not the system one:

```bash
LUTEPY=~/.local/share/uv/tools/lute3/bin/python
```

## lute-corpus.py

Builds a graded English corpus from Project Gutenberg and strips the
boilerplate (licence header, table of contents, illustration markers) that
Lute would otherwise index as if it were the book.

```bash
python3 lute-corpus.py all list.tsv ~/corpus
python3 lute-corpus.py fetch list.tsv ~/corpus/raw
```

`list.tsv` columns: `gutenberg_id`, `level`, `title`, `author`.

**Every download is verified against the `Title:` header inside the file.**
A Gutenberg ID is just a number and numbers get misremembered: 164 is
*Twenty Thousand Leagues under the Sea*, not Aesop, and 2701 is *Moby
Dick*, not Dracula. Anything that does not match is rejected and reported
rather than imported under the wrong name.

Output files are named `LEVEL - Title.txt`, so the level survives as a
filename and can be turned into a tag on import.

## lute-setup.py

Finishes the Lute configuration and imports the corpus.

```bash
lute-remote --stop                     # Lute must not hold the database
$LUTEPY lute-setup.py setup            # L1=Spanish L2=English, drop demo books
$LUTEPY lute-setup.py corpus ~/corpus/clean
$LUTEPY lute-setup.py status
lute-remote
```

- `setup` sets L1 to Spanish and L2 to English, which is what makes the
  word popup show a Spanish translation, and removes the 15 demo books
  Lute ships in Chinese, Czech, Greek and so on.
- `corpus` imports through Lute's own `import_books_from_csv`, tagging
  each book `gutenberg,graded,<level>`, so you can filter by level in the
  UI.

It uses Lute's models and services rather than raw SQL, so the schema is
never guessed at.

## irregular-verbs.py

Builds the complete irregular verb table from Wiktionary, into
`anki/content/irregular.json`.

```bash
python3 irregular-verbs.py --out ../anki/content/irregular.json --categories
```

Two sources, because neither alone is enough:

- **Appendix:English irregular verbs** gives the forms, including the
  prefixed variants: *forbear / forbore / forborne*, *overbear*, and so
  on, which are real English verbs.
- **Category:English irregular verbs** and its four subcategories give the
  curated list of *which* verbs are irregular, so typos and coinages do
  not get in.

Result: 415 verbs, all three forms each. Modals are deliberately not
included; they follow their own patterns and are chapter 05 of the deck.

The appendix is wikitext, so it is parsed with a small state machine
rather than a regex. Two things that cost time and are worth knowing:

- the italic marker opening a table cell is a **pair** of apostrophes, so
  matching four finds nothing at all
- the cell may contain a comment, and comments contain apostrophes, so
  comments have to be stripped *before* matching

## Why the -ing form needs its own function

Deriving `-ing` is not one rule, it is four, tested in this order:

1. ends in `ie` -> `ying` (lie -> lying)
2. ends in consonant + `y` -> `ying` (study -> studying)
3. ends in `e` -> drop the `e` (abide -> abiding, come -> coming)
4. consonant-vowel-consonant -> double (stop -> stopping)

Order matters: testing the doubling rule before the `-e` rule turns
*like* into *liking* and *come* into *comming*. And the doubling rule
only fires when the last syllable is stressed, which is why *open* needs
an exception rather than the rule: it looks like CVC but the stress is on
the first syllable.

## Why csv.field_size_limit is raised

Lute's CSV importer uses the stdlib `csv` module, whose default field
limit is 131072 bytes. A single chapter of a novel blows past that, so the
import dies with `field larger than field limit` unless the limit is
raised first.
