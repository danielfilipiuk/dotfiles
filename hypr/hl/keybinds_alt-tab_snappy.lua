

--- ALT TAB SNAPPY  ----------------------------------------------
hl.bind("ALT + Tab", hl.dsp.exec_cmd("snappy-switcher next --mod alt --linear"), {description = "alt+tab"})
hl.bind("ALT + SHIFT + Tab", hl.dsp.exec_cmd("snappy-switcher prev --mod alt --linear"), {description = "alt+tab reverse"})
-- Super+Tab (workspace-filtered)
hl.bind("CTRL + Tab", hl.dsp.exec_cmd("snappy-switcher next --workspace --mod CTRL --linear"), {description = "alt+tab in workspace"})
hl.bind("CTRL + SHIFT + Tab", hl.dsp.exec_cmd("snappy-switcher prev --workspace --mod CTRL --linear"), {description = "alt+tab in workspace reverse"})
-- Toggle visibility
hl.bind("ALT + Space", hl.dsp.exec_cmd("snappy-switcher toggle --linear"), {description = "alt+tab fijo"})
---------------------------------------------------------------


