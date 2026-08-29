#!/usr/bin/env bash

# FAST keypresses are NOT detected, and same status is notified-.

# delay for hyprland to detect the status change and not only the key press.
sleep 0.25
	
# numlock needs to check NO state, because all "keyboard" devices generated shows YES already, so the real change is reflected in main-no
	
if hyprctl devices | grep -A10 "Keyboard at " | grep -q "numLock: no"; then

notify-send "     NumLock OFF" -i /home/daniel/icons/hicolor/scalable/status/numlock-off-status.svg -e -h string:x-canonical-private-synchronous:numlock && pw-play /home/daniel/sounds/soft-stop.oga

    
else
    
        notify-send "1-2-3 Num_Lock ON" -i /home/daniel/icons/hicolor/scalable/status/numlock-on-status.svg -e -h string:x-canonical-private-synchronous:numlock && pw-play /home/daniel/sounds/soft-start.oga
        
fi
