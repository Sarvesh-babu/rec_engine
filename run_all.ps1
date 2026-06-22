param(
    [string]$BackendPort = "8000",
    [string]$FrontendPort = "5173"
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Join-Path $root "backend"
$frontendDir = Join-Path $root "frontend"
# venv lives outside the project (and outside OneDrive) because this project's
# path is long enough to hit Windows' 260-char path limit, which breaks
# installing packages (e.g. torch) that have deeply nested internal files.
$backendVenv = "C:\venvs\rec_engine_venv\Scripts\Activate.ps1"

if (!(Test-Path $backendVenv)) {
    throw "Backend virtual environment not found at $backendVenv"
}

if (!(Test-Path (Join-Path $frontendDir "package.json"))) {
    throw "Frontend package.json not found at $frontendDir"
}

# Launch via temp script files (-File) rather than inline -Command strings:
# this project's path contains an "&", which breaks PowerShell's command-line
# parsing when a multi-statement -Command string is round-tripped through
# Start-Process -ArgumentList (the & gets parsed as the reserved operator
# instead of literal text, and the process silently does nothing).
$backendScript = Join-Path $env:TEMP "rec_engine_backend_launch.ps1"
$frontendScript = Join-Path $env:TEMP "rec_engine_frontend_launch.ps1"

@"
& '$backendVenv'
Set-Location '$backendDir'
uvicorn app.main:app --reload --host 127.0.0.1 --port $BackendPort
"@ | Set-Content -Path $backendScript -Encoding UTF8

@"
Set-Location '$frontendDir'
npm run dev -- --host 127.0.0.1 --port $FrontendPort
"@ | Set-Content -Path $frontendScript -Encoding UTF8

Start-Process PowerShell -WindowStyle Hidden -ArgumentList @(
    "-NoExit", "-ExecutionPolicy", "Bypass", "-File", $backendScript
)

Start-Process PowerShell -WindowStyle Hidden -ArgumentList @(
    "-NoExit", "-ExecutionPolicy", "Bypass", "-File", $frontendScript
)

Write-Host "Backend:  http://127.0.0.1:$BackendPort"
Write-Host "Frontend: http://127.0.0.1:$FrontendPort"
