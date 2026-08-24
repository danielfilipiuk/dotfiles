#!/usr/bin/env bash

# delay for hyprland to detect the status change and not only the key press.
sleep 0.25
	
if hyprctl devices | grep -A10 "Keyboard at 55e73b5c3c20" | grep -q "numLock: yes"; then

    notify-send "1-2-3 Num_Lock ON" -i /home/daniel/icons/hicolor/scalable/status/numlock-on-status.svg && pw-play /home/daniel/sounds/soft_start.wav
else
    notify-send "⬆️⬇️⬅️➡️ NumLock OFF" -i /home/daniel/icons/hicolor/scalable/status/numlock-off-status.svg && pw-play /home/daniel/sounds/soft_stop.wav
fi
