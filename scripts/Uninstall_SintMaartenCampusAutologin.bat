@echo off
REM Uninstaller voor Sint Maarten Campus Autologin Tool
REM Verwijdert de geïnstalleerde applicatie. Gebruikersdata wordt alleen verwijderd na bevestiging.
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
set "HELPER=%TEMP%\smca_uninstall_helper.bat"

echo Stoppen van de applicatie...
taskkill /F /T /IM SintMaartenCampusAutologin.exe >nul 2>&1
taskkill /F /T /IM chromedriver.exe >nul 2>&1
powershell -NoProfile -ExecutionPolicy Bypass -Command "$tokens=@('%INSTALL_DIR%','%APPDATA_DIR%') | ForEach-Object { $_.ToLowerInvariant() }; Get-CimInstance Win32_Process | Where-Object { $_.Name -in @('chrome.exe','msedgewebview2.exe','chromedriver.exe') -and ($cmd=([string]$_.CommandLine).ToLowerInvariant()) -and ($tokens | Where-Object { $_ -and $cmd.Contains($_) }) } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }" >nul 2>&1
timeout /t 3 /nobreak >nul

echo Verwijderen van snelkoppelingen...
if exist "%DESKTOP_LNK%" del /F /Q "%DESKTOP_LNK%" && echo   - Bureaublad snelkoppeling verwijderd.
if exist "%STARTMENU_LNK%" del /F /Q "%STARTMENU_LNK%" && echo   - Start Menu snelkoppeling verwijderd.

echo.
echo Lokale credentials en configuratie verwijderen?
echo Map: %APPDATA_DIR%
choice /C YN /N /D N /T 30 /M "Remove local credentials and configuration? [y/N] "
if errorlevel 2 goto keepdata

echo Verwijderen van gebruikersdata (credentials, servers)...
if exist "%APPDATA_DIR%" (
    rd /S /Q "%APPDATA_DIR%"
    echo   - %APPDATA_DIR% verwijderd.
) else (
    echo   - Geen gebruikersdata map gevonden.
)
goto afterdata

:keepdata
echo Gebruikersdata bewaard.

:afterdata

echo Verwijderen van programma-map...
if exist "%INSTALL_DIR%" (
    cd /d "%TEMP%" >nul 2>&1
    > "%HELPER%" echo @echo off
    >> "%HELPER%" echo timeout /t 2 /nobreak ^>nul
    >> "%HELPER%" echo rd /S /Q "%INSTALL_DIR%" ^>nul 2^>^&1
    >> "%HELPER%" echo del /F /Q "%HELPER%" ^>nul 2^>^&1
    start "" /D "%TEMP%" cmd /c "%HELPER%"
    timeout /t 4 /nobreak >nul
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
