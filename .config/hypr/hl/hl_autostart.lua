-------------------
---- AUTOSTART ----
-------------------

-- See https://wiki.hypr.land/Configuring/Basics/Autostart/

-- Autostart necessary processes (like notifications daemons, status bars, etc.)
-- Or execute your favorite apps at launch like this:
--
--hl.on("hyprland.start", function () 
-- Force systemd to activate user services whenever Hyprland starts
--hl.on("hyprland.start", hl.config.exec_once("systemctl --user start graphical-session.target")


--    hl.exec_cmd("systemctl --user import-environment WAYLAND_DISPLAY XDG_CURRENT_DESKTOP")
--    hl.exec_cmd("systemctl --user start graphical-session.target")
--end)

---------------------------------------------------------------
hl.on("hyprland.start", function()
    hl.exec_cmd("systemctl --user start hyprland-session.target")
	hl.exec_cmd("hyprpm reload -v -n")
	hl.exec_cmd("sleep 1 && hyprctl reload")
    hl.exec_cmd("sleep 5 && xhost +si:localuser:root")
  --  hl.exec_cmd("app2unit -S out -- tomboy-ng")
	--hl.exec_cmd("swaybg -o DP-1 -i pictures/wallpapers/1280x1024.svg -o DVI-D-1 -i pictures/wallpapers/1280x800.svg -m center")
--    hl.exec_cmd("hyprpaper")
--    hl.exec_cmd("hyprsunset")
--    hl.exec_cmd("waybar")
--    hl.exec_cmd("hypridle")
end)
---------------------------------------------------------------
hl.on("hyprland.shutdown", function()
    os.execute("systemctl --user stop hyprland-session.target && sleep 0.1")

    -- uses a blocking exec function and sleeps a bit to give things time to close
    -- you might also want to kill troublesome/crashing non-systemd background services here:
    -- os.execute("pkill wallpaperthing; systemctl --user stop hyprland-session.target && sleep 0.1")
end)
---------------------------------------------------------------


-- already started as services:

--hl.exec_cmd("/usr/local/bin/awww_randomize_multi.sh $HOME/pictures/hyprwallpaper/")
--     hl.exec_cmd("hyprpaper")
--     hl.exec_cmd("hypridle")
--end)

