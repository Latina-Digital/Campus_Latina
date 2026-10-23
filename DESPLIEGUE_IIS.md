# Publicar Campus Latina en IIS

Guía para instalar el campus en un servidor Windows con IIS y dejarlo accesible desde internet.

## Cómo funciona

```
Internet ──http(s)──> IIS (puerto del campus, ej. 7010)
                       └─ HttpPlatformHandler ──http──> Waitress + Django (127.0.0.1, puerto interno)
                                                          ├─ API Syspro (7070) /api/syspro/users          login
                                                          ├─ API Syspro (7070) /api/syspro/campus/datos   todos los datos
                                                          │                     └─ SQL Server, base CAMPUS, tablas dbo.CV_*
                                                          ├─ media\   videos, imágenes y PDF subidos
                                                          └─ data\    copia de trabajo y sesiones (se rehace al arrancar)
```

- **Usuarios:** son los de Syspro. No hay cuentas propias del campus; el rol y el supervisor vienen de `api/syspro/users`.
- **Datos:** cursos, avance, evaluaciones, certificados, productos y anuncios se guardan en SQL Server a través de `api/syspro/campus/datos`. El campus no se conecta a SQL Server directamente.
- **Copia de trabajo:** al arrancar, el campus descarga todos los datos de la API y los guarda en `data\copia_api.sqlite3` para leerlos rápido. Cada cambio se envía primero a la API; si la API falla, el cambio se cancela. Por eso los datos nunca quedan solo en el servidor del campus.
- **Archivos subidos** (videos, portadas, PDF): quedan en la carpeta `media\` del servidor. En la base solo se guarda su ruta.

IIS recibe las visitas y arranca la aplicación Python automáticamente (también tras reiniciar el servidor). No hace falta crear ningún servicio aparte.

## 1. Requisitos en el servidor (una sola vez)

| Componente | Dónde conseguirlo | Nota |
| --- | --- | --- |
| IIS | Administrador del servidor → Agregar roles → Servidor web (IIS) | |
| **HttpPlatformHandler v1.2** | https://www.iis.net/downloads/microsoft/httpplatformhandler | Obligatorio |
| URL Rewrite 2.1 | https://www.iis.net/downloads/microsoft/url-rewrite | Solo para redirigir http → https |
| **Python 3.12 o superior** | https://www.python.org/downloads/windows/ | Marcar **Install for all users** y **Add python.exe to PATH** |
| Git | https://git-scm.com/download/win | Para descargar y actualizar el código |

En la **API Syspro** (puerto 7070):

1. Ejecutar [`deploy/api_campus/01_campus_nuevo.sql`](deploy/api_campus/01_campus_nuevo.sql) en la base **CAMPUS**. Crea las tablas `dbo.CV_*` y el procedimiento `dbo.spCampus_Datos`; no toca las tablas del campus anterior.
2. Agregar a la API el endpoint `api/syspro/campus/datos` de [`deploy/api_campus/CampusDatos.cs`](deploy/api_campus/CampusDatos.cs) y publicarla.

## 2. Instalar

En PowerShell **como Administrador**:

```powershell
cd C:\inetpub
git clone https://github.com/Latina-Digital/Campus_Latina.git
cd Campus_Latina
powershell -ExecutionPolicy Bypass -File .\deploy\instalar_iis.ps1 -IpPublica 181.78.203.134 -IpLocal 192.168.1.97 -Puerto 7010 -ApiKey "LA-API-KEY"
```

- `-IpLocal` permite entrar también desde la red interna.
- `-ApiBase` indica dónde está la API si no es `http://192.168.1.97:7070`.
- Con dominio y HTTPS: `-Dominio campus.latina.com.ec -Https` en lugar de `-IpPublica`/`-Puerto`.

El script:
1. Verifica los requisitos.
2. Crea el entorno de Python e instala las dependencias.
3. Genera el `.env` de producción con una clave secreta nueva y `DEBUG=False`, y guarda la API key.
4. Prueba la API y descarga los datos del campus.
5. Crea el sitio y el grupo de aplicaciones en IIS.
6. Asigna permisos y abre el puerto en el firewall de Windows.

Se puede volver a ejecutar sin perder datos.

> Usa un puerto libre (el 7003 ya lo ocupa otro sitio). Para ver los puertos en uso: `Get-WebBinding | Select-Object bindingInformation`.

### Contenido inicial

La primera vez, las tablas están vacías. Para cargar los cursos, productos y rutas de ejemplo (se guardan en SQL Server por la API):

```powershell
.venv\Scripts\python manage.py seed_campus
Restart-WebAppPool CampusLatina
```

Solo carga el contenido si todavía no hay cursos. Revisa los textos con las fichas técnicas oficiales antes de publicarlos al equipo.

## 3. Configuración de la API en `.env`

El instalador deja esto en `C:\inetpub\Campus_Latina\.env`:

```
SYSPRO_ENABLED=True
SYSPRO_API_URL=http://192.168.1.97:7070/api/syspro/users
SYSPRO_API_URLS=http://181.78.203.134:7070/api/syspro/users
SYSPRO_API_KEY=(la API key)
SYSPRO_ADMIN_USERS=Xbriones

CAMPUS_API_URL=http://192.168.1.97:7070/api/syspro/campus/datos
CAMPUS_API_URLS=http://181.78.203.134:7070/api/syspro/campus/datos
CAMPUS_API_KEY=            (vacía = la misma SYSPRO_API_KEY)
```

Usa la IP interna como principal: el campus y la API están en el mismo servidor. Después de cambiar `.env`, reinicia el sitio (`Restart-WebAppPool CampusLatina`).

Para probar:

```powershell
.venv\Scripts\python manage.py probar_syspro USUARIO CLAVE   # login
.venv\Scripts\python manage.py cargar_api                    # datos
```

### Roles

El rol sale del campo `rol` de Syspro:

| Si `rol` contiene… | Rol en el campus |
| --- | --- |
| admin | Administrador |
| nacional | Jefe nacional de ventas |
| jefe, gerente | Jefe de ventas |
| super | Supervisor |
| (otro) | Ejecutivo comercial |

Los usuarios listados en `SYSPRO_ADMIN_USERS` entran siempre como administradores.

## 4. HTTPS (certificado SSL)

Un campus con contraseñas debería publicarse con HTTPS.

- **Certificado gratuito (Let's Encrypt):** instala [win-acme](https://www.win-acme.com/), ejecuta `wacs.exe` y elige el sitio `CampusLatina`. Emite el certificado, crea el enlace 443 y lo renueva automáticamente. Requiere un dominio que apunte a la IP pública y el puerto 80 abierto.
- **Certificado comprado:** impórtalo en IIS (Certificados de servidor) y agrega un enlace `https` puerto 443 al sitio.

Después, en `.env`: `HTTPS=True` y `CAMPUS_PUBLIC_URL` / `DJANGO_CSRF_TRUSTED_ORIGINS` con `https://...`.

## 5. Red

- En el router o firewall perimetral: redirigir el puerto del campus (ej. **7010**) hacia `192.168.1.97`.
- Con dominio: un registro **A** apuntando a la IP pública (por ejemplo `campus.latina.com.ec → 181.78.203.134`).
- El servidor del campus debe llegar a la API Syspro (puerto 7070).

## 6. Después de publicar

1. Ingresa con un usuario de Syspro con rol administrador (o incluido en `SYSPRO_ADMIN_USERS`).
2. Revisa y ajusta los cursos desde el panel (`/panel/`).
3. Respaldos:
   - **Datos:** están en SQL Server (base `CAMPUS`, tablas `dbo.CV_*`). Se respaldan con los planes de mantenimiento de SQL Server, igual que las demás bases.
   - **Archivos subidos:** programa a diario (Programador de tareas)
     `powershell -ExecutionPolicy Bypass -File C:\inetpub\Campus_Latina\deploy\respaldo.ps1`
     y copia la carpeta `backups` a otro disco o a la nube.

## Actualizar a una nueva versión

```powershell
powershell -ExecutionPolicy Bypass -File .\deploy\actualizar.ps1
```

Hace un respaldo de los archivos, descarga los cambios y reinicia el sitio (que vuelve a cargar los datos de la API).

## Seguridad incluida

- `DEBUG=False`, clave secreta propia y hosts permitidos.
- La API key solo vive en el servidor (`.env`), nunca en el navegador.
- El procedimiento `dbo.spCampus_Datos` solo acepta tablas `dbo.CV_*`, valida cada columna y recibe los valores como parámetros.
- Bloqueo de 15 minutos tras 5 intentos fallidos de login.
- Cookies seguras con HTTPS. IIS bloquea el acceso web a `.env`, `data`, `logs` y `.venv`.
- Videos, recursos y lecciones solo son accesibles con sesión iniciada.

## Si algo falla

| Síntoma | Revisar |
| --- | --- |
| Error 500.19 | Falta HttpPlatformHandler o URL Rewrite |
| Error 502.3 / el sitio no arranca | `logs\iis-stdout_*.log`. Si dice "No se pudo conectar con la API del campus", revisa que la API (7070) esté arriba y `CAMPUS_API_URL` |
| "No pudimos conectarnos con el sistema corporativo" al ingresar | La API de usuarios (`SYSPRO_API_URL`) no responde |
| Error al guardar ("API del campus: ...") | El mensaje trae el error de SQL Server; `logs\campus.log` |
| Cambios hechos directamente en SQL Server no aparecen | El campus lee la copia de trabajo: reinicia el sitio o ejecuta `manage.py cargar_api` |
| "Bad Request (400)" | El dominio o IP no está en `DJANGO_ALLOWED_HOSTS` |
| "CSRF verification failed" | `DJANGO_CSRF_TRUSTED_ORIGINS` debe tener la URL exacta (con https y puerto) |
| No suben videos grandes | Límite de 1 GB en `web.config` (`maxAllowedContentLength`) |
