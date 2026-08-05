
perf stat -d  7z u -t7z -mx=9 -mmt=16 -aou -bt /run/media/daniel/DIETER/ScummVM/ScummVM.7z /mnt/data/ScummVM/

perf stat -d 7z u -t7z -mx=9 -mmt=16 -aou -bt /run/media/daniel/DIETER/dreamm/dreamm.7z /mnt/data/dreamm/

for d in /mnt/data/DOS/*/; do dir=$(basename "$d"); perf stat -d 7z u -t7z -mx=9 -mmt=16 -ms=on -aou -bt "/run/media/daniel/DIETER/DOS/$dir.7z" "$d"; done

for d in /mnt/data/linux/*/; do dir=$(basename "$d"); 7z u -t7z -mx=9 -mmt=16 -ms=on -aou -bt "/run/media/daniel/DIETER/linux/$dir.7z" "$d"; done


for d in /mnt/data/portables/*/; do dir=$(basename "$d"); perf stat -d 7z u -t7z -mx=9 -mmt=16 -ms=on -aou -bt "/run/media/daniel/DIETER/portables/$dir.7z" "$d"; done

rsync /mnt/data/mac /run/media/daniel/DIETER -PahiuvtU --progress --info=progress2,misc,stats2 --size-only

rsync /home/daniel/profile /run/media/daniel/DIETER -PahiuvtU --progress --info=progress2,misc,stats2 --size-only

rsync /mnt/500G/videos /run/media/daniel/DIETER -PahiuvtU --progress --info=progress2,misc,stats2 --size-only

rsync /mnt/500G/books-PDF /run/media/daniel/DIETER -PahiuvtU --progress --info=progress2,misc,stats2 --size-only

rsync /mnt/data/MAME /run/media/daniel/DIETER -PahiuvtU --progress --info=progress2,misc,stats2 --size-only

rsync /mnt/data/roms /run/media/daniel/DIETER -PahiuvtU --progress --info=progress2,misc,stats2 --size-only

tar -czvf /run/media/daniel/DIETER/wine/win.tar.gz /mnt/data/wine/win

tar -czvf /run/media/daniel/DIETER/wine/default.tar.gz /mnt/data/wine/default

tar -czvf /run/media/daniel/DIETER/steam/compatdata.tar.gz /mnt/data/SteamLibrary/steamapps/compatdata

tar -czvf /run/media/daniel/DIETER/heroic/prefixes.tar.gz /mnt/data/Heroic_Library/prefixes

cp /mnt/data/wine/setup_wine.txt



