#!/bin/bash

echo
echo "------------------------------------------"
echo "🔏 Signing kernel for Secure Boot "
 
KEY="/etc/sb/keys/MOK.key"
CRT="/etc/sb/keys/MOK.crt"

# detect newest kernel image
KERNEL_IMG=$(ls -1t ../*.deb | grep "linux-image" | head -n 1)

if [[ -z "$KERNEL_IMG" ]]; then
    echo "❌ No kernel image .deb found."
    exit 1
fi

echo "📦 Installing $KERNEL_IMG"
sudo dpkg -i "$KERNEL_IMG"

# after installation, sign the kernel binary in /boot
KVER=$(basename "$KERNEL_IMG" | sed 's/linux-image-//; s/_.*//')
KERNEL="/boot/vmlinuz-$KVER"

echo "🔐 Signing: $KERNEL"
sudo sbsign --key "$KEY" --cert "$CRT" --output "${KERNEL}.signed" "$KERNEL"
sudo mv "${KERNEL}.signed" "$KERNEL"

echo "✅ Kernel signed successfully."
echo "Done."
