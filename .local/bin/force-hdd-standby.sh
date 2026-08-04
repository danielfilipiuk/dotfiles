#!/bin/bash

DRIVES=(sda sdb sdc sdd)

for DEV in "${DRIVES[@]}"; do
    DEVPATH="/dev/$DEV"

    # --- Check current power state ---
    STATE=$(hdparm -C "$DEVPATH" 2>/dev/null | awk '/state/ {print $4}')

    if [[ "$STATE" == "standby" || "$STATE" == "sleeping" ]]; then
        echo "$DEVPATH already in standby, skipping."
        continue
    fi

    # --- Check if mounted ---
    if mount | grep -q "^$DEVPATH"; then
        echo "$DEVPATH is mounted, skipping standby."
        continue
    fi

    # --- Check if in use by any process ---
    if fuser -m "$DEVPATH" >/dev/null 2>&1; then
        echo "$DEVPATH is busy (open by process), skipping standby."
        continue
    fi

    echo "$DEVPATH is active/idle and unused, sending to standby..."
    hdparm -y "$DEVPATH"
    hdparm -C "$DEVPATH"
done
