# Contributing

## Reporting a problem

Open an issue and include:

- `cat /etc/os-release | head -2` and `uname -m`
- which step of `install.sh` failed, with the output
- `nvim --version | head -1` if the problem is the editor integration

## Adding a rule to the grammar checker

Edit `config/ltex/ltex.json`. Keep the ruleset English-only and start from
the default: a rule that fires on every correct sentence trains people to
ignore the checker.

Useful `diagnosticLevel` values, from quiet to noisy:

- `error` - only definite mistakes
- `hint` (default here) - includes style and collocation suggestions

## Changing the Anki deck

The deck is generated, never edited by hand.

```bash
cd anki
.venv/bin/python build.py deck.apkg
.venv/bin/python lint.py deck.apkg
.venv/bin/python spanish_check.py deck.apkg   # must stay English-only
```

One module per chapter in `anki/content/`, registered in `build.py`.
Note GUIDs are stable, so regenerating does not duplicate cards in an
existing collection.

## Style

- Shell: `bash -n` must pass, `shellcheck` clean
- Python: follow the surrounding module, no new dependencies without a reason
- English only in anything a learner will read, including error messages
