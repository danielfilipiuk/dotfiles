#!/bin/bash

# --- Check dependencies ---
if ! command -v zenity &>/dev/null; then
    echo "Error: 'zenity' is not installed. Install it with: sudo apt install zenity"
    exit 1
fi

if ! command -v xsct &>/dev/null; then
    echo "Error: 'xsct' is not installed."
    exit 1
fi

# --- Show Zenity form with 2 combo fields ---
response=$(zenity --forms \
    --title="Screen Tuner" \
    --text="Choose color temperature and brightness" \
    --separator="|" \
    --add-combo="Color Temperature (K)" \
        --combo-values="6500|5500|4500" \
    --add-combo="Brightness" \
        --combo-values="1.0|0.9|0.8|0.7|0.6|0.5|0.4|0.3|0.2|0.1|0.0")

# --- Cancel check ---
[ $? -ne 0 ] && exit 0

# --- Parse values ---
temp=$(echo "$response" | cut -d"|" -f1)
brightness=$(echo "$response" | cut -d"|" -f2)

# --- Apply settings ---
xsct "$temp" "$brightness"

