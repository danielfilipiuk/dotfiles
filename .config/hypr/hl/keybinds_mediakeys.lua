
------------------------------- MEDIA KLEYS -------------------------------
---------------------------------------------------------------
-- Laptop multimedia keys for volume and LCD brightness
--hl.bind("XF86AudioRaiseVolume", hl.dsp.exec_cmd("wpctl set-volume -l 1 @DEFAULT_AUDIO_SINK@ 5%+"), { locked = true, repeating = true })

--hl.bind("XF86AudioRaiseVolume", hl.dsp.exec_cmd("pamixer --increase 5"), { locked = true, repeating = true })
--hl.bind("XF86AudioLowerVolume", hl.dsp.exec_cmd("pamixer --decrease 5"), { locked = true, repeating = true })
--hl.bind("XF86AudioMute",        hl.dsp.exec_cmd("pamixer --toggle-mute"),     { locked = true, repeating = true })

--hl.bind("XF86AudioLowerVolume", hl.dsp.exec_cmd("wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-"),      { locked = true, repeating = true })
--hl.bind("XF86AudioMute",        hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle"),     { locked = true, repeating = true })
--hl.bind("XF86AudioMicMute",     hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle"),   { locked = true, repeating = true })
--hl.bind("XF86MonBrightnessUp",  hl.dsp.exec_cmd("brightnessctl -e4 -n2 set 5%+"),                  { locked = true, repeating = true })
--hl.bind("XF86MonBrightnessDown",hl.dsp.exec_cmd("brightnessctl -e4 -n2 set 5%-"),                  { locked = true, repeating = true })

---------------------------------------------------------------
----VOLUME UP -----
hl.bind("XF86AudioRaiseVolume", hl.dsp.exec_cmd("volumechange --inc && \
						pw-play /usr/share/sounds/freedesktop/stereo/audio-volume-change.oga --volume 0.5"),
{ locked = true, repeating = true },
{description = "volume up"})
----VOLUME DOWN -----
hl.bind("XF86AudioLowerVolume", hl.dsp.exec_cmd("volumechange --dec && \
						pw-play /usr/share/sounds/freedesktop/stereo/audio-volume-change.oga --volume 0.5"), 
{ locked = true, repeating = true },
{description = "volume down"})
----VOLUME MUTE -----
hl.bind("XF86AudioMute", hl.dsp.exec_cmd("volumechange --toggle && \
						pw-play /usr/share/sounds/freedesktop/stereo/audio-volume-change.oga --volume 0.5"),
{ locked = true},
{description = "volume mute"})

---------------------------------------------------------------
-- Requires playerctl MEDIA PLAY/PAUSE
---------------------------------------------------------------
--hl.bind("XF86AudioNext",  hl.dsp.exec_cmd("playerctl next"),       { locked = true })
hl.bind("XF86AudioPause", hl.dsp.exec_cmd("playerctl play-pause"),
{ locked = true },
{description = "media play-pause"})
-- Requires playerctl MEDIA PLAY/PAUSE
hl.bind("XF86AudioPlay",  hl.dsp.exec_cmd("playerctl play-pause"),
{ locked = true },
{description = "media play-pause toggle"})
--hl.bind("XF86AudioPrev",  hl.dsp.exec_cmd("playerctl previous"),   { locked = true })


---------------------------------------------------------------
-- MPC CONTROL ---
---------------------------------------------------------------
-- volume UP
hl.bind("SUPER + XF86AudioRaiseVolume", hl.dsp.exec_cmd("mpc volume +5"),
{ locked = true, repeating = true },
{description = "mpc volume +5"})
-- volume DOWN
hl.bind("SUPER + XF86AudioLowerVolume", hl.dsp.exec_cmd("mpc volume -5"),
{ locked = true, repeating = true },
{description = "mpc volume -5"})
-- play pause toggle
hl.bind("SUPER + XF86AudioPause", hl.dsp.exec_cmd("mpc toggle"),
{ locked = true},
{description = "mpc toggle"})
-- play pause toggle
hl.bind("SUPER + XF86AudioPlay",  hl.dsp.exec_cmd("mpc toggle"),
{ locked = true},
{description = "mpc play-pause toggle"})
-- seek +5
hl.bind("SUPER + SHIFT + XF86AudioRaiseVolume", hl.dsp.exec_cmd("mpc seek +5"),
{ locked = true, repeating = true },
{description = "mpc seek +5"})
-- seek -5
hl.bind("SUPER + SHIFT + XF86AudioLowerVolume", hl.dsp.exec_cmd("mpc seek -5"),
{ locked = true, repeating = true },
{description = "mpc seek -5"})
-- next 
hl.bind("SUPER + CTRL + XF86AudioRaiseVolume", hl.dsp.exec_cmd("mpc next"),
{ locked = true},
{description = "mpc next song"})
-- prev
hl.bind("SUPER + CTRL + XF86AudioLowerVolume", hl.dsp.exec_cmd("mpc prev"),
{ locked = true},
{description = "mpc previous song"})
-- restart song 
hl.bind("SUPER + CTRL + XF86AudioMute",  hl.dsp.exec_cmd("mpc seek 0"),
{ locked = true},
{description = "mpc restart song"})

------------------------------------------------------------------------
-- open ncmpcpp
hl.bind("SUPER + XF86AudioMute",  hl.dsp.exec_cmd("app2unit -T ncmpcpp"),
{description = "ncMPCpp"})



