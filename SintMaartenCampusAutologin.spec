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
        'src.auto_login.auto_smartschool_login', 'src.auto_login.auto_microsoft_admin_login',
        'src.auto_login.auto_google_admin_login', 'src.auto_login.auto_easy4u_login',
        'src.auto_login.auto_rdp_sessions', 'src.auto_login.auto_ssh_connect',
        'src.core.credentials_manager', 'src.core.security_utils', 'src.core.clean_credentials',
        'src.core.migrate_key_file', 'src.core.security_test', 'src.core.clean_servers',
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
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
