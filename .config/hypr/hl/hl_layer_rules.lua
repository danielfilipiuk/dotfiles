------------------
---- LAYERS ----
------------------
-- Enable blur for waybar
hl.layer_rule({ 
	match = { namespace = "Waybar" }, 
	blur = true,
	--shadow = true,
    	blur_popups = true,
    	ignore_alpha = 0.25
})

-- Liquid Glass blur rules
 hl.layer_rule({ 
 	match = { namespace = "snappy-switcher" }, 
 	blur = true,
 	dim_around = true,
 	animation = "popin",
})


hl.layer_rule({ 
	match = { namespace = "logout_dialog" }, 
	blur = true,
    	blur_popups = true,
    	dim_around = true,
})

hl.layer_rule({ 
	match = { namespace = "notifications" }, 
	blur = true,
    	animation = "slide",
    	ignore_alpha = 0.2,
    	above_lock = 2,
})

hl.layer_rule({ 
	match = { namespace = "launcher" }, 
	blur = true,
    	blur_popups = true,
    	ignore_alpha = 0.2,
    	animation = "popin",
    	dim_around = true,
})


hl.layer_rule({ 
	match = { namespace = "wlclock" }, 
	blur = true,
    	blur_popups = true,
    	animation = "popin",
    	ignore_alpha = 0.5,
    	dim_around = true,
})
