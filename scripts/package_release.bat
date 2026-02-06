@echo off
echo ========================================
echo Creating Release Package
echo ========================================
echo.

set RELEASE_DIR=release
set EXE_NAME=SintMaartenCampusAutologin

if not exist dist\%EXE_NAME%.exe (
    echo ERROR: Executable not found. Please run build_exe.bat first.
    pause
    exit /b 1
)

echo Creating release directory...
if exist %RELEASE_DIR% rmdir /s /q %RELEASE_DIR%
mkdir %RELEASE_DIR%

echo Copying executable...
copy dist\%EXE_NAME%.exe %RELEASE_DIR%\ >nul

echo Copying templates...
xcopy templates %RELEASE_DIR%\templates\ /E /I /Y >nul

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
