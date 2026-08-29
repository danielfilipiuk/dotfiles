
---------------------
---- KEYBINDINGS ----
---------------------------------------------------------------
 mainMod = "SUPER" -- Sets "Windows" key as main modifier
---------------------------------------------------------------


---------------------------------------------------------------
-- SUBMAP RESIZE WINDOWS WITH KEYS
---------------------------------------------------------------
-- Switch to a submap called `resize`.
hl.bind("SUPER + ALT + R", hl.dsp.submap(" "),
{description = "resize windows with keys submap"} )
-- Start a submap called "resize".
hl.define_submap(" ", function()

    -- Set repeating binds for resizing the active window.
    hl.bind("right", hl.dsp.window.resize({ x = 10, y = 0, relative = true}),
    { repeating = true },
    {description = "enlarge window width"})
    hl.bind("left", hl.dsp.window.resize({ x = -10, y = 0, relative = true}),
    { repeating = true },
    {description = "reduce window width"})
    hl.bind("up", hl.dsp.window.resize({ x = 0, y = 10, relative = true}),
    { repeating = true },
    {description = "enlarge window height"})
    hl.bind("down", hl.dsp.window.resize({ x = 0, y = -10, relative = true}),
    { repeating = true },
    {description = "reduce window height"})

    -- Use `reset` to go back to the global submap
    hl.bind("escape", hl.dsp.submap("reset"), {description = "reset submap RESIZE"})

end)

---------------------------------------------------------------
-- SUBMAP MOVE WINDOWS WITH KEYS
---------------------------------------------------------------
-- Switch to a submap called `move`.
hl.bind("SUPER + ALT + M", hl.dsp.submap(" "),
{description = "move windows with keys submap"})

-- Start a submap called "move".
hl.define_submap(" ", function()


    -- Set repeating binds for moving the active window.
    hl.bind("right", hl.dsp.window.move({ x = 10, y = 0, relative = true}),
    { repeating = true },
    {description = "move window right"})
    hl.bind("left", hl.dsp.window.move({ x = -10, y = 0, relative = true}),
    { repeating = true },
    {description = "move window left"})
    hl.bind("up", hl.dsp.window.move({ x = 0, y = -10, relative = true}),
    { repeating = true },
    {description = "move window up"})
    hl.bind("down", hl.dsp.window.move({ x = 0, y = 10, relative = true}),
    { repeating = true },
    {description = "move window down"})

    -- Use `reset` to go back to the global submap
    hl.bind("escape", hl.dsp.submap("reset"), {description = "reset submap MOVE"})

end)
---------------------------------------------------------------


