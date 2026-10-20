@echo off
REM Instala (la primera vez) y arranca Campus Latina en modo desarrollo.
cd /d "%~dp0"
if not exist .venv (
  echo Creando entorno virtual...
  python -m venv .venv
  .venv\Scripts\python -m pip install --upgrade pip
  .venv\Scripts\python -m pip install -r requirements.txt
)
if not exist .env copy .env.example .env
.venv\Scripts\python manage.py migrate
if not exist db.sqlite3.seeded (
  .venv\Scripts\python manage.py seed_campus
  echo ok > db.sqlite3.seeded
)
echo.
echo  Campus Latina disponible en http://127.0.0.1:8000
echo.
.venv\Scripts\python manage.py runserver 0.0.0.0:8000
