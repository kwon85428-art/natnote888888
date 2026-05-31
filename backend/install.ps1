# 安装依赖
# cd backend; .\install.ps1
$ErrorActionPreference = 'Stop'
$BackendDir = $PSScriptRoot
Set-Location $BackendDir

if (-not (Test-Path '.venv')) { python -m venv .venv }
$py = Join-Path $BackendDir '.venv\Scripts\python.exe'
& $py -m pip install -q -U pip setuptools wheel
& $py -m pip install -q -r requirements.txt

if (-not (Test-Path '.env')) {
    if ($args -contains '--prod' -and (Test-Path '.env.production.example')) {
        Copy-Item '.env.production.example' '.env'
    } elseif (Test-Path '.env.example') {
        Copy-Item '.env.example' '.env'
    }
}

New-Item -ItemType Directory -Force -Path data, uploads, .run | Out-Null
Write-Host "==> backend ready: $py"
