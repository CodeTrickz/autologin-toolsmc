# -*- mode: python ; coding: utf-8 -*-
# Entry: desktop_app (venster), niet web_interface (alleen Flask).
# Run pyinstaller vanuit project root.

a = Analysis(
    ['src/web/desktop_app.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('static_export', 'static_export'),
        ('README.md', '.'),
    ],
    hiddenimports=[
        'selenium', 'selenium.webdriver', 'selenium.webdriver.chrome',
        'flask', 'cryptography', 'markdown', 'webview', 'dotenv', 'requests',
        'auto_smartschool_login', 'auto_microsoft_admin_login', 'auto_google_admin_login',
        'auto_easy4u_login', 'auto_rdp_sessions', 'auto_ssh_connect',
        'credentials_manager', 'security_utils', 'clean_credentials',
        'migrate_key_file', 'security_test', 'clean_servers',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SintMaartenCampusAutologin',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
