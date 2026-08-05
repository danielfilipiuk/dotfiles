#!/bin/bash

# DOS 

for d in /mnt/data/DOS/*/; do dir=$(basename "$d"); perf stat -d 7z u -t7z -mx=9 -mmt=16 -ms=on -aou -bt "/run/media/daniel/DIETER/DOS/$dir.7z" "$d"; done
