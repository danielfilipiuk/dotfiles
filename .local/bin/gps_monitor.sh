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
    notify "⬛ Monitor Recording stopped" "💾 Video saved."  && pw-play /usr/share/sounds/freedesktop/stereo/camera-shutter.oga --volume 0.25
    exit 0
fi

# Get the name of the currently focused monitor from hyprctl JSON output
MONITOR_NAME=$(hyprctl monitors -j | jq -r '.[] | select(.focused == true) | .name')

# Fallback: Default to active window monitor if no focused monitor was matched
if [ -z "$MONITOR_NAME" ]; then
    MONITOR_NAME=$(hyprctl activeworkspace -j | jq -r '.monitor')
fi

# Generate a timestamped filename
FILENAME="$OUTPUT_DIR/monitor_${MONITOR_NAME}_$(date +%Y-%m-%d_%H-%M-%S).mp4"

# Set audio device
AUDIO_DEVICE="alsa_output.pci-0000_30_00.6.analog-stereo.monitor"

notify "🔴 Monitor Recording started" "$(basename "$FILENAME")" && pw-play /usr/share/sounds/freedesktop/stereo/message.oga --volume 0.25

# Record the target monitor directly by passing its output name (e.g., DVI-D-1 or DP-1)
gpu-screen-recorder \
    -w "$MONITOR_NAME" \
    -f 60 \
    -a "$AUDIO_DEVICE" \
    -o "$FILENAME"

STATUS=$?

# Only notify if we exited normally
if [ $STATUS -eq 0 ]; then
    notify "⬛ Monitor Recording finished" "$(basename "$FILENAME")"
fi
