@echo off
REM Altijd naar de map van dit script gaan (ook bij "Als administrator uitvoeren")
cd /d "%~dp0"

echo ========================================
echo Building Sint Maarten Campus Autologin Tool
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if PyInstaller is installed
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller
        pause
        exit /b 1
    )
)

echo.
echo Cleaning previous build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__

echo.
echo Export static HTML voor standalone-modus...
python -c "import sys; sys.path.insert(0, '.'); from src.web.export_static import export; export()"
if errorlevel 1 (
    echo WAARSCHUWING: export_static mislukt. Standalone-modus kan bij eerste start iets trager zijn.
)

echo.
echo Building executable...
pyinstaller SintMaartenCampusAutologin.spec --clean

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo The executable can be found in: dist\SintMaartenCampusAutologin.exe
echo.
echo IMPORTANT: Copy the following files to the dist folder:
echo   - templates\ (entire folder)
echo   - README.md
echo.
echo You can also create a release package by running: package_release.bat
echo.
pause
