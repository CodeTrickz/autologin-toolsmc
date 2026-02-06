# Installatie Handleiding - Sint Maarten Campus Autologin Tool

## Snelle Installatie

### Optie 1: Gebruik de Installer (Aanbevolen)

1. **Run `install.bat` als Administrator:**
   - Rechtermuisknop op `install.bat`
   - Kies "Run as administrator"
   - Volg de instructies

2. **Start de applicatie:**
   - Dubbelklik op het icoon op je bureaublad: **"Sint Maarten Campus Autologin"**
   - De web interface opent automatisch in je browser

### Optie 2: Maak een Professional Installer (Met Inno Setup)

1. **Download Inno Setup:**
   - Ga naar: https://jrsoftware.org/isdl.php
   - Download en installeer Inno Setup 6

2. **Maak de installer:**
   ```powershell
   .\create_installer.ps1
   ```

3. **Distribueer de installer:**
   - De installer staat in: `installer_output\SintMaartenCampusAutologin_Setup.exe`
   - Dit is een professionele Windows installer die je kunt distribueren

## Wat gebeurt er tijdens installatie?

- ✅ Applicatie wordt geïnstalleerd in `C:\Program Files\SintMaartenCampusAutologin`
- ✅ Snelkoppeling wordt gemaakt op het bureaublad
- ✅ Snelkoppeling wordt toegevoegd aan Start Menu
- ✅ Uninstall script wordt aangemaakt

## Gebruik

Na installatie:
1. Dubbelklik op het icoon op je bureaublad
2. De applicatie start automatisch
3. Je browser opent automatisch naar `http://127.0.0.1:5000`
4. Configureer je credentials via de web interface

## Verwijderen

1. Ga naar: `C:\Program Files\SintMaartenCampusAutologin`
2. Run `uninstall.bat`
3. Of gebruik "Add or Remove Programs" in Windows (als geïnstalleerd via Inno Setup installer)

## Troubleshooting

### Applicatie start niet
- Controleer of Chrome browser is geïnstalleerd
- Run als Administrator
- Controleer Windows Firewall

### Browser opent niet automatisch
- Start de applicatie handmatig
- Open browser en ga naar: `http://127.0.0.1:5000`

### Snelkoppeling werkt niet
- Controleer of de applicatie in `C:\Program Files\SintMaartenCampusAutologin` staat
- Maak handmatig een nieuwe snelkoppeling naar `start_autologin.bat`
