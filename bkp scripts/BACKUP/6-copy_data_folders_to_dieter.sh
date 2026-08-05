#!/bin/bash

rsync /mnt/data/MAME /run/media/daniel/DIETER -PahiuvtU --progress --info=progress2,misc,stats2 --size-only

rsync /mnt/data/roms /run/media/daniel/DIETER -PahiuvtU --progress --info=progress2,misc,stats2 --size-only

rsync /mnt/data/fonts /run/media/daniel/DIETER -PahiuvtU --progress --info=progress2,misc,stats2 --size-only

rsync /mnt/data/Books /run/media/daniel/DIETER -PahiuvtU --progress --info=progress2,misc,stats2 --size-only

rsync /mnt/data/SteamLibrary /run/media/daniel/DIETER -PahiuvtU --progress --info=progress2,misc,stats2 --size-only

rsync /mnt/data/DownBKP /run/media/daniel/DIETER -PahiuvtU --progress --info=progress2,misc,stats2 --size-only

rsync /mnt/data/gameswin /run/media/daniel/DIETER -PahiuvtU --progress --info=progress2,misc,stats2 --size-only

