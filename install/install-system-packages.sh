#!/usr/bin/env bash
# english-stack-install
# Instala el resto del stack de inglés que necesita privilegios de root.
# Ejecutar UNA vez:  bash ~/.local/share/english-stack/install-sudo.sh
#
# Idioma de salida: inglés (tu requisito: nada de español en las herramientas)

set -uo pipefail

log()  { printf '\n\033[1;36m==> %s\033[0m\n' "$*"; }
warn() { printf '\033[1;33m[warn]\033[0m %s\n' "$*"; }
die()  { printf '\033[1;31m[error]\033[0m %s\n' "$*" >&2; exit 1; }

[[ $EUID -eq 0 ]] || die "Run with sudo:  sudo bash $0"

printf '\033[1;36m%s\033[0m\n' "English learning stack - system packages"
printf '%s\n' "Installing: languagetool, vale, dictionaries and spell checkers."

# ---------------------------------------------------------------- 1. packages
log "Syncing package databases"
pacman -Sy --noconfirm || die "pacman -Sy failed"

PKGS=(
  languagetool      # LanguageTool: GUI + --serve (offline grammar engine)
  vale              # prose linter (style, not grammar)
  aspell-en         # English aspell dictionary
  dictd             # dictionary server
  dict-gcide        # Cambridge dictionary for dictd
  sdcv             # StarDict console dictionary (TUI)
  gnome-dictionary  # GNOME dictionary GUI
  words             # /usr/share/dict/words
)

log "Installing from the official repositories"
for p in "${PKGS[@]}"; do
  if pacman -Qi "$p" >/dev/null 2>&1; then
    printf '    already installed: %s\n' "$p"
  else
    printf '    installing: %s\n' "$p"
    pacman -S --needed --noconfirm "$p" || warn "failed to install $p"
  fi
done

# AUR packages (yay) - optional, skipped automatically if unavailable
if command -v yay >/dev/null 2>&1; then
  log "Installing AUR packages"
  for p in hunspell-en hunspell-en-gb; do
    yay -S --needed --noconfirm "$p" || warn "AUR install failed: $p"
  done
else
  warn "yay not found - skipping hunspell dictionaries"
fi

# ------------------------------------------------------------- 2. dictionaries
log "Building the dictd database"
if command -v dictd >/dev/null 2>&1; then
  if [[ -f /var/lib/dictd/dictd.db || -f /usr/share/dictd/dictd.db ]]; then
    echo "    dictd database already present"
  else
    systemctl enable --now dictd.socket 2>/dev/null || true
    dictd -c /dev/null 2>/dev/null || true
  fi
  systemctl enable --now dictd.socket 2>/dev/null \
    && echo "    dictd.socket enabled" \
    || warn "could not enable dictd.socket"
else
  warn "dictd not installed - skipping"
fi

# ------------------------------------------------------------- 3. languages
log "Setting the default system locale helpers"
# LanguageTool needs a UTF-8 locale; ensure one is generated and current.
if ! locale -a 2>/dev/null | grep -qiE 'en_US\.utf-?8'; then
  sed -i 's/^#\(en_US.UTF-8\)/\1/' /etc/locale.gen 2>/dev/null || true
  locale-gen en_US.UTF-8 2>/dev/null || warn "could not generate en_US.UTF-8"
else
  echo "    en_US.UTF-8 locale present"
fi

# ---------------------------------------------------------------- 4. verify
log "Verification"
for b in languagetool languagetool-server vale aspell dict sdcv gnome-dictionary; do
  if command -v "$b" >/dev/null 2>&1; then
    printf '    OK   %s  (%s)\n' "$b" "$(command -v "$b")"
  else
    printf '    MISS %s\n' "$b"
  fi
done

printf '\n\033[1;32m==> Done.\033[0m\n'
cat <<'EOF'

Next steps:

  1. Open a NEW terminal (or run: source ~/.bashrc) so PATH is refreshed.

  2. Test the grammar checker (offline, works in any terminal):
         encheck -p "She dont have no time. I look forward to see you."

  3. Test the terminal dictionary:
         sdcv look forward to
         dict -d en_eng collocation

  4. Test the style linter on a file:
         vale notas.md

  5. Optional: run LanguageTool as a local server so Obsidian, the
     browser extension or scripts can use it:
         languagetool --serve            # listens on localhost:8081

  6. FSRS in Anki (3 clicks, one time):
     open Anki -> Tools -> Preferences -> FSRS -> enable
     then: Deck Options -> FSRS -> Desired Retention 0.90 -> Save
     (needs ~2000 honest reviews before you "Optimize" the parameters)

  7. Lute is already installed and needs no root:
         lute --local        # then open http://localhost:5001
EOF
