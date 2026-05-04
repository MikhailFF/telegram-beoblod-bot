param(
    [string]$DeployDir = "C:\bots\telegram-beoblod-bot",
    [string]$TaskName = "TelegramBeoblodBot"
)

$ErrorActionPreference = "Stop"

Write-Host "Task:"
Get-ScheduledTask -TaskName $TaskName | Select-Object TaskName, State

Write-Host "Processes:"
Get-CimInstance Win32_Process |
    Where-Object { $_.CommandLine -like "*morale_bot.bot*" } |
    Select-Object ProcessId, CommandLine

$EnvPath = Join-Path $DeployDir ".env"
$LogPath = Join-Path $DeployDir "bot.log"
$Token = $null

if (Test-Path $EnvPath) {
    $TokenLine = Get-Content -LiteralPath $EnvPath |
        Where-Object { $_ -like "TELEGRAM_BOT_TOKEN=*" } |
        Select-Object -First 1
    if ($TokenLine) {
        $Token = $TokenLine.Substring("TELEGRAM_BOT_TOKEN=".Length)
    }
}

Write-Host "Log tail:"
if (Test-Path $LogPath) {
    Get-Content -LiteralPath $LogPath -Tail 40 | ForEach-Object {
        if ($Token) {
            $_ -replace [regex]::Escape($Token), "<TOKEN>"
        } else {
            $_
        }
    }
} else {
    Write-Host "No log file found."
}
