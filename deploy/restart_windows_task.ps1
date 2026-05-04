param(
    [string]$TaskName = "TelegramBeoblodBot"
)

$ErrorActionPreference = "Stop"

try {
    Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
} catch {
}

$BotProcesses = Get-CimInstance Win32_Process |
    Where-Object { $_.CommandLine -like "*morale_bot.bot*" }

foreach ($Process in $BotProcesses) {
    Stop-Process -Id $Process.ProcessId -Force -ErrorAction SilentlyContinue
}

Start-ScheduledTask -TaskName $TaskName
Start-Sleep -Seconds 5

Get-CimInstance Win32_Process |
    Where-Object { $_.CommandLine -like "*morale_bot.bot*" } |
    Select-Object ProcessId, CommandLine
