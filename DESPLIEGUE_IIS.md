# Publicar Campus Latina en IIS

Guía para instalar el campus en un servidor Windows con IIS y dejarlo accesible desde internet.

## Cómo funciona

```
Internet ──https──> IIS (puerto 443/80, certificado SSL)
                     └─ HttpPlatformHandler ──http──> Waitress + Django (127.0.0.1, puerto interno)
                                                        ├─ SQL Server o data\campus.sqlite3 (base de datos)
                                                        ├─ media\                (videos, imágenes, PDFs subidos)
                                                        └─ API Syspro (7070)     (login corporativo)
```

IIS recibe las visitas, maneja el certificado HTTPS y arranca la aplicación Python automáticamente (también tras reiniciar el servidor). No hace falta crear ningún servicio aparte.

## 1. Requisitos en el servidor (una sola vez)

| Componente | Dónde conseguirlo | Nota |
| --- | --- | --- |
| IIS | Administrador del servidor → Agregar roles → Servidor web (IIS) | |
| **HttpPlatformHandler v1.2** | https://www.iis.net/downloads/microsoft/httpplatformhandler | Obligatorio |
| URL Rewrite 2.1 | https://www.iis.net/downloads/microsoft/url-rewrite | Para redirigir http → https |
| **Python 3.12 o superior** | https://www.python.org/downloads/windows/ | Marcar **Install for all users** y **Add python.exe to PATH** |
| Git | https://git-scm.com/download/win | Para descargar y actualizar el código |
| ODBC Driver 18 for SQL Server | https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server | Solo si los datos van en SQL Server |

## 2. Instalar

En PowerShell **como Administrador**:

```powershell
cd C:\inetpub
git clone https://github.com/Latina-Digital/Campus_Latina.git
cd Campus_Latina
```

Con dominio y HTTPS (recomendado):

```powershell
powershell -ExecutionPolicy Bypass -File .\deploy\instalar_iis.ps1 -Dominio campus.latina.com.ec -Https
```

Solo con IP pública y un puerto (`-IpLocal` permite entrar también desde la red interna):

```powershell
powershell -ExecutionPolicy Bypass -File .\deploy\instalar_iis.ps1 -IpPublica 181.78.203.134 -IpLocal 192.168.1.97 -Puerto 7010
```

Con IP pública y los datos en **SQL Server** del mismo servidor:

```powershell
powershell -ExecutionPolicy Bypass -File .\deploy\instalar_iis.ps1 -IpPublica 181.78.203.134 -IpLocal 192.168.1.97 -Puerto 7010 `
    -SqlServidor localhost -SqlBase CampusLatina -SqlUsuario campus -SqlClave "la-clave"
```

Sin `-SqlServidor` los datos quedan en SQLite (`data\campus.sqlite3`). Ver [SQL Server](#sql-server) para preparar el usuario.

El script:
1. Verifica los requisitos.
2. Crea el entorno de Python e instala las dependencias.
3. Genera el `.env` de producción con una clave secreta nueva y `DEBUG=False`.
4. Crea la base de datos (en SQL Server la crea si no existe), las tablas y el usuario `admin` (contraseña `Latina2026*`).
5. Crea el sitio y el grupo de aplicaciones en IIS.
6. Asigna permisos y abre el puerto en el firewall de Windows.

Se puede volver a ejecutar sin perder datos.

> Usa un puerto libre (el 7003 ya lo ocupa otro sitio). Para ver los puertos en uso: `Get-WebBinding | Select-Object bindingInformation`.

### SQL Server

El campus usa su **propia base** (`CampusLatina`) y crea sus tablas; no toca las bases de Syspro ni las del campus anterior.

1. Instala **ODBC Driver 18 for SQL Server** (64 bits).
2. En SQL Server Management Studio crea un inicio de sesión para el campus. Con permiso `dbcreator`, el instalador crea la base solo:

   ```sql
   CREATE LOGIN campus WITH PASSWORD = 'una-clave-segura', CHECK_POLICY = ON;
   ALTER SERVER ROLE dbcreator ADD MEMBER campus;
   ```

   Si prefieres crear la base tú mismo:

   ```sql
   CREATE DATABASE CampusLatina;
   USE CampusLatina;
   CREATE USER campus FOR LOGIN campus;
   ALTER ROLE db_owner ADD MEMBER campus;
   ```

3. SQL Server debe aceptar **autenticación de SQL Server** (modo mixto) y conexiones **TCP/IP** (SQL Server Configuration Manager). Si es una instancia con nombre, usa `-SqlServidor "localhost\NOMBRE"`.
4. Para probar la conexión en cualquier momento: `.venv\Scripts\python manage.py preparar_sqlserver`.

Para cambiar una instalación existente de SQLite a SQL Server, vuelve a ejecutar el instalador con los parámetros `-Sql*`. La base nueva empieza con el contenido de ejemplo; lo cargado en SQLite no se copia.

## 3. Configurar el login con Syspro

Edita `C:\inetpub\Campus_Latina\.env`:

```
SYSPRO_ENABLED=True
SYSPRO_API_URL=http://192.168.1.97:7070/api/syspro/users
SYSPRO_API_URLS=http://181.78.203.134:7070/api/syspro/users
SYSPRO_API_KEY=(la clave de la API)
SYSPRO_ADMIN_USERS=Xbriones
```

Si el campus está en la misma red que Syspro, usa la IP interna como principal. Luego reinicia el sitio (`Restart-WebAppPool CampusLatina`) y prueba con un usuario real:

```powershell
.venv\Scripts\python manage.py probar_syspro USUARIO CLAVE
```

## 4. HTTPS (certificado SSL)

Un campus con contraseñas debe publicarse con HTTPS.

- **Certificado gratuito (Let's Encrypt):** instala [win-acme](https://www.win-acme.com/), ejecuta `wacs.exe` y elige el sitio `CampusLatina`. Emite el certificado, crea el enlace 443 y lo renueva automáticamente. Requiere un dominio que apunte a la IP pública y el puerto 80 abierto.
- **Certificado comprado:** impórtalo en IIS (Certificados de servidor) y agrega un enlace `https` puerto 443 al sitio.

Después, en `.env`: `HTTPS=True` y `CAMPUS_PUBLIC_URL` / `DJANGO_CSRF_TRUSTED_ORIGINS` con `https://...`.

## 5. Red

- En el router o firewall perimetral: redirigir los puertos **80 y 443** (o el puerto elegido) hacia la IP interna del servidor.
- En el DNS del dominio: un registro **A** apuntando a la IP pública (por ejemplo `campus.latina.com.ec → 181.78.203.134`).
- El servidor debe poder llegar a la API de Syspro (puerto 7070).

## 6. Después de publicar

1. Ingresa con `admin` / `Latina2026*` y **cambia la contraseña**.
2. Si cargaste usuarios de prueba: `.venv\Scripts\python manage.py seed_campus --remove-demo`.
3. Revisa y ajusta los cursos de ejemplo desde el panel.
4. Programa el respaldo diario (Programador de tareas):
   `powershell -ExecutionPolicy Bypass -File C:\inetpub\Campus_Latina\deploy\respaldo.ps1`
   Copia la carpeta `backups` a otro disco o a la nube. Con SQL Server, ese respaldo incluye los archivos subidos (`media`); la base `CampusLatina` se respalda con los planes de mantenimiento de SQL Server, igual que las demás bases.

## Actualizar a una nueva versión

```powershell
powershell -ExecutionPolicy Bypass -File .\deploy\actualizar.ps1
```

Hace un respaldo, descarga los cambios, aplica migraciones y reinicia el sitio.

## Seguridad incluida

- `DEBUG=False`, clave secreta propia y hosts permitidos.
- La API key de Syspro solo vive en el servidor (`.env`), nunca en el navegador.
- Bloqueo de 15 minutos tras 5 intentos fallidos de login.
- Cookies seguras con HTTPS. IIS bloquea el acceso web a `.env`, `data`, `logs` y `.venv`.
- Videos, recursos y lecciones solo son accesibles con sesión iniciada.

## Si algo falla

| Síntoma | Revisar |
| --- | --- |
| Error 500.19 | Falta HttpPlatformHandler o URL Rewrite |
| Error 502.3 / el sitio no arranca | `logs\iis-stdout_*.log` (errores de Python) |
| "Bad Request (400)" | El dominio o IP no está en `DJANGO_ALLOWED_HOSTS` |
| "CSRF verification failed" | `DJANGO_CSRF_TRUSTED_ORIGINS` debe tener la URL exacta (con https y puerto) |
| Errores de la aplicación | `logs\campus.log` |
| No suben videos grandes | Límite de 1 GB en `web.config` (`maxAllowedContentLength`) |

## Capacidad

SQLite funciona bien para cientos de usuarios con uso normal. Si el campus crece mucho (muchos usuarios rindiendo evaluaciones al mismo tiempo), se puede pasar a SQL Server (ver [SQL Server](#sql-server)) o PostgreSQL cambiando las variables `DB_*` del `.env`.
