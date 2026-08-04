#!/usr/bin/env bash

# Conseguir la lista de dispositivos unificados
choise=$(udiskie-info -o path,label,mounted | rofi -dmenu -p "Drives")

# Si no se selecciona nada, salir
[ -z "$choise" ] && exit 0

# Extraer la ruta del dispositivo (ej: /dev/sdb1)
dev_path=$(echo "$choise" | awk '{print $1}')

# Si ya está montado (el output de udiskie-info lo muestra), lo desmontamos. Si no, lo montamos.
if echo "$choise" | grep -q "mounted=True"; then
    udiskie-umount "$dev_path" && notify-send "Drives" "Disk unmounted: $dev_path"
else
    udiskie-mount "$dev_path" && notify-send "Drives" "Disk mounted: $dev_path"
fi
