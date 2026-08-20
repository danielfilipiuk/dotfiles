
---------------------
---- KEYBINDINGS ----
---------------------------------------------------------------
 mainMod = "SUPER" -- Sets "Windows" key as main modifier

---------------------------------------------------------------
-- Switch workspaces with mainMod + [0-9]
-- Move active window to a workspace with mainMod + SHIFT + [0-9]
for i = 1, 10 do
    local key = i % 10 -- 10 maps to key 0
    hl.bind(mainMod .. " + " .. key,             hl.dsp.focus({ workspace = i}),
    {description = "switch workspaces with super+numbers"})
    hl.bind(mainMod .. " + SHIFT + " .. key,     hl.dsp.window.move({ workspace = i }),
    {description = "switch workspaces with super+numbers in reverse"})
end

---------------------------------------------------------------
-- Scroll through existing workspaces with mainMod + scroll
hl.bind(mainMod .. " + mouse_down", hl.dsp.focus({ workspace = "e+1" }),
{description = "switch workspaces withmouse scroll down"})

hl.bind(mainMod .. " + mouse_up",   hl.dsp.focus({ workspace = "e-1" }),
{description = "switch workspaces withmouse scroll up"})

---------------------------------------------------------------
-- Example special workspace (scratchpad)
-- MAGIC TOGGLE
hl.bind(" SUPER   + S ",         hl.dsp.workspace.toggle_special("magic"),
{description = "invoke magic workspace"})

---------------------------------------------------------------
-- ATRAPA EN MAGIC
hl.bind(" SUPER + SHIFT + S", hl.dsp.window.move({ workspace = "special:magic" }),
{description = "move window to magic workspace"})

---------------------------------------------------------------
-------CYCLE LAYOUT
hl.bind(mainMod .. " + tab",hl.dsp.exec_cmd("cycle-layout"),
{description = "cycle to next layout"}) -- Set next layout
hl.bind(mainMod .. " + SHIFT + tab", hl.dsp.exec_cmd("cycle-layout --previous"),
{description = "cycle to previous layout"}) -- Set previous layout

---------------------------------------------------------------
--- Use this one to bind different actions to the same key binding based on current layout:
---------------------------------------------------------------
local function layout_bind(bind_table)
    return function ()
        local workspace = hl.get_active_special_workspace() or
                          hl.get_active_workspace()

        if not workspace then
            return
        end

        local layout = workspace.tiled_layout
                
        if bind_table[layout] then
            hl.dispatch(bind_table[layout])
        end
    end
end

hl.bind("SUPER + CTRL + Return", layout_bind({
    scrolling = hl.dsp.layout("swapcol l"),
    	{description = "Scrolling: swap column with left one"},
    dwindle   = hl.dsp.layout("swapsplit"),
    	{description = "Dwindle: swap window split"},
    monocle   = hl.dsp.layout("cycleprev"),
    	{description = "Monocle and master: cycle prev window"},
    master    = hl.dsp.layout("cycleprev"),
    	{description = "Monocle and master: cycle prev window"},
}), {description = "cycle layout types"})

hl.bind("SUPER + CTRL + SHIFT + Return", layout_bind({
    scrolling = hl.dsp.layout("swapcol r"),
    	{description = "Scrolling: swap column with right one"},
    dwindle   = hl.dsp.layout("togglesplit"),
    	{description = "Dwindle: toggle window split "},
    monocle   = hl.dsp.layout("cyclenext"),
    	{description = "Monocle and master: cycle next window"},
    master    = hl.dsp.layout("cyclenext"),
    	{description = "Monocle and master: cycle next window"},
}), {description = "cycle layout types reverse"})
---------------------------------------------------------------
---------------------------------------------------------------




