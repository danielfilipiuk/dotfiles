#!/bin/bash

FONT_DIRS=(
    "/usr/share/fonts/opentype/noto"
    "/usr/share/fonts/truetype/noto"
)

KEEP_PATTERNS=(
#    "NotoMono-*"
#    "NotoSans-*"
#    "NotoSansDisplay-*"
#    "NotoSansLinearB-*"
#    "NotoSansMono-*"
#    "NotoSansSymbols*"
#    "NotoSansMath-*"
#    "NotoSerif-*"
#    "NotoSerifDisplay-*"
#    "NotoEmoji-*"
#    "NotoColorEmoji*"
#    "NotoMusic*"
	"NotoMono*"
	"NotoMusic*"
	"NotoSans-*"
	"NotoSansDisplay*"
	"NotoSansGothic*"
	"NotoSansLinear*"
	"NotoSansMath*"
	"NotoSansMono*"
	"NotoSansRunic*"
#	"NotoSansSign*"
	"NotoSansSymbols*"
	"NotoSerif-*"
	"NotoSerifDisplay-*"
	"NotoColorEmoji*"
	"NotoEmoji*"
	"NotoSansCJK*"
	"NotoSerifCJK*"
)

for dir in "${FONT_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "Processing directory: $dir"
        for file in "$dir"/*; do
            keep=false
            for pattern in "${KEEP_PATTERNS[@]}"; do
                if [[ $(basename "$file") == $pattern ]]; then
                    keep=true
                    break
                fi
            done
            if ! $keep; then
                echo "Removing: $file"
                rm -f "$file"
            fi
        done
    else
        echo "Directory not found: $dir"
    fi
done
