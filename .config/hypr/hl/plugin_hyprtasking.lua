
---------------------
---- KEYBINDINGS ----
---------------------------------------------------------------
 mainMod = "SUPER" -- Sets "Windows" key as main modifier
---------------------------------------------------------------



------------------------------- PLUGIN HYPRTASKING  -------------------------------
--------------------------------------------------------------
hl.bind(mainMod .. " + mouse:275", function() hl.plugin.hyprtasking.toggle("cursor") end)
hl.bind(mainMod .. " + mouse:276", function() hl.plugin.hyprtasking.toggle("all") end)
--hl.bind(mainMod .. " + SHIFT + Tab", function() hl.plugin.hyprtasking.toggle("cursor") end)
hl.bind(mainMod .. " + CTRL + Tab", function() hl.plugin.hyprtasking.toggle("all") end)
-- escape closes the overview if it's open
hl.bind("escape", function()
  if hl.plugin.hyprtasking.is_active() then
    hl.plugin.hyprtasking.toggle('all')
  end
end, { non_consuming = true })

-------------  CERRAR VENTANAS  ---------------------
--hl.bind(mainMod .. " + Q ", function() hl.plugin.hyprtasking.killhovered() end)

-------------  MOVERSE ENTRE WORKSPACES   ---------------------
hl.bind(mainMod .. " + CTRL + Left", function() hl.plugin.hyprtasking.move("left") end)
hl.bind(mainMod .. " + CTRL + Right", function() hl.plugin.hyprtasking.move("right") end)
hl.bind(mainMod .. " + CTRL + Up", function() hl.plugin.hyprtasking.move("up") end)
hl.bind(mainMod .. " + CTRL + Down", function() hl.plugin.hyprtasking.move("down") end)

-------------  MOVER VENTANAS ENTRE WORKSPACES   ---------------------
hl.bind(mainMod .. " + ALT + Left", function() hl.plugin.hyprtasking.movewindow("left") end)
hl.bind(mainMod .. " + ALT + Right", function() hl.plugin.hyprtasking.movewindow("right") end)
hl.bind(mainMod .. " + ALT + Up", function() hl.plugin.hyprtasking.movewindow("up") end)
hl.bind(mainMod .. " + ALT + Down", function() hl.plugin.hyprtasking.movewindow("down") end)

--hl.bind("SUPER + D", function() hl.plugin.hyprtasking.move("out") end)
--hl.bind("SUPER + SHIFT + A", function() hl.plugin.hyprtasking.movewindow("out") end)

-------------  LAYERS ---------------------
hl.bind(mainMod .. " + CTRL + 1", function() hl.plugin.hyprtasking.setlayer(1) end)
hl.bind(mainMod .. " + CTRL + 2", function() hl.plugin.hyprtasking.setlayer(2) end)


------------- CONFIG  ---------------------
hl.config({
  plugin = {
    hyprtasking = {
      layout = "grid", --linear
      gap_size = 0,
      bg_color = 0xfafafa,
      border_size = 0,
      exit_on_hovered = false,
      warp_on_move_window = 1,
      close_overview_on_reload = true,

      -- for other mouse buttons see <linux/input-event-codes.h>
      drag_button = 0x110,   -- left mouse button
      select_button = 0x111, -- right mouse button

      gestures = {
        enabled = false,
        move_fingers = 3,
        move_distance = 300,
        open_fingers = 4,
        open_distance = 300,
        open_positive = true,
      },

      grid = {
        rows = 3,
        cols = 3,
        loop = true,
        layers = 2,
        loop_layers = true,
        gaps_use_aspect_ratio = false,
      },

      linear = {
        top = true,
        height = 400,
        scroll_speed = 1.0,
        blur = true,
      }
    }
  },
})

