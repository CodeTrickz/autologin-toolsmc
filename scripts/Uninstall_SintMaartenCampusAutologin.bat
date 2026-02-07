@echo off
REM Uninstaller voor Sint Maarten Campus Autologin Tool
REM Verwijdert elke geïnstalleerde versie (Program Files + AppData).
REM Rechtermuisknop -> "Als administrator uitvoeren" aanbevolen.

echo ========================================
echo Sint Maarten Campus Autologin Tool
echo Verwijderen (alle versies)
echo ========================================
echo.

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Waarschuwing: Niet als Administrator. Sommige mappen worden mogelijk niet verwijderd.
    echo Voor volledige verwijdering: rechtermuisknop op dit bestand -^> "Als administrator uitvoeren"
    echo.
    pause
)

set "INSTALL_DIR=%ProgramFiles%\SintMaartenCampusAutologin"
set "APPDATA_DIR=%LOCALAPPDATA%\SintMaartenCampusAutologin"
set "DESKTOP_LNK=%USERPROFILE%\Desktop\Sint Maarten Campus Autologin.lnk"
set "STARTMENU_LNK=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Sint Maarten Campus Autologin.lnk"

echo Stoppen van de applicatie...
taskkill /F /IM SintMaartenCampusAutologin.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo Verwijderen van snelkoppelingen...
if exist "%DESKTOP_LNK%" del /F /Q "%DESKTOP_LNK%" && echo   - Bureaublad snelkoppeling verwijderd.
if exist "%STARTMENU_LNK%" del /F /Q "%STARTMENU_LNK%" && echo   - Start Menu snelkoppeling verwijderd.

echo Verwijderen van gebruikersdata (credentials, servers)...
if exist "%APPDATA_DIR%" (
    rd /S /Q "%APPDATA_DIR%"
    echo   - %APPDATA_DIR% verwijderd.
) else (
    echo   - Geen gebruikersdata map gevonden.
)

echo Verwijderen van programma-map...
if exist "%INSTALL_DIR%" (
    rd /S /Q "%INSTALL_DIR%" 2>nul
    if exist "%INSTALL_DIR%" (
        echo   - Kon programma-map niet verwijderen (mogelijk in gebruik).
        echo   - Sluit alle vensters van de applicatie en voer dit script opnieuw uit.
        echo   - Of verwijder handmatig: %INSTALL_DIR%
    ) else (
        echo   - Programma-map verwijderd.
    )
) else (
    echo   - Geen programma-map gevonden in Program Files.
)

echo.
echo ========================================
echo Verwijderen afgerond.
echo ========================================
echo.
pause
