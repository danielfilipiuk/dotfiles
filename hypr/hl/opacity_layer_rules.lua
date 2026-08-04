------------------
---- LAYERS ----
------------------
-- Enable blur for waybar
hl.layer_rule({ 
	match = { namespace = "Waybar" }, 
	blur = true,
    	blur_popups = true,
    	ignore_alpha = 0.5,
})

-- Liquid Glass blur rules
 hl.layer_rule({ 
 	match = { namespace = "snappy-switcher" }, 
 	blur = true,
 	ignore_alpha = 0.5, 
 	})


hl.layer_rule({ 
	match = { namespace = "logout_dialog" }, 
	blur = true,
    	blur_popups = true,
    	ignore_alpha = 0.5
})

hl.layer_rule({ 
	match = { namespace = "notifications" }, 
	blur = true,
    	blur_popups = true,
    	ignore_alpha = 0.5,
})

hl.layer_rule({ 
	match = { namespace = "launcher" }, 
	blur = true,
    	blur_popups = true,
    	ignore_alpha = 0.5,
})
