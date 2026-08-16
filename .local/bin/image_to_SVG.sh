#!/bin/bash
for file in *.{png,jpg,jpeg}; do
    [ -e "$file" ] || continue
    magick "$file" -threshold 45% pbm:- | potrace -s -o "${file%.*}.svg"
done
