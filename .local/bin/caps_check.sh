#!/usr/bin/env bash

# delay for hyprland to detect the status change and not only the key press.
sleep 0.25

if hyprctl devices | grep -A10 "Keyboard at 55e73b5c3c20" | grep -q "capsLock: yes"; then

    notify-send "A-B-C ON Caps Lock" -i /home/daniel/icons/hicolor/scalable/status/capslock-on-status.svg && pw-play /home/daniel/sounds/soft_start.wav
else
    notify-send "a-b-c OFF Caps Lock" -i /home/daniel/icons/hicolor/scalable/status/capslock-off-status.svg && pw-play /home/daniel/sounds/soft_stop.wav
fi
