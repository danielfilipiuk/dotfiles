#!/bin/bash

# --- Check dependencies ---
if ! command -v yad &>/dev/null; then
    echo "Error: 'yad' is not installed. Install it with: sudo apt install yad"
    exit 1
fi

if ! command -v xsct &>/dev/null; then
    echo "Error: 'xsct' is not installed."
    exit 1
fi

# --- Show GUI with dropdowns only ---
result=$(yad --form \
    --title="Screen Color & Brightness" \
    --center \
    --width=300 \
    --height=200 \
    --separator="|" \
    --field="Color Temp (K):CB" "6500!5500!4500" \
    --field="Brightness:CB" "1.0!0.9!0.8!0.7!0.6!0.5!0.4!0.3!0.2!0.1!0.0" \
    --button=OK:0 --button=Cancel:1)

# --- Cancel check ---
if [ $? -ne 0 ]; then
    exit 0
fi

# --- Parse values ---
temp=$(echo "$result" | cut -d"|" -f1)
brightness=$(echo "$result" | cut -d"|" -f2)

# --- Apply settings ---
xsct "$temp" "$brightness"
