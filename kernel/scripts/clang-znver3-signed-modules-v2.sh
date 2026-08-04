#!/bin/bash
# configure kernel for zen3 arch

# https://kernel-team.pages.debian.net/kernel-handbook/ch-common-tasks.html#s-common-building
# https://wiki.archlinux.org/title/Kernel/Traditional_compilation
# https://www.kernel.org/doc/makehelp.txt

# enable module signing
scripts/config --enable CONFIG_MODULE_SIG
scripts/config --enable CONFIG_MODULE_SIG_ALL
scripts/config --set-str CONFIG_MODULE_SIG_KEY "/etc/sb/keys/signing_key.pem"

# disable debug info
scripts/config --disable DEBUG_INFO
scripts/config --disable CONFIG_DEBUG_INFO
scripts/config --disable DEBUG_INFO_DWARF_TOOLCHAIN_DEFAULT

#configure for zen2 arch
scripts/config --enable CONFIG_MZEN3
#scripts/config --disable CONFIG_LTO_NONE
#scripts/config --enable CONFIG_LTO_CLANG
#scripts/config --enable CONFIG_LTO_CLANG_FULL

export LLVM=1
export CC=clang
export CXX=clang++
export CPP=clang-cpp
export AR=llvm-ar
export NM=llvm-nm
export LD=ld.lld
export STRIP=llvm-strip
export RANLIB=llvm-ranlib
export CLANG_FLAGS="-target=x86_64-pc-linux-gnu -march=znver3 -mcpu=znver3 -print-sgf "
export KBUILD_CFLAGS="$CLANG_FLAGS"
export KBUILD_CXXFLAGS="$CLANG_FLAGS"
export KBUILD_CPPFLAGS="$CLANG_FLAGS"

echo
echo "		 ---  🐧 Linux Kernel Configuration & Build   ---   "
echo "		---   Running oldconfig to detail NEW options   ---   "
echo
#run kernel config
make oldconfig
echo
echo "		---  🐧 Linux Kernel Configuration & Build   ---   "
echo
PS3="		---   Choose an option : "
while true; do
echo
    select choice in "⚙️   Configuration using nconfig" "❌  Delete Previous build" "🚀  Start Kernel build" "🛑  Exit"; do
        case $REPLY in
            1)
		make nconfig
		break
		;;
            2)
		make clean
		break
		;;
	    3)
#		perf stat -e make bindeb-pkg -j"$(nproc)"
		perf stat -e cycles,instructions,branches,branch-misses \
	          -e cache-references,cache-misses \
	          -e task-clock,context-switches,cpu-migrations,page-faults \
	          make bindeb-pkg -j16
                exit 0
                ;;
            4)
                echo "Cancelled."
                exit 0
                ;;
            *)
                echo "Invalid option."
		break
                ;;
        esac
    done
done

