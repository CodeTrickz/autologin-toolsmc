@echo off
REM Script om de installatie te repareren door start_autologin.bat toe te voegen

echo ========================================
echo Repareren van installatie
echo ========================================
echo.

REM Controleer admin rechten
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Dit script moet als Administrator worden uitgevoerd!
    echo Rechtermuisknop op dit bestand en kies "Run as administrator"
    pause
    exit /b 1
)

set "INSTALL_DIR=C:\Program Files\SintMaartenCampusAutologin"

REM Maak start_autologin.bat
echo Maken van start_autologin.bat...
(
echo @echo off
echo REM Start de Sint Maarten Campus Autologin Tool
echo set "INSTALL_DIR=C:\Program Files\SintMaartenCampusAutologin"
echo set "EXE_PATH=%%INSTALL_DIR%%\SintMaartenCampusAutologin.exe"
echo.
echo if not exist "%%EXE_PATH%%" ^(
echo     echo ERROR: SintMaartenCampusAutologin.exe niet gevonden!
echo     echo Zoekt in: %%EXE_PATH%%
echo     pause
echo     exit /b 1
echo ^)
echo.
echo cd /d "%%INSTALL_DIR%%"
echo.
echo tasklist /FI "IMAGENAME eq SintMaartenCampusAutologin.exe" 2^>NUL ^| find /I /N "SintMaartenCampusAutologin.exe"^>NUL
echo if "%%ERRORLEVEL%%"=="0" ^(
echo     echo Applicatie draait al. Openen van web interface...
echo     start http://127.0.0.1:5000
echo     exit
echo ^)
echo.
echo echo Starten van applicatie...
echo start /MIN "" "%%EXE_PATH%%"
echo timeout /t 4 /nobreak ^>nul
echo start http://127.0.0.1:5000
echo timeout /t 1 /nobreak ^>nul
echo exit
) > "%INSTALL_DIR%\start_autologin.bat"

if exist "%INSTALL_DIR%\start_autologin.bat" (
    echo ✅ start_autologin.bat aangemaakt.
) else (
    echo ❌ Kon start_autologin.bat niet aanmaken!
    pause
    exit /b 1
)

REM Repareer snelkoppeling op bureaublad
echo.
echo Repareren van snelkoppeling op bureaublad...
set "DESKTOP=%USERPROFILE%\Desktop"
set "SHORTCUT=%DESKTOP%\Sint Maarten Campus Autologin.lnk"

powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); $Shortcut.TargetPath = '%INSTALL_DIR%\start_autologin.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'Sint Maarten Campus Autologin Tool'; $Shortcut.Save()"

if exist "%SHORTCUT%" (
    echo ✅ Snelkoppeling op bureaublad gerepareerd.
) else (
    echo ⚠️  Kon snelkoppeling niet repareren.
)

REM Repareer snelkoppeling in Start Menu
echo.
echo Repareren van snelkoppeling in Start Menu...
set "START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs"
set "START_SHORTCUT=%START_MENU%\Sint Maarten Campus Autologin.lnk"

powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%START_SHORTCUT%'); $Shortcut.TargetPath = '%INSTALL_DIR%\start_autologin.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'Sint Maarten Campus Autologin Tool'; $Shortcut.Save()"

if exist "%START_SHORTCUT%" (
    echo ✅ Snelkoppeling in Start Menu gerepareerd.
) else (
    echo ⚠️  Kon Start Menu snelkoppeling niet repareren.
)

echo.
echo ========================================
echo Reparatie voltooid!
echo ========================================
echo.
echo Je kunt nu het icoon op je bureaublad gebruiken.
echo.
pause
