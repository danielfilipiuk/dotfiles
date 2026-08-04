 -- https://wiki.hypr.land/Configuring/Advanced-and-Cool/Animations/
  hl.curve("smooth", { type = "bezier", points = { { 0.22, 1 }, { 0.1, 1.1 } } })
  hl.curve("quick", { type = "bezier", points = { { 0.15, 0.85 }, { 0.25, 1.0 } } })
  hl.curve("overshot", { type = "bezier", points = { { 0.05, 0.9 }, { 0.1, 1.08 } } })
  hl.curve("linearish", { type = "bezier", points = { { 0.3, 0.0 }, { 0.7, 1.0 } } })
  hl.curve("easeOutQuint", { type = "bezier", points = { { 0.23, 1 }, { 0.32, 1 } } })

  -- WINDOWS
  hl.animation({ leaf = "windows", enabled = true, speed = 4, bezier = "smooth", style = "popin 95%" })
  hl.animation({ leaf = "windowsIn", enabled = true, speed = 4, bezier = "smooth", style = "popin 85%" })
  hl.animation({ leaf = "windowsOut", enabled = true, speed = 3, bezier = "quick", style = "popin 90%" })
  hl.animation({ leaf = "windowsMove", enabled = true, speed = 3, bezier = "quick" })

  -- WORKSPACES
  hl.animation({ leaf = "workspaces", enabled = true, speed = 5, bezier = "smooth", style = "slidefade 20%" })
  hl.animation({ leaf = "specialWorkspace", enabled = true, speed = 3, bezier = "smooth", style = "slidefadevert 5%" })

  -- LAYERS
  hl.animation({ leaf = "layers", enabled = true, speed = 3, bezier = "quick", style = "fade" })
  hl.animation({ leaf = "layersIn", enabled = true, speed = 3, bezier = "quick" })
  hl.animation({ leaf = "layersOut", enabled = true, speed = 3, bezier = "quick" })
  hl.animation({ leaf = "fadeLayersIn", enabled = true, speed = 3, bezier = "linearish" })
  hl.animation({ leaf = "fadeLayersOut", enabled = true, speed = 3, bezier = "linearish" })

  -- FADE
  hl.animation({ leaf = "fade", enabled = true, speed = 4, bezier = "smooth" })
