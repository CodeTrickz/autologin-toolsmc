# -*- mode: python ; coding: utf-8 -*-
# Entry: desktop_app (venster), niet web_interface (alleen Flask).
# Run pyinstaller vanuit project root.

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

hidden_imports = [
    'flask', 'cryptography', 'markdown', 'webview', 'dotenv', 'requests',
    'src.auto_login.auto_smartschool_login', 'src.auto_login.auto_microsoft_admin_login',
    'src.auto_login.auto_intune_admin_login', 'src.auto_login.auto_azure_admin_login',
    'src.auto_login.auto_google_admin_login', 'src.auto_login.auto_easy4u_login',
    'src.auto_login.auto_rdp_sessions', 'src.auto_login.auto_ssh_connect',
    'src.core.credentials_manager', 'src.core.security_utils', 'src.core.clean_credentials',
    'src.core.migrate_key_file', 'src.core.security_test', 'src.core.clean_servers',
    'src.core.process_cleanup',
]
hidden_imports += collect_submodules('selenium')
hidden_imports += collect_submodules('webdriver_manager')
hidden_imports = list(dict.fromkeys(hidden_imports))

a = Analysis(
    ['src/web/desktop_app.py'],
    pathex=['.'],
    binaries=[],

    datas=[
        ('templates', 'templates'),
        ('static_export', 'static_export'),
        ('README.md', '.'),
    ] + collect_data_files('webdriver_manager'),
    hiddenimports=hidden_imports,
    hookspath=['pyinstaller_hooks'],
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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
