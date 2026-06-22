param(
    [string]$BackendPort = "8000",
    [string]$FrontendPort = "5173"
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = (Join-Path $root "backend").Replace('\', '\\')
$frontendDir = (Join-Path $root "frontend").Replace('\', '\\')

function Stop-CommandTree {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Pattern,
        [Parameter(Mandatory = $true)]
        [string]$Label
    )

    $matches = Get-CimInstance Win32_Process |
        Where-Object { $_.CommandLine -and $_.CommandLine -match $Pattern }

    if (-not $matches) {
        Write-Host "$Label not found"
        return
    }

    foreach ($proc in $matches) {
        try {
            Stop-Process -Id $proc.ProcessId -Force -ErrorAction Stop
            Write-Host "Stopped $Label (PID $($proc.ProcessId))"
        } catch {
            Write-Host "Could not stop $Label (PID $($proc.ProcessId)): $($_.Exception.Message)"
        }
    }
}

$backendPattern = "uvicorn\s+app\.main:app.*--port\s+$BackendPort"
$frontendPattern = "npm\s+run\s+dev.*--port\s+$FrontendPort"

Stop-CommandTree -Pattern $backendPattern -Label "backend"
Stop-CommandTree -Pattern $frontendPattern -Label "frontend"

# Fallback for leftover port listeners.
$ports = @($BackendPort, $FrontendPort)
foreach ($port in $ports) {
    $listeners = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    if ($listeners) {
        $listeners | Select-Object -ExpandProperty OwningProcess -Unique | ForEach-Object {
            try {
                Stop-Process -Id $_ -Force -ErrorAction Stop
                Write-Host "Stopped listener PID $_ on port $port"
            } catch {
                Write-Host "Could not stop listener PID $_ on port $port: $($_.Exception.Message)"
            }
        }
    }
}
