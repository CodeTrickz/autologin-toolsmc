# Installatie Instructies - Sint Maarten Campus Autologin Tool

## Vereisten

Voordat je de applicatie installeert, zorg ervoor dat je hebt:
- **Windows 10 of 11**
- **Chrome browser** (vereist voor automatische logins)
- **Internet verbinding**

## Installatie Methoden

### Methode 1: Installatie via Installer (Aanbevolen)

1. **Download of maak de installer:**
   - Als je Inno Setup hebt: Run `create_installer.ps1` om een installer te maken
   - Of gebruik het `install.bat` script voor een eenvoudige installatie

2. **Run de installer:**
   - Dubbelklik op `SintMaartenCampusAutologin_Setup.exe` (als gemaakt met Inno Setup)
   - Of run `install.bat` als Administrator (rechtermuisknop → "Run as administrator")

3. **Volg de installatie wizard:**
   - Kies installatie locatie (standaard: `C:\Program Files\SintMaartenCampusAutologin`)
   - Kies of je een snelkoppeling op het bureaublad wilt
   - Klik op "Install"

4. **Start de applicatie:**
   - Dubbelklik op het icoon op je bureaublad: **"Sint Maarten Campus Autologin"**
   - De applicatie start automatisch en opent de web interface in je browser

### Methode 2: Handmatige Installatie

1. **Kopieer de applicatie:**
   - Kopieer de hele `dist\SintMaartenCampusAutologin` folder naar je computer
   - Plaats deze folder op een locatie waar je gemakkelijk bij kunt (bijvoorbeeld: `C:\Program Files\SintMaartenCampusAutologin`)

2. **Maak een snelkoppeling:**
   - Rechtermuisknop op `start_autologin.bat` (of maak deze aan)
   - Kies "Create shortcut"
   - Sleep de snelkoppeling naar je Desktop

3. **Start de applicatie:**
   - Dubbelklik op de snelkoppeling
   - De applicatie start automatisch en opent de web interface in je browser

### Stap 4: Configureer Credentials

1. Klik op **"🔐 Credentials"** in het menu
2. Vul je inloggegevens in voor:
   - Smartschool
   - Microsoft Admin
   - Google Admin
   - Easy4U
3. Klik op **"Opslaan"** voor elke service

**Belangrijk:** Je credentials worden versleuteld opgeslagen en zijn niet leesbaar in plaintext.

### Stap 5: (Optioneel) Voeg RDP/SSH Servers Toe

1. Klik op **"🖥️ Remote Connections"** in het menu
2. Voeg RDP of SSH servers toe via de web interface
3. Configureer de verbindingsgegevens

## Automatisch Starten bij Windows Opstarten

### Methode 1: Via Startup Folder (Eenvoudig)

1. Druk op `Windows + R`
2. Typ: `shell:startup` en druk Enter
3. Maak een snelkoppeling naar `SintMaartenCampusAutologin.exe`
4. Sleep deze snelkoppeling naar de Startup folder

### Methode 2: Via Task Scheduler (Geavanceerd)

1. Open **Task Scheduler** (zoek in Start menu)
2. Klik op **"Create Basic Task"**
3. Geef een naam: "Sint Maarten Campus Autologin"
4. Trigger: **"When I log on"**
5. Action: **"Start a program"**
6. Program: Navigeer naar `SintMaartenCampusAutologin.exe`
7. Start in: De folder waar de .exe staat
8. Vink **"Run with highest privileges"** aan (optioneel)
9. Klik **Finish**

## Troubleshooting

### Probleem: Applicatie start niet

**Oplossingen:**
1. Controleer of Chrome browser is geïnstalleerd
2. Controleer of antivirus de applicatie niet blokkeert
3. Run als Administrator (rechtermuisknop → "Run as administrator")
4. Controleer of poort 5000 niet al in gebruik is

### Probleem: Web interface laadt niet

**Oplossingen:**
1. Controleer of de console venster nog open is
2. Controleer of je naar `http://127.0.0.1:5000` gaat (niet `localhost`)
3. Controleer Windows Firewall instellingen
4. Probeer een andere browser

### Probleem: Auto-login werkt niet

**Oplossingen:**
1. Controleer of Chrome browser is geïnstalleerd en up-to-date is
2. Controleer of je credentials correct zijn ingevuld
3. Controleer je internet verbinding
4. Bekijk de console output voor foutmeldingen

### Probleem: RDP/SSH verbinding werkt niet

**Oplossingen:**
1. Voor RDP: Controleer of Remote Desktop is ingeschakeld op de server
2. Voor SSH: Controleer of OpenSSH of PuTTY is geïnstalleerd
3. Controleer of de hostname/IP correct is
4. Controleer of de gebruikersnaam en wachtwoord correct zijn

## Verwijderen van de Applicatie

1. Stop de applicatie (sluit het console venster)
2. Verwijder de `SintMaartenCampusAutologin` folder
3. (Optioneel) Verwijder de snelkoppeling uit de Startup folder
4. (Optioneel) Verwijder de taak uit Task Scheduler

**Let op:** Je opgeslagen credentials worden ook verwijderd. Maak een backup als je deze wilt behouden.

## Backup van Credentials

Je credentials worden opgeslagen in:
- `%LOCALAPPDATA%\SintMaartenCampusAutologin\.credentials_key` (encryptie key)
- In de folder waar de applicatie staat: `credentials.json` (versleutelde credentials)

Voor backup, kopieer beide bestanden naar een veilige locatie.

## Support

Voor vragen of problemen, raadpleeg de documentatie in de applicatie zelf via de **"📚 Documentatie"** tab.
