#!/usr/bin/env bash

set -euo pipefail

readonly VERSION="v2.0.1"

readonly -a THEMES=(
  "macOS|macOS|#000000|#FFFFFF"
  "macOS-White|White macOS|#FFFFFF|#000000"
  "macOS-Catppuccin-Latte-Dark|Catppuccin Latte Dark|#eff1f5|#8839ef"
  "macOS-Catppuccin-Latte|Catppuccin Latte|#8839ef|#eff1f5"
  "macOS-Catppuccin-Frappe-Dark|Catppuccin Frappe Dark|#303446|#ca9ee6"
  "macOS-Catppuccin-Frappe|Catppuccin Frappe|#ca9ee6|#303446"
  "macOS-Catppuccin-Macchiato-Dark|Catppuccin Macchiato Dark|#24273a|#c6a0f6"
  "macOS-Catppuccin-Macchiato|Catppuccin Macchiato|#c6a0f6|#24273a"
  "macOS-Catppuccin-Mocha-Dark|Catppuccin Mocha Dark|#1e1e2e|#cba6f7"
  "macOS-Catppuccin-Mocha|Catppuccin Mocha|#cba6f7|#1e1e2e"
)

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    printf 'Required command not found: %s\n' "$1" >&2
    exit 127
  fi
}

require_command npx
require_command ctgen
require_command python3
require_command tar

rm -rf bin bitmaps themes
mkdir -p bin

for theme in "${THEMES[@]}"; do
  IFS='|' read -r name comment base_color outline_color <<< "$theme"

  npx --no-install cbmp \
    -d svg \
    -o "bitmaps/$name" \
    -bc "$base_color" \
    -oc "$outline_color"

  ctgen build.toml \
    -p x11 \
    -d "bitmaps/$name" \
    -n "$name" \
    -c "$comment ($VERSION) XCursors"

  python3 build_svg_theme.py \
    --config build.toml \
    --svg-dir svg \
    --output-dir "themes/$name/cursors_scalable" \
    --base-color "$base_color" \
    --outline-color "$outline_color" \
    --canvas-size 32 \
    --nominal-size 24

  tar -C themes -cJf "bin/$name.tar.xz" "$name"
done
