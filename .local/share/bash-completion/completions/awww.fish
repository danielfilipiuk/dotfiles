# Print an optspec for argparse to handle cmd's options that are independent of any subcommand.
function __fish_awww_global_optspecs
	string join \n h/help V/version
end

function __fish_awww_needs_command
	# Figure out if the current invocation already has a command.
	set -l cmd (commandline -opc)
	set -e cmd[1]
	argparse -s (__fish_awww_global_optspecs) -- $cmd 2>/dev/null
	or return
	if set -q argv[1]
		# Also print the command, so this can be used to figure out what it is.
		echo $argv[1]
		return 1
	end
	return 0
end

function __fish_awww_using_subcommand
	set -l cmd (__fish_awww_needs_command)
	test -z "$cmd"
	and return 1
	contains -- $cmd[1] $argv
end

complete -c awww -n "__fish_awww_needs_command" -s h -l help -d 'Print help (see more with \'--help\')'
complete -c awww -n "__fish_awww_needs_command" -s V -l version -d 'Print version'
complete -c awww -n "__fish_awww_needs_command" -f -a "clear" -d 'Fills the specified outputs with the given color'
complete -c awww -n "__fish_awww_needs_command" -f -a "restore" -d 'Restores the last displayed image on the specified outputs'
complete -c awww -n "__fish_awww_needs_command" -f -a "clear-cache" -d 'Clears the awww cache'
complete -c awww -n "__fish_awww_needs_command" -f -a "img" -d 'Sends an image (or animated gif) for the daemon to display'
complete -c awww -n "__fish_awww_needs_command" -f -a "toggle" -d 'Toggles the daemon'
complete -c awww -n "__fish_awww_needs_command" -f -a "pause" -d 'Pauses the daemon'
complete -c awww -n "__fish_awww_needs_command" -f -a "unpause" -d 'Unpauses the daemon'
complete -c awww -n "__fish_awww_needs_command" -f -a "kill" -d 'Kills the daemon'
complete -c awww -n "__fish_awww_needs_command" -f -a "query" -d 'Asks the daemon to print output information (names and dimensions)'
complete -c awww -n "__fish_awww_needs_command" -f -a "help" -d 'Print this message or the help of the given subcommand(s)'
complete -c awww -n "__fish_awww_using_subcommand clear" -s n -l namespace -d 'The daemon\'s namespace' -r
complete -c awww -n "__fish_awww_using_subcommand clear" -s o -l outputs -d 'Comma separated list of outputs to display the image at' -r
complete -c awww -n "__fish_awww_using_subcommand clear" -s a -l all -d 'Clear all awww-daemon instances (all namespaces)'
complete -c awww -n "__fish_awww_using_subcommand clear" -s h -l help -d 'Print help (see more with \'--help\')'
complete -c awww -n "__fish_awww_using_subcommand restore" -s n -l namespace -d 'The daemon\'s namespace' -r
complete -c awww -n "__fish_awww_using_subcommand restore" -s o -l outputs -d 'Comma separated list of outputs to restore' -r
complete -c awww -n "__fish_awww_using_subcommand restore" -s a -l all -d 'Restore all awww-daemon instances (all namespaces)'
complete -c awww -n "__fish_awww_using_subcommand restore" -s h -l help -d 'Print help (see more with \'--help\')'
complete -c awww -n "__fish_awww_using_subcommand clear-cache" -s h -l help -d 'Print help (see more with \'--help\')'
complete -c awww -n "__fish_awww_using_subcommand img" -s o -l outputs -d 'Comma separated list of outputs to display the image at' -r
complete -c awww -n "__fish_awww_using_subcommand img" -s n -l namespace -d 'The daemon\'s namespace' -r
complete -c awww -n "__fish_awww_using_subcommand img" -l resize -d 'Whether to resize the image and the method by which to resize it' -r -f -a "no\t'Do not resize the image'
crop\t'Resize the image to fill the whole screen, cropping out parts that don\'t fit'
fit\t'Resize the image to fit inside the screen, preserving the original aspect ratio'
stretch\t'Resize the image to fit inside the screen, without preserving the original aspect ratio'"
complete -c awww -n "__fish_awww_using_subcommand img" -l crop-gravity -d 'Specify which portion of the image to anchor when cropping. Only used when `--resize crop` is specified' -r -f -a "top-left\t''
top\t''
top-right\t''
left\t''
center\t''
right\t''
bottom-left\t''
bottom\t''
bottom-right\t''"
complete -c awww -n "__fish_awww_using_subcommand img" -l fill-color -d 'Which color to fill the padding with when output image does not fill screen' -r
complete -c awww -n "__fish_awww_using_subcommand img" -s f -l filter -d 'Filter to use when scaling images (run awww img --help to see options)' -r
complete -c awww -n "__fish_awww_using_subcommand img" -s t -l transition-type -d 'Sets the type of transition. Default is \'simple\', that fades into the new image' -r
complete -c awww -n "__fish_awww_using_subcommand img" -l transition-step -d 'How fast the transition approaches the new image' -r
complete -c awww -n "__fish_awww_using_subcommand img" -l transition-duration -d 'How long the transition takes to complete in seconds' -r
complete -c awww -n "__fish_awww_using_subcommand img" -l transition-fps -d 'Frame rate for the transition effect' -r
complete -c awww -n "__fish_awww_using_subcommand img" -l transition-angle -d 'This is used for the \'wipe\' and \'wave\' transitions. It controls the angle of the wipe' -r
complete -c awww -n "__fish_awww_using_subcommand img" -l transition-pos -d 'This is only used for the \'grow\',\'outer\' transitions. It controls the center of circle (default is \'center\')' -r
complete -c awww -n "__fish_awww_using_subcommand img" -l transition-bezier -d 'bezier curve to use for the transition https://cubic-bezier.com is a good website to get these values from' -r
complete -c awww -n "__fish_awww_using_subcommand img" -l transition-wave -d 'currently only used for \'wave\' transition to control the width and height of each wave' -r
complete -c awww -n "__fish_awww_using_subcommand img" -s a -l all -d 'Set the image for all awww-daemon instances (all namespaces)'
complete -c awww -n "__fish_awww_using_subcommand img" -l no-cache -d 'Do not update the cache'
complete -c awww -n "__fish_awww_using_subcommand img" -l no-resize -d 'Do not resize the image. Equivalent to `--resize=no`'
complete -c awww -n "__fish_awww_using_subcommand img" -l invert-y -d 'inverts the y position sent in \'transition_pos\' flag'
complete -c awww -n "__fish_awww_using_subcommand img" -s h -l help -d 'Print help (see more with \'--help\')'
complete -c awww -n "__fish_awww_using_subcommand toggle" -s n -l namespace -d 'The daemon\'s namespace' -r
complete -c awww -n "__fish_awww_using_subcommand toggle" -s a -l all -d 'Toggle all awww-daemon instances (all namespaces)'
complete -c awww -n "__fish_awww_using_subcommand toggle" -s h -l help -d 'Print help (see more with \'--help\')'
complete -c awww -n "__fish_awww_using_subcommand pause" -s n -l namespace -d 'The daemon\'s namespace' -r
complete -c awww -n "__fish_awww_using_subcommand pause" -s a -l all -d 'Pause all awww-daemon instances (all namespaces)'
complete -c awww -n "__fish_awww_using_subcommand pause" -s h -l help -d 'Print help (see more with \'--help\')'
complete -c awww -n "__fish_awww_using_subcommand unpause" -s n -l namespace -d 'The daemon\'s namespace' -r
complete -c awww -n "__fish_awww_using_subcommand unpause" -s a -l all -d 'Unpause all awww-daemon instances (all namespaces)'
complete -c awww -n "__fish_awww_using_subcommand unpause" -s h -l help -d 'Print help (see more with \'--help\')'
complete -c awww -n "__fish_awww_using_subcommand kill" -s n -l namespace -d 'The daemon\'s namespace' -r
complete -c awww -n "__fish_awww_using_subcommand kill" -s a -l all -d 'Kill all awww-daemon instances (all namespaces)'
complete -c awww -n "__fish_awww_using_subcommand kill" -s h -l help -d 'Print help (see more with \'--help\')'
complete -c awww -n "__fish_awww_using_subcommand query" -s n -l namespace -d 'The daemon\'s namespace' -r
complete -c awww -n "__fish_awww_using_subcommand query" -s a -l all -d 'Query all awww-daemon instances (all namespaces)'
complete -c awww -n "__fish_awww_using_subcommand query" -s j -l json -d 'Print the information in `json` format'
complete -c awww -n "__fish_awww_using_subcommand query" -s h -l help -d 'Print help (see more with \'--help\')'
complete -c awww -n "__fish_awww_using_subcommand help; and not __fish_seen_subcommand_from clear restore clear-cache img toggle pause unpause kill query help" -f -a "clear" -d 'Fills the specified outputs with the given color'
complete -c awww -n "__fish_awww_using_subcommand help; and not __fish_seen_subcommand_from clear restore clear-cache img toggle pause unpause kill query help" -f -a "restore" -d 'Restores the last displayed image on the specified outputs'
complete -c awww -n "__fish_awww_using_subcommand help; and not __fish_seen_subcommand_from clear restore clear-cache img toggle pause unpause kill query help" -f -a "clear-cache" -d 'Clears the awww cache'
complete -c awww -n "__fish_awww_using_subcommand help; and not __fish_seen_subcommand_from clear restore clear-cache img toggle pause unpause kill query help" -f -a "img" -d 'Sends an image (or animated gif) for the daemon to display'
complete -c awww -n "__fish_awww_using_subcommand help; and not __fish_seen_subcommand_from clear restore clear-cache img toggle pause unpause kill query help" -f -a "toggle" -d 'Toggles the daemon'
complete -c awww -n "__fish_awww_using_subcommand help; and not __fish_seen_subcommand_from clear restore clear-cache img toggle pause unpause kill query help" -f -a "pause" -d 'Pauses the daemon'
complete -c awww -n "__fish_awww_using_subcommand help; and not __fish_seen_subcommand_from clear restore clear-cache img toggle pause unpause kill query help" -f -a "unpause" -d 'Unpauses the daemon'
complete -c awww -n "__fish_awww_using_subcommand help; and not __fish_seen_subcommand_from clear restore clear-cache img toggle pause unpause kill query help" -f -a "kill" -d 'Kills the daemon'
complete -c awww -n "__fish_awww_using_subcommand help; and not __fish_seen_subcommand_from clear restore clear-cache img toggle pause unpause kill query help" -f -a "query" -d 'Asks the daemon to print output information (names and dimensions)'
complete -c awww -n "__fish_awww_using_subcommand help; and not __fish_seen_subcommand_from clear restore clear-cache img toggle pause unpause kill query help" -f -a "help" -d 'Print this message or the help of the given subcommand(s)'
