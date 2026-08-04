#!/bin/bash
set -e

echo
echo "------------------------------------------"
echo "🔧 Configuring Kernel for Zen2 + Secure Boot"
echo

KEY="/etc/sb/keys/MOK.key"
CRT="/etc/sb/keys/MOK.crt"

if [[ ! -f Makefile ]]; then
    echo "❌ Run inside kernel source tree."
    exit 1
fi

# Module auto-signing
scripts/config --enable CONFIG_MODULE_SIG
scripts/config --enable CONFIG_MODULE_SIG_ALL
scripts/config --set-str CONFIG_MODULE_SIG_KEY "/etc/sb/keys/signing_key.pem"

# Remove debug symbols
scripts/config --disable DEBUG_INFO
scripts/config --disable DEBUG_INFO_DWARF_TOOLCHAIN_DEFAULT

# Zen2 tuning
scripts/config --enable CONFIG_MZEN2
scripts/config --disable CONFIG_GENERIC_CPU
export KCFLAGS="-march=znver2"
export KCPPFLAGS="-march=znver2"

make oldconfig
make nconfig

echo
echo "------------------------------------------"
read -r -p "⚙️ Build kernel image (no .deb yet)? [y/N] " response
[[ ! "$response" =~ ^([yY])$ ]] && exit 1

perf stat -d make KCFLAGS="-march=znver2" KCPPFLAGS="-march=znver2" -j"$(nproc)" bzImage modules

echo
echo "------------------------------------------"
echo "🔍 Locating kernel version..."
KVER=$(make kernelrelease)
echo "➡️ Kernel version: $KVER"

# The kernel artifact before packaging
ORIG="arch/x86/boot/bzImage"
SIGNED="arch/x86/boot/vmlinuz-$KVER"

echo
echo "------------------------------------------"
echo "🔏 Signing kernel BEFORE packaging"
echo "Key : $KEY"
echo "Cert: $CRT"
echo "Out : $SIGNED"

sbsign --key "$KEY" --cert "$CRT" --output "$SIGNED" "$ORIG"

echo
echo "------------------------------------------"
echo "📦 Building signed .deb packages (bindeb-pkg)"
fakeroot perf stat -d  make KCFLAGS="-march=znver2" KCPPFLAGS="-march=znver2" bindeb-pkg -j"$(nproc)"

echo
echo "✅ Done. Signed kernel packaged."
echo "The .deb files are in: ../"
