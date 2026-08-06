
use builtin;
use str;

set edit:completion:arg-completer[awww] = {|@words|
    fn spaces {|n|
        builtin:repeat $n ' ' | str:join ''
    }
    fn cand {|text desc|
        edit:complex-candidate $text &display=$text' '(spaces (- 14 (wcswidth $text)))$desc
    }
    var command = 'awww'
    for word $words[1..-1] {
        if (str:has-prefix $word '-') {
            break
        }
        set command = $command';'$word
    }
    var completions = [
        &'awww'= {
            cand -h 'Print help (see more with ''--help'')'
            cand --help 'Print help (see more with ''--help'')'
            cand -V 'Print version'
            cand --version 'Print version'
            cand clear 'Fills the specified outputs with the given color'
            cand restore 'Restores the last displayed image on the specified outputs'
            cand clear-cache 'Clears the awww cache'
            cand img 'Sends an image (or animated gif) for the daemon to display'
            cand toggle 'Toggles the daemon'
            cand pause 'Pauses the daemon'
            cand unpause 'Unpauses the daemon'
            cand kill 'Kills the daemon'
            cand query 'Asks the daemon to print output information (names and dimensions)'
            cand help 'Print this message or the help of the given subcommand(s)'
        }
        &'awww;clear'= {
            cand -n 'The daemon''s namespace'
            cand --namespace 'The daemon''s namespace'
            cand -o 'Comma separated list of outputs to display the image at'
            cand --outputs 'Comma separated list of outputs to display the image at'
            cand -a 'Clear all awww-daemon instances (all namespaces)'
            cand --all 'Clear all awww-daemon instances (all namespaces)'
            cand -h 'Print help (see more with ''--help'')'
            cand --help 'Print help (see more with ''--help'')'
        }
        &'awww;restore'= {
            cand -n 'The daemon''s namespace'
            cand --namespace 'The daemon''s namespace'
            cand -o 'Comma separated list of outputs to restore'
            cand --outputs 'Comma separated list of outputs to restore'
            cand -a 'Restore all awww-daemon instances (all namespaces)'
            cand --all 'Restore all awww-daemon instances (all namespaces)'
            cand -h 'Print help (see more with ''--help'')'
            cand --help 'Print help (see more with ''--help'')'
        }
        &'awww;clear-cache'= {
            cand -h 'Print help (see more with ''--help'')'
            cand --help 'Print help (see more with ''--help'')'
        }
        &'awww;img'= {
            cand -o 'Comma separated list of outputs to display the image at'
            cand --outputs 'Comma separated list of outputs to display the image at'
            cand -n 'The daemon''s namespace'
            cand --namespace 'The daemon''s namespace'
            cand --resize 'Whether to resize the image and the method by which to resize it'
            cand --crop-gravity 'Specify which portion of the image to anchor when cropping. Only used when `--resize crop` is specified'
            cand --fill-color 'Which color to fill the padding with when output image does not fill screen'
            cand -f 'Filter to use when scaling images (run awww img --help to see options)'
            cand --filter 'Filter to use when scaling images (run awww img --help to see options)'
            cand -t 'Sets the type of transition. Default is ''simple'', that fades into the new image'
            cand --transition-type 'Sets the type of transition. Default is ''simple'', that fades into the new image'
            cand --transition-step 'How fast the transition approaches the new image'
            cand --transition-duration 'How long the transition takes to complete in seconds'
            cand --transition-fps 'Frame rate for the transition effect'
            cand --transition-angle 'This is used for the ''wipe'' and ''wave'' transitions. It controls the angle of the wipe'
            cand --transition-pos 'This is only used for the ''grow'',''outer'' transitions. It controls the center of circle (default is ''center'')'
            cand --transition-bezier 'bezier curve to use for the transition https://cubic-bezier.com is a good website to get these values from'
            cand --transition-wave 'currently only used for ''wave'' transition to control the width and height of each wave'
            cand -a 'Set the image for all awww-daemon instances (all namespaces)'
            cand --all 'Set the image for all awww-daemon instances (all namespaces)'
            cand --no-cache 'Do not update the cache'
            cand --no-resize 'Do not resize the image. Equivalent to `--resize=no`'
            cand --invert-y 'inverts the y position sent in ''transition_pos'' flag'
            cand -h 'Print help (see more with ''--help'')'
            cand --help 'Print help (see more with ''--help'')'
        }
        &'awww;toggle'= {
            cand -n 'The daemon''s namespace'
            cand --namespace 'The daemon''s namespace'
            cand -a 'Toggle all awww-daemon instances (all namespaces)'
            cand --all 'Toggle all awww-daemon instances (all namespaces)'
            cand -h 'Print help (see more with ''--help'')'
            cand --help 'Print help (see more with ''--help'')'
        }
        &'awww;pause'= {
            cand -n 'The daemon''s namespace'
            cand --namespace 'The daemon''s namespace'
            cand -a 'Pause all awww-daemon instances (all namespaces)'
            cand --all 'Pause all awww-daemon instances (all namespaces)'
            cand -h 'Print help (see more with ''--help'')'
            cand --help 'Print help (see more with ''--help'')'
        }
        &'awww;unpause'= {
            cand -n 'The daemon''s namespace'
            cand --namespace 'The daemon''s namespace'
            cand -a 'Unpause all awww-daemon instances (all namespaces)'
            cand --all 'Unpause all awww-daemon instances (all namespaces)'
            cand -h 'Print help (see more with ''--help'')'
            cand --help 'Print help (see more with ''--help'')'
        }
        &'awww;kill'= {
            cand -n 'The daemon''s namespace'
            cand --namespace 'The daemon''s namespace'
            cand -a 'Kill all awww-daemon instances (all namespaces)'
            cand --all 'Kill all awww-daemon instances (all namespaces)'
            cand -h 'Print help (see more with ''--help'')'
            cand --help 'Print help (see more with ''--help'')'
        }
        &'awww;query'= {
            cand -n 'The daemon''s namespace'
            cand --namespace 'The daemon''s namespace'
            cand -a 'Query all awww-daemon instances (all namespaces)'
            cand --all 'Query all awww-daemon instances (all namespaces)'
            cand -j 'Print the information in `json` format'
            cand --json 'Print the information in `json` format'
            cand -h 'Print help (see more with ''--help'')'
            cand --help 'Print help (see more with ''--help'')'
        }
        &'awww;help'= {
            cand clear 'Fills the specified outputs with the given color'
            cand restore 'Restores the last displayed image on the specified outputs'
            cand clear-cache 'Clears the awww cache'
            cand img 'Sends an image (or animated gif) for the daemon to display'
            cand toggle 'Toggles the daemon'
            cand pause 'Pauses the daemon'
            cand unpause 'Unpauses the daemon'
            cand kill 'Kills the daemon'
            cand query 'Asks the daemon to print output information (names and dimensions)'
            cand help 'Print this message or the help of the given subcommand(s)'
        }
        &'awww;help;clear'= {
        }
        &'awww;help;restore'= {
        }
        &'awww;help;clear-cache'= {
        }
        &'awww;help;img'= {
        }
        &'awww;help;toggle'= {
        }
        &'awww;help;pause'= {
        }
        &'awww;help;unpause'= {
        }
        &'awww;help;kill'= {
        }
        &'awww;help;query'= {
        }
        &'awww;help;help'= {
        }
    ]
    $completions[$command]
}
