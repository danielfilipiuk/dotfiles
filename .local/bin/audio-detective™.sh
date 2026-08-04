#!/bin/bash
watch -s"/home/daniel/downloads" -t --color -n 0.5 '
echo "\e[36m════════════════════════════════════════════════════════════\e[0m"
echo ░█▀█░█░█░█▀▄░▀█▀░█▀█░░░░░█▀▄░█▀▀░▀█▀░█▀▀░█▀▀░▀█▀░▀█▀░█░█░█▀▀TM
echo ░█▀█░█░█░█░█░░█░░█░█░▄▄▄░█░█░█▀▀░░█░░█▀▀░█░░░░█░░░█░░▀▄▀░█▀▀
echo ░▀░▀░▀▀▀░▀▀░░▀▀▀░▀▀▀░░░░░▀▀░░▀▀▀░░▀░░▀▀▀░▀▀▀░░▀░░▀▀▀░░▀░░▀▀▀
echo "\e[1;36mＬｉｎｕｘ＿Ａｕｄｉｏ＿Ｐｉｐｅｌｉｎｅ＿Ｉｎｓｐｅｃｔｏｒ\e[0m"
echo "\e[36m════════════════════════════════════════════════════════════\e[0m"
printf "\e[1;36mdate & time:\t\t"
date "+%A %d %B %Y, %H:%M:%S %p"
echo "\e[0m"
echo "\e[33m─ \e[1;33mＨＡＲＤＷＡＲＥ ＆ ＳＩＮＫ\e[0m \e[33m─────────────────────────────\e[0m"
echo
printf "\t"
cat /proc/asound/card1/codec#0 | grep --color=always "Codec:"
pactl list sinks | grep -E --color=always "Description:|State:|Sample Specification:|Name:|Latency:"
echo
echo "\e[33m─ \e[1;33mＣＬＩＥＮＴＳ\e[0m \e[33m───────────────────────────────────────────\e[0m"
echo
pactl list sink-inputs | grep --color=always -Ei "application.name =|Sample Specification:|resample method:"
echo
echo "\e[33m─ \e[1;33mＭＰＤ  ＳＴＡＴＵＳ\e[0m \e[33m─────────────────────────────────────\e[0m"
echo
mpc status "%state%   %currenttime%-%totaltime%\t Volume: %volume%\t BitRate: %audioformat%"
mpc current --format="%artist% - %album% - %title%\n%file%"
echo
echo "\e[33m─ \e[1;33mＡＬＳＡ  ＨＷ＿ＰＡＲＡＭＳ\e[0m \e[33m─────────────────────────────\e[0m"
echo
cat /proc/asound/card1/pcm0p/sub0/hw_params | grep --color=always -Ei "access:|format:|subformat:|channles:|rate:|period_size:|buffer_size:"
echo
echo "\e[33m─ \e[1;33mＰＵＬＳＥＡＵＤＩＯ  ＣＯＮＦＩＧ\e[0m \e[33m───────────────────────\e[0m"
echo
#pw-top -b
#pulseaudio --dump-conf | grep --color=always -Ei "default-sample-format =|default-sample-rate =|alternate-sample-rate =|resample-method =|avoid-resampling ="
echo
echo "\e[33m────────────\e[0m  \e[1;35mＣＴＲＬ＋Ｃ\e[0m  ｔｏ  ＥＸＩＴ \e[33m─────────────────\e[0m"
echo
'
echo
echo ──────────────────────────────────────────────────────────── | lolcat
echo "Audio-Detective™ - Linux Audio Pipeline Inspector" | lolcat
echo "2026 Dany's Pirasoft©" | lolcat
echo "Created by Dany's Pirasoft with assistance from ChatGPT" | lolcat
echo ──────────────────────────────────────────────────────────── | lolcat
echo
