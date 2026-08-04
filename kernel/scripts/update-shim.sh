#!/usr/bin/env bash
set -e

# === Adjust ONLY if your keys are elsewhere ===
KEY_DIR="/etc/sb/keys"
KEY="$KEY_DIR/MOK.key"
CRT="$KEY_DIR/MOK.crt"

# === Nothing to change below this line ===

EFI_DIR="/boot/efi"
GRUB_DIR="$EFI_DIR/EFI/debian"
GRUB_EFI="$GRUB_DIR/grubx64.efi"
GRUB_EFI_SIGNED="$GRUB_DIR/grubx64.efi.signed"

FONT="/boot/grub/fonts/unifont-24.pf2" # Change if you want another font

echo "→ Checking keys..."
if [[ ! -f "$KEY" || ! -f "$CRT" ]]; then
    echo "❌ SecureBoot keys not found in: $KEY_DIR"
    exit 1
fi

echo "→ Ensuring GRUB font is configured..."
if [[ -f "$FONT" ]]; then
    sed -i "s|^GRUB_FONT=.*|GRUB_FONT=$FONT|" /etc/default/grub 2>/dev/null || \
    echo "GRUB_FONT=$FONT" >> /etc/default/grub
else
    echo "⚠ Font not found at $FONT (you can ignore this)"
fi

sudo nano /etc/grub.d/40_custom
echo "→ Updating GRUB config..."
grub-mkconfig -o /boot/grub/grub.cfg

echo "→ Reinstalling GRUB to EFI..."
grub-install --target=x86_64-efi --efi-directory="$EFI_DIR" --bootloader-id=debian --no-nvram

echo "→ Signing GRUB EFI binary..."
if [[ ! -f "$GRUB_EFI" ]]; then
    echo "❌ Could not find GRUB EFI binary at: $GRUB_EFI"
    exit 1
fi

sbsign --key "$KEY" --cert "$CRT" --output "$GRUB_EFI_SIGNED" "$GRUB_EFI"

echo "→ Replacing unsigned GRUB with signed one..."
mv "$GRUB_EFI_SIGNED" "$GRUB_EFI"

echo "✅ Done!"
echo "→ GRUB is now signed and Secure Boot compatible."
echo "→ You can reboot now."
