
---------------------
---- KEYBINDINGS ----
---------------------------------------------------------------
 mainMod = "SUPER" -- Sets "Windows" key as main modifier
---------------------------------------------------------------


---------------------------------------------------------------
-- HYPRSHOT REGION SCREENSHOT
hl.bind(mainMod .. " + Print", hl.dsp.exec_cmd("hyprshot -m region -o ~/downloads"),
{description = "screenshot - hyprshot region" })

---------------------------------------------------------------
-- HYPRSHOT MONITOR SCREENSHOT
hl.bind(mainMod .. " + SHIFT + CTRL + Print", hl.dsp.exec_cmd("hyprshot -m output -o ~/downloads"),
{description = "screenshot - hyprshot monitor" })

---------------------------------------------------------------
-- HYPRSHOT WINDOW SCREENSHOT
hl.bind(mainMod .. " + CTRL + Print", hl.dsp.exec_cmd("hyprshot -m window -o ~/downloads"),
{description = "screenshot - hyprshot window" })

---------------------------------------------------------------
--GPU SCREEN RECORDER VENTANA
hl.bind(mainMod .. " + F12",  hl.dsp.exec_cmd("app2unit -- /home/daniel/.local/bin/gps_window.sh"),
{description = "GPU screen record Window"})

---------------------------------------------------------------
--GPU SCREEN RECORDER MONITOR
hl.bind(mainMod .. " + CTRL + F12",  hl.dsp.exec_cmd("app2unit -- /home/daniel/.local/bin/gps_monitor.sh"),
{description = "GPU screen record MONITOR"})
---------------------------------------------------------------



-- METODO DIRECTO ---------------------------------------

-- REGION SCREENSHOT
-- Region Screenshot: Saves file to ~/Downloads with a date-time stamp
--hl.bind(mainMod .. " + Print", hl.dsp.exec_cmd([[grim -g "$(slurp)" "$HOME/downloads/Screenshot_$(date +'%Y-%m-%d_%H-%M-%S').png"]]))
---------------------------------------------------------------
-- FULLSCREEN SCREENSHOT
-- Fullscreen Screenshot: Saves entire workspace to ~/Downloads with a date-time stamp
--hl.bind(mainMod .. " + SHIFT + Print", hl.dsp.exec_cmd([[grim "$HOME/downloads/Screenshot_$(date +'%Y-%m-%d_%H-%M-%S').png"]]))








