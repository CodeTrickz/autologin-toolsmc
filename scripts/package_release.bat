@echo off
set "SCRIPT_DIR=%~dp0"
set "ROOT=%SCRIPT_DIR%"
if not exist "%ROOT%SintMaartenCampusAutologin.spec" set "ROOT=%SCRIPT_DIR%..\"
cd /d "%ROOT%"

echo ========================================
echo Creating Release Package
echo ========================================
echo.

set RELEASE_DIR=release
set EXE_NAME=SintMaartenCampusAutologin

if not exist dist\%EXE_NAME%.exe (
    echo ERROR: Executable not found. Run scripts\build_exe.bat first.
    pause
    exit /b 1
)

echo Checking for sensitive data before packaging...
python wipe_before_build.py
if errorlevel 1 (
    echo WARNING: wipe_before_build failed. Continuing with staging cleanup.
)

echo Creating release directory...
if exist %RELEASE_DIR% rmdir /s /q %RELEASE_DIR%
mkdir %RELEASE_DIR%

echo Copying executable...
copy dist\%EXE_NAME%.exe %RELEASE_DIR%\ >nul

echo Copying templates...
if exist templates xcopy templates %RELEASE_DIR%\templates\ /E /I /Y >nul

echo Copying uninstaller...
if exist "%SCRIPT_DIR%Uninstall_SintMaartenCampusAutologin.bat" copy "%SCRIPT_DIR%Uninstall_SintMaartenCampusAutologin.bat" %RELEASE_DIR%\ >nul

echo Removing sensitive files from release staging if present...
for %%F in (credentials.json rdp_servers.json ssh_servers.json .env .credentials_key .credentials_key.dpapi) do (
    if exist "%RELEASE_DIR%\%%F" del /F /Q "%RELEASE_DIR%\%%F" >nul 2>&1
)
for /D %%D in ("%RELEASE_DIR%\chrome_user_data*" "%RELEASE_DIR%\chrome_profiles*") do (
    if exist "%%~fD" rmdir /S /Q "%%~fD" >nul 2>&1
)

echo Copying documentation...
copy README.md %RELEASE_DIR%\ >nul

echo Creating startup script...
echo @echo off > %RELEASE_DIR%\start.bat
echo echo Starting Sint Maarten Campus Autologin Tool... >> %RELEASE_DIR%\start.bat
echo %EXE_NAME%.exe >> %RELEASE_DIR%\start.bat
echo pause >> %RELEASE_DIR%\start.bat

echo Creating README...
echo Sint Maarten Campus Autologin Tool > %RELEASE_DIR%\INSTALL.txt
echo. >> %RELEASE_DIR%\INSTALL.txt
echo INSTALLATIE: >> %RELEASE_DIR%\INSTALL.txt
echo 1. Kopieer alle bestanden naar een map op je computer >> %RELEASE_DIR%\INSTALL.txt
echo 2. Dubbelklik op start.bat om de applicatie te starten >> %RELEASE_DIR%\INSTALL.txt
echo 3. Open je browser en ga naar http://127.0.0.1:5000 >> %RELEASE_DIR%\INSTALL.txt
echo. >> %RELEASE_DIR%\INSTALL.txt
echo BELANGRIJK: >> %RELEASE_DIR%\INSTALL.txt
echo - Zorg dat Chrome browser is geinstalleerd >> %RELEASE_DIR%\INSTALL.txt
echo - De eerste keer kan het langer duren om te starten >> %RELEASE_DIR%\INSTALL.txt
echo - Configureer je credentials via de web interface >> %RELEASE_DIR%\INSTALL.txt

echo.
echo ========================================
echo Release package created successfully!
echo ========================================
echo.
echo Release files are in: %RELEASE_DIR%\
echo.
echo You can now distribute this folder to users.
echo.
pause
