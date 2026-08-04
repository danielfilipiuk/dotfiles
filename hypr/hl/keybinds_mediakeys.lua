
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

hl.bind("XF86AudioRaiseVolume", hl.dsp.exec_cmd("volumechange --inc"), { locked = true, repeating = true }, {description = "volume up"})
hl.bind("XF86AudioLowerVolume", hl.dsp.exec_cmd("volumechange --dec"), { locked = true, repeating = true }, {description = "volume down"})
hl.bind("XF86AudioMute",        hl.dsp.exec_cmd("volumechange --toggle"),     { locked = true, repeating = true }, {description = "volume mute"})

---------------------------------------------------------------
-- Requires playerctl
--hl.bind("XF86AudioNext",  hl.dsp.exec_cmd("playerctl next"),       { locked = true })
hl.bind("XF86AudioPause", hl.dsp.exec_cmd("playerctl play-pause"), { locked = true }, {description = "media play-pause"})
hl.bind("XF86AudioPlay",  hl.dsp.exec_cmd("playerctl play-pause"), { locked = true }, {description = "media play-pause toggle"})
--hl.bind("XF86AudioPrev",  hl.dsp.exec_cmd("playerctl previous"),   { locked = true })
---------------------------------------------------------------



