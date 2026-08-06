---------------------
---- KEYBINDINGS ----
---------------------------------------------------------------
 mainMod = "SUPER" -- Sets "Windows" key as main modifier
---------------------------------------------------------------
---------------------------------------------------------------
-- Bind SUPER + N to run a command (dsp) and show a built-in notification
hl.bind(mainMod .. " + CTRL + SHIFT + R", function()
    -- Execute your command or custom script
    hl.dispatch(hl.dsp.exec_cmd("app2unit -T -- hyprctl reload"), {description = "hyprctl reload"})
    
    -- Trigger a native Hyprland on-screen notification popup
    hl.notification.create({
        text = "hyprctl reloaded!",
        timeout = 5000, -- duration in milliseconds
        icon = 5,       -- icon type (5 corresponds to OK/success)
    })
end)

---------------------------------------------------------------
-- RELOAD HYPRCTL
--Rhl.bind(mainMod .. " + CTRL + SHIFT + R",  hl.dsp.exec_cmd("app2unit -T -- hyprctl reload"), {description = "hyprctl reload"})
---------------------------------------------------------------
-- UDISKSCTL MOUNTS WITH FUZZEL 
hl.bind(mainMod .. " + M",  hl.dsp.exec_cmd("app2unit -- fuzzel-mount"), {description = "udisks mount drives with fuzzel"})
---------------------------------------------------------------
-- UUCTL SERICE MANAGER
hl.bind("CTRL + ALT + End", hl.dsp.exec_cmd("app2unit -S out -- uuctl fuzzel -d --placeholder \"type Service name...\" --counter --no-sort -w 80 -l 15"), {description = "uwsm - uuctl"})
---------------------------------------------------------------
-- HYPRLOCK
hl.bind(mainMod .. " + L", hl.dsp.exec_cmd("pidof hyprlock || app2unit -S both -- hyprlock"), {locked = true}, {description = "Lock the screen"})
---------------------------------------------------------------
-- WLOGOUT
hl.bind("CTRL + ALT + Delete", hl.dsp.exec_cmd("pidof wlogout || app2unit -S both -- wlogout"), {description = "wlogout"})
---------------------------------------------------------------
-- TASK MANAGER 
hl.bind("CTRL + SHIFT + Escape",  hl.dsp.exec_cmd("app2unit -- kitty -e btop"), {description = "task manager"})
---------------------------------------------------------------
-- RENDERER RELOAD
-- Bind SUPER + N to run a command (dsp) and show a built-in notification
hl.bind(mainMod .. " + CTRL + SHIFT + Backspace", function()
    -- Execute your command or custom script
    hl.dispatch(hl.dsp.force_renderer_reload(), {description = "renderer reload"})
    
    -- Trigger a native Hyprland on-screen notification popup
    hl.notification.create({
        text = "Renderer reloaded!",
        timeout = 5000, -- duration in milliseconds
        icon = 5,       -- icon type (5 corresponds to OK/success)
    })
end)

---------------------------------------------------------------


