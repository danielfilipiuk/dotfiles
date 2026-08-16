#!/usr/bin/env bash

# Check if any files were passed
if [ "$#" -eq 0 ]; then
    zenity --error --text="No files selected!" --title="Error"
    exit 1
fi

# 1. Ask for the threshold percentage using a visual slider window
THRESHOLD=$(zenity --scale --title="Vectorize PNG/JPG" \
    --text="Select the ImageMagick Threshold percentage:" \
    --value=45 --min-value=1 --max-value=100 --step=1)

# Exit if user hits Cancel
if [ -z "$THRESHOLD" ]; then
    exit 0
fi

# 2. Loop through all files passed from Thunar
for file in "$@"; do
    # Only process if file exists
    if [ -f "$file" ]; then
        # Create output name replacing old extension with .svg
        output_file="${file%.*}.svg"
        
        # Execute the conversion pipeline
        magick "$file" -threshold "${THRESHOLD}%" pbm:- | potrace -s -o "$output_file"
    fi
done

# 3. Success Notification
zenity --info --text="Successfully vectorized $(( $# )) file(s) at ${THRESHOLD}% threshold!" --title="Done"
