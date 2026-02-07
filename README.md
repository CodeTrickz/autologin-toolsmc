# Sint Maarten Campus Autologin Tool

Een veilige, geautomatiseerde login tool voor het Sint Maarten Campus die automatisch kan inloggen op verschillende web services en remote connections kan beheren via een gebruiksvriendelijke web interface.

---

<a id="download-voor-andere-pcs"></a>
## 📥 Download voor andere PC's

**Wil je de applicatie op andere computers installeren (zonder development-omgeving)?**

1. Ga naar **[Releases](https://github.com/CodeTrickz/autologin-toolsmc/releases)** op GitHub.
2. Download bij de nieuwste release het bestand **`SintMaartenCampusAutologin_Installatie.zip`** (onder Assets).
3. Pak de zip uit op de doel-PC.
4. Rechtermuisknop op **`install.bat`** → **Als administrator uitvoeren**.
5. Volg de instructies; er wordt een snelkoppeling op het bureaublad gemaakt.
6. Start de applicatie via het icoon **Sint Maarten Campus Autologin**.

De zip bevat de .exe, `install.bat` en **Uninstall_SintMaartenCampusAutologin.bat**. Er zitten geen credentials of servergegevens in.

---

## 📋 Inhoudsopgave

- [Download voor andere PC's](#download-voor-andere-pcs)
- [Overzicht](#overzicht)
- [Functionaliteiten](#functionaliteiten)
- [Installatie](#installatie)
- [Configuratie](#configuratie)
- [Gebruik](#gebruik)
- [Utilities](#utilities)
- [Documentatie](#documentatie)
- [Beperkingen](#beperkingen)
- [Beveiliging](#beveiliging)
- [Troubleshooting](#troubleshooting)

## 🎯 Overzicht

De Sint Maarten Campus Autologin Tool is een Python-gebaseerde applicatie die:

- **Automatische web logins** uitvoert voor:
  - Smartschool (via Microsoft SSO)
  - Smartschool Beheerder (zelfde flow, aparte credentials)
  - Microsoft 365 Admin Center
  - Google Workspace Admin Console
  - Easy4U

- **Remote connections** beheert via een web interface:
  - RDP (Remote Desktop Protocol) servers
  - SSH servers

- **Veilige credential opslag** met encryptie

- **Web interface** voor eenvoudig beheer zonder command line kennis

## ✨ Functionaliteiten

### Auto Login Services

De tool ondersteunt automatische login voor de volgende services:

1. **Smartschool** - Login via Microsoft SSO
2. **Smartschool Beheerder** - Zelfde login als Smartschool, met apart beheerdersaccount (eigen credentials)
3. **Microsoft Admin** - Directe login naar Microsoft 365 Admin Center
4. **Google Admin** - Login naar Google Workspace Admin Console (inclusief Microsoft SSO redirect handling)
5. **Easy4U** - Automatische login naar Easy4U platform

**Belangrijk:** Je kunt geen nieuwe auto-login services toevoegen via de web interface. Alleen de bovenstaande 5 services zijn ondersteund. Voor nieuwe services is code-aanpassing nodig.

### Remote Connections

#### RDP Servers
- Voeg RDP servers toe met hostname/IP, gebruikersnaam en wachtwoord
- Start RDP verbindingen met één klik
- Wachtwoorden worden encrypted opgeslagen
- Automatische credential management via Windows `cmdkey`

#### SSH Servers
- Voeg SSH servers toe met hostname/IP, poort, gebruikersnaam
- Ondersteunt zowel wachtwoord- als key file authenticatie
- Start SSH verbindingen in een CMD prompt venster
- Gebruikt OpenSSH (standaard op Windows 10+) of PuTTY als fallback
- Automatische wachtwoord authenticatie met PuTTY (plink.exe) wanneer beschikbaar

## 📦 Installatie

### Vereisten

- **Python 3.8 of hoger**
- **Windows 10/11** (voor RDP functionaliteit)
- **Chrome browser** (voor Selenium web automation)
- **Internet verbinding**

### Stap 1: Download en Extract

1. Download of clone de scripts directory
2. Open een terminal/command prompt in de scripts directory

### Stap 2: Installeer Dependencies

```bash
pip install -r requirements.txt
```

Dit installeert o.a.:
- `selenium` - Voor browser automation (andere auto-logins)
- `playwright` - Voor Easy4U auto-login (easy4u.nl)
- `python-dotenv` - Voor environment variables
- `flask` - Voor de web interface
- `cryptography` - Voor encryptie van credentials
- `markdown` - Voor documentatie weergave in web interface
- `pyinstaller` - Voor het maken van een Windows executable

**Easy4U (alleen bij development):** Bij development moet je één keer Chromium voor Playwright installeren. De **desktop .exe** gebruikt op Windows automatisch Microsoft Edge.
```bash
playwright install chromium
```

### Stap 2b: (Optioneel) Maak een Windows Executable

Voor distributie als standalone Windows applicatie (uitvoeren vanuit de projectmap):

```bash
scripts\build_exe.bat
```

- **Wipe vóór build:** De build wist automatisch credentials en servergegevens uit de ontwikkelmap (`src/core`), zodat er geen gevoelige data in de .exe of zip komt. Optioneel: `python wipe_before_build.py --appdata` om ook gebruikersdata (AppData) te wissen.
- De .exe komt in de map `dist\`.

**Zip voor verspreiding naar andere PC's:**

```bash
scripts\maak_zip_installatie.bat
```

Dit maakt `SintMaartenCampusAutologin_Installatie.zip` met de .exe, `install.bat` en **Uninstall_SintMaartenCampusAutologin.bat**. Gebruikers kunnen na installatie de applicatie verwijderen met de uninstaller (verwijdert elke geïnstalleerde versie, inclusief Program Files en AppData).

**Zip op GitHub zetten (zodat anderen hem kunnen downloaden):**

1. Maak lokaal de zip: `scripts\maak_zip_installatie.bat` (zo nodig eerst `scripts\build_exe.bat`).
2. Run **`scripts\publish_release.bat`**:
   - Met **GitHub CLI (`gh`)** geïnstalleerd: maakt automatisch een release met tag `v<versie>` en uploadt de zip.
   - Zonder `gh`: opent de pagina [New release](https://github.com/CodeTrickz/autologin-toolsmc/releases/new); kies tag (bv. `v1.0.9`), sleep de zip naar de pagina en klik op **Publish release**.
3. Daarna is de zip downloadbaar via [Releases](https://github.com/CodeTrickz/autologin-toolsmc/releases).

Voor een complete release package (map):

```bash
scripts\package_release.bat
```

### Stap 3: (Optioneel) Installeer PuTTY

Voor automatische SSH wachtwoord authenticatie (optioneel):
- Download PuTTY van https://www.putty.org/
- Installeer PuTTY (plink.exe wordt automatisch gedetecteerd)

## ⚙️ Configuratie

### Eerste Opstarten

1. **Start de web interface:**
   ```bash
   python web_interface.py
   ```

2. **Open je browser:**
   - Ga naar: `http://127.0.0.1:5000`
   - De web interface opent automatisch

3. **Configureer credentials:**
   - Klik op "Credentials Beheer" in het menu
   - Selecteer een service (bijv. Smartschool)
   - Vul je e-mail en wachtwoord in
   - Klik op "Opslaan"

### Credentials Instellen

Voor elke auto-login service moet je de volgende gegevens invullen:

#### Smartschool
- **E-mail:** Je Microsoft e-mail adres
- **Wachtwoord:** Je Microsoft wachtwoord

#### Smartschool Beheerder
- **E-mail:** Beheerders-Microsoft e-mail adres
- **Wachtwoord:** Beheerders-wachtwoord (zelfde loginflow als Smartschool)

#### Microsoft Admin
- **URL:** Admin URL (standaard: `https://admin.microsoft.com`)
- **E-mail:** Je admin e-mail adres
- **Wachtwoord:** Je admin wachtwoord

#### Google Admin
- **URL:** Admin URL (standaard: `https://admin.google.com`)
- **E-mail:** Je Google Workspace admin e-mail
- **Wachtwoord:** Je Google wachtwoord (kan Microsoft SSO redirect vereisen)

#### Easy4U
- **URL:** Easy4U login URL (standaard: `https://easy4u.nl/admin/`)
- **E-mail:** Je Easy4U e-mail adres
- **Wachtwoord:** Je Easy4U wachtwoord  
- **Desktop .exe op Windows:** gebruikt Microsoft Edge (standaard aanwezig); geen aparte browser-installatie nodig.

### RDP Servers Toevoegen

1. Ga naar "Remote Connections" in het menu
2. Klik op "➕ Server Toevoegen" onder RDP Servers
3. Vul in:
   - **Naam:** Een beschrijvende naam (bijv. "File Server")
   - **Host:** IP adres of hostname (bijv. `192.168.1.100`)
   - **Gebruikersnaam:** (Optioneel) `DOMAIN\user` of `user@domain.com`
   - **Wachtwoord:** (Optioneel) Wachtwoord voor automatische login

### SSH Servers Toevoegen

1. Ga naar "Remote Connections" in het menu
2. Klik op "➕ Server Toevoegen" onder SSH Servers
3. Vul in:
   - **Naam:** Een beschrijvende naam (bijv. "Linux Server")
   - **Host:** IP adres of hostname (bijv. `192.168.1.100`)
   - **Gebruikersnaam:** (Optioneel) SSH gebruikersnaam
   - **Poort:** (Standaard: 22)
   - **Private Key bestand:** (Optioneel) Pad naar private key (bijv. `C:\Users\...\.ssh\id_rsa`)
   - **Wachtwoord:** (Optioneel) Wordt automatisch ingevuld met PuTTY (plink.exe), anders handmatig invoeren

## 🚀 Gebruik

### Auto Login Starten

1. Open de web interface (`http://127.0.0.1:5000`)
2. Ga naar "Auto Login"
3. Klik op de knop van de gewenste service
4. Een Chrome browser venster opent automatisch en voert de login uit
5. **Let op:** Voor 2FA (twee-factor authenticatie) moet je handmatig de code invoeren

### RDP Verbinding Starten

1. Ga naar "Remote Connections"
2. Klik op "🔌 Verbinden" naast de gewenste RDP server
3. Een Remote Desktop venster opent automatisch

### SSH Verbinding Starten

1. Ga naar "Remote Connections"
2. Klik op "🔌 Verbinden" naast de gewenste SSH server
3. Een CMD prompt venster opent met de SSH verbinding
4. Als er een wachtwoord is opgegeven en PuTTY is geïnstalleerd, wordt het automatisch ingevuld
5. Anders moet je het wachtwoord handmatig invoeren

## 🔧 Utilities

De web interface bevat een Utilities pagina waar je verschillende onderhoudstaken kunt uitvoeren:

### Clean Credentials
- Verwijdert alle credentials uit `.env` bestand
- Verwijdert `credentials.json` bestand
- Verwijdert wachtwoorden uit RDP en SSH servers
- Verwijdert encryptie key file

**Let op:** Deze actie kan niet ongedaan worden gemaakt. Gebruik alleen als je alle credentials wilt wissen.

### Migrate Key File
- Migreert de encryptie key file van de oude locatie naar een veiligere locatie
- Oude key file blijft staan voor backward compatibility
- Nieuwe locatie: `%LOCALAPPDATA%\SintMaartenCampusAutologin\.credentials_key` (Windows)

### Security Test
- Voert automatische security tests uit
- Controleert op plaintext wachtwoorden
- Controleert bestandspermissies
- Controleert encryptie implementatie
- Controleert web interface beveiliging
- Toont gedetailleerde resultaten met aanbevelingen

**Aanbeveling:** Voer regelmatig een security test uit om te controleren of alles nog veilig is.

### Clean Servers
- Verwijdert alle RDP servers volledig uit de applicatie
- Verwijdert alle SSH servers volledig uit de applicatie
- Maakt de server lijsten leeg
- Toont gedetailleerde resultaten per server type

**Let op:** Deze actie kan niet ongedaan worden gemaakt. Alle servers worden permanent verwijderd uit de applicatie. Je kunt daarna nieuwe servers toevoegen via de web interface.

## 📚 Documentatie

De web interface bevat een ingebouwde documentatie pagina die automatisch de `README.md` leest en weergeeft:

- **Inhoudsopgave:** Navigatiebalk (sidebar) met inhoudsopgave naast de tekst; klik om naar een sectie te springen
- **Automatische updates:** Wanneer je `README.md` aanpast, wordt de documentatie automatisch bijgewerkt in de web interface
- **Markdown ondersteuning:** Volledige markdown syntax wordt ondersteund
- **Toegankelijk:** Documentatie is altijd beschikbaar via het menu

Ga naar "📚 Documentatie" in het menu om de volledige documentatie te bekijken.

## ⚠️ Beperkingen

### Auto Login Beperkingen

1. **Geen nieuwe services toevoegen via web interface**
   - Alleen de 4 vooraf geconfigureerde services zijn beschikbaar
   - Nieuwe services vereisen code-aanpassing en een nieuwe login module

2. **2FA (Twee-Factor Authenticatie)**
   - De tool kan niet automatisch 2FA codes invoeren
   - Je moet handmatig de 2FA code invoeren wanneer gevraagd
   - De browser blijft open zodat je dit kunt doen

3. **Microsoft SSO Redirects**
   - Google Admin login kan redirecten naar Microsoft SSO
   - De tool handelt dit automatisch af, maar kan extra tijd kosten

4. **Browser Automatisering**
   - Vereist Chrome browser
   - Selenium WebDriver wordt automatisch gedownload bij eerste gebruik
   - Kan traag zijn bij langzame internetverbindingen

### Remote Connections Beperkingen

1. **RDP**
   - Werkt alleen op Windows
   - Vereist Remote Desktop Client (standaard op Windows)
   - Wachtwoorden worden opgeslagen in Windows Credential Manager

2. **SSH**
   - OpenSSH is standaard op Windows 10+, anders vereist PuTTY
   - Automatische wachtwoord authenticatie vereist PuTTY met plink.exe
   - Zonder PuTTY moet je wachtwoorden handmatig invoeren

### Algemene Beperkingen

1. **Single User**
   - De tool is ontworpen voor gebruik door één gebruiker
   - Credentials worden opgeslagen per Windows gebruiker

2. **Localhost Only**
   - Web interface draait standaard alleen op localhost (127.0.0.1)
   - Niet geschikt voor remote access zonder extra configuratie

3. **Windows Only**
   - RDP functionaliteit werkt alleen op Windows
   - SSH werkt op Windows, Linux en macOS, maar is geoptimaliseerd voor Windows

## 🔒 Beveiliging

### Encryptie van Credentials

Alle wachtwoorden worden encrypted opgeslagen met **Fernet (AES-128)** encryptie:

- **Encryptie methode:** Fernet symmetric encryption
- **Key opslag:** Encryptie key wordt opgeslagen in een beveiligde locatie:
  - Windows: `%LOCALAPPDATA%\SintMaartenCampusAutologin\.credentials_key`
  - Linux/macOS: `~/.config/sintmaartencampus-autologin/.credentials_key`
- **Key beveiliging:** Key file heeft restricted permissions (alleen eigenaar kan lezen)

### Bestandsbeveiliging

- **Credentials bestand:** `credentials.json` bevat alleen encrypted wachtwoorden
- **RDP/SSH servers:** Wachtwoorden worden encrypted opgeslagen in JSON bestanden
- **Bestandspermissies:** Op Linux/macOS worden bestanden beschermd met 600 permissions
- **Windows:** Key files worden hidden gemaakt en hebben restricted permissions

### Input Validatie en XSS Preventie

Alle user input wordt gevalideerd en gesanitized:

- **HTML Escaping:** Alle string input wordt HTML-escaped om XSS aanvallen te voorkomen
- **Input Validatie:**
  - E-mail adressen worden gevalideerd met regex
  - URLs worden gevalideerd (alleen http/https)
  - Hostnames en IP adressen worden gevalideerd
  - Poort nummers worden gevalideerd (1-65535)
- **Path Traversal Preventie:** File paths worden gesanitized om directory traversal te voorkomen
- **Service Validatie:** Alleen geldige service namen worden geaccepteerd

### Web Interface Beveiliging

- **Flask Secret Key:** Secret key wordt gebruikt voor sessie beveiliging
  - Standaard: `dev-secret-key-change-in-production`
  - Productie: Stel `FLASK_SECRET_KEY` environment variable in
- **Localhost Only:** Web interface draait standaard alleen op localhost
- **JSON Input Validatie:** Alle JSON input wordt gevalideerd voordat verwerkt

### Git Security

- **.gitignore:** Alle gevoelige bestanden worden genegeerd:
  - `credentials.json`
  - `.credentials_key`
  - `.env`
  - `rdp_servers.json`
  - `ssh_servers.json`
- **Geen Plaintext Passwords:** Geen wachtwoorden worden gecommit naar Git

### Aanvullende Security Measures

1. **Master Password Ondersteuning**
   - Optioneel: Gebruik `CREDENTIALS_MASTER_PASSWORD` environment variable
   - Key wordt dan gegenereerd vanuit master password (geen key file nodig)

2. **Automatische Key Migratie**
   - Oude key files worden automatisch gemigreerd naar veilige locatie
   - Backward compatibility wordt behouden

3. **Error Handling**
   - Gevoelige informatie wordt niet gelekt in error messages
   - Decryptie fouten worden stil afgehandeld

4. **Security Test Script**
   - `src/core/security_test.py` controleert encryptie, bestandspermissies, key file, web security en gevoelige data
   - Via de app: **Utilities** → **SECURITY TEST**
   - Via command line: `python -c "import sys; sys.path.insert(0,'.'); from src.core.security_test import SecurityTest; t=SecurityTest(); t.run_all_tests(); t.print_results()"`
   - **Productie:** Zet `FLASK_SECRET_KEY` in .env om de waarschuwing over de default secret key weg te nemen
   - Geen kritieke problemen = groen; waarschuwing (bijv. default Flask secret key) = in productie FLASK_SECRET_KEY zetten

### Bescherming Tegen Aanvallen

#### XSS (Cross-Site Scripting)
- ✅ Alle user input wordt HTML-escaped
- ✅ Jinja2 templates gebruiken auto-escaping
- ✅ JavaScript input wordt gevalideerd

#### Path Traversal
- ✅ File paths worden gesanitized
- ✅ `..` en `//` worden verwijderd uit paths

#### SQL Injection
- ✅ Geen database gebruikt (niet van toepassing)

#### CSRF (Cross-Site Request Forgery)
- ⚠️ Geen CSRF tokens geïmplementeerd (interne tool)
- ✅ Web interface draait alleen op localhost
- 💡 Voor productie: Overweeg Flask-WTF voor CSRF protection

#### Credential Theft
- ✅ Wachtwoorden worden nooit in plaintext opgeslagen
- ✅ Encryptie key wordt apart opgeslagen
- ✅ Bestandspermissies beperken toegang
- ✅ Geen credentials in Git repository

#### Man-in-the-Middle
- ✅ HTTPS wordt gebruikt voor web logins (via browser)
- ⚠️ Web interface gebruikt HTTP (localhost only)
- 💡 Voor remote access: Gebruik HTTPS reverse proxy

## 🔧 Troubleshooting

### Probleem: "Credentials ontbreken" foutmelding

**Oplossing:**
1. Ga naar "Credentials Beheer" in de web interface
2. Vul alle verplichte velden in voor de service
3. Klik op "Opslaan"
4. Probeer opnieuw

### Probleem: Browser opent niet of login werkt niet

**Oplossingen:**
1. Controleer of Chrome is geïnstalleerd
2. Controleer je internetverbinding
3. Controleer of de credentials correct zijn
4. Bekijk de terminal output voor error messages

### Probleem: SSH wachtwoord wordt niet automatisch ingevuld

**Oplossingen:**
1. Installeer PuTTY (vereist voor automatische wachtwoord authenticatie)
2. Of gebruik een private key file in plaats van wachtwoord
3. Of voer wachtwoord handmatig in wanneer gevraagd

### Probleem: RDP verbinding werkt niet

**Oplossingen:**
1. Controleer of Remote Desktop is ingeschakeld op de server
2. Controleer of de hostname/IP correct is
3. Controleer of de gebruikersnaam en wachtwoord correct zijn
4. Test handmatig met `mstsc` command

### Probleem: Encryptie key niet gevonden

**Oplossingen:**
1. De key wordt automatisch aangemaakt bij eerste gebruik
2. Controleer bestandspermissies
3. Voer `python migrate_key_file.py` uit als migratie nodig is

### Probleem: Security test faalt

**Oplossingen:**
1. Voer `python security_test.py` uit om problemen te identificeren
2. Of gebruik de Utilities pagina in de web interface om de security test uit te voeren
3. Controleer of alle bestanden correct zijn geconfigureerd
4. Controleer bestandspermissies

### Probleem: Utilities scripts werken niet

**Oplossingen:**
1. Controleer of je de juiste permissies hebt om bestanden te wijzigen
2. Controleer of de scripts bestaan in de scripts directory
3. Bekijk de resultaten in de web interface voor specifieke foutmeldingen

### Probleem: Clean Servers verwijdert geen servers

**Oplossingen:**
1. Controleer of er daadwerkelijk servers zijn opgeslagen
2. Controleer of de JSON bestanden (rdp_servers.json, ssh_servers.json) bestaan
3. Bekijk de resultaten in de web interface voor details per server type
4. Controleer of je de juiste permissies hebt om bestanden te wijzigen

## 🔐 Security Best Practices

1. **Gebruik een sterke Flask secret key in productie:**
   ```bash
   set FLASK_SECRET_KEY=your-strong-random-secret-key-here
   ```
   Of voor de executable: Maak een `.env` bestand met `FLASK_SECRET_KEY=your-key`

2. **Voor productie gebruik:**
   ```bash
   set FLASK_DEBUG=False
   set FLASK_PORT=5000
   ```

3. **Voer regelmatig security tests uit:**
   - Via web interface: Ga naar "Utilities" → "Security Test"
   - Of via command line: `python security_test.py`

3. **Gebruik master password voor extra beveiliging:**
   ```bash
   set CREDENTIALS_MASTER_PASSWORD=your-master-password
   ```

4. **Houd dependencies up-to-date:**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

5. **Backup encryptie key:**
   - Backup de `.credentials_key` file op een veilige locatie
   - Zonder deze key kun je encrypted credentials niet decrypten

## 📞 Ondersteuning

Voor vragen of problemen:
1. Controleer deze documentatie
2. Voer `python security_test.py` uit om beveiligingsproblemen te identificeren
3. Bekijk de terminal output voor error messages

## 📄 Licentie

Deze tool is ontwikkeld voor intern gebruik bij Sint-Maarten Campus.

---

**Versie:** 1.0.9  
**Laatste update:** Februari 2026  
**Auteur:** Wesley Van Hoof

### Changelog

#### Versie 1.0.9 (Februari 2026)
- ✅ **Release:** Wipe van credentials en servers vóór elke build in de workflow; schone zip zonder login-restanten
- ✅ **Easy4U:** Gebruikt Microsoft Edge op Windows (werkt op elke PC zonder extra installatie)
- ✅ **Titelbalk:** Versie in HTML-titel zodat de venstertitel overal de versie toont

#### Versie 1.0.8 (Februari 2026)
- ✅ **Desktop .exe:** Geen console-venster en geen DevTools meer bij start; alleen het applicatievenster
- ✅ **Venstertitel:** Versie zichtbaar in de titelbalk (Sint Maarten Campus Autologin Tool v1.0.8)
- ✅ **Release workflow:** Juiste rechten voor GitHub Releases; build (Windows) en release (Ubuntu) gesplitst; zip als asset

#### Versie 1.0.7 (Februari 2026)
- ✅ **Documentatie:** Zoekfunctie toegevoegd op de documentatiepagina (live zoeken, markeren van treffers, scroll naar eerste resultaat)
- ✅ **Desktop-app:** Verbeterd laadgedrag: directe URL naar hoofdpagina met cache-busting, langere wachttijd na serverstart, no-cache headers voor HTML om wit scherm te verminderen
- ✅ **Desktop-app:** Route `/loading` beschikbaar voor same-origin laadscherm; standalone-modus gebruikt `loading.html` in static export

#### Versie 1.0.6 (Februari 2026)
- ✅ **Documentatie:** Nieuwe navigatiebalk met inhoudsopgave op de documentatiepagina (sticky sidebar, smooth scroll)
- ✅ **Security:** Security test controleert op default Flask secret key; README tip voor FLASK_SECRET_KEY in productie

#### Versie 1.0.5 (Februari 2026)
- ✅ **Easy4U:** Auto-login overgezet naar Playwright voor betrouwbare invulling en klik op easy4u.nl
- ✅ **Easy4U:** Standaard-URL en normalisatie naar `https://easy4u.nl/admin/` (voor iedereen)
- ✅ **API-bridge:** Credentials, utilities en remote connections werken in desktop-app (pywebview + fetch-fallback)
- ✅ **Routes:** Correcte API-routes (`/api/rdp/servers`, `/api/ssh/servers`, `/api/utilities/<name>`)
- ✅ **Security test:** Imports en paden gefixt voor `src.core`; encryptie- en security-utils tests slagen
- ✅ **Documentatie:** Playwright + `playwright install chromium` toegevoegd aan installatie-instructies
- ✅ **Build:** js_api in Flask-modus doorgegeven zodat API in alle modi beschikbaar is

#### Versie 1.0.3 (Februari 2026)
- ✅ Clean Servers functionaliteit aangepast: verwijdert nu volledige servers (niet alleen wachtwoorden)
- ✅ Verbeterde web interface display voor Clean Servers resultaten
- ✅ Duidelijke waarschuwing dat Clean Servers actie niet ongedaan kan worden gemaakt
- ✅ Security test uitgevoerd: alle tests geslaagd
- ✅ Productie-instellingen toegevoegd (debug mode, secret key handling)
- ✅ Windows executable build ondersteuning (PyInstaller)
- ✅ Build scripts toegevoegd voor distributie

#### Versie 1.0.2 (Februari 2026)
- ✅ Clean Servers script geïntegreerd in web interface
- ✅ Verbeterde documentatie voor Utilities functionaliteit
- ✅ Clean Servers ondersteunt encrypted wachtwoorden (decrypt, verwijder, opslaan)
- ✅ Verbeterde error handling in Clean Servers script

#### Versie 1.0.1 (Februari 2026)
- ✅ Utilities pagina toegevoegd voor uitvoeren van fix scripts
- ✅ Ingebouwde documentatie pagina die automatisch README.md leest
- ✅ SSH wachtwoord authenticatie ondersteuning (met PuTTY)
- ✅ Verbeterde input validatie en XSS preventie
- ✅ Security test script geïntegreerd in web interface
- ✅ Automatische key file migratie functionaliteit
- ✅ Clean Servers script toegevoegd (RDP en SSH wachtwoorden verwijderen)
- ✅ Verbeterde error handling en gebruikersfeedback

#### Versie 1.0 (Februari 2026)
- ✅ Eerste release
- ✅ Auto-login voor Smartschool, Smartschool Beheerder, Microsoft Admin, Google Admin, Easy4U
- ✅ RDP en SSH server beheer
- ✅ Encrypted credential opslag
- ✅ Web interface voor beheer
