@echo off
REM Upload de installatie-zip naar GitHub Releases zodat anderen hem daar kunnen downloaden.
REM Vereist: GitHub CLI (gh) - https://cli.github.com/
REM Of: maak handmatig een release op GitHub en upload de zip.

set "SCRIPT_DIR=%~dp0"
set "ROOT=%SCRIPT_DIR%"
if not exist "%ROOT%SintMaartenCampusAutologin.spec" set "ROOT=%SCRIPT_DIR%..\"
cd /d "%ROOT%"

set "ZIP_NAME=SintMaartenCampusAutologin_Installatie.zip"
REM Versie uit src/web/web_interface.py (APP_VERSION) - zo blijft het in sync
for /f "usebackq delims=" %%v in (`python -c "import sys; sys.path.insert(0,'.'); from src.web.web_interface import APP_VERSION; print(APP_VERSION)" 2^>nul`) do set "VERSION=%%~v"
if not defined VERSION set "VERSION=1.0.7"

echo ========================================
echo Zip naar GitHub Releases uploaden
echo ========================================
echo Versie: %VERSION%
echo.

if not exist "%ZIP_NAME%" (
    echo Zip niet gevonden. Eerst bouwen?
    echo.
    call "%SCRIPT_DIR%maak_zip_installatie.bat"
    if not exist "%ZIP_NAME%" (
        echo ERROR: Zip kon niet worden gemaakt.
        pause
        exit /b 1
    )
)

where gh >nul 2>&1
if errorlevel 1 (
    echo GitHub CLI ^(gh^) is niet geinstalleerd.
    echo.
    echo HANDMATIG:
    echo 1. Ga naar: https://github.com/CodeTrickz/autologin-toolsmc/releases/new
    echo 2. Tag: v%VERSION% ^(of kies "Choose existing tag" als v%VERSION% al bestaat^)
    echo 3. Titel: bv. "v%VERSION% - Installatie zip"
    echo 4. Sleep het bestand "%ZIP_NAME%" naar de pagina ^(onder "Assets"^)
    echo 5. Klik op "Publish release"
    echo.
    echo Daarna kunnen anderen de zip downloaden via:
    echo https://github.com/CodeTrickz/autologin-toolsmc/releases
    echo.
    start "" "https://github.com/CodeTrickz/autologin-toolsmc/releases/new"
    pause
    exit /b 0
)

echo Release aanmaken met zip als asset...
echo Tag: v%VERSION%
echo.
gh release create "v%VERSION%" "%ZIP_NAME%" --title "v%VERSION% - Installatie voor andere PC's" --notes "Download de zip en voer op de doel-PC install.bat uit als administrator." 2>nul
if errorlevel 1 (
    echo.
    echo Release "v%VERSION%" bestaat mogelijk al. Toevoegen van zip aan bestaande release...
    gh release upload "v%VERSION%" "%ZIP_NAME%" --clobber 2>nul
    if errorlevel 1 (
        echo.
        echo Mislukt. Maak handmatig een release op:
        echo https://github.com/CodeTrickz/autologin-toolsmc/releases/new
        echo en upload %ZIP_NAME%
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo Klaar.
echo ========================================
echo.
echo Download-URL: https://github.com/CodeTrickz/autologin-toolsmc/releases
echo.
pause
