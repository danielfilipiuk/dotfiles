#!/bin/bash

# --- Check dependencies ---
if ! command -v yad &>/dev/null; then
    echo "YAD is not installed. Try: sudo apt install yad"
    exit 1
fi

if ! command -v cpupower &>/dev/null; then
    yad --error --text="xsct is not installed."
    exit 1
fi

# --- Step 1: Main mode selection ---
yad --center \
    --title="Power Mode Selector" \
    --width=240 --height=100 \
    --text="⚡  Choose power mode ⚡" \
    --button="🚀  Performance" \
    --button="⚖️   Balanced" \

case $? in
    0)  # Performance
        pkexec cpupower --cpu all frequency-set --governor performance
        exit 0
        ;;
    1)  # Balanced
        pkexec cpupower --cpu all frequency-set --governor schedutil
        exit 0
        ;;
    *)  # Cancel or close
        exit 0
        ;;
esac
