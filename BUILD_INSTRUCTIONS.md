# Build Instructies voor Windows Executable

## Vereisten
- Python 3.8 of hoger
- PyInstaller geïnstalleerd: `pip install pyinstaller`
- Alle dependencies geïnstalleerd: `pip install -r requirements.txt`

## Build Methode 1: Directory-based (Aanbevolen)

```bash
pyinstaller --name SintMaartenCampusAutologin --onedir --console --add-data "templates;templates" --add-data "README.md;." --hidden-import selenium --hidden-import flask --hidden-import cryptography --hidden-import markdown --hidden-import auto_smartschool_login --hidden-import auto_microsoft_admin_login --hidden-import auto_google_admin_login --hidden-import auto_easy4u_login --hidden-import auto_rdp_sessions --hidden-import auto_ssh_connect --hidden-import credentials_manager --hidden-import security_utils --hidden-import clean_credentials --hidden-import migrate_key_file --hidden-import security_test --hidden-import clean_servers --clean --noconfirm web_interface.py
```

Dit maakt een folder `dist\SintMaartenCampusAutologin\` met:
- `SintMaartenCampusAutologin.exe` - Het hoofdprogramma
- Alle benodigde DLLs en dependencies
- `templates\` folder
- `README.md`

## Build Methode 2: Onefile (Kan permission errors geven)

```bash
pyinstaller --name SintMaartenCampusAutologin --onefile --console --add-data "templates;templates" --add-data "README.md;." --hidden-import selenium --hidden-import flask --hidden-import cryptography --hidden-import markdown --hidden-import auto_smartschool_login --hidden-import auto_microsoft_admin_login --hidden-import auto_google_admin_login --hidden-import auto_easy4u_login --hidden-import auto_rdp_sessions --hidden-import auto_ssh_connect --hidden-import credentials_manager --hidden-import security_utils --hidden-import clean_credentials --hidden-import migrate_key_file --hidden-import security_test --hidden-import clean_servers --clean --noconfirm web_interface.py
```

## Troubleshooting

### Permission Error
Als je een permission error krijgt:
1. Sluit alle running instances van de applicatie
2. Run als Administrator
3. Controleer of antivirus de build blokkeert
4. Gebruik `--onedir` in plaats van `--onefile`

### Executable niet gevonden
Na de build, check:
- `dist\SintMaartenCampusAutologin\SintMaartenCampusAutologin.exe` (onedir)
- `dist\SintMaartenCampusAutologin.exe` (onefile)

## Distributie

Voor distributie, kopieer:
- De hele `dist\SintMaartenCampusAutologin\` folder (onedir)
- Of alleen `dist\SintMaartenCampusAutologin.exe` + `templates\` folder (onefile)
