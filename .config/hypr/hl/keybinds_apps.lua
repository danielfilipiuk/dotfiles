---------------------
---- MY PROGRAMS ----
---------------------------------------------------------------
-- Set programs that you use
local terminal    = "app2unit -S both -- kitty"
local fileManager = "app2unit -S both -- thunar"
local menu        = "pidof fuzzel || app2unit -S both -- fuzzel --log-level=error"
local editor	  = "app2unit -S both -- mousepad"


---------------------
---- KEYBINDINGS ----
---------------------------------------------------------------
 mainMod = "SUPER" -- Sets "Windows" key as main modifier
---------------------------------------------------------------



------------------------------- APPLICATIONS -------------------------------
---------------------------------------------------------------
-- Example binds, see https://wiki.hypr.land/Configuring/Basics/Binds/ for more
---------------------------------------------------------------
-- TERMINAL
--hl.bind(mainMod .. " + T", hl.dsp.exec_cmd("uwsm-app -Sout -p StandardOutput=null -- kitty"), 	{ description = "terminal emulator" })
hl.bind(mainMod .. " + T", hl.dsp.exec_cmd(terminal), 	{ description = "terminal emulator" })
---------------------------------------------------------------
-- FILE MANAGER
hl.bind(mainMod .. " + E", hl.dsp.exec_cmd(fileManager), 	{ description = "file explorer" })
---------------------------------------------------------------
-- APP LAUNCHER
hl.bind(mainMod .. " + Space", hl.dsp.exec_cmd(menu), 	{ description = "app launcher" })
---------------------------------------------------------------
-- SCREENSABER
hl.bind(mainMod .. " + Pause", hl.dsp.exec_cmd("pidof glmatrix || glmatrix_screensaver"), {description = "glmatrix" })
---------------------------------------------------------------
-- OMACALC
hl.bind("XF86Calculator",  hl.dsp.exec_cmd("app2unit -S both -- omacalc"), {description = "omacalc"})
---------------------------------------------------------------
-- QALCULATE-GTK
hl.bind(mainMod .. " + XF86Calculator",  hl.dsp.exec_cmd("app2unit -S both -- qalculate-gtk"), {description = "qalculate"})
---------------------------------------------------------------
-- REGLA
hl.bind(mainMod .. " + R",  hl.dsp.exec_cmd("app2unit -S both -- length"), {description = "regla"})
---------------------------------------------------------------
-- FSEARCH
hl.bind(mainMod .. " + F",  hl.dsp.exec_cmd("pidof fsearch || app2unit -S both -- fsearch"), {description = "fsearch"})
---------------------------------------------------------------
-- CURSOR CLIP COPY PASTE
--hl.bind(mainMod .. " + V",  hl.dsp.exec_cmd("app2unit -S both -- cursor-clip"), {description = "cursor-clip"})
hl.bind(mainMod .. " + V",  hl.dsp.exec_cmd("app2unit -- cliphist-fuzzel-img"), {description = "cliphist"})
---------------------------------------------------------------
-- HYPRPICKER COLOR PICK
hl.bind(mainMod .. " + I",  hl.dsp.exec_cmd("pidof hyprpicker || app2unit -- hyprpicker -a -n"), {description = "hyprpicker color picker"})
---------------------------------------------------------------
-- eyedropper COLOR PICK
hl.bind(mainMod .. " + CTRL + I",  hl.dsp.exec_cmd("pidof hyprpicker || app2unit -- eyedropper"), {description = "eyedropper color picker"})
---------------------------------------------------------------
-- EFCK EMOJIS
hl.bind(mainMod .. " + period",  hl.dsp.exec_cmd("efck-chat-keyboard"), {description = "efck emojis"})
---------------------------------------------------------------
-- WLCLOCK 
hl.bind(mainMod .. " + K",  hl.dsp.exec_cmd("app2unit -- wlclock-hypr"), {description = "wlclock"})
---------------------------------------------------------------
-- TOMBOY NEW NOTE 
hl.bind(mainMod .. " + N",  hl.dsp.exec_cmd("app2unit -- env QT_QPA_PLATFORM=xcb tomboy-ng -c"), {description = "tomboy new note"})
---------------------------------------------------------------
-- TOMBOY SEARCH NOTES 
hl.bind(mainMod .. " + ALT + N",  hl.dsp.exec_cmd("app2unit -- env QT_QPA_PLATFORM=xcb tomboy-ng"), {description = "tomboy search note"})
---------------------------------------------------------------




---------------------------------------------------------------
------------------------------ HYPRSHADE -------------------------------
--------------------------------------------------------------
-- SHADERS - NO ANDAN BIEN
--hl.bind(mainMod .. " + F10",  hl.dsp.exec_cmd("uwsm-app -Sout -- hyprshade -v toggle night_shift_sepia"))
--------------------------------------------------------------










