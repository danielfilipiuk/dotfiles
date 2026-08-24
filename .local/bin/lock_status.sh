#!/usr/bin/env bash

DEVICE="55e73b5c3c20"

case "$1" in
    caps)
        STATE=$(hyprctl devices | awk -v dev="$DEVICE" '
            $0 ~ "Keyboard at " dev {
                found=1
                next
            }
            found && /capsLock:/ {
                print $2
                exit
            }
        ')

        [[ "$STATE" == "yes" ]] && \
            notify-send "CapsLock is ACTIVE" || \
            notify-send "CapsLock is INACTIVE"
        ;;

    num)
        STATE=$(hyprctl devices | awk -v dev="$DEVICE" '
            $0 ~ "Keyboard at " dev {
                found=1
                next
            }
            found && /numLock:/ {
                print $2
                exit
            }
        ')

        [[ "$STATE" == "yes" ]] && \
            notify-send "NumLock is ACTIVE" || \
            notify-send "NumLock is INACTIVE"
        ;;

    *)
        echo "Usage: $0 {caps|num}"
        exit 1
        ;;
esac
