#!/bin/bash

# games folder


for d in /mnt/data/linux/*/; do dir=$(basename "$d"); 7z u -t7z -mx=9 -mmt=16 -ms=on -aou -bt "/run/media/daniel/DIETER/linux/$dir.7z" "$d"; done
