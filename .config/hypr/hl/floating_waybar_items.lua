hl.window_rule({
	 name = "pavucontrol",
	 match = {class = "org.pulseaudio.pavucontrol"},
	 opacity = .85,
	 float = true,
	 size = "500 500",
	 move = "775 30",
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
