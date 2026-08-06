
hl.window_rule({
	 name = "xscreensaver",
	 match = {title = ".*XScreenSaver.*"},
	 size = "2500 1300",
	 monitor = "0",
	 content = "game",
	 move = "-106 -145",
	 float = true,
	 opacity = 0.65,
	 decorate = false,
	 rounding = 0,
	 confine_pointer = true,
	 stay_focused = true,
	 --animation = "slide 100%",
	 focus_on_activate = true,
	 no_shortcuts_inhibit = false,
 	 animation = "popin",
 	  	 
})
