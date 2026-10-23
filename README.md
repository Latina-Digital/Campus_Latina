# Campus Latina

Plataforma de formación de **Industrial Latina S.A.** e **Induless**: cursos sobre los productos de la empresa, evaluaciones con tiempo límite, certificados en PDF verificables con código QR, rutas de aprendizaje, ranking y un panel de gestión.

## Funcionalidades

**Para colaboradores**
- Inicio personalizado: cursos en progreso, obligatorios, recomendados, nivel y puntos.
- Explorar cursos con búsqueda y filtros (marca, categoría, nivel) y orden por popularidad o valoración.
- Reproductor de lecciones: video subido (no se puede adelantar la primera vez y se retoma donde quedó), YouTube, lecturas y PDF.
- Evaluación final: preguntas al azar, opciones mezcladas, temporizador, autoguardado y revisión de respuestas.
- Certificados en PDF con código QR, página pública de verificación y botón "Agregar a LinkedIn".
- Rutas de aprendizaje, cursos guardados, reseñas con estrellas, catálogo de productos.
- Gamificación: puntos, 5 niveles, insignias, ranking por persona y por equipo (supervisor).
- "Mi equipo" para supervisores y jefaturas. Modo claro/oscuro y diseño adaptado a celulares.

**Panel de gestión** (`/panel/`)
- Resumen con indicadores y gráficos.
- Constructor de cursos: módulos, lecciones con editor de texto enriquecido, materiales descargables y evaluación.
- Banco de preguntas: carga manual o importación desde **Word (.docx)**, **Excel/CSV** o texto pegado.
- Usuarios: consulta de quienes ya ingresaron (los usuarios, roles y supervisores se administran en Syspro).
- Resultados con filtros, exportación a Excel/CSV e informe imprimible por intento.
- Certificados (consulta y revocación), productos, categorías, rutas y anuncios.

## Tecnología

| Capa | Herramienta |
| --- | --- |
| Backend | Python 3.12+ · Django 6 |
| Datos | SQL Server a través de la API Syspro (`api/syspro/campus/datos`) · copia de trabajo local en SQLite |
| Frontend | Plantillas Django · CSS propio con variables de tema · Alpine.js · Lucide · Chart.js · Quill |
| PDF | ReportLab (certificados con QR) |
| Importación | python-docx, openpyxl |
| Producción | Waitress + WhiteNoise |

Las librerías de JavaScript están en `static/vendor/`, así que el campus funciona en una red interna sin internet. Solo las fuentes de Google tienen respaldo con fuentes del sistema.

## Estructura

```
config/            Configuración del proyecto (settings, urls)
apps/accounts/     Usuarios, roles, login con Syspro, perfil, Mi equipo
apps/apidata/      Conexión con la API de datos: carga inicial y envío de cada cambio
apps/courses/      Cursos, módulos, lecciones, progreso, reseñas, rutas
apps/assessments/  Evaluaciones, preguntas, intentos y calificación
apps/certificates/ Certificados, PDF con QR y verificación pública
apps/catalog/      Catálogo de productos
apps/core/         Portada, ranking, gamificación, anuncios, datos iniciales (seed)
apps/panel/        Panel de gestión e importadores
templates/         HTML de todas las páginas
deploy/api_campus/ Script SQL (tablas dbo.CV_*) y código C# del endpoint para la API Syspro
static/            CSS, JS, imágenes de marca y librerías
legacy/            Versión anterior (index.html único) como referencia
```

## Dónde están los datos

- **Usuarios:** los de Syspro. Se ingresa con el usuario y la clave de Syspro (`api/syspro/users`); no hay cuentas propias del campus.
- **Todo lo demás** (cursos, avance, evaluaciones, certificados, productos, anuncios): en SQL Server, base `CAMPUS`, tablas `dbo.CV_*`, a través del endpoint `api/syspro/campus/datos`. El script de las tablas y el código C# del endpoint están en [deploy/api_campus/](deploy/api_campus/).
- Al arrancar, el campus descarga todo desde la API a una copia de trabajo (`data/copia_api.sqlite3`) para leer rápido. Cada cambio se envía primero a la API; si la API falla, el cambio se cancela.
- Los archivos subidos (videos, portadas, PDF) quedan en `media/`.

## Puesta en marcha (Windows)

Opción rápida: doble clic en **`iniciar_campus.bat`**. La primera vez instala todo y crea el `.env`: escribe la API key en `SYSPRO_API_KEY` y vuelve a ejecutarlo. Abre el campus en http://127.0.0.1:8000.

Opción manual:

```bash
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
copy .env.example .env               # y escribe la API key en SYSPRO_API_KEY
.venv\Scripts\python manage.py cargar_api       # prueba la API y descarga los datos
.venv\Scripts\python manage.py runserver 0.0.0.0:8000
```

### Contenido de ejemplo

Si la API todavía no tiene cursos, `seed_campus` carga 6 cursos (Duralin, Satinado, Elastomérico, Siliconas, Induzinc y Venta consultiva), 8 productos, 3 rutas y un anuncio, y los guarda en SQL Server por la API:

```bash
.venv\Scripts\python manage.py seed_campus
```

**Revisa los textos con las fichas técnicas oficiales** antes de publicarlos al equipo. Las imágenes de producto salen de la foto de exhibición; reemplázalas por fotos oficiales desde el panel.

Sin `CAMPUS_API_URL` en `.env` el campus trabaja solo con una base local, útil para desarrollo: ahí `seed_campus --demo` agrega 10 usuarios ficticios con actividad para ver el ranking y los gráficos. Los usuarios demo nunca se cargan en la API.

## Login corporativo (Syspro)

Todo ingreso se valida contra la API de Syspro: el campus toma de ahí el nombre, el rol y el supervisor de cada persona. A diferencia de la versión anterior, la API key ya no se envía al navegador: queda solo en el servidor. Los usuarios listados en `SYSPRO_ADMIN_USERS` entran como administradores.

La petición es `POST` con `{"user": "...", "pass": "...", "ApiKey": "..."}`. Si la API responde con una lista con datos, el ingreso es válido; si responde `[]`, el usuario o la clave son incorrectos.

```
SYSPRO_API_URL=http://181.78.203.134:7070/api/syspro/users     # principal
SYSPRO_API_URLS=http://192.168.1.97:7070/api/syspro/users      # respaldos, separados por coma
```

Si una URL no responde (sin conexión o 404), se prueba la siguiente. Si ninguna responde, el login muestra "No pudimos conectarnos con el sistema corporativo".

Para diagnosticar, este comando muestra la respuesta de cada URL y cómo se crearía el usuario:

```bash
.venv\Scripts\python manage.py probar_syspro USUARIO CLAVE
```

> La API key anterior quedó publicada en el historial de git (`legacy/index_v1.html`). Se recomienda pedir una nueva al área de sistemas.

## Roles

| Rol | Acceso |
| --- | --- |
| Ejecutivo comercial | Campus |
| Supervisor | Campus + Mi equipo |
| Jefe de ventas / Jefe nacional | Campus + Mi equipo + panel (sin gestión de usuarios) |
| Administrador | Todo, incluida la gestión de usuarios y la revocación de certificados |

## Reglas de aprendizaje

- La evaluación final se habilita al completar todas las lecciones.
- Nota mínima, tiempo, número de preguntas e intentos se configuran por curso (por defecto 70%, 10 minutos, 10 preguntas, intentos ilimitados).
- Al aprobar se emite el certificado. Si el curso no tiene preguntas, el certificado se emite al completar las lecciones.
- Puntos: 10 por lección, la mejor nota de cada evaluación aprobada y 50 por certificado.

## Publicar en IIS

Ver **[DESPLIEGUE_IIS.md](DESPLIEGUE_IIS.md)**: requisitos, instalador automático (`deploy/instalar_iis.ps1`), HTTPS, actualizaciones y respaldos.

## Personalizar el diseño

Los colores, radios y sombras son variables en `static/css/campus.css` (`:root` para el tema claro y `[data-theme="dark"]` para el oscuro). Para un tema nuevo basta con redefinir esas variables.

## Pruebas

```bash
.venv\Scripts\python manage.py test apps
```
