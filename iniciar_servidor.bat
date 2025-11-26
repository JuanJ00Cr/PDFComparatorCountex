@echo off
echo ========================================
echo  INICIANDO SERVIDOR DE COMPARACION PDF
echo ========================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en el PATH
    echo.
    echo Por favor:
    echo 1. Instala Python desde: https://www.python.org/downloads/
    echo 2. Durante la instalacion, marca "Add Python to PATH"
    echo 3. Reinicia esta ventana y vuelve a intentar
    echo.
    pause
    exit /b 1
)

echo [OK] Python encontrado
python --version
echo.

REM Verificar si las dependencias están instaladas
echo Verificando dependencias...
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo [ADVERTENCIA] Las dependencias no estan instaladas
    echo.
    echo Instalando dependencias...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] No se pudieron instalar las dependencias
        pause
        exit /b 1
    )
    echo [OK] Dependencias instaladas
) else (
    echo [OK] Dependencias ya instaladas
)
echo.

REM Cambiar al directorio del script
cd /d "%~dp0"

REM Iniciar el servidor
echo ========================================
echo  SERVIDOR INICIANDO...
echo ========================================
echo.
echo El servidor estara disponible en:
echo   http://localhost:8000
echo.
echo Presiona Ctrl+C para detener el servidor
echo.
echo ========================================
echo.

python main.py

pause




