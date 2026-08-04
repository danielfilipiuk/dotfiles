#!/bin/bash

# --- Check dependencies ---
if ! command -v yad &>/dev/null; then
    echo "YAD is not installed. Try: sudo apt install yad"
    exit 1
fi

if ! command -v xsct &>/dev/null; then
    yad --error --text="xsct is not installed."
    exit 1
fi

# --- Step 1: Main mode selection ---
yad --center \
    --title="Day / Night color temperature selector" \
    --width=320 --height=50 \
    --text="🌗 Choose screen mode:" \
    --button="🌞 Day Mode!weather-clear:0" \
    --button="🌙 Night Mode!weather-clear-night:1" \
    --button="⚙️ Advanced...!preferences-system:2"

case $? in
    0)  # Day Mode
        xsct 6500 1.0
        exit 0
        ;;
    1)  # Night Mode
        xsct 5500 0.9
        exit 0
        ;;
    2)  # Advanced Selection
        # Fall through to advanced dialog
        ;;
    *)  # Cancel or close
        exit 0
        ;;
esac

# --- Step 2: Advanced combo selection ---
response=$(yad --center \
    --title="Advanced Screen Tuning" \
    --form \
    --separator="|" \
    --width=400 --height=180 \
    --text="Fine-tune color temperature and brightness:" \
    --field="Color Temp (K):CB" "6500!5500!4500" \
    --field="Brightness:CB" "1.0!0.9!0.8!0.7!0.6!0.5!0.4!0.3!0.2!0.1!0.0")

[ $? -ne 0 ] && exit 0

# --- Parse and apply advanced values ---
IFS='|' read -r temp bright <<< "$response"
xsct "$temp" "$bright"
