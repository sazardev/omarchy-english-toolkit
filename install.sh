#!/usr/bin/env bash
# omarchy-english-toolkit :: install.sh
# One-shot installer. Reproduces the whole stack on Arch/Omarchy (or any Arch derivative).
#
#   bash install.sh              # user-level parts only, no root needed
#   sudo bash install.sh         # everything, including system packages
#
# Everything is offline and English-only by design.

set -uo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USER_LEVEL=1
[[ ${EUID:-$(id -u)} -eq 0 ]] && USER_LEVEL=0

BOLD=$'\033[1m'; BLUE=$'\033[1;36m'; GREEN=$'\033[1;32m'
YELLOW=$'\033[1;33m'; RED=$'\033[1;31m'; OFF=$'\033[0m'

log()  { printf '\n%s==>%s %s\n' "$BLUE" "$OFF" "$*"; }
ok()   { printf '    %sOK%s   %s\n' "$GREEN" "$OFF" "$*"; }
warn() { printf '    %swarn%s %s\n' "$YELLOW" "$OFF" "$*"; }
die()  { printf '\n%serror%s %s\n' "$RED" "$OFF" "$*" >&2; exit 1; }

DEST_LTEX="$HOME/.local/opt/ltex"
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}"
BIN_DIR="$HOME/.local/bin"
LTEX_VERSION="18.7.0"
LTEX_BIN="$DEST_LTEX/ltex-ls-plus-$LTEX_VERSION/bin/ltex-ls-plus"

printf '%s\n' "$BOLD"
cat <<'BANNER'
  omarchy-english-toolkit
  Offline English learning stack for Arch / Omarchy
  grammar + dictionary + reading + speaking, 100% local
BANNER
printf '%s\n' "$OFF"

# ============================================================ 1. system packages
install_system_packages() {
  log "System packages (needs root)"

  local PKGS=(
    languagetool vale          # grammar engine + prose linter
    aspell-en hunspell-en      # English spell dictionaries
    dictd sdcv                 # DICT protocol server + console client
    gnome-dictionary          # dictionary GUI
    words ffmpeg              # word list + audio for shadowing
  )

  for p in "${PKGS[@]}"; do
    if pacman -Qi "$p" >/dev/null 2>&1; then
      ok "$p already installed"
    else
      printf '    installing %s\n' "$p"
      pacman -S --needed --noconfirm "$p" || warn "could not install $p"
    fi
  done

  # AUR dictionaries. Without these, `dictd` and `sdcv` are installed but
  # empty. dict-gcide does not exist on Arch; these are the working ones.
  #   eng-spa : English -> Spanish, for reading English
  #   spa-eng : Spanish -> English, for checking your own translations
  #   gcide   : GCIDE, a large English-only dictionary for definitions
  if command -v yay >/dev/null 2>&1; then
    local AUR=(
      dict-freedict-eng-spa-bin
      dict-freedict-spa-eng-bin
      stardict-dictd_www.dict.org_gcide
      hunspell-en-gb
    )
    for p in "${AUR[@]}"; do
      if pacman -Qi "$p" >/dev/null 2>&1; then
        ok "$p already installed"
      else
        printf '    installing AUR: %s\n' "$p"
        yay -S --needed --noconfirm "$p" || warn "AUR install failed: $p"
      fi
    done
  else
    warn "yay not found - skipping the dictionaries (dictd/sdcv will be empty)"
  fi

  log "Dictionary server"
  # Arch ships dictd.service, not dictd.socket. Starting a unit that does
  # not exist fails with "could not be found", which looks like a broken
  # install rather than a wrong unit name.
  if systemctl list-unit-files dictd.service >/dev/null 2>&1; then
    systemctl enable --now dictd.service 2>/dev/null \
      && ok "dictd.service enabled" \
      || warn "could not enable dictd.service"
  elif [[ -f /usr/lib/systemd/system/dictd.service ]]; then
    systemctl enable --now dictd.service 2>/dev/null \
      && ok "dictd.service enabled" \
      || warn "could not enable dictd.service"
  else
    warn "dictd not installed - skipping"
  fi
}

# A dictionary that answers is the only thing that counts. `dictd` and
# `sdcv` can both be installed and still be completely empty.
verify_dictionary() {
  log "Dictionary content"
  if command -v dict >/dev/null 2>&1; then
    local n
    n=$(dict -h 2>/dev/null | sed -n 's/^ *\([0-9]*\) dictionaries defined.*/\1/p' | head -1)
    if [[ -n ${n:-} && $n -gt 0 ]]; then
      ok "dict: $n dictionaries available"
    else
      warn "dictd has no database. Install dict-freedict-eng-spa-bin"
    fi
  fi
  if command -v sdcv >/dev/null 2>&1; then
    if sdcv collocation 2>/dev/null | grep -qiE 'collocat|group|arrange'; then
      ok "sdcv: lookup works"
    else
      warn "sdcv has no dictionaries. Install stardict-dictd_www.dict.org_gcide"
    fi
  fi
}

# ============================================================ 2. LTeX+
install_ltex() {
  log "LTeX+ $LTEX_VERSION (offline grammar engine)"

  local arch tarball url
  case "$(uname -m)" in
    x86_64)  arch="x64" ;;
    aarch64) arch="aarch64" ;;
    *) die "unsupported architecture: $(uname -m)" ;;
  esac
  tarball="ltex-ls-plus-$LTEX_VERSION-linux-$arch.tar.gz"
  url="https://github.com/ltex-plus/ltex-ls-plus/releases/latest/download/$tarball"

  if [[ -x "$LTEX_BIN" ]]; then
    ok "already installed at $LTEX_BIN"
    return
  fi

  mkdir -p "$DEST_LTEX"
  printf '    downloading %s\n' "$tarball"
  if ! curl -fL --progress-bar -o "$DEST_LTEX/ltex.tar.gz" "$url"; then
    die "download failed: $url"
  fi
  tar xzf "$DEST_LTEX/ltex.tar.gz" -C "$DEST_LTEX"
  rm -f "$DEST_LTEX/ltex.tar.gz"

  chmod +x "$DEST_LTEX/ltex-ls-plus-$LTEX_VERSION/bin/"* 2>/dev/null
  # convenience aliases so both `ltex-ls` and `ltex` work
  local bd="$DEST_LTEX/ltex-ls-plus-$LTEX_VERSION/bin"
  [[ -e "$bd/ltex-ls"   ]] || ln -sf ltex-ls-plus "$bd/ltex-ls"
  [[ -e "$bd/ltex"      ]] || ln -sf ltex-cli-plus "$bd/ltex"

  [[ -x "$LTEX_BIN" ]] && ok "installed at $LTEX_BIN" || die "binary missing after extract"
}

# ============================================================ 3. config files
install_configs() {
  log "Configuration files"

  mkdir -p "$CONFIG_DIR/ltex"
  cp "$REPO_DIR/config/ltex/ltex.json" "$CONFIG_DIR/ltex/ltex.json"
  ok "$CONFIG_DIR/ltex/ltex.json"

  mkdir -p "$CONFIG_DIR/vale/.vale/styles/config/vocabularies/English"
  cp "$REPO_DIR/config/vale/vale.ini" "$CONFIG_DIR/vale/vale.ini"
  cp "$REPO_DIR/config/vale/.vale/styles/config/vocabularies/English/"*.txt \
     "$CONFIG_DIR/vale/.vale/styles/config/vocabularies/English/"
  ok "$CONFIG_DIR/vale/ (vale.ini + English vocabulary)"
}

# ============================================================ 4. scripts
install_scripts() {
  log "Command line tools"
  mkdir -p "$BIN_DIR"
  for s in encheck enpractice; do
    cp "$REPO_DIR/scripts/$s" "$BIN_DIR/$s"
    chmod +x "$BIN_DIR/$s"
    ok "$BIN_DIR/$s"
  done
}

# ============================================================ 5. desktop entries
install_desktop_entries() {
  log "Application menu entries"
  local apps="$HOME/.local/share/applications"
  mkdir -p "$apps"

  local lute_bin
  lute_bin="$(command -v lute 2>/dev/null || true)"
  if [[ -z $lute_bin ]]; then
    lute_bin="$HOME/.local/share/uv/tools/lute3/bin/lute"
  fi

  if [[ -x $lute_bin ]]; then
    cat > "$apps/lute.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Lute
GenericName=Language Reader
Comment=Learn languages by reading - built-in dictionary, TTS and Anki export
Exec=$lute_bin --local
Icon=accessories-dictionary
Terminal=false
Categories=Education;Languages;Literature;
Keywords=english;learning;reading;dictionary;
StartupNotify=true
EOF
    ok "lute.desktop"
  else
    warn "lute not installed - skipping its menu entry (run: uv tool install lute3)"
  fi

  local bd="$DEST_LTEX/ltex-ls-plus-$LTEX_VERSION/bin"
  if [[ -x "$bd/ltex-cli-plus" ]]; then
    cat > "$apps/ltex-plus.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Grammar Check (LTeX+)
GenericName=Spelling and Grammar Checker
Comment=Check the spelling and grammar of a text file with LanguageTool, fully offline
Exec=$bd/ltex-cli-plus --client-configuration $CONFIG_DIR/ltex/ltex.json %F
Icon=accessories-dictionary
Terminal=true
Categories=Education;Languages;Utility;
Keywords=grammar;spelling;english;languagetool;ltex;
MimeType=text/plain;text/markdown;
EOF
    ok "ltex-plus.desktop"
  fi
}

# ============================================================ 6. shell rc
install_shell_rc() {
  log "Shell integration"

  local rc
  for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
    # only .bashrc is created on demand: a missing .zshrc usually means zsh
    # is not the login shell and creating it would be noise.
    if [[ ! -f $rc ]]; then
      [[ $rc == */.bashrc ]] || continue
      touch "$rc"
    fi
    if grep -q 'ltex-ls-plus' "$rc" 2>/dev/null; then
      continue
    fi
    {
      printf '\n# ---- omarchy-english-toolkit ----\n'
      printf 'export PATH="%s/ltex-ls-plus-%s/bin:%s:$PATH"\n' "$DEST_LTEX" "$LTEX_VERSION" "$BIN_DIR"
      printf "alias lt='ltex --client-configuration %s/ltex/ltex.json'\n" "$CONFIG_DIR"
    } >> "$rc"
    ok "updated $rc"
  done
}

# ============================================================ 7. nvim
install_nvim() {
  log "Neovim / LazyVim integration"

  if [[ ! -d "$HOME/.config/nvim" ]]; then
    warn "no Neovim config found - skipping (see config/nvim/ltex.lua to copy manually)"
    return
  fi
  if [[ ! -d "$HOME/.config/nvim/lua/plugins" ]]; then
    warn "not a LazyVim layout - skipping"
    return
  fi

  local dest="$HOME/.config/nvim/lua/plugins/ltex.lua"
  if [[ -f $dest ]]; then
    cp "$dest" "$dest.bak"
    warn "existing $dest backed up to $dest.bak"
  fi
  cp "$REPO_DIR/config/nvim/ltex.lua" "$dest"
  ok "$dest"
}

# ============================================================ 8. ollama
install_ollama() {
  log "Local AI for conversation practice"

  if ! command -v ollama >/dev/null 2>&1; then
    warn "ollama not installed - skipping (https://ollama.com)"
    return
  fi

  if ! ollama list 2>/dev/null | awk 'NR>1{print $1}' | grep -qx 'qwen2.5:7b'; then
    printf '    pulling qwen2.5:7b (about 4.7 GB, one time)\n'
    (systemctl --user start ollama 2>/dev/null || true)
    sleep 3
    ollama pull qwen2.5:7b && ok "qwen2.5:7b ready" || warn "pull failed - retry later with: ollama pull qwen2.5:7b"
  else
    ok "qwen2.5:7b already present"
  fi
}

# ============================================================ 9. lute
install_lute() {
  log "Lute (reader with built-in dictionary, TTS and Anki export)"

  if command -v lute >/dev/null 2>&1; then
    ok "already installed"
    return
  fi
  if command -v uv >/dev/null 2>&1; then
    uv tool install lute3 && ok "lute installed via uv" || warn "lute install failed"
  elif command -v pipx >/dev/null 2>&1; then
    pipx install lute3 && ok "lute installed via pipx" || warn "lute install failed"
  else
    warn "neither uv nor pipx found - install manually: pipx install lute3"
  fi
}

# ============================================================ verify
verify() {
  log "Verification"

  local fail=0
  printf '    %-34s %s\n' "ltex (grammar CLI)" \
    "$([[ -x $DEST_LTEX/ltex-ls-plus-$LTEX_VERSION/bin/ltex-cli-plus ]] && echo OK || { echo MISSING; fail=1; })"
  printf '    %-34s %s\n' "encheck" \
    "$([[ -x $BIN_DIR/encheck ]] && echo OK || { echo MISSING; fail=1; })"
  printf '    %-34s %s\n' "enpractice" \
    "$([[ -x $BIN_DIR/enpractice ]] && echo OK || { echo MISSING; fail=1; })"
  printf '    %-34s %s\n' "ltex.json config" \
    "$([[ -f $CONFIG_DIR/ltex/ltex.json ]] && echo OK || { echo MISSING; fail=1; })"
  for b in languagetool vale sdcv dict aspell; do
    printf '    %-34s %s\n' "$b" \
      "$(command -v $b >/dev/null 2>&1 && echo OK || echo "not installed (needs root)")"
  done
  printf '    %-34s %s\n' "lute" \
    "$(command -v lute >/dev/null 2>&1 && echo OK || echo "not installed")"

  echo
  if [[ $fail -eq 0 ]]; then
    printf '%s==> Core stack ready.%s\n' "$GREEN" "$OFF"
  else
    printf '%s==> Some user-level parts failed. Check the output above.%s\n' "$YELLOW" "$OFF"
  fi

  verify_dictionary

  cat <<'EOF'

------------------------------------------------------------------------
 Quick start
------------------------------------------------------------------------

  source ~/.bashrc

  # check any text (file, inline or piped) - fully offline
  encheck notas.md
  encheck -p "I look forward to see you"
  cat notas.md | encheck
  encheck -q notas.md            # compact output

  # terminal dictionary
  sdcv look forward to
  dict -d en_eng collocation

  # style linter
  vale notas.md

  # reading with built-in dictionary + TTS
  lute --local                   # then open http://localhost:5001

  # conversation and writing practice with a local model
  enpractice "job interviews"
  EN_LEVEL=C1 enpractice "academic writing"

  # Neovim: checks automatically while you type
  #   <leader>ld  hover diagnostic
  #   <leader>le  diagnostics into loclist
  #   <leader>gl  jump to next diagnostic

  # LanguageTool as a local server, for Obsidian / browser / scripts
  languagetool --serve           # localhost:8081

------------------------------------------------------------------------
 Anki: enable FSRS (one time, in the GUI)
------------------------------------------------------------------------

  Anki 26.x stores deck options as protobuf, so this is not scripted.

  1. Anki > Tools > Preferences > FSRS > enable
  2. Deck Options > FSRS > Desired Retention 0.90 > Save
  3. After ~2000 honest reviews, press Optimize in the same tab

  The bundled deck: anki/Ingles-Grammar-B1C2-EN.apkg
  Import it with File > Import, enable "Allow HTML in fields".
------------------------------------------------------------------------
EOF
}

# ==================================================================== main
main() {
  if [[ $USER_LEVEL -eq 0 ]]; then
    export HOME_ORIG="$HOME"
    [[ -z ${SUDO_USER:-} ]] || export HOME="/home/$SUDO_USER"
    install_system_packages
    verify_dictionary
  else
    log "Skipping system packages (no root)"
    warn "run: sudo bash install.sh   to add languagetool, vale, sdcv, dictd"
  fi

  install_ltex
  install_configs
  install_scripts
  install_desktop_entries
  install_shell_rc
  install_nvim
  install_lute
  install_ollama
  verify
}

main "$@"
