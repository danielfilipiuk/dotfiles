#!/bin/bash

SESSION_NAME="dash"

tmux has-session -t $SESSION_NAME 2>/dev/null && tmux kill-session -t $SESSION_NAME

tmux new-session -d -s $SESSION_NAME -n Monitor 'btop'
tmux split-window -v 'amdgpu_top'
tmux split-window -h 'journalctl --no-hostname -f'
tmux split-window -v 'neo'

# Reapply perfect layout
tmux select-layout tiled

# Optional pretty names
tmux select-pane -t 0 -T "btop"
tmux select-pane -t 1 -T "amdgpu_top"
tmux select-pane -t 2 -T "journal"
tmux select-pane -t 3 -T "matrix"

# Trap window close (SIGHUP, SIGINT) and clean up
cleanup() {
    tmux kill-session -t $SESSION_NAME 2>/dev/null
}
trap cleanup EXIT HUP INT TERM

# Attach in the *foreground*
tmux attach-session -t $SESSION_NAME
