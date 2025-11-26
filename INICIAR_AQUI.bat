@echo off
chcp 65001 >nul
echo ========================================
echo  INICIANDO SERVIDOR PDF COMPARATOR
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] Verificando Python...
python --version
if errorlevel 1 (
    echo ERROR: Python no encontrado
    pause
    exit /b 1
)
echo.

echo [2/3] Instalando dependencias (esto puede tardar unos minutos)...
python -m pip install --quiet --upgrade pip
python -m pip install --user fastapi "uvicorn[standard]" pdfplumber openai python-dotenv python-multipart aiofiles PyPDF2
if errorlevel 1 (
    echo ERROR: No se pudieron instalar las dependencias
    pause
    exit /b 1
)
echo.

echo [3/3] Iniciando servidor...
echo.
echo ========================================
echo  SERVIDOR INICIANDO...
echo ========================================
echo.
echo El servidor estara disponible en:
echo.
echo    http://localhost:8000
echo.
echo Presiona Ctrl+C para detener el servidor
echo.
echo ========================================
echo.

python main.py

pause




