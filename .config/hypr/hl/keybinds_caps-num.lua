-- CAPS LOCK NOTIFICATION
hl.bind("Caps_lock",  hl.dsp.exec_cmd("notify-send -i capslock-enabled-symbolic 'CAPS LOCK'"),
{description = "CAPSLOCK"})

-- NUM LOCK NOTIFICATION
hl.bind("Num_lock",  hl.dsp.exec_cmd("notify-send -i numlock-enabled-symbolic 'NUM LOCK'"),
{description = "NUMLOCK"})
