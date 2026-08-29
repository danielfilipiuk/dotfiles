-- CAPS LOCK NOTIFICATION
hl.bind("Caps_Lock",  hl.dsp.exec_cmd("caps_check.sh"), { locked = true}, {description = "caps_lock check"})

-- NUM LOCK NOTIFICATION
hl.bind("Num_Lock",  hl.dsp.exec_cmd("num_check.sh"), { locked = true}, {description = "num_lock check"})

-- NUM LOCK NOTIFICATION
--hl.bind("Num_lock",  hl.dsp.exec_cmd("~/.config/hypr/scripts/kbd-state.sh num"),
--{description = "NUMLOCK"})
