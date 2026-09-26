# omarchy-english-toolkit

A complete, **fully offline** English learning stack for **Arch Linux / Omarchy**.

Grammar checking while you write, an offline dictionary, a reader with
built-in TTS, a local AI conversation partner, and a ready-to-import
Anki deck with 2,141 English grammar notes. Nothing leaves your machine.

```
encheck  notas.md          # grammar + spelling, offline
sdcv     collocation       # dictionary in your terminal
vale     notas.md          # prose style
lute --local               # reader + dictionary + TTS
enpractice "job interviews"  # speak and write with a local model
```

---

## Why

Most English-learning tooling wants your text uploaded somewhere. This
does not. LTeX+ bundles its own Java runtime, Lute and `encheck` are
local, and the conversation partner runs on Ollama on your own GPU.
You can fly with the wifi off.

## What's inside

| Tool | Role | Needs root |
|---|---|---|
| **LTeX+ 18.7.0** | LSP + CLI grammar and spelling engine (LanguageTool) | no |
| **encheck** | tidy CLI wrapper around LTeX+, exit code 1 when issues found | no |
| **enpractice** | conversation and writing practice against a local Ollama model | no |
| **Lute 3.10.3** | EPUB/PDF reader with tap-to-define dictionary, TTS, Anki export | no |
| **Ollama** (`qwen2.5:7b`) | local AI examiner and conversation partner | no |
| **Neovim / LazyVim** | checks your writing live as you type | no |
| **LanguageTool** | desktop app and `--serve` server for Obsidian/browser/scripts | yes |
| **Vale** | prose style linter (style, not grammar) | yes |
| **dictd + sdcv** | offline dictionary, terminal and via DICT protocol | yes |
| **FreeDict eng-spa / spa-eng** | English-Spanish, both directions | yes |
| **GCIDE (StarDict)** | large English-only dictionary for definitions | yes |
| **aspell-en / hunspell-en** | English spell dictionaries | yes |
| **GNOME Dictionary** | dictionary GUI | yes |

## Install

```bash
git clone https://github.com/sazardev/omarchy-english-toolkit.git
cd omarchy-english-toolkit

bash install.sh              # user-level only, no root
sudo bash install.sh         # everything, including system packages
```

`install.sh` is idempotent: run it again to repair or update any part.

### What it does

1. **System packages** (only with root): `languagetool`, `vale`,
   `aspell-en`, `hunspell-en`, `dictd`, `sdcv`, `gnome-dictionary`,
   `words`, `ffmpeg`, plus the AUR dictionaries `dict-freedict-eng-spa-bin`,
   `dict-freedict-spa-eng-bin`, `stardict-dictd_www.dict.org_gcide` and
   `hunspell-en-gb`

   The AUR dictionaries matter. `dictd` and `sdcv` install fine without
   them and then answer every lookup with "nothing similar to", which looks
   like a broken tool rather than a missing database. The installer checks
   that a lookup actually returns a result and tells you if it does not.

   On Arch the unit is `dictd.service`, not `dictd.socket`:

   ```bash
   sudo systemctl enable --now dictd.service
   ```

   `sdcv` needs no server at all, it reads the StarDict files directly,
   so it is usable immediately after `install.sh` with no root at all.
2. **LTeX+** from the official GitHub release, with `ltex-ls` and
   `ltex` aliases
3. **Configs** to `~/.config/ltex/` and `~/.config/vale/`
4. **Scripts** to `~/.local/bin/`
5. **Desktop entries** so Lute and the grammar checker show up in your
   application menu
6. **Shell integration** in `~/.bashrc` and `~/.zshrc`
7. **Neovim** plugin if it detects a LazyVim layout (backs up any
   existing `lua/plugins/ltex.lua` first)
8. **Lute** via `uv tool install lute3` or `pipx`
9. **Ollama** model `qwen2.5:7b` (~4.7 GB, one time)

## Usage

### Check your writing

```bash
encheck notas.md                      # a file
encheck -p "I look forward to see you" # inline
cat notas.md | encheck                # piped
encheck -q notas.md                   # compact: line:col + message
encheck --help
```

Real output:

```
prueba.md:1:39: info: In the grammatical structure
'look + forward + to + verb', the verb 'to' is used with the gerund.
[ADMIT_ENJOY_VB]
She dont have no time. I look forward to see you in Madrid.
                                      Use 'to seeing'
```

Exit code is `1` when issues are found, so it drops into scripts and CI.

The ruleset is British English (`en-GB`) with `diagnosticLevel: hint`, so
you get gentle nudges while writing rather than red walls. Edit
`config/ltex/ltex.json` to switch to `en-US`, or add your own vocabulary
to `userDictionary` so LTeX+ stops flagging your technical terms.

### Dictionary

```bash
sdcv look forward to              # GCIDE, console
dict -d eng-spa collocation      # English -> Spanish
dict -d spa-eng esperar          # Spanish -> English, to check your own
alias d='sdcv'                    # optional shorthand
```

To add a word, edit `/usr/share/dictd/local.dict` (a plain text file that
dictd reads at every start) and restart with `sudo systemctl restart dictd`.

### Style

```bash
vale notas.md
```

`config/vale/` ships a vocabulary that stops Vale flagging words like
Anki, FSRS, LTeX or Neovim, and a reject list of classic learner typos
(`teh`, `recieve`, `would of`).

### Reading

```bash
lute --local        # then open http://localhost:5001
```

From another machine on your Tailscale network:

```bash
lute-remote         # start and publish to your tailnet over HTTPS
lute-remote --status
lute-remote --stop
```

Lute has **no `--host` flag**. It either binds `127.0.0.1` (`--local`) or
`0.0.0.0` (no flag), so you cannot bind it to one interface. Running it on
`0.0.0.0` would expose it to whatever wifi you are on, and since Lute has
no authentication, anyone on that network could read and edit your
material.

`lute-remote` therefore keeps Lute on `127.0.0.1` and has the Tailscale
daemon proxy it, so it is reachable from your other devices and invisible
to every network Lute is not on. One-time setup:

```bash
# open once and click enable
https://login.tailscale.com/f/serve?node=<your-node-id>
```

After that `lute-remote` configures the proxy itself and prints the
address to open on the other machine.

Anything already joined to your tailnet can reach it. Do not add devices
you do not control.

Tap any word for a definition, read and listen at the same time, and
export the words you looked up straight to Anki. On first run set
**L1 = your native language, L2 = English**.

### Conversation and writing

```bash
enpractice "job interviews"
enpractice "describing a chart" --level C1
EN_LEVEL=C1 enpractice "academic writing"
EN_MODEL=qwen2.5-coder:7b enpractice
```

Write in English, then type `/check` to get every error grouped by type
(grammar, articles, prepositions, verb form, word choice, punctuation)
with a reason and a more natural B2 alternative. Never uses your native
language.

### Neovim

`config/nvim/ltex.lua` enables the grammar server for markdown, plain
text, LaTeX, org, rst, asciidoc and more.

| Key | Action |
|---|---|
| `<leader>ld` | hover the diagnostic under the cursor |
| `<leader>le` | send all diagnostics to the loclist |
| `<leader>gl` | jump to the next diagnostic |

The config sets `mason = false` on purpose. LazyVim otherwise hands
`ltex_plus` to mason-lspconfig, which waits for a package that does not
exist and the server never attaches.

### LanguageTool as a server

```bash
languagetool --serve      # localhost:8081
```

Then point the Obsidian *LanguageTool Integration* plugin or a browser
extension at `http://localhost:8081` to check text anywhere.

## The Anki deck

`anki/Ingles-Grammar-B1C2-EN.apkg` — 2,141 notes, 2,973 cards, B1 to C2.

- 23 chapters: verb system, tenses, modals, conditionals, passive and
  causative, verb patterns, relative clauses, clause order, noun
  phrases, determiners, adjectives, adverbs, prepositions, phrasal verbs,
  discourse markers, questions, complex sentences, reported speech
- cloze deletions, tables, example sentences with audio-style prompts
- English only, no native-language scaffolding

Import it with **File → Import**, tick **Allow HTML in fields**.

Turn on **FSRS** afterwards for much better retention. Anki 26.x stores
deck options as protobuf, so this is deliberately not scripted: enable it
in **Tools → Preferences → FSRS**, then set Desired Retention to `0.90`
in the deck options.

### Regenerating the deck

The deck is generated, not hand-written, so it is reproducible:

```bash
cd anki
python3 -m venv .venv && .venv/bin/pip install genanki
.venv/bin/python build.py deck.apkg      # rebuild from content/
.venv/bin/python lint.py deck.apkg       # check for encoding damage
.venv/bin/python preview.py deck.apkg    # HTML preview
```

Edit the chapter modules in `anki/content/` to add or change material.

## Layout

```
install.sh                 one-shot installer
install/
  install-system-packages.sh  root-only packages, run on its own if needed
config/
  ltex/ltex.json           grammar ruleset (language, rules, dictionary)
  nvim/ltex.lua            LazyVim / Neovim LSP setup
  vale/vale.ini            style config
  vale/.vale/.../English/  accept.txt, reject.txt
scripts/
  encheck                  grammar CLI wrapper
  enpractice               conversation practice with a local model
anki/
  Ingles-Grammar-B1C2-EN.apkg   the deck
  build.py                 rebuild the deck
  ankilib.py               models, CSS, cloze, GUIDs, HTML sanitising
  content/c01..c23*.py     one module per chapter
  lint.py                  encoding and text validation
  preview.py               HTML preview
  spanish_check.py         dev tool: flags leftover native-language text
```

## Troubleshooting

**Neovim shows no diagnostics.** Check the server is registered:

```bash
nvim --headless -c 'lua print(vim.inspect(vim.lsp.is_enabled("ltex_plus")))' -c q
```

If `false`, the config did not load. Make sure
`~/.config/nvim/lua/plugins/ltex.lua` exists, then restart Neovim.

**`encheck: could not analyse`.** The file must exist and be readable.
Markdown, text, LaTeX, org, rst, asciidoc and HTML are checked; other
formats are skipped.

**`ollama` says it cannot connect.** The service is not running:

```bash
systemctl --user start ollama
```

**Lute has no dictionary.** Leave it running through the first import,
it downloads language data on the first launch.

**Want American English?** In `~/.config/ltex/ltex.json` set
`"language": "en-US"` and `"dictionary": "american"`, then restart
Neovim.

## License

MIT. See [LICENSE](LICENSE).

The bundled Anki deck is original work, also MIT. The LTeX+ binary is
downloaded from its own releases and is licensed by its authors
(GPL-3.0); it is not redistributed in this repository.
