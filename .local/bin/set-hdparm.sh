#!/bin/bash
for drive in sda; do
#    /usr/sbin/hdparm -B 127 -S 240 /dev/$drive
#       -B APM 254  - high perf
#       -S 0 - disable standby
# 	-S 242 - 1 hora para suspension
     /usr/sbin/hdparm -B 254 -S 0 /dev/$drive
#       -S 240 - 20 minutos standy
done
for drive in sdb; do
    /usr/sbin/hdparm -S 0 /dev/$drive
done
for drive in sdc; do
#    /usr/sbin/hdparm -B 127 -S 240 /dev/$drive
# -B 1 - more power management. /  -B 254 more performance
    /usr/sbin/hdparm -B 254 -S 0 /dev/$drive
done
for drive in sdd; do
#       -M 254 -> acoustic mode in performance (loud) mode
    /usr/sbin/hdparm -S 0 -M 254 /dev/$drive
done

