# 后台启停：.\service.ps1 start dev|prod|stop|status
param(
    [Parameter(Position = 0)][string]$Action = 'help',
    [Parameter(Position = 1)][string]$Mode = 'dev'
)

$ErrorActionPreference = 'Stop'
$BackendDir = $PSScriptRoot
$RunDir = Join-Path $BackendDir '.run'
$PidFile = Join-Path $RunDir 'backend.pid'
$LogFile = Join-Path $RunDir 'backend.log'
$VenvPy = Join-Path $BackendDir '.venv\Scripts\python.exe'

function Get-Port {
    $line = Select-String -Path (Join-Path $BackendDir '.env') -Pattern '^\s*UVICORN_PORT=' -ErrorAction SilentlyContinue | Select-Object -Last 1
    if ($line) { return ($line.Line -split '=', 2)[1].Trim().Trim('"') }
    return '8000'
}

switch ($Action) {
    'start' {
        if (-not (Test-Path $VenvPy)) { throw 'run .\install.ps1 first' }
        New-Item -ItemType Directory -Force -Path $RunDir | Out-Null
        if (Test-Path $PidFile) {
            $old = [int]((Get-Content $PidFile -Raw).Trim())
            if (Get-Process -Id $old -ErrorAction SilentlyContinue) { throw "already running PID $old, run: .\service.ps1 stop" }
        }
        Push-Location $BackendDir
        try {
            if ($Mode -eq 'prod') {
                $env:NAVNOTE_SERVER = 'gunicorn'
                $proc = Start-Process -FilePath $VenvPy -ArgumentList '-m', 'gunicorn', '-c', 'gunicorn.conf.py', 'app.main:app' -PassThru `
                    -RedirectStandardOutput $LogFile -RedirectStandardError $LogFile -WindowStyle Hidden
            } else {
                $proc = Start-Process -FilePath $VenvPy -ArgumentList 'run.py' -PassThru `
                    -RedirectStandardOutput $LogFile -RedirectStandardError $LogFile -WindowStyle Hidden
            }
            $proc.Id | Set-Content $PidFile
            Write-Host "==> started [$Mode] PID=$($proc.Id) log=$LogFile"
        } finally { Pop-Location }
    }
    'stop' {
        if (Test-Path $PidFile) {
            $backendPid = [int]((Get-Content $PidFile -Raw).Trim())
            Stop-Process -Id $backendPid -Force -ErrorAction SilentlyContinue
            Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
            Write-Host "==> stopped PID $backendPid"
        }
        $port = Get-Port
        Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue |
            ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
    }
    'status' {
        if (Test-Path $PidFile) {
            $backendPid = [int]((Get-Content $PidFile -Raw).Trim())
            if (Get-Process -Id $backendPid -ErrorAction SilentlyContinue) {
                Write-Host "running PID=$backendPid"; exit 0
            }
        }
        Write-Host 'not running'; exit 1
    }
    default {
        Write-Host 'Usage: .\service.ps1 start dev|prod | stop | status'
    }
}
