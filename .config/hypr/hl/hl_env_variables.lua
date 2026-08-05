-------------------------------
---- ENVIRONMENT VARIABLES ----
-------------------------------

-- See https://wiki.hypr.land/Configuring/Advanced-and-Cool/Environment-variables/

hl.env("WAYLANDDRV_PRIMARY_MONITOR", "DP-1")

-- xcursors
hl.env("XCURSOR_SIZE", "22")
hl.env("XCURSOR_THEME", "Bibata-Modern-Ice")

--  hyprcursors
hl.env("HYPRCURSOR_SIZE", "22")
hl.env("HYPRCURSOR_THEME", "hypr_Bibata-Modern-Ice")

-- themes
--hl.env("GTK_THEME", "Orchis-Purple-Light-Compact-Nord")  --  nwg-look
hl.env("QT_QPA_PLATFORMTHEME", "hyprqt6engine")

-- verbose
hl.env("HYPRLAND_TRACE", "0")
hl.env("AQ_TRACE", "0")

-- toolkit backends
--hl.env("GDK_BACKEND", "wayland;x11;*")
--hl.env("QT_QPA_PLATFORM", "wayland;xcb")
--hl.env("SDL_VIDEODRIVER", "wayland,")
--hl.env("SDL_VIDEODRIVER", "wayland;x11,.*")

-- XDG 
--hl.env("XDG_CURRENT_DESKTOP", "Hyprland")
--hl.env("XDG_SESSION_TYPE", "wayland")
--hl.env("XDG_SESSION_DESKTOP", "Hyprland")

-- QT variables
hl.env("QT_AUTO_SCREEN_SCALE_FACTOR", "1")

-- brave 
hl.env("MOZ_ENABLE_WAYLAND", "1")
hl.env("ELECTRON_OZONE_PLATFORM_HINT", "wayland")
