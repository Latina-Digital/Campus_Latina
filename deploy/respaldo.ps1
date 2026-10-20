<#
  Respaldo de la base de datos y los archivos subidos (videos, imágenes, PDFs).
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

# Copia consistente de SQLite usando la API de respaldo de Python.
$db = Join-Path $AppDir "data\campus.sqlite3"
if (-not (Test-Path $db)) { $db = Join-Path $AppDir "db.sqlite3" }
if (Test-Path $db) {
    & (Join-Path $AppDir ".venv\Scripts\python.exe") -c "import sqlite3,sys; s=sqlite3.connect(sys.argv[1]); d=sqlite3.connect(sys.argv[2]); s.backup(d); d.close(); s.close()" $db (Join-Path $tmp "campus.sqlite3")
}
if (Test-Path (Join-Path $AppDir "media")) { Copy-Item (Join-Path $AppDir "media") (Join-Path $tmp "media") -Recurse }
Copy-Item (Join-Path $AppDir ".env") (Join-Path $tmp ".env") -ErrorAction SilentlyContinue

$zip = Join-Path $Destino "campus_$stamp.zip"
Compress-Archive -Path "$tmp\*" -DestinationPath $zip
Remove-Item $tmp -Recurse -Force
Get-ChildItem $Destino -Filter "campus_*.zip" | Sort-Object Name -Descending | Select-Object -Skip $Conservar | Remove-Item -Force
Write-Host "Respaldo creado: $zip" -ForegroundColor Green
