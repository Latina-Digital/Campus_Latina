<#
.SYNOPSIS
  Instala o reinstala Campus Latina en IIS (Windows Server).

.DESCRIPTION
  Ejecutar en PowerShell COMO ADMINISTRADOR desde la carpeta del proyecto:

    powershell -ExecutionPolicy Bypass -File .\deploy\instalar_iis.ps1 -IpPublica 181.78.203.134 -IpLocal 192.168.1.97 -Puerto 7010 -ApiKey "LA-API-KEY"

  o con dominio y HTTPS:

    powershell -ExecutionPolicy Bypass -File .\deploy\instalar_iis.ps1 -Dominio campus.latina.com.ec -Https -ApiKey "LA-API-KEY"

  Los usuarios y todos los datos vienen de la API Syspro (puerto 7070):
    - login:  api/syspro/users
    - datos:  api/syspro/campus/datos  (requiere deploy\api_campus\01_campus_nuevo.sql en la base CAMPUS)
  -ApiBase indica dónde está la API (por defecto http://192.168.1.97:7070).

  Es seguro volver a ejecutarlo: no borra datos ni reemplaza un .env existente
  (solo actualiza la API key y las URL de la API si se pasan -ApiKey / -ApiBase).

  Requisitos previos (ver DESPLIEGUE_IIS.md):
    - IIS instalado
    - HttpPlatformHandler v1.2  https://www.iis.net/downloads/microsoft/httpplatformhandler
    - Python 3.12 o superior instalado "para todos los usuarios"
    - URL Rewrite (solo si usas -Https, para redirigir http -> https)
#>
param(
    [string]$Dominio = "",
    [string]$IpPublica = "",
    [string]$IpLocal = "",
    [int]$Puerto = 80,
    [switch]$Https,
    [string]$NombreSitio = "CampusLatina",
    [string]$Python = "",
    [string]$ApiBase = "",
    [string]$ApiKey = ""
)

$ErrorActionPreference = "Stop"
$AppDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $AppDir

function Paso($texto) { Write-Host "`n==> $texto" -ForegroundColor Cyan }
function Falla($texto) { Write-Host "`nERROR: $texto" -ForegroundColor Red; exit 1 }

# Cambia CLAVE=valor en .env (también si estaba comentada) o la agrega al final.
function Set-EnvValor($clave, $valor) {
    $ruta = Join-Path $AppDir ".env"
    $texto = [IO.File]::ReadAllText($ruta)
    $linea = "$clave=$valor"
    $re = [regex]"(?m)^#?\s*$clave=.*$"
    if ($re.IsMatch($texto)) { $texto = $re.Replace($texto, [Text.RegularExpressions.MatchEvaluator]{ param($m) $linea }, 1) }
    else { $texto = $texto.TrimEnd() + "`r`n$linea`r`n" }
    [IO.File]::WriteAllText($ruta, $texto, (New-Object Text.UTF8Encoding $false))
}

# ---------------------------------------------------------------- Comprobaciones
Paso "Comprobando requisitos"
$admin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $admin) { Falla "Ejecuta PowerShell como Administrador." }
if (-not (Get-Service W3SVC -ErrorAction SilentlyContinue)) { Falla "IIS no está instalado." }
if (-not (Test-Path "$env:windir\System32\inetsrv\httpPlatformHandler.dll")) {
    Falla "Falta HttpPlatformHandler. Descárgalo de https://www.iis.net/downloads/microsoft/httpplatformhandler e instálalo."
}
$tieneRewrite = Test-Path "$env:windir\System32\inetsrv\rewrite.dll"
if ($Https -and -not $tieneRewrite) {
    Write-Host "Aviso: URL Rewrite no está instalado; no se agregará la redirección http -> https." -ForegroundColor Yellow
}
if (-not $Python) {
    $cmd = Get-Command py -ErrorAction SilentlyContinue
    if ($cmd) { $Python = (& py -3 -c "import sys; print(sys.executable)").Trim() }
    else {
        $cmd = Get-Command python -ErrorAction SilentlyContinue
        if (-not $cmd) { Falla "No se encontró Python. Instala Python 3.12+ marcando 'Install for all users' y 'Add to PATH'." }
        $Python = $cmd.Source
    }
}
$version = & $Python -c "import sys; print('%d.%d' % sys.version_info[:2])"
if ([version]$version -lt [version]"3.12") { Falla "Se requiere Python 3.12 o superior (encontrado $version)." }
if ($Python -like "*\Users\*") {
    Write-Host "Aviso: Python está instalado en una carpeta de usuario ($Python). IIS podría no tener acceso; se recomienda instalarlo para todos los usuarios." -ForegroundColor Yellow
}
Write-Host "Python $version -> $Python"

# ---------------------------------------------------------------- Entorno Python
Paso "Preparando entorno virtual y dependencias"
if (-not (Test-Path ".venv\Scripts\python.exe")) { & $Python -m venv .venv }
$VenvPy = Join-Path $AppDir ".venv\Scripts\python.exe"
& $VenvPy -m pip install --upgrade pip --quiet
& $VenvPy -m pip install -r requirements.txt --quiet
if ($LASTEXITCODE -ne 0) { Falla "No se pudieron instalar las dependencias." }

# ---------------------------------------------------------------- Archivo .env
$hosts = @("localhost", "127.0.0.1")
if ($Dominio) { $hosts += $Dominio }
if ($IpPublica) { $hosts += $IpPublica }
if ($IpLocal) { $hosts += $IpLocal }
$esquema = if ($Https) { "https" } else { "http" }
$hostPublico = if ($Dominio) { $Dominio } elseif ($IpPublica) { $IpPublica } else { "localhost" }
$puertoUrl = if (($Https -and $Puerto -eq 443) -or (-not $Https -and $Puerto -eq 80)) { "" } else { ":$Puerto" }
if ($Https -and $Puerto -eq 80) { $puertoUrl = "" }
$urlPublica = "${esquema}://$hostPublico$puertoUrl"

if (-not (Test-Path ".env")) {
    Paso "Creando .env de producción"
    $secret = & $VenvPy -c "import secrets; print(secrets.token_urlsafe(50))"
    $contenido = Get-Content ".env.example" -Raw -Encoding UTF8
    $contenido = $contenido -replace "(?m)^DJANGO_SECRET_KEY=.*$", "DJANGO_SECRET_KEY=$secret"
    $contenido = $contenido -replace "(?m)^DJANGO_DEBUG=.*$", "DJANGO_DEBUG=False"
    $contenido = $contenido -replace "(?m)^DJANGO_ALLOWED_HOSTS=.*$", "DJANGO_ALLOWED_HOSTS=$($hosts -join ',')"
    $contenido = $contenido -replace "(?m)^DJANGO_CSRF_TRUSTED_ORIGINS=.*$", "DJANGO_CSRF_TRUSTED_ORIGINS=$urlPublica"
    $contenido = $contenido -replace "(?m)^CAMPUS_PUBLIC_URL=.*$", "CAMPUS_PUBLIC_URL=$urlPublica"
    $contenido += "`r`n# --- Producción ---`r`nHTTPS=$(if ($Https) {'True'} else {'False'})`r`n"
    [IO.File]::WriteAllText((Join-Path $AppDir ".env"), $contenido, (New-Object Text.UTF8Encoding $false))
} else {
    Write-Host ".env ya existe: no se modifica."
    if ((Get-Content ".env" -Raw) -match "(?m)^DJANGO_DEBUG=True") {
        Write-Host "Aviso: .env tiene DJANGO_DEBUG=True. En un sitio público debe ser False." -ForegroundColor Yellow
    }
}

if ($ApiBase) {
    $ApiBase = $ApiBase.TrimEnd("/")
    Set-EnvValor "SYSPRO_API_URL" "$ApiBase/api/syspro/users"
    Set-EnvValor "CAMPUS_API_URL" "$ApiBase/api/syspro/campus/datos"
}
if ($ApiKey) { Set-EnvValor "SYSPRO_API_KEY" $ApiKey }
if ((Get-Content ".env" -Raw) -notmatch "(?m)^SYSPRO_API_KEY=\S") {
    Falla "Falta la API key de Syspro. Vuelve a ejecutar con -ApiKey ""LA-API-KEY"" (o escríbela en .env, SYSPRO_API_KEY)."
}

# ---------------------------------------------------------------- Django
Paso "Datos desde la API y archivos estáticos"
New-Item -ItemType Directory -Force -Path data, media, logs | Out-Null
& $VenvPy manage.py collectstatic --noinput -v 0
if ($LASTEXITCODE -ne 0) { Falla "Falló collectstatic." }
& $VenvPy manage.py cargar_api
if ($LASTEXITCODE -ne 0) { Falla "No se pudo leer la API del campus (ver el mensaje de arriba). Revisa CAMPUS_API_URL y la API key en .env." }
& $VenvPy manage.py check --deploy --fail-level ERROR
if ($LASTEXITCODE -ne 0) { Falla "La configuración tiene errores (ver arriba)." }

# ---------------------------------------------------------------- web.config
Paso "Generando web.config"
$redir = ""
if ($Https -and $tieneRewrite) {
    $redir = @"
    <rewrite>
      <rules>
        <rule name="Redirigir a HTTPS" stopProcessing="true">
          <match url="(.*)" />
          <conditions><add input="{HTTPS}" pattern="off" ignoreCase="true" /></conditions>
          <action type="Redirect" url="https://{HTTP_HOST}/{R:1}" redirectType="Permanent" />
        </rule>
      </rules>
    </rewrite>
"@
}
$plantilla = Get-Content "deploy\web.config.plantilla" -Raw -Encoding UTF8
$webConfig = $plantilla.Replace("{{PYTHON}}", $VenvPy).Replace("{{HTTPS_REDIRECT}}", $redir)
[IO.File]::WriteAllText((Join-Path $AppDir "web.config"), $webConfig, (New-Object Text.UTF8Encoding $false))

# ---------------------------------------------------------------- IIS
Paso "Configurando IIS (sitio '$NombreSitio')"
Import-Module WebAdministration
& "$env:windir\System32\inetsrv\appcmd.exe" unlock config -section:system.webServer/handlers | Out-Null
$poolPath = "IIS:\AppPools\$NombreSitio"
if (-not (Test-Path $poolPath)) { New-WebAppPool -Name $NombreSitio | Out-Null }
Set-ItemProperty $poolPath -Name managedRuntimeVersion -Value ""
Set-ItemProperty $poolPath -Name startMode -Value "AlwaysRunning"
Set-ItemProperty $poolPath -Name processModel.idleTimeout -Value ([TimeSpan]::Zero)
Set-ItemProperty $poolPath -Name processModel.loadUserProfile -Value $true

$sitePath = "IIS:\Sites\$NombreSitio"
if (-not (Test-Path $sitePath)) {
    $ocupado = Get-WebBinding | Where-Object { $_.bindingInformation -like "*:${Puerto}:*" -and $_.protocol -eq "http" }
    if ($ocupado) {
        Write-Host "Aviso: el puerto $Puerto ya lo usa otro sitio. Detén ese sitio o elige otro -Puerto." -ForegroundColor Yellow
    }
    New-Website -Name $NombreSitio -PhysicalPath $AppDir -ApplicationPool $NombreSitio -Port $Puerto -HostHeader $Dominio | Out-Null
} else {
    Set-ItemProperty $sitePath -Name physicalPath -Value $AppDir
    Set-ItemProperty $sitePath -Name applicationPool -Value $NombreSitio
}

# ---------------------------------------------------------------- Permisos
Paso "Asignando permisos a 'IIS AppPool\$NombreSitio'"
$cuenta = "IIS AppPool\$NombreSitio"
icacls $AppDir /grant "${cuenta}:(OI)(CI)RX" /T /Q | Out-Null
foreach ($dir in "data", "media", "logs") { icacls (Join-Path $AppDir $dir) /grant "${cuenta}:(OI)(CI)M" /T /Q | Out-Null }
$pyBase = & $Python -c "import sys; print(sys.base_prefix)"
icacls $pyBase /grant "${cuenta}:(OI)(CI)RX" /T /Q | Out-Null

# ---------------------------------------------------------------- Firewall
Paso "Firewall de Windows"
$regla = "Campus Latina ($Puerto)"
if (-not (Get-NetFirewallRule -DisplayName $regla -ErrorAction SilentlyContinue)) {
    New-NetFirewallRule -DisplayName $regla -Direction Inbound -Protocol TCP -LocalPort $Puerto -Action Allow | Out-Null
}
if ($Https -and -not (Get-NetFirewallRule -DisplayName "Campus Latina (443)" -ErrorAction SilentlyContinue)) {
    New-NetFirewallRule -DisplayName "Campus Latina (443)" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow | Out-Null
}

# ---------------------------------------------------------------- Arranque
Paso "Iniciando el sitio"
Restart-WebAppPool -Name $NombreSitio -ErrorAction SilentlyContinue
Start-Website -Name $NombreSitio -ErrorAction SilentlyContinue
Start-Sleep -Seconds 5
$hostPrueba = if ($Dominio) { $Dominio } else { "localhost" }
try {
    $r = Invoke-WebRequest "http://127.0.0.1:$Puerto/cuenta/ingresar/" -Headers @{ Host = $hostPrueba } -UseBasicParsing -TimeoutSec 90
    Write-Host "`nSitio respondiendo (HTTP $($r.StatusCode))." -ForegroundColor Green
} catch {
    Write-Host "`nEl sitio aún no responde: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host "Revisa logs\iis-stdout*.log y logs\campus.log"
}
Write-Host "`nURL pública: $urlPublica" -ForegroundColor Green
if ($Https) { Write-Host "Falta asociar el certificado SSL al sitio (puerto 443). Ver DESPLIEGUE_IIS.md." -ForegroundColor Yellow }
