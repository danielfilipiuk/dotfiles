#!/usr/bin/env bash

# Create output directory if it doesn't exist
OUTPUT_DIR="$HOME/videos"
mkdir -p "$OUTPUT_DIR"

notify() {
    notify-send \
        -a "GPU Screen Recorder" \
        -i camera-video \
        -u normal \
        -t 5000 \
        "$1" "$2"
}


# Handle process toggle safely for long process name string lengths
if pgrep -f "gpu-screen-recorder" >/dev/null; then
    pkill -SIGINT -f "gpu-screen-recorder"
    notify "  Window Recording stopped" "  Video saved."
    exit 0
fi

# Get the current active window's geometry from hyprctl
GEOM=$(hyprctl activewindow -j | jq -r '"\(.size[0]) \(.size[1]) \(.at[0]) \(.at[1])"')

# Read the geometry parameters
read -r WIDTH HEIGHT X_POS Y_POS <<< "$GEOM"

# Generate a timestamped filename
FILENAME="$OUTPUT_DIR/window_$(date +%Y-%m-%d_%H-%M-%S).mp4"

# Set audio device
AUDIO_DEVICE="alsa_output.pci-0000_30_00.6.analog-stereo.monitor"

notify " Window Recording started" "$(basename "$FILENAME")"

# FIX: Use "-w region" and pass the specific geometry structure to "-region"
#gpu-screen-recorder -w region -region "${WIDTH}x${HEIGHT}+${X_POS}+${Y_POS}" -f 60 -a "$AUDIO_DEVICE" -o "$FILENAME"

# Modern syntax: -w accepts the "WIDTHxHEIGHT+X+Y" format directly now
gpu-screen-recorder \
	-w "${WIDTH}x${HEIGHT}+${X_POS}+${Y_POS}" \
	-f 60 \
	-a "$AUDIO_DEVICE" \
	-o "$FILENAME"

STATUS=$?

# Only notify if we exited normally
if [ $STATUS -eq 0 ]; then
    notify " Window Recording finished" "$(basename "$FILENAME")"
fi
