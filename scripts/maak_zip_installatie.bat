@echo off
REM Maak zip voor installatie op andere PC's. Gebruikt project root (waar dist\ na build staat).
set "SCRIPT_DIR=%~dp0"
set "ROOT=%SCRIPT_DIR%"
if not exist "%ROOT%SintMaartenCampusAutologin.spec" set "ROOT=%SCRIPT_DIR%..\"
cd /d "%ROOT%"

set EXE_NAME=SintMaartenCampusAutologin
set ZIP_DIR=SintMaartenCampusAutologin_Installatie
set ZIP_FILE=SintMaartenCampusAutologin_Installatie.zip

echo ========================================
echo Zip voor installatie op andere PC's
echo ========================================
echo.

if not exist "dist\%EXE_NAME%.exe" (
    echo De .exe is nog niet gebouwd.
    echo Eerst bouwen? (build_exe.bat wordt uitgevoerd)
    echo.
    call "%SCRIPT_DIR%build_exe.bat"
    if not exist "dist\%EXE_NAME%.exe" (
        echo ERROR: Build mislukt of .exe niet gevonden.
        pause
        exit /b 1
    )
)

echo Controleren op gevoelige data voor packaging...
python wipe_before_build.py
if errorlevel 1 (
    echo WAARSCHUWING: wipe_before_build mislukt. Packaging gaat door, staging wordt extra gecontroleerd.
)

echo Aanmaken van map: %ZIP_DIR%
if exist "%ZIP_DIR%" rmdir /s /q "%ZIP_DIR%"
mkdir "%ZIP_DIR%"

echo Kopieren van bestanden...
copy "dist\%EXE_NAME%.exe" "%ZIP_DIR%\" >nul
copy "%SCRIPT_DIR%install.bat" "%ZIP_DIR%\" >nul
copy "%SCRIPT_DIR%Uninstall_SintMaartenCampusAutologin.bat" "%ZIP_DIR%\" >nul
if exist "README.md" copy "README.md" "%ZIP_DIR%\" >nul

echo Verwijderen van gevoelige bestanden uit staging indien aanwezig...
for %%F in (credentials.json rdp_servers.json ssh_servers.json .env .credentials_key .credentials_key.dpapi) do (
    if exist "%ZIP_DIR%\%%F" del /F /Q "%ZIP_DIR%\%%F" >nul 2>&1
)
for /D %%D in ("%ZIP_DIR%\chrome_user_data*" "%ZIP_DIR%\chrome_profiles*") do (
    if exist "%%~fD" rmdir /S /Q "%%~fD" >nul 2>&1
)

echo Schrijven van INSTALLATIE.txt...
(
echo Sint Maarten Campus Autologin Tool - Installatie
echo =================================================
echo.
echo INSTALLATIE OP DEZE OF EEN ANDERE PC:
echo.
echo 1. Pak dit zip-bestand uit in een map ^(bijv. Downloads of Bureaublad^).
echo 2. Ga in de uitgepakte map naar het bestand: install.bat
echo 3. Rechtermuisknop op install.bat --^> "Als administrator uitvoeren"
echo 4. Volg de instructies. Er wordt een snelkoppeling op het bureaublad gemaakt.
echo 5. Start de applicatie via het icoon "Sint Maarten Campus Autologin" op het bureaublad.
echo.
echo UPDATE:
echo - Voer install.bat opnieuw uit. De draaiende applicatie wordt gestopt en de bestanden worden vervangen.
echo - Lokale credentials, configuratie en voorkeuren in %%LOCALAPPDATA%%\SintMaartenCampusAutologin blijven bewaard.
echo.
echo EERSTE KEER GEBRUIK:
echo - Configureer je inloggegevens via Credentials in de applicatie.
echo - Chrome moet geinstalleerd zijn voor de auto-login functies.
echo.
echo VERWIJDEREN ^(alle versies^):
echo - Voer Uninstall_SintMaartenCampusAutologin.bat uit ^(uit deze map of na installatie uit Program Files^)
echo - Of: Ga naar C:\Program Files\SintMaartenCampusAutologin en voer uninstall.bat uit
echo - De uninstaller vraagt of lokale credentials en configuratie verwijderd moeten worden. Standaard: Nee.
echo.
echo Voor meer informatie: zie README.md in deze map.
echo =================================================
) > "%ZIP_DIR%\INSTALLATIE.txt"

echo Maken van zip: %ZIP_FILE%
if exist "%ZIP_FILE%" del /q "%ZIP_FILE%"
powershell -NoProfile -Command "Compress-Archive -Path '%ZIP_DIR%\*' -DestinationPath '%ZIP_FILE%' -Force"

echo Opruimen...
rmdir /s /q "%ZIP_DIR%"

echo.
echo ========================================
echo Klaar!
echo ========================================
echo.
echo Bestand: %ZIP_FILE%
echo.
echo Geef dit zip-bestand aan anderen. Zij pakken het uit,
echo voeren install.bat als administrator uit, en kunnen
echo daarna de applicatie via het bureaublad-icoon starten.
echo.
pause
