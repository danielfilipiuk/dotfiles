
use builtin;
use str;

set edit:completion:arg-completer[kmon] = {|@words|
    fn spaces {|n|
        builtin:repeat $n ' ' | str:join ''
    }
    fn cand {|text desc|
        edit:complex-candidate $text &display=$text' '(spaces (- 14 (wcswidth $text)))$desc
    }
    var command = 'kmon'
    for word $words[1..-1] {
        if (str:has-prefix $word '-') {
            break
        }
        set command = $command';'$word
    }
    var completions = [
        &'kmon'= {
            cand -a 'Set the accent color using hex or color name'
            cand --accent-color 'Set the accent color using hex or color name'
            cand -c 'Set the main color using hex or color name'
            cand --color 'Set the main color using hex or color name'
            cand -t 'Set the refresh rate of the terminal'
            cand --tickrate 'Set the refresh rate of the terminal'
            cand -r 'Reverse the kernel module list'
            cand --reverse 'Reverse the kernel module list'
            cand -u 'Show Unicode symbols for the block titles'
            cand --unicode 'Show Unicode symbols for the block titles'
            cand -E 'Interpret the module search query as a regular expression'
            cand --regex 'Interpret the module search query as a regular expression'
            cand -h 'Print help'
            cand --help 'Print help'
            cand -V 'Print version'
            cand --version 'Print version'
            cand sort 'Sort kernel modules'
            cand help 'Print this message or the help of the given subcommand(s)'
        }
        &'kmon;sort'= {
            cand -s 'Sort modules by their sizes'
            cand --size 'Sort modules by their sizes'
            cand -n 'Sort modules by their names'
            cand --name 'Sort modules by their names'
            cand -d 'Sort modules by their dependent modules'
            cand --dependent 'Sort modules by their dependent modules'
            cand -h 'Print help'
            cand --help 'Print help'
        }
        &'kmon;help'= {
            cand sort 'Sort kernel modules'
            cand help 'Print this message or the help of the given subcommand(s)'
        }
        &'kmon;help;sort'= {
        }
        &'kmon;help;help'= {
        }
    ]
    $completions[$command]
}
