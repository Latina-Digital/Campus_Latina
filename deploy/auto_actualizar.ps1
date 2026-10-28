<#
  Actualización automática del campus desde GitHub.

  Revisa si hay commits nuevos en GitHub y, solo si los hay, ejecuta
  actualizar.ps1 (respaldo, git pull, migraciones, archivos estáticos y
  reinicio del sitio). Si no hay cambios no hace nada.

  Instalar UNA VEZ en el servidor (PowerShell como Administrador):
    powershell -ExecutionPolicy Bypass -File .\deploy\auto_actualizar.ps1 -Instalar
  Eso crea la tarea programada "CampusLatina-Actualizar", que lo ejecuta cada
  5 minutos. Para quitarla:
    Unregister-ScheduledTask -TaskName CampusLatina-Actualizar -Confirm:$false

  Cada actualización queda anotada en logs\auto_actualizar.log.
#>
param([switch]$Instalar, [int]$Minutos = 5, [string]$NombreSitio = "CampusLatina")
$ErrorActionPreference = "Stop"
$AppDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

if ($Instalar) {
    $accion = New-ScheduledTaskAction -Execute "powershell.exe" `
        -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`" -NombreSitio $NombreSitio" -WorkingDirectory $AppDir
    $disparador = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes $Minutos)
    $usuario = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
    $opciones = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 30)
    Register-ScheduledTask -TaskName "$NombreSitio-Actualizar" -Action $accion -Trigger $disparador `
        -Principal $usuario -Settings $opciones -Force | Out-Null
    Write-Host "Tarea '$NombreSitio-Actualizar' creada: revisa GitHub cada $Minutos minutos." -ForegroundColor Green
    exit 0
}

Set-Location $AppDir
# La tarea corre como SYSTEM, que no es dueño de la carpeta: git la rechazaría sin esto.
# Las variables se heredan también al git pull de actualizar.ps1.
$env:GIT_CONFIG_COUNT = "1"
$env:GIT_CONFIG_KEY_0 = "safe.directory"
$env:GIT_CONFIG_VALUE_0 = $AppDir.Replace("\", "/")

$log = Join-Path $AppDir "logs\auto_actualizar.log"
New-Item -ItemType Directory -Force -Path (Split-Path $log) | Out-Null
function Anotar($texto) { Add-Content -Path $log -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  $texto" -Encoding utf8 }

git fetch --quiet origin
if ($LASTEXITCODE -ne 0) { Anotar "No se pudo conectar con GitHub."; exit 1 }
$local = (git rev-parse HEAD).Trim()
$remoto = (git rev-parse "@{u}").Trim()
if ($local -eq $remoto) { exit 0 }

Anotar "Cambios nuevos ($($local.Substring(0,7)) -> $($remoto.Substring(0,7))). Actualizando..."
try {
    & (Join-Path $PSScriptRoot "actualizar.ps1") -NombreSitio $NombreSitio *>> $log
    Anotar "Actualizado a $((git rev-parse --short HEAD).Trim())."
} catch {
    Anotar "Falló la actualización: $_"
    exit 1
}
