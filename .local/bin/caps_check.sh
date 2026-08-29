#!/usr/bin/env bash

# FAST keypresses are NOT detected, and same status is notified-.

# delay for hyprland to detect the status change and not only the key press. 
sleep 0.25

# caps lock is the only state that change to YES in all keyboard devices generated, thus that value is searched. 

if hyprctl devices | grep -A10 "Keyboard at " | grep -q "capsLock: yes"; then

    notify-send "A-B-C ON Caps Lock" -i /home/daniel/icons/hicolor/scalable/status/capslock-on-status.svg -e -h string:x-canonical-private-synchronous:capslock && pw-play /home/daniel/sounds/soft-start.oga
else
    notify-send "a-b-c OFF Caps Lock" -i /home/daniel/icons/hicolor/scalable/status/capslock-off-status.svg -e -h string:x-canonical-private-synchronous:capslock && pw-play /home/daniel/sounds/soft-stop.oga
fi
