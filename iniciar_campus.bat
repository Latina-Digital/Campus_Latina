@echo off
REM Instala (la primera vez) y arranca Campus Latina en modo desarrollo.
REM Los datos se leen y guardan en la API del campus (CAMPUS_API_URL en .env).
cd /d "%~dp0"
if not exist .venv (
  echo Creando entorno virtual...
  python -m venv .venv
  .venv\Scripts\python -m pip install --upgrade pip
  .venv\Scripts\python -m pip install -r requirements.txt
)
if not exist .env (
  copy .env.example .env
  echo.
  echo  Se creo el archivo .env: escribe la API key en SYSPRO_API_KEY y vuelve a ejecutar.
  pause
  exit /b
)
echo.
echo  Campus Latina disponible en http://127.0.0.1:8000  (carga los datos desde la API al arrancar)
echo.
.venv\Scripts\python manage.py runserver 0.0.0.0:8000
