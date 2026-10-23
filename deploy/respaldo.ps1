<#
  Respaldo de los archivos subidos (videos, imágenes, PDFs) y del .env.
  Los datos del campus están en SQL Server (base CAMPUS, tablas dbo.CV_*): se
  respaldan con los planes de mantenimiento de SQL Server, no con este script.
  Guarda un .zip en la carpeta backups y conserva los últimos 14.
  Se puede programar a diario con el Programador de tareas de Windows.
#>
param([string]$Destino = "", [int]$Conservar = 14)
$ErrorActionPreference = "Stop"
$AppDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
if (-not $Destino) { $Destino = Join-Path $AppDir "backups" }
New-Item -ItemType Directory -Force -Path $Destino | Out-Null
$stamp = Get-Date -Format "yyyyMMdd_HHmm"
$tmp = Join-Path $env:TEMP "campus_respaldo_$stamp"
New-Item -ItemType Directory -Force -Path $tmp | Out-Null

if (Test-Path (Join-Path $AppDir "media")) { Copy-Item (Join-Path $AppDir "media") (Join-Path $tmp "media") -Recurse }
Copy-Item (Join-Path $AppDir ".env") (Join-Path $tmp ".env") -ErrorAction SilentlyContinue

$zip = Join-Path $Destino "campus_$stamp.zip"
Compress-Archive -Path "$tmp\*" -DestinationPath $zip
Remove-Item $tmp -Recurse -Force
Get-ChildItem $Destino -Filter "campus_*.zip" | Sort-Object Name -Descending | Select-Object -Skip $Conservar | Remove-Item -Force
Write-Host "Respaldo creado: $zip" -ForegroundColor Green
