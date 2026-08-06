
---------------------
---- KEYBINDINGS ----
---------------------------------------------------------------
 mainMod = "SUPER" -- Sets "Windows" key as main modifier
---------------------------------------------------------------



---------------------------------------------------------------
-- CERRAR VENTANA
local closeWindowBind = hl.bind(mainMod .. " + Escape", hl.dsp.window.close(),	{ description = "close window" })
-- closeWindowBind:set_enabled(false)
---------------------------------------------------------------
---------------------------------------------------------------
-- MATAR PROCESO 
local closeWindowBind = hl.bind(mainMod .. " + CTRL + Escape", hl.dsp.window.kill(),	{ description = "kill process & window" })
-- closeWindowBind:set_enabled(false)
---------------------------------------------------------------


---------------------------------------------------------------
-- FLOAT TOGGLE
hl.bind(mainMod .. " + Return", hl.dsp.window.float({ action = "toggle" }),	{ description = "toggle float / tiled" })
---------------------------------------------------------------
-- FULLSCREEN  TOGGLE
hl.bind(mainMod .. " + ALT + Return", hl.dsp.window.fullscreen({ action = "toggle" }),	{ description = "toggle fullscreen" })
---------------------------------------------------------------
-- PSEUDO SPLIT
hl.bind(mainMod .. " + P", hl.dsp.window.pseudo(),	{ description = "toggle pseudo tile" })
---------------------------------------------------------------
-- Move/resize windows with mainMod + LMB/RMB and dragging

hl.bind(mainMod .. " + mouse:272", hl.dsp.window.drag(),   { mouse = true }, {description = "drag window with mouse+super"})
hl.bind(mainMod .. " + mouse:272", hl.dsp.window.float(), { mouse = true, click = true }, {description = "float window on click+super"}) 
hl.bind(mainMod .. " + mouse:273", hl.dsp.window.resize(), { mouse = true }, {description = "resize window with mouseright+super"})
---------------------------------------------------------------

-- FOCUS MOVE WITH KEYS
-- Move focus with mainMod + arrow keys
hl.bind(mainMod .. " + left",  hl.dsp.focus({ direction = "left" }), {description = "focus left window"})
hl.bind(mainMod .. " + right", hl.dsp.focus({ direction = "right" }), {description = "focus right window"})
hl.bind(mainMod .. " + up",    hl.dsp.focus({ direction = "up" }), {description = "focus top window"})
hl.bind(mainMod .. " + down",  hl.dsp.focus({ direction = "down" }), {description = "focus bottom window"})
---------------------------------------------------------------

-- RESIZE WINDOWS WITH KEYS
---------------------------------------------------------------
-- Switch to a submap called `resize`.
hl.bind("SUPER + ALT + R", hl.dsp.submap(" "), {description = "resize windows with keys submap"} )

-- Start a submap called "resize".
hl.define_submap(" ", function()

    -- Set repeating binds for resizing the active window.
    hl.bind("right", hl.dsp.window.resize({ x = 10, y = 0, relative = true}), { repeating = true }, {description = "enlarge window width"})
    hl.bind("left", hl.dsp.window.resize({ x = -10, y = 0, relative = true}), { repeating = true }, {description = "reduce window width"})
    hl.bind("up", hl.dsp.window.resize({ x = 0, y = 10, relative = true}), { repeating = true }, {description = "enlarge window heigth"})
    hl.bind("down", hl.dsp.window.resize({ x = 0, y = -10, relative = true}), { repeating = true }, {description = "reduce window heigth"})

    -- Use `reset` to go back to the global submap
    hl.bind("escape", hl.dsp.submap("reset"), {description = "reset submap"})

end)

-- MOVE WINDOWS WITH KEYS
---------------------------------------------------------------
-- Switch to a submap called `move`.
hl.bind("SUPER + ALT + M", hl.dsp.submap(" "), {description = "move windows with keys submap"})

-- Start a submap called "move".
hl.define_submap(" ", function()


    -- Set repeating binds for moving the active window.
    hl.bind("right", hl.dsp.window.move({ x = 10, y = 0, relative = true}), { repeating = true }, {description = "move window right"})
    hl.bind("left", hl.dsp.window.move({ x = -10, y = 0, relative = true}), { repeating = true }, {description = "move window left"})
    hl.bind("up", hl.dsp.window.move({ x = 0, y = -10, relative = true}), { repeating = true }, {description = "move window up"})
    hl.bind("down", hl.dsp.window.move({ x = 0, y = 10, relative = true}), { repeating = true }, {description = "move window down"})

    -- Use `reset` to go back to the global submap
    hl.bind("escape", hl.dsp.submap("reset"), {description = "reset submap"})

end)
---------------------------------------------------------------



