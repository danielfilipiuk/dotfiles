#!/usr/bin/env bash
#
# kbd-state.sh — instant, event-driven Caps Lock / Num Lock reporter
# for Hyprland + Waybar.
#
# Why this exists: Waybar's built-in "keyboard-state" module polls
# libinput/evdev on a timer, so toggles get missed or lag. This script
# is instead triggered directly by a Hyprland keybind the moment the
# key is pressed, reads the live state from `hyprctl devices -j`
# (no device polling), fires a notification, writes a small state
# file for Waybar, and signals Waybar to redraw immediately.
#
# Usage:
#   kbd-state.sh caps [init]
#   kbd-state.sh num  [init]
#
# The optional "init" second argument suppresses the notification —
# use it for the exec-once startup call so you don't get a popup on login.
#
# --- Wire it up ---
#
# 1) hyprland.conf:
#
#    bindl = , Caps_Lock, exec, ~/.config/hypr/scripts/kbd-state.sh caps
#    bindl = , Num_Lock,  exec, ~/.config/hypr/scripts/kbd-state.sh num
#
#    exec-once = ~/.config/hypr/scripts/kbd-state.sh caps init
#    exec-once = ~/.config/hypr/scripts/kbd-state.sh num init
#
#    (bindl = "l" flag = also fires while a screen lock/inhibitor is
#    active, so you still get feedback with hyprlock up.)
#
# 2) waybar config.jsonc — see waybar-keyboard-state.jsonc
# 3) waybar style.css     — see waybar-keyboard-state.css

set -euo pipefail

MODE="${1:-}"
INIT="${2:-}"

if [[ "$MODE" != "caps" && "$MODE" != "num" ]]; then
    echo "Usage: $0 caps|num [init]" >&2
    exit 1
fi

LOCKFILE="/tmp/kbd-state-${MODE}.lock"
STATE_FILE="$HOME/.cache/waybar-kbd-${MODE}.json"
WAYBAR_SIGNAL=8   # must match "signal" in the waybar module config

# Drop overlapping runs instead of queueing (e.g. key held / auto-repeat).
exec 9>"$LOCKFILE"
flock -n 9 || exit 0

# Live state straight from the compositor — no evdev polling.
DEVICES_JSON="$(hyprctl devices -j)"

case "$MODE" in
  caps)
    FIELD="capsLock"
    LABEL="Caps Lock"
    GLYPH_ON=$'\uf023 CAPS'    #  (locked)
    GLYPH_OFF=$'\uf09c CAPS'   #  (unlocked)
    ;;
  num)
    FIELD="numLock"
    LABEL="Num Lock"
    GLYPH_ON=$'\uf023 NUM'
    GLYPH_OFF=$'\uf09c NUM'
    ;;
esac

# Check ALL reported keyboards, not just the one flagged "main" — on some
# setups "main" is missing or points at a virtual/duplicate device that
# never reflects the real toggle, which made the module look permanently stuck.
STATE="$(jq -r --arg f "$FIELD" '[.keyboards[]?[$f]] | any' <<<"$DEVICES_JSON")"

if [[ "$STATE" == "true" ]]; then
  STATUS_TEXT="active"
  CLASS="active"
  ICON="changes-prevent-symbolic"   # standard freedesktop "locked" icon
  GLYPH="$GLYPH_ON"
else
  STATUS_TEXT="not active"
  CLASS="inactive"
  ICON="changes-allow-symbolic"     # standard freedesktop "unlocked" icon
  GLYPH="$GLYPH_OFF"
fi

if [[ "$INIT" != "init" ]]; then
  notify-send -a "Keyboard" -i "$ICON" -u low -t 1500 \
    -h string:x-canonical-private-synchronous:"kbd-$MODE" \
    "Keyboard" "$LABEL: $STATUS_TEXT" || true
fi

# IMPORTANT: -c (compact) is required. Waybar reads custom-module JSON
# one line at a time; pretty-printed multi-line output only ever shows
# it the opening "{" and it fails to parse.
mkdir -p "$(dirname "$STATE_FILE")"
TMP_FILE="${STATE_FILE}.tmp.$$"
jq -nc --arg text "$GLYPH" --arg class "$CLASS" \
       --arg tooltip "$LABEL: $STATUS_TEXT" \
       '{text: $text, class: $class, tooltip: $tooltip}' > "$TMP_FILE"
mv "$TMP_FILE" "$STATE_FILE"

pkill -RTMIN+"$WAYBAR_SIGNAL" waybar 2>/dev/null || true
