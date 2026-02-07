@echo off
REM Bouw .exe voor distributie. Project root = map met SintMaartenCampusAutologin.spec
set "SCRIPT_DIR=%~dp0"
set "ROOT=%SCRIPT_DIR%"
if not exist "%ROOT%SintMaartenCampusAutologin.spec" set "ROOT=%SCRIPT_DIR%..\"
cd /d "%ROOT%"

echo ========================================
echo Sint Maarten Campus Autologin Tool - Build
echo ========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python niet gevonden in PATH
    pause
    exit /b 1
)

python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo PyInstaller installeren...
    pip install pyinstaller
    if errorlevel 1 ( echo ERROR: PyInstaller installatie mislukt. & pause & exit /b 1 )
)

echo.
echo [1/4] Wissen van credentials en servers (geen gevoelige data in build)...
python wipe_before_build.py
if errorlevel 1 (
    echo WAARSCHUWING: wipe_before_build mislukt. Build gaat door.
)

echo.
echo [2/4] Opschonen vorige build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo [3/4] Export static HTML voor standalone-modus...
python -c "import sys; sys.path.insert(0,'.'); from src.web.export_static import export; export()"
if errorlevel 1 (
    echo WAARSCHUWING: export_static mislukt. Standalone-modus kan trager starten.
)

echo.
echo [4/4] Bouwen executable...
pyinstaller SintMaartenCampusAutologin.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo ERROR: Build mislukt!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build voltooid.
echo ========================================
echo.
echo .exe staat in: dist\SintMaartenCampusAutologin.exe
echo.
echo Voor zip-verspreiding: scripts\maak_zip_installatie.bat
echo.
pause
