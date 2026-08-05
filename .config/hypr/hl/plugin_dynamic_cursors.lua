--  https://github.com/VirtCode/hypr-dynamic-cursors  

--avoid config errors when the plugin is not loaded.

if hl.plugin.dynamic_cursors then

-------------------------------------------------------------------------


hl.config { plugin = { dynamic_cursors = {

    -- enables the plugin
    enabled = true,

    -- sets the cursor behaviour, supports these values:
    -- tilt    - tilt the cursor based on x-velocity
    -- rotate  - rotate the cursor based on movement direction
    -- stretch - stretch the cursor shape based on direction and velocity
    -- none    - do not change the cursor's behaviour
    mode = "tilt",

    -- minimum angle difference in degrees after which the shape is changed
    -- smaller values are smoother, but more expensive for hw cursors
    threshold = 1,

    -- for mode = "rotate"
    rotate = {

        -- length in px of the simulated stick used to rotate the cursor
        -- most realistic if this is your actual cursor size
        length = 22,

        -- clockwise offset applied to the angle in degrees
        -- this will apply to ALL shapes
        offset = 0.0,
    },

    -- for mode = "tilt"
    tilt = {

        -- controls how powerful the tilt is, the lower, the more power
        -- this value controls at which speed (px/s) the full tilt is reached
        limit = 2500,

        -- relationship between speed and tilt, supports these values:
        -- linear             - a linear function is used
        -- quadratic          - a quadratic function is used (most realistic to actual air drag)
        -- negative_quadratic - negative version of the quadratic one, feels more aggressive
        -- see `activation` in `src/mode/utils.cpp` for how exactly the calculation is done
        activation = "negative_quadratic",

        -- time window (ms) over which the speed is calculated
        -- higher values will make slow motions smoother but more delayed
        window = 100,

        -- full tilt for each side (°)
        full = 60,
    },

    -- for mode = "stretch"
    stretch = {

        -- controls how much the cursor is stretched
        -- this value controls at which speed (px/s) the full stretch is reached
        -- the full stretch being twice the original length
        limit = 3000,

        -- relationship between speed and stretch amount, supports these values:
        -- linear             - a linear function is used
        -- quadratic          - a quadratic function is used
        -- negative_quadratic - negative version of the quadratic one, feels more aggressive
        -- see `activation` in `src/mode/utils.cpp` for how exactly the calculation is done
        activation = "quadratic",

        -- time window (ms) over which the speed is calculated
        -- higher values will make slow motions smoother but more delayed
        window = 100,
    },

    -- configure shake to find
    -- magnifies the cursor if its is being shaken
    shake = {

        -- enables shake to find
        enabled = true,

        -- controls how soon a shake is detected
        -- lower values mean sooner
        threshold = 3.0,

        -- magnification level immediately after shake start
        base = 4.0,
        -- magnification increase per second when continuing to shake
        speed = 4.0,
        -- how much the speed is influenced by the current shake intensity
        influence = .5,

        -- maximal magnification the cursor can reach
        -- values below 1 disable the limit (e.g. 0)
        limit = 0.0,

        -- time in milliseconds the cursor will stay magnified after a shake has ended
        timeout = 2000,

        -- show cursor behaviour `tilt`, `rotate`, etc. while shaking
        effects = true,

        -- enable ipc events for shake
        -- see the `ipc` section below
        ipc = true,
    },

    -- use hyprcursor to get a higher resolution texture when the cursor is magnified
    -- see the `hyprcursor` section below
    hyprcursor = {

        -- use nearest-neighbour (pixelated) scaling when magnifying beyond texture size
        -- this will also have effect without hyprcursor support being enabled
        -- 0 - never use pixelated scaling
        -- 1 - use pixelated when no highres image
        -- 2 - always use pixelated scaling
        nearest = 1,

        -- enable dedicated hyprcursor support
        enabled = true,

        -- resolution in pixels to load the magnified shapes at
        -- be warned that loading a very high-resolution image will take a long time and might impact memory consumption
        -- -1 means we use [normal cursor size] * [shake:base option]
        resolution = -1,

        -- shape to use when clientside cursors are being magnified
        -- see the shape-name property of shape rules for possible names
        -- specifying clientside will use the actual shape, but will be pixelated
        fallback = "clientside",
    },
}}}





end


--  BIND PAA AGRANDAR EL CURSOR--------------------------------

--hl.bind("CTRL + SUPER + M", hl.plugin.dynamic_cursors.dsp_magnify({ duration = 5000, size = 20.0 }))

-- apply a 90° offset in rotate mode to the text shape
hl.plugin.dynamic_cursors.shape_rule { shape = "text", rotate = { offset = 90.0 } }

-- use stretch mode when grabbing, and set the limit low
hl.plugin.dynamic_cursors.shape_rule { shape = "grab", mode = "stretch", stretch = { limit = 2000 } }

-- do not show any effects on clientside cursors
--hl.plugin.dynamic_cursors.shape_rule { shape = "clientside", mode = "none" }



