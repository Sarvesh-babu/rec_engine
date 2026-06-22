param(
    [string]$BackendPort = "8000",
    [string]$FrontendPort = "5173"
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Join-Path $root "backend"
$frontendDir = Join-Path $root "frontend"
$backendVenv = Join-Path $backendDir "venv\Scripts\Activate.ps1"

if (!(Test-Path $backendVenv)) {
    throw "Backend virtual environment not found at $backendVenv"
}

if (!(Test-Path (Join-Path $frontendDir "package.json"))) {
    throw "Frontend package.json not found at $frontendDir"
}

Start-Process PowerShell -WindowStyle Hidden -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "& `"$backendVenv`"; Set-Location `"$backendDir`"; uvicorn app.main:app --reload --host 127.0.0.1 --port $BackendPort"
)

Start-Process PowerShell -WindowStyle Hidden -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "Set-Location `"$frontendDir`"; npm run dev -- --host 127.0.0.1 --port $FrontendPort"
)

Write-Host "Backend:  http://127.0.0.1:$BackendPort"
Write-Host "Frontend: http://127.0.0.1:$FrontendPort"
