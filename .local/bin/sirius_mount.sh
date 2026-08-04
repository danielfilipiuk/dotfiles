#!/bin/bash

# Define mount points
MOUNTS=("/mnt/SIRIUS/data" "/mnt/SIRIUS/profile")

# Function to check if a mount point is already mounted
is_mounted() {
    mountpoint -q "$1"
}

# Loop through all mount points and toggle them
for MOUNT in "${MOUNTS[@]}"; do
    if is_mounted "$MOUNT"; then
        echo "Unmounting: $MOUNT"
        umount "$MOUNT" || echo "Failed to unmount $MOUNT"
    else
        echo "Mounting: $MOUNT"
        mount "$MOUNT" || echo "Failed to mount $MOUNT"
    fi
done