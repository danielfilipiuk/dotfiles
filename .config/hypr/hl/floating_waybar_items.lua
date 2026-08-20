hl.window_rule({
	 name = "pavucontrol",
	 match = {class = "org.pulseaudio.pavucontrol"},
	 opacity = .85,
	 float = true,
	 size = "500 500",
	 move = "750 50",
})

hl.window_rule({
	 name = "wpa_gui",
	 match = {class = "wpa_gui"},
	 float = true,
 	 opacity = .85,
	 move = "927 25",	 
})


hl.window_rule({
	 name = "qpwgraph",
	 match = {class = "org.rncbc.qpwgraph"},
	 opacity = 0.85,
	 float = true,
 	 move = "531 25",
 	 size = "748 503",
})

hl.window_rule({
	 name = "pwvucontrol",
	 match = {class = "com.saivert.pwvucontrol"},
	 float = true,
	 opacity = .85,
	 size = "680 500",
--	 move = "50% 50%",   
})
