<#
  Actualiza Campus Latina con la última versión del repositorio.
  Ejecutar como Administrador:  powershell -ExecutionPolicy Bypass -File .\deploy\actualizar.ps1
#>
param([string]$NombreSitio = "CampusLatina")
$ErrorActionPreference = "Stop"
$AppDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $AppDir
$py = ".venv\Scripts\python.exe"

& (Join-Path $PSScriptRoot "respaldo.ps1")
git pull --ff-only
if ($LASTEXITCODE -ne 0) { Write-Host "git pull falló: revisa cambios locales." -ForegroundColor Red; exit 1 }
& $py -m pip install -r requirements.txt --quiet
& $py manage.py migrate --noinput
& $py manage.py collectstatic --noinput -v 0
Import-Module WebAdministration
Restart-WebAppPool -Name $NombreSitio
Write-Host "Campus actualizado." -ForegroundColor Green
