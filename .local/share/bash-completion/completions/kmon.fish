# Print an optspec for argparse to handle cmd's options that are independent of any subcommand.
function __fish_kmon_global_optspecs
	string join \n a/accent-color= c/color= t/tickrate= r/reverse u/unicode E/regex h/help V/version
end

function __fish_kmon_needs_command
	# Figure out if the current invocation already has a command.
	set -l cmd (commandline -opc)
	set -e cmd[1]
	argparse -s (__fish_kmon_global_optspecs) -- $cmd 2>/dev/null
	or return
	if set -q argv[1]
		# Also print the command, so this can be used to figure out what it is.
		echo $argv[1]
		return 1
	end
	return 0
end

function __fish_kmon_using_subcommand
	set -l cmd (__fish_kmon_needs_command)
	test -z "$cmd"
	and return 1
	contains -- $cmd[1] $argv
end

complete -c kmon -n "__fish_kmon_needs_command" -s a -l accent-color -d 'Set the accent color using hex or color name' -r
complete -c kmon -n "__fish_kmon_needs_command" -s c -l color -d 'Set the main color using hex or color name' -r
complete -c kmon -n "__fish_kmon_needs_command" -s t -l tickrate -d 'Set the refresh rate of the terminal' -r
complete -c kmon -n "__fish_kmon_needs_command" -s r -l reverse -d 'Reverse the kernel module list'
complete -c kmon -n "__fish_kmon_needs_command" -s u -l unicode -d 'Show Unicode symbols for the block titles'
complete -c kmon -n "__fish_kmon_needs_command" -s E -l regex -d 'Interpret the module search query as a regular expression'
complete -c kmon -n "__fish_kmon_needs_command" -s h -l help -d 'Print help'
complete -c kmon -n "__fish_kmon_needs_command" -s V -l version -d 'Print version'
complete -c kmon -n "__fish_kmon_needs_command" -f -a "sort" -d 'Sort kernel modules'
complete -c kmon -n "__fish_kmon_needs_command" -f -a "help" -d 'Print this message or the help of the given subcommand(s)'
complete -c kmon -n "__fish_kmon_using_subcommand sort" -s s -l size -d 'Sort modules by their sizes'
complete -c kmon -n "__fish_kmon_using_subcommand sort" -s n -l name -d 'Sort modules by their names'
complete -c kmon -n "__fish_kmon_using_subcommand sort" -s d -l dependent -d 'Sort modules by their dependent modules'
complete -c kmon -n "__fish_kmon_using_subcommand sort" -s h -l help -d 'Print help'
complete -c kmon -n "__fish_kmon_using_subcommand help; and not __fish_seen_subcommand_from sort help" -f -a "sort" -d 'Sort kernel modules'
complete -c kmon -n "__fish_kmon_using_subcommand help; and not __fish_seen_subcommand_from sort help" -f -a "help" -d 'Print this message or the help of the given subcommand(s)'
