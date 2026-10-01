------------------
---- MONITORS ----
------------------

-- See https://wiki.hypr.land/Configuring/Basics/Monitors/
hl.monitor({
    output   = "DP-1",
    mode     = "1280x1024@60.020",
    position = "0x0",
    scale    = "1",
})
hl.monitor({
    output   = "DVI-D-1",
    mode     = "1024x768@60.004",
    position = "auto-center-left",
    scale    = "1",
})

hl.monitor({
    output   = "HDMI-A-1",
    mode     = "preferred",
    position = "auto-center-right",
    scale    = "1",
})
