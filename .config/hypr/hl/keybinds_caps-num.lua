-- CAPS LOCK NOTIFICATION
hl.bind("Caps_Lock",  hl.dsp.exec_cmd("caps_check.sh"), {description = "caps_lock check"})
hl.bind("Num_Lock",  hl.dsp.exec_cmd("num_check.sh"), {description = "num_lock check"})

-- NUM LOCK NOTIFICATION
--hl.bind("Num_lock",  hl.dsp.exec_cmd("~/.config/hypr/scripts/kbd-state.sh num"),
--{description = "NUMLOCK"})
