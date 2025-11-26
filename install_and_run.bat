@echo off
chcp 65001 >nul 2>&1
setlocal EnableDelayedExpansion

REM RMLSA-STATIC - Script de instalación y ejecución para Windows

echo.
echo ==============================================
echo    RMLSA-STATIC - Simulador de Redes Opticas
echo ==============================================
echo.

REM Obtener directorio del script
cd /d "%~dp0"

REM Verificar Python
echo [INFO] Verificando instalacion de Python...

set "PYTHON_CMD="

REM Intentar python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set "PYVER=%%v"
    for /f "tokens=1,2 delims=." %%a in ("!PYVER!") do (
        set "MAJOR=%%a"
        set "MINOR=%%b"
    )
    if !MAJOR! geq 3 if !MINOR! geq 10 (
        set "PYTHON_CMD=python"
        echo [OK] Python !PYVER! encontrado
        goto :python_found
    )
)

REM Intentar python3
python3 --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2 delims= " %%v in ('python3 --version 2^>^&1') do set "PYVER=%%v"
    for /f "tokens=1,2 delims=." %%a in ("!PYVER!") do (
        set "MAJOR=%%a"
        set "MINOR=%%b"
    )
    if !MAJOR! geq 3 if !MINOR! geq 10 (
        set "PYTHON_CMD=python3"
        echo [OK] Python !PYVER! encontrado
        goto :python_found
    )
)

REM Intentar py launcher
py -3 --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2 delims= " %%v in ('py -3 --version 2^>^&1') do set "PYVER=%%v"
    for /f "tokens=1,2 delims=." %%a in ("!PYVER!") do (
        set "MAJOR=%%a"
        set "MINOR=%%b"
    )
    if !MAJOR! geq 3 if !MINOR! geq 10 (
        set "PYTHON_CMD=py -3"
        echo [OK] Python !PYVER! encontrado
        goto :python_found
    )
)

echo [ERROR] Python 3.10 o superior no encontrado.
echo.
echo Por favor, instala Python 3.10+ desde:
echo   https://www.python.org/downloads/
echo.
echo Asegurate de marcar "Add Python to PATH" durante la instalacion.
echo.
pause
exit /b 1

:python_found

REM Crear entorno virtual si no existe
if not exist "venv" (
    echo [INFO] Creando entorno virtual...
    %PYTHON_CMD% -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] No se pudo crear el entorno virtual
        pause
        exit /b 1
    )
    echo [OK] Entorno virtual creado
) else (
    echo [INFO] Entorno virtual existente detectado
)

REM Activar entorno virtual
echo [INFO] Activando entorno virtual...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] No se pudo activar el entorno virtual
    pause
    exit /b 1
)
echo [OK] Entorno virtual activado

REM Instalar dependencias
echo [INFO] Instalando dependencias...
pip install --upgrade pip -q >nul 2>&1
pip install -r requirements.txt -q
if %errorlevel% neq 0 (
    echo [ERROR] No se pudieron instalar las dependencias
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas

REM Ejecutar simulador
echo.
echo ==============================================
echo    Ejecutando Simulador RMLSA
echo ==============================================
echo.

python simulator.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] La simulacion fallo
    pause
    exit /b 1
)

REM Mensaje final
echo.
echo ==============================================
echo    Simulacion completada exitosamente
echo ==============================================
echo.
echo Archivos generados:
echo   - resultado_comparativa.png (grafico comparativo)
echo   - assignments_details.txt (reporte detallado)
echo.
pause
