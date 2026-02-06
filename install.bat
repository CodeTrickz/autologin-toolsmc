@echo off
REM Installatie script voor Sint Maarten Campus Autologin Tool
REM Dit script installeert de desktop applicatie en maakt een snelkoppeling op het bureaublad

echo ========================================
echo Sint Maarten Campus Autologin Tool
echo Installatie Script
echo ========================================
echo.

REM Controleer of we admin rechten hebben
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Dit script moet als Administrator worden uitgevoerd!
    echo Rechtermuisknop op dit bestand en kies "Run as administrator"
    pause
    exit /b 1
)

REM Controleer of de .exe bestaat (zelfde map als dit script, of dist\)
set "EXE_PATH="
set "SCRIPT_DIR=%~dp0"

if exist "%SCRIPT_DIR%SintMaartenCampusAutologin.exe" (
    set "EXE_PATH=%SCRIPT_DIR%SintMaartenCampusAutologin.exe"
    echo .exe gevonden: %EXE_PATH%
) else if exist "%SCRIPT_DIR%dist\SintMaartenCampusAutologin.exe" (
    set "EXE_PATH=%SCRIPT_DIR%dist\SintMaartenCampusAutologin.exe"
    echo .exe gevonden: %EXE_PATH%
) else if exist "%SCRIPT_DIR%dist\SintMaartenCampusAutologin\SintMaartenCampusAutologin.exe" (
    set "EXE_PATH=%SCRIPT_DIR%dist\SintMaartenCampusAutologin\SintMaartenCampusAutologin.exe"
    echo .exe gevonden: %EXE_PATH%
) else (
    echo ERROR: SintMaartenCampusAutologin.exe niet gevonden!
    echo.
    echo Script directory: %SCRIPT_DIR%
    echo Zoekt in: %SCRIPT_DIR%dist\SintMaartenCampusAutologin.exe
    echo En in: %SCRIPT_DIR%dist\SintMaartenCampusAutologin\SintMaartenCampusAutologin.exe
    echo.
    echo Zorg dat je eerst de applicatie hebt gebouwd.
    echo Run: pyinstaller SintMaartenCampusAutologin.spec --clean --noconfirm
    pause
    exit /b 1
)

REM Vraag installatie locatie
set "INSTALL_DIR=%ProgramFiles%\SintMaartenCampusAutologin"
echo Installatie locatie: %INSTALL_DIR%
echo.

REM Maak installatie directory
if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%"
    echo Installatie directory aangemaakt.
) else (
    echo Installatie directory bestaat al. Overschrijven...
)

REM Kopieer de .exe
echo Kopieren van bestanden...
echo Van: %EXE_PATH%
echo Naar: %INSTALL_DIR%\SintMaartenCampusAutologin.exe
copy /Y "%EXE_PATH%" "%INSTALL_DIR%\SintMaartenCampusAutologin.exe"
if errorlevel 1 (
    echo ERROR: Kon bestand niet kopieren!
    pause
    exit /b 1
)
echo Bestand succesvol gekopieerd.

REM Maak snelkoppeling op bureaublad (direct naar .exe, geen batch file nodig)
echo.
echo Maken van snelkoppeling op bureaublad...
set "DESKTOP=%USERPROFILE%\Desktop"
set "SHORTCUT=%DESKTOP%\Sint Maarten Campus Autologin.lnk"

REM Zorg dat Desktop-map bestaat (bij sommige accounts bestaat deze nog niet)
if not exist "%DESKTOP%" (
    mkdir "%DESKTOP%" 2>nul
)

powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); $Shortcut.TargetPath = '%INSTALL_DIR%\SintMaartenCampusAutologin.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'Sint Maarten Campus Autologin Tool - Desktop Applicatie'; $Shortcut.Save()"

if exist "%SHORTCUT%" (
    echo Snelkoppeling aangemaakt op bureaublad.
) else (
    echo WAARSCHUWING: Kon snelkoppeling niet maken. Maak handmatig een snelkoppeling naar:
    echo %INSTALL_DIR%\SintMaartenCampusAutologin.exe
)

REM Maak snelkoppeling in Start Menu
echo.
echo Maken van snelkoppeling in Start Menu...
set "START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs"
set "START_SHORTCUT=%START_MENU%\Sint Maarten Campus Autologin.lnk"

REM Zorg dat Start Menu-map bestaat
if not exist "%START_MENU%" (
    mkdir "%START_MENU%" 2>nul
)

powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%START_SHORTCUT%'); $Shortcut.TargetPath = '%INSTALL_DIR%\SintMaartenCampusAutologin.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'Sint Maarten Campus Autologin Tool - Desktop Applicatie'; $Shortcut.Save()"

if exist "%START_SHORTCUT%" (
    echo Snelkoppeling toegevoegd aan Start Menu.
) else (
    echo WAARSCHUWING: Kon Start Menu snelkoppeling niet maken.
)

REM Maak uninstall script
echo.
echo Maken van uninstall script...
(
echo @echo off
echo REM Uninstall script voor Sint Maarten Campus Autologin Tool
echo echo Verwijderen van Sint Maarten Campus Autologin Tool...
echo.
echo REM Stop de applicatie als deze draait
echo taskkill /F /IM SintMaartenCampusAutologin.exe ^>nul 2^>^&1
echo.
echo REM Verwijder snelkoppelingen
echo del /F /Q "%DESKTOP%\Sint Maarten Campus Autologin.lnk" ^>nul 2^>^&1
echo del /F /Q "%START_MENU%\Sint Maarten Campus Autologin.lnk" ^>nul 2^>^&1
echo.
echo REM Verwijder installatie directory
echo rd /S /Q "%INSTALL_DIR%" ^>nul 2^>^&1
echo.
echo echo Applicatie verwijderd.
echo pause
) > "%INSTALL_DIR%\uninstall.bat"

echo.
echo ========================================
echo Installatie voltooid!
echo ========================================
echo.
echo De desktop applicatie is geinstalleerd in: %INSTALL_DIR%
echo.
echo Er is een snelkoppeling gemaakt op je bureaublad.
echo Dubbelklik op "Sint Maarten Campus Autologin" om te starten.
echo.
echo Dit is een echte standalone desktop applicatie - geen browser nodig!
echo.
pause
