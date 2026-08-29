
---------------------
---- KEYBINDINGS ----
---------------------------------------------------------------
 mainMod = "SUPER" -- Sets "Windows" key as main modifier
---------------------------------------------------------------



---------------------------------------------------------------
-- CERRAR VENTANA
local closeWindowBind = hl.bind(mainMod .. " + Escape", hl.dsp.window.close(),
{ description = "close window" })
-- closeWindowBind:set_enabled(false)

---------------------------------------------------------------
-- MATAR PROCESO 
local closeWindowBind = hl.bind(mainMod .. " + CTRL + Escape", hl.dsp.window.kill(),
{ description = "kill process & window" })
-- closeWindowBind:set_enabled(false)

---------------------------------------------------------------
-- FLOAT TOGGLE
hl.bind(mainMod .. " + Return", hl.dsp.window.float({ action = "toggle" }),
{ description = "toggle float / tiled" })

---------------------------------------------------------------
-- FULLSCREEN  TOGGLE
hl.bind(mainMod .. " + ALT + Return", hl.dsp.window.fullscreen({ action = "toggle" }),
{ description = "toggle fullscreen" })

---------------------------------------------------------------
-- PSEUDO SPLIT
hl.bind(mainMod .. " + P", hl.dsp.window.pseudo(),
{ description = "toggle pseudo tile" })

---------------------------------------------------------------
-- MOUSE ACTIONS ON WINDOWS
---------------------------------------------------------------
-- drag window with super+left click pressed
hl.bind(mainMod .. " + mouse:272", hl.dsp.window.drag(), { mouse = true }, {description = "drag window with mouse+super"})
-- tile / float window wiht super+left click
hl.bind(mainMod .. " + mouse:272", hl.dsp.window.float(), { mouse = true, click = true }, {description = "float window on click+super"}) 
-- resize window with super + right click
hl.bind(mainMod .. " + mouse:273", hl.dsp.window.resize(), { mouse = true }, {description = "resize window with mouseright+super"})

---------------------------------------------------------------
-- FOCUS MOVE WITH KEYS
-- Move focus with mainMod + arrow keys
hl.bind(mainMod .. " + left",  hl.dsp.focus({ direction = "left" }), {description = "focus left window"})
hl.bind(mainMod .. " + right", hl.dsp.focus({ direction = "right" }), {description = "focus right window"})
hl.bind(mainMod .. " + up",    hl.dsp.focus({ direction = "up" }), {description = "focus top window"})
hl.bind(mainMod .. " + down",  hl.dsp.focus({ direction = "down" }), {description = "focus bottom window"})


