
-----------------------
---- LOOK AND FEEL ----
-----------------------

-- Refer to https://wiki.hypr.land/Configuring/Basics/Variables/
hl.config({
    general = {
		-- gaps between windows
        gaps_in  = 1,
		-- gaps between windows and monitor edges
        gaps_out = 0,
        -- gaps between windows and monitor edges for floating windows -1 means default
	float_gaps = 3,
		
        border_size = 3,
---------------------------------------------------------------
        col = {
            active_border   = { colors = {"rgba(238, 130, 238,1)", "rgba(0, 255, 153, 1)"}, angle = 45 },
              --active_border   = { colors = {"rgba(23e0d5ff)", "rgba(00ff99ff)"}, angle = 45 },
            inactive_border = "rgba(59595955)",
        },
---------------------------------------------------------------
        -- Set to true to enable resizing windows by clicking and dragging on borders and gaps
        resize_on_border = false,
---------------------------------------------------------------
        -- Please see https://wiki.hypr.land/Configuring/Advanced-and-Cool/Tearing/ before you turn this on
        allow_tearing = false,
---------------------------------------------------------------
        layout = "dwindle",
---------------------------------------------------------------
        snap = {
        	enabled = true,
        	window_gap = 10,
        	monitor_gap = 10,
        },
    },
---------------------------------------------------------------
    decoration = {
        rounding       = 10,
        rounding_power = 5,

        -- Change transparency of focused and unfocused windows
        active_opacity   = 1.0,
        inactive_opacity = 1.0,
---------------------------------------------------------------
        shadow = {
            enabled      = true,
            range        = 15,
            render_power = 4,
            scale = 1,
            offset = {0, 0},
            color = "rgba(30,30,30,.25)",
            --color_inactive = "rgba(59595911)",
      --            color        = 0x2062049
        },
---------------------------------------------------------------
        blur = {
            enabled   = true,
            size      = 3, 	-- blur.size and blur.passes have to be at least 1.
	    passes    = 1,	-- Increasing blur.passes is necessary to prevent blur looking wrong on higher blur.
				-- size values, but remember that higher blur.passes will require more strain on the GPU.
            contrast = 0.8916,  -- contrast modulation for blur. [0.0 - 2.0]
            vibrancy  = 0.1696, -- Increase saturation of blurred colors. [0.0 - 1.0]
            brightness = 1, 	-- brightness modulation for blur. [0.0 - 2.0]
            vibrancy_darkness = 0.1696, -- How strong the effect of vibrancy is on dark areas . [0.0 - 1.0]
            popups = true, -- whether to blur popups (e.g. right-click menus)
            special = true, -- whether to blur behind the special workspace (note: expensive)
        },
---------------------------------------------------------------
        glow = {
        	enabled = true,
        	range = 15, --Glow range (“size”) in layout px
        	render_power = 2, --in what power to render the falloff (more power, the faster the falloff) [1 - 4]
	--color =  "rgba(23e0d522)",--glow’s color. Alpha dictates glow’s opacity.
		color =  "rgba(228,226,222,.20)",--glow’s color. Alpha dictates glow’s opacity.
		color_inactive = "rgba(30,30,30,.15)",
			--#23e0d511
        },
---------------------------------------------------------------
        --motion_blur = {
        	--enabled = true,
        	--samples = 7,
        --},
---------------------------------------------------------------
        --wobble = {
        --	enabled = true,
        --	mesh = 12,
        --	stifness = 200,
        --	damping = 12,
        --	mass = 1,
        --	intensity = 0.2,
        --	value_epsilon = 0.25,
        --	velocity_epsilon = 2,
        --},
---------------------------------------------------------------
    },
---------------------------------------------------------------
    animations = {
        enabled = true,
	workspace_wraparound = true,
    },
})

