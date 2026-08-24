
using namespace System.Management.Automation
using namespace System.Management.Automation.Language

Register-ArgumentCompleter -Native -CommandName 'kmon' -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)

    $commandElements = $commandAst.CommandElements
    $command = @(
        'kmon'
        for ($i = 1; $i -lt $commandElements.Count; $i++) {
            $element = $commandElements[$i]
            if ($element -isnot [StringConstantExpressionAst] -or
                $element.StringConstantType -ne [StringConstantType]::BareWord -or
                $element.Value.StartsWith('-') -or
                $element.Value -eq $wordToComplete) {
                break
        }
        $element.Value
    }) -join ';'

    $completions = @(switch ($command) {
        'kmon' {
            [CompletionResult]::new('-a', '-a', [CompletionResultType]::ParameterName, 'Set the accent color using hex or color name')
            [CompletionResult]::new('--accent-color', '--accent-color', [CompletionResultType]::ParameterName, 'Set the accent color using hex or color name')
            [CompletionResult]::new('-c', '-c', [CompletionResultType]::ParameterName, 'Set the main color using hex or color name')
            [CompletionResult]::new('--color', '--color', [CompletionResultType]::ParameterName, 'Set the main color using hex or color name')
            [CompletionResult]::new('-t', '-t', [CompletionResultType]::ParameterName, 'Set the refresh rate of the terminal')
            [CompletionResult]::new('--tickrate', '--tickrate', [CompletionResultType]::ParameterName, 'Set the refresh rate of the terminal')
            [CompletionResult]::new('-r', '-r', [CompletionResultType]::ParameterName, 'Reverse the kernel module list')
            [CompletionResult]::new('--reverse', '--reverse', [CompletionResultType]::ParameterName, 'Reverse the kernel module list')
            [CompletionResult]::new('-u', '-u', [CompletionResultType]::ParameterName, 'Show Unicode symbols for the block titles')
            [CompletionResult]::new('--unicode', '--unicode', [CompletionResultType]::ParameterName, 'Show Unicode symbols for the block titles')
            [CompletionResult]::new('-E', '-E ', [CompletionResultType]::ParameterName, 'Interpret the module search query as a regular expression')
            [CompletionResult]::new('--regex', '--regex', [CompletionResultType]::ParameterName, 'Interpret the module search query as a regular expression')
            [CompletionResult]::new('-h', '-h', [CompletionResultType]::ParameterName, 'Print help')
            [CompletionResult]::new('--help', '--help', [CompletionResultType]::ParameterName, 'Print help')
            [CompletionResult]::new('-V', '-V ', [CompletionResultType]::ParameterName, 'Print version')
            [CompletionResult]::new('--version', '--version', [CompletionResultType]::ParameterName, 'Print version')
            [CompletionResult]::new('sort', 'sort', [CompletionResultType]::ParameterValue, 'Sort kernel modules')
            [CompletionResult]::new('help', 'help', [CompletionResultType]::ParameterValue, 'Print this message or the help of the given subcommand(s)')
            break
        }
        'kmon;sort' {
            [CompletionResult]::new('-s', '-s', [CompletionResultType]::ParameterName, 'Sort modules by their sizes')
            [CompletionResult]::new('--size', '--size', [CompletionResultType]::ParameterName, 'Sort modules by their sizes')
            [CompletionResult]::new('-n', '-n', [CompletionResultType]::ParameterName, 'Sort modules by their names')
            [CompletionResult]::new('--name', '--name', [CompletionResultType]::ParameterName, 'Sort modules by their names')
            [CompletionResult]::new('-d', '-d', [CompletionResultType]::ParameterName, 'Sort modules by their dependent modules')
            [CompletionResult]::new('--dependent', '--dependent', [CompletionResultType]::ParameterName, 'Sort modules by their dependent modules')
            [CompletionResult]::new('-h', '-h', [CompletionResultType]::ParameterName, 'Print help')
            [CompletionResult]::new('--help', '--help', [CompletionResultType]::ParameterName, 'Print help')
            break
        }
        'kmon;help' {
            [CompletionResult]::new('sort', 'sort', [CompletionResultType]::ParameterValue, 'Sort kernel modules')
            [CompletionResult]::new('help', 'help', [CompletionResultType]::ParameterValue, 'Print this message or the help of the given subcommand(s)')
            break
        }
        'kmon;help;sort' {
            break
        }
        'kmon;help;help' {
            break
        }
    })

    $completions.Where{ $_.CompletionText -like "$wordToComplete*" } |
        Sort-Object -Property ListItemText
}
