--hl.window_rule({
---	 name = "general floating dialogs",
--	 match = {float = "1"},
--	 center = true,
--})
hl.window_rule({
	 name = "About",
	 match = {title = ".*About.*"},
	 float = true,
	 center = true,
})

hl.window_rule({
	 name = "Properties window",
	 match = {title = ".*Properties.*"},
	 float = true,
})

hl.window_rule({
	 name = "save as dialog",
	 match = {title = "^Save As.*"},
	 float = true,
})

hl.window_rule({
	 name = "Save dialog",
	 match = {title = "^Save.*"},
	 float = true,
})

hl.window_rule({
	 name = "save dialog",
	 match = {title = ".save.*"},
	 float = true,
})


hl.window_rule({
	 name = "XDG save as...",
	 match = {class = "xdg-desktop-portal-gtk"},
	 float = true,
})

hl.window_rule({
	 name = "select directory qdirstat",
	 match = {title = "Select Directory"},
	 size = "530 697",
	 float = true,
})

hl.window_rule({
	 name = "Preferences",
	 match = {title = ".*Preferences.*"},
	 float = true,
	 center = true,
})



hl.window_rule({
	 name = "yad dialog",
	 match = {class = "yad"},
	 float = true,
	 center = true,
})

hl.window_rule({
	 name = "Thunar Rename",
	 match = {title = ".*Rename.*"},
	 float = true,
	 center = true,	 
})

hl.window_rule({
	 name = "Thunar properties",
	 match = {title = ".*Properties.*"},
	 float = true,
	 center = true,	 
})

hl.window_rule({
	 name = "Thunar custom actions",
	 match = {title = "Custom Actions"},
	 float = true,
	 center = true,	 
})


hl.window_rule({
	 name = "Thunar audio info",
	 match = {title = ".*Audio Information.*"},
	 float = true,
	 center = true,
})


hl.window_rule({
	 name = "Thunar launcher edit",
	 match = {class = "exo-desktop-item-edit"},
	 float = true,
	 center = true,
})


hl.window_rule({
	 name = "Thunar confirm replace",
	 match = {title = "File Operation Progress"},
	 float = true,
	 center = true,
})

hl.window_rule({
	 name = "synaptic dialogs",
	 match = {title = "synaptic"},
	 center = false,
})

hl.window_rule({
	 name = "print",
	 match = {title = ".*Print.*"},
	 center = true,
	 float = true,
})

hl.window_rule({
	 name = "open file - mousepad",
	 match = {title = ".*Open File.*"},
	 center = true,
	 float = true,
})

hl.window_rule({
	 name = "Mousepad Shortcuts - mousepad",
	 match = {title = "Mousepad Shortcuts"},
	 center = true,
	 float = true,
})




