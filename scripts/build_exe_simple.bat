@echo off
echo ========================================
echo Building Sint Maarten Campus Autologin Tool
echo ========================================
echo.

REM Stop any running instances
taskkill /F /IM SintMaartenCampusAutologin.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Clean previous builds
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist *.spec del /F /Q *.spec

echo Building executable...
pyinstaller --name SintMaartenCampusAutologin --onefile --console --add-data "templates;templates" --add-data "README.md;." --hidden-import selenium --hidden-import flask --hidden-import cryptography --hidden-import markdown --hidden-import auto_smartschool_login --hidden-import auto_microsoft_admin_login --hidden-import auto_google_admin_login --hidden-import auto_easy4u_login --hidden-import auto_rdp_sessions --hidden-import auto_ssh_connect --hidden-import credentials_manager --hidden-import security_utils --hidden-import clean_credentials --hidden-import migrate_key_file --hidden-import security_test --hidden-import clean_servers --clean --noconfirm web_interface.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    echo.
    echo Possible solutions:
    echo 1. Close any running instances of the application
    echo 2. Run as Administrator
    echo 3. Check if antivirus is blocking the build
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
if exist dist\SintMaartenCampusAutologin.exe (
    echo The executable can be found in: dist\SintMaartenCampusAutologin.exe
    echo.
    echo IMPORTANT: Copy the templates folder to the same directory as the .exe
    echo.
) else (
    echo WARNING: Executable not found in dist folder!
)
echo.
pause
