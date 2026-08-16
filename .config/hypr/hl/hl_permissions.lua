-----------------------
----- PERMISSIONS -----
-----------------------

-- See https://wiki.hypr.land/Configuring/Advanced-and-Cool/Permissions/
-- Please note permission changes here require a Hyprland restart and are not applied on-the-fly
-- for security reasons

 hl.config({
  ecosystem = {
   enforce_permissions = true,
   },
})

 hl.permission("/usr/(bin|local/bin)/grim", "screencopy", "allow")
 hl.permission("/usr/(lib|libexec|lib64)/xdg-desktop-portal-hyprland", "screencopy", "allow")
 hl.permission("/usr/(bin|local/bin)/hyprpm", "plugin", "allow")
 hl.permission("/usr/(bin|local/bin)/blue-recorder", "screencopy", "allow")
 hl.permission("/usr/(bin|local/bin)/gps_window.sh", "screencopy", "allow")
 hl.permission("/usr/(bin|local/bin)/gps_monitor.sh", "screencopy", "allow")
 hl.permission("/usr/(bin|local/bin)/gpu-screen-recorder", "screencopy", "allow")
 hl.permission("/usr/(bin|local/bin)/hyprshot", "screencopy", "allow")
 hl.permission("/usr/(bin|local/bin)/hyprlock", "screencopy", "allow")
 hl.permission("/usr/(bin|local/bin)/hyprpicker", "screencopy", "allow")
 hl.permission("/usr/(bin|local/bin)/eyedropper", "screencopy", "allow")
