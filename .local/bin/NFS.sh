#!/bin/bash

# ============================
#     NFS Toggle (FIXED)
#     - No pkexec
#     - Must run with sudo
#     - Detect active state
# ============================

# Check sudo
if [[ $EUID -ne 0 ]]; then
    echo "This script must be run with sudo:"
    echo "   sudo ./NFS.sh"
    exit 1
fi

ICON_DIR="$HOME/.local/share/icons"
ICON_ON="$ICON_DIR/nfs-on.png"
ICON_OFF="$ICON_DIR/nfs-off.png"
ICON_MAIN="$ICON_DIR/nfs-main.png"

SERVICES="
nfs-kernel-server.service
nfs-utils.service
nfs-common.service
nfs-server.service
nfs-mountd.service
nfs-idmapd.service
nfsdcld.service
rpc-statd.service
rpc-gssd.service
rpc-svcgssd.service
rpcbind.service
rpc-gssd.service
rpc-statd-notify.service
auth-rpcgss-module.service
run-rpc_pipefs.mount
rpcbind.socket
rpcbind.target
rpc_pipefs.target
fsidd.service
proc-fs-nfsd.mount
"

create_icons() {
    mkdir -p "$ICON_DIR"

    convert -size 128x128 xc:none \
        -fill '#38c172' -draw 'circle 64,64 64,5' "$ICON_ON"

    convert -size 128x128 xc:none \
        -fill '#e3342f' -draw 'circle 64,64 64,5' "$ICON_OFF"

    convert -size 128x128 xc:none \
        -fill '#3490dc' -draw 'circle 64,64 64,5' "$ICON_MAIN"
}

[[ ! -f $ICON_MAIN ]] && create_icons

# REAL detection: active, not enabled
is_nfs_active() {
    for S in $SERVICES; do
        if systemctl is-active "$S" &>/dev/null; then
            return 0
        fi
    done
    return 1
}

enable_nfs() {
    for S in $SERVICES; do
	modprobe -i nfs nfsd auth_rpcgss lockd grace sunrpc
        systemctl enable "$S" >/dev/null 2>&1
        systemctl start "$S" >/dev/null 2>&1
    done
}

disable_nfs() {
    for S in $SERVICES; do
        systemctl stop "$S" >/dev/null 2>&1
        systemctl disable "$S" >/dev/null 2>&1
	rmmod -f nfs nfsd auth_rpcgss lockd grace sunrpc
    done
}

while true; do

    if is_nfs_active; then
        STATE="NFS Status: <b>ENABLED</b>"
        BTN="Disable NFS"
        IMG="$ICON_ON"
    else
        STATE="NFS Status: <b>DISABLED</b>"
        BTN="Enable NFS"
        IMG="$ICON_OFF"
    fi

    yad --title="NFS Toggle" \
        --window-icon="$ICON_MAIN" \
        --width=350 --height=180 \
        --image="$IMG" --image-on-top \
        --text="$STATE\n\nChoose an action:" \
        --button="$BTN:0" \
        --button="Quit:1" \
        --center

    [[ $? -eq 1 ]] && exit 0

    if is_nfs_active; then
        disable_nfs
        notify-send -i "$ICON_OFF" "NFS Disabled" "All NFS and RPC services stopped"
        yad --title="NFS" --image="$ICON_OFF" --text="✔ NFS Disabled" --button=OK
    else
        enable_nfs
        notify-send -i "$ICON_ON" "NFS Enabled" "NFS server and RPC running"
        yad --title="NFS" --image="$ICON_ON" --text="✔ NFS Enabled" --button=OK
    fi

done
