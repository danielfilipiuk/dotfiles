#!/bin/bash
# configure kernel for zen2 arch

# disable module signature
#scripts/config --disable MODULE_SIG

# enable module signing

scripts/config --enable CONFIG_MODULE_SIG
scripts/config --enable CONFIG_MODULE_SIG_ALL
scripts/config --set-str CONFIG_MODULE_SIG_KEY "/etc/sb/keys/signing_key.pem"

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


# https://kernel-team.pages.debian.net/kernel-handbook/ch-common-tasks.html#s-common-building
# https://wiki.archlinux.org/title/Kernel/Traditional_compilation
# 
