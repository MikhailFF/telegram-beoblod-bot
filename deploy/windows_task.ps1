param(
    [string]$RepoZipUrl = "https://github.com/MikhailFF/telegram-beoblod-bot/archive/refs/heads/main.zip",
    [string]$DeployDir = "C:\bots\telegram-beoblod-bot",
    [string]$TaskName = "TelegramBeoblodBot"
)

$ErrorActionPreference = "Stop"

$DeployRoot = Split-Path -Parent $DeployDir
$ArchivePath = Join-Path $env:TEMP "telegram-beoblod-bot-main.zip"
$ExtractDir = Join-Path $env:TEMP "telegram-beoblod-bot-main-extract"
$EnvBackupPath = Join-Path $env:TEMP "telegram-beoblod-bot.env.backup"

New-Item -ItemType Directory -Force -Path $DeployRoot | Out-Null

try {
    Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
} catch {
}

if (Test-Path (Join-Path $DeployDir ".env")) {
    Copy-Item -LiteralPath (Join-Path $DeployDir ".env") -Destination $EnvBackupPath -Force
}

if (Test-Path $ArchivePath) {
    Remove-Item -LiteralPath $ArchivePath -Force
}

if (Test-Path $ExtractDir) {
    Remove-Item -LiteralPath $ExtractDir -Recurse -Force
}

Write-Host "Downloading $RepoZipUrl"
Invoke-WebRequest -Uri $RepoZipUrl -OutFile $ArchivePath -UseBasicParsing

New-Item -ItemType Directory -Force -Path $ExtractDir | Out-Null
Expand-Archive -LiteralPath $ArchivePath -DestinationPath $ExtractDir -Force

$ExpandedProject = Get-ChildItem -LiteralPath $ExtractDir -Directory | Select-Object -First 1
if (-not $ExpandedProject) {
    throw "Could not find expanded project directory."
}

if (Test-Path $DeployDir) {
    $ResolvedRoot = (Resolve-Path $DeployRoot).Path
    $ResolvedDeploy = (Resolve-Path $DeployDir).Path
    if (-not $ResolvedDeploy.StartsWith($ResolvedRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to remove unexpected path: $ResolvedDeploy"
    }
    Remove-Item -LiteralPath $DeployDir -Recurse -Force
}

Move-Item -LiteralPath $ExpandedProject.FullName -Destination $DeployDir

if (Test-Path $EnvBackupPath) {
    Copy-Item -LiteralPath $EnvBackupPath -Destination (Join-Path $DeployDir ".env") -Force
}

if (-not (Test-Path (Join-Path $DeployDir ".env"))) {
    throw "Missing .env in $DeployDir. Copy it before starting the bot."
}

$PythonCommand = Get-Command python -ErrorAction SilentlyContinue
if (-not $PythonCommand) {
    throw "Python was not found on PATH."
}

$VenvDir = Join-Path $DeployDir ".venv"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
$RunCmd = Join-Path $DeployDir "run_bot.cmd"
$LogPath = Join-Path $DeployDir "bot.log"

& $PythonCommand.Source -m venv $VenvDir
& $VenvPython -m pip install --upgrade pip
& $VenvPython -m pip install -e $DeployDir

$RunCmdContent = @"
@echo off
cd /d "$DeployDir"
"$VenvPython" -m morale_bot.bot >> "$LogPath" 2>&1
"@
Set-Content -LiteralPath $RunCmd -Value $RunCmdContent -Encoding ASCII

$Action = New-ScheduledTaskAction -Execute $RunCmd
$Trigger = New-ScheduledTaskTrigger -AtStartup
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -RunLevel Highest
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Principal $Principal -Force | Out-Null

Start-ScheduledTask -TaskName $TaskName
Start-Sleep -Seconds 5

$BotProcess = Get-CimInstance Win32_Process |
    Where-Object { $_.CommandLine -like "*morale_bot.bot*" } |
    Select-Object -First 1 ProcessId, CommandLine

if ($BotProcess) {
    Write-Host "Bot is running. PID: $($BotProcess.ProcessId)"
} else {
    Write-Host "Bot process was not found. Last log lines:"
    if (Test-Path $LogPath) {
        Get-Content -LiteralPath $LogPath -Tail 40
    }
    exit 1
}
