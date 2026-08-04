#!/bin/bash

# -- Check if xsct is installed --
#if ! command -v xsct &>/dev/null; then
#    zenity --error --text="xsct not installed"
#    exit 1
#fi

# -- Show emoji-only choice --
choice=$(zenity --list \
    --title="Choose Mode" \
    --text="🌗 Pick screen mode:" \
    --radiolist \
    --column="Select" --column="Mode" \
    TRUE "🌞 Day Mode" FALSE "🌙 Night Mode")

# -- Handle choice --
if [[ "$choice" == "🌞 Day Mode" ]]; then
    xsct 6500 1.0
elif [[ "$choice" == "🌙 Night Mode" ]]; then
    xsct 5500 0.9
fi
