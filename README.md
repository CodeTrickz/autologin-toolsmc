# Sint Maarten Campus Autologin Tool

Een veilige, geautomatiseerde login tool voor het Sint Maarten Campus die automatisch kan inloggen op verschillende web services en remote connections kan beheren via een gebruiksvriendelijke web interface.

## 📋 Inhoudsopgave

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
2. **Microsoft Admin** - Directe login naar Microsoft 365 Admin Center
3. **Google Admin** - Login naar Google Workspace Admin Console (inclusief Microsoft SSO redirect handling)
4. **Easy4U** - Automatische login naar Easy4U platform

**Belangrijk:** Je kunt geen nieuwe auto-login services toevoegen via de web interface. Alleen de bovenstaande 4 services zijn ondersteund. Voor nieuwe services is code-aanpassing nodig.

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

1. Download of clone de repository
2. Open een terminal/command prompt in de project root directory

### Stap 2: Installeer Dependencies

```bash
pip install -r requirements.txt
```

Dit installeert:
- `selenium` - Voor browser automation
- `python-dotenv` - Voor environment variables
- `flask` - Voor de web interface
- `cryptography` - Voor encryptie van credentials
- `markdown` - Voor documentatie weergave in web interface
- `pyinstaller` - Voor het maken van een Windows executable

### Stap 2b: (Optioneel) Maak een Windows Executable

Voor distributie als standalone Windows applicatie:

```bash
scripts\build_exe.bat
```

Dit maakt een `SintMaartenCampusAutologin.exe` bestand in de `dist` folder.

Voor een complete release package:

```bash
scripts\package_release.bat
```

Dit maakt een `release` folder met alle benodigde bestanden.

### Stap 3: Installatie op Windows Device

Zie `docs/INSTALLATIE.md` voor gedetailleerde installatie-instructies.

**Kort overzicht:**
1. Kopieer de `dist\SintMaartenCampusAutologin` folder naar je computer
2. Dubbelklik op `SintMaartenCampusAutologin.exe` om te starten
3. Open je browser en ga naar `http://127.0.0.1:5000`
4. Configureer je credentials via de web interface
- `markdown` - Voor documentatie weergave in web interface

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

#### Microsoft Admin
- **URL:** Admin URL (standaard: `https://admin.microsoft.com`)
- **E-mail:** Je admin e-mail adres
- **Wachtwoord:** Je admin wachtwoord

#### Google Admin
- **URL:** Admin URL (standaard: `https://admin.google.com`)
- **E-mail:** Je Google Workspace admin e-mail
- **Wachtwoord:** Je Google wachtwoord (kan Microsoft SSO redirect vereisen)

#### Easy4U (Portal Easy4u)
- **URL:** `https://my.easy4u.be/nl/login` (standaard)
- **E-mail:** Je gebruikersnaam of e-mail voor Portal Easy4u
- **Wachtwoord:** Je Easy4U wachtwoord

### Bestandslocaties

- **Bij normaal gebruik (Python):** credentials en serverbestanden staan in de projectmap.
- **Bij gebruik van de .exe:** alle data staat in een persistente map zodat die behouden blijft:
  - Windows: `%LOCALAPPDATA%\SintMaartenCampusAutologin\` (o.a. `credentials.json`, `.env`, `rdp_servers.json`, `ssh_servers.json`).
- **Clean Credentials** en **Utilities** werken in dezelfde map, dus alle credentials worden correct opgeschoond.

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
   - `security_test.py` controleert automatisch op beveiligingsproblemen
   - Voer regelmatig uit: `python security_test.py`

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
3. Voer `python src/core/migrate_key_file.py` uit als migratie nodig is

### Probleem: Security test faalt

**Oplossingen:**
1. Voer `python src/core/security_test.py` uit om problemen te identificeren
2. Of gebruik de Utilities pagina in de web interface om de security test uit te voeren
3. Controleer of alle bestanden correct zijn geconfigureerd
4. Controleer bestandspermissies

### Waarschuwing: "Failed to remove temporary directory" (bij afsluiten .exe)

**Wat het is:** Bij het sluiten van de desktop-app (.exe) probeert PyInstaller de tijdelijke map `C:\Users\...\AppData\Local\Temp\_MEI...` te verwijderen. Soms lukt dat niet (bestand nog in gebruik, antivirus).

**Wat je kunt doen:**
- **Negeer de melding** – de app is gewoon gesloten; je kunt op OK drukken. Eventuele restmap in Temp kun je later handmatig verwijderen.
- **Optioneel:** Voeg een uitzondering toe voor de app in je antivirus, of sluit geen andere programma’s die bestanden in die map kunnen openen terwijl je de app afsluit.

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
   - Of via command line: `python src/core/security_test.py`

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
2. Voer `python src/core/security_test.py` uit om beveiligingsproblemen te identificeren
3. Bekijk de terminal output voor error messages

## 📄 Licentie

Deze tool is ontwikkeld voor intern gebruik bij Sint-Maarten Campus.

---

**Versie:** 1.0.4  
**Laatste update:** Februari 2026  
**Auteur:** Wesley Van Hoof

### Changelog

#### Versie 1.0.4 (Februari 2026)
- ✅ Clean Credentials gebruikt nu dezelfde datamap als de app (werkt voor alle credentials, ook vanuit .exe)
- ✅ Easy4U auto-login afgestemd op Portal Easy4u (my.easy4u.be/nl/login): Gebruikersnaam, Wachtwoord, knop Inloggen
- ✅ Documentatie wordt direct meegenomen bij static export (geen laadstap meer)
- ✅ Credentials en serverbestanden in persistente map bij .exe (AppData\Local\SintMaartenCampusAutologin)
- ✅ Troubleshooting: waarschuwing "Failed to remove temporary directory" (_MEI) toegevoegd
- ✅ Standalone desktop-modus: .exe gebruikt standaard geen Flask/localhost in browser

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
- ✅ Auto-login voor Smartschool, Microsoft Admin, Google Admin, Easy4U
- ✅ RDP en SSH server beheer
- ✅ Encrypted credential opslag
- ✅ Web interface voor beheer
