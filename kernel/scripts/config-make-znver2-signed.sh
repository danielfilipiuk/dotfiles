#!/bin/bash
# configure kernel for zen2 arch

# disable module signature
scripts/config --disable MODULE_SIG

# disable debug info
scripts/config --disable DEBUG_INFO
scripts/config --disable DEBUG_INFO_DWARF_TOOLCHAIN_DEFAULT

#configure for zen2 arch
scripts/config --enable CONFIG_MZEN2
scripts/config --disable CONFIG_GENERIC_CPU
export KCFLAGS="-march=znver2"
export KCPPFLAGS="-march=znver2"

#run kernel config
make oldconfig
make nconfig

#clean previous compilation files
#make clean

echo 
echo "------------------------------------------"
read -r -p "Start Linux Kernel build? [y/N] " response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]
then
	perf stat -d make KCFLAGS="-march=znver2" KCPPFLAGS="-march=znver2" bindeb-pkg -j$(nproc)
else
	echo build cancelled.
fi

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

# https://kernel-team.pages.debian.net/kernel-handbook/ch-common-tasks.html#s-common-building
# https://wiki.archlinux.org/title/Kernel/Traditional_compilation
# 
