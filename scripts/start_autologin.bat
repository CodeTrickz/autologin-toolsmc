@echo off
REM Start de Sint Maarten Campus Autologin Tool (standalone desktop-app, geen browser/localhost)

set "INSTALL_DIR=C:\Program Files\SintMaartenCampusAutologin"
set "EXE_PATH=%INSTALL_DIR%\SintMaartenCampusAutologin.exe"

if not exist "%EXE_PATH%" (
    echo ERROR: SintMaartenCampusAutologin.exe niet gevonden!
    echo Zoekt in: %EXE_PATH%
    echo.
    echo Controleer of de applicatie correct is geinstalleerd.
    pause
    exit /b 1
)

cd /d "%INSTALL_DIR%"

REM Als de applicatie al draait: niets doen (er is geen aparte browser om te openen)
tasklist /FI "IMAGENAME eq SintMaartenCampusAutologin.exe" 2>NUL | find /I /N "SintMaartenCampusAutologin.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo Applicatie draait al.
    exit /b 0
)

REM Start de applicatie (standalone: eigen venster, geen localhost in browser)
start "" "%EXE_PATH%"
exit
