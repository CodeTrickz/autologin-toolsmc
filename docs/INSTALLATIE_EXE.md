# Installatie als Enkele .exe Bestand

## Huidige Situatie

De applicatie is gebouwd als **directory-based** versie (folder met .exe + dependencies). Dit is de meest betrouwbare methode.

## Optie 1: Gebruik de Directory-Based Versie (Aanbevolen)

De applicatie werkt perfect als directory-based versie:

1. **Kopieer de hele folder:**
   - Ga naar: `dist\SintMaartenCampusAutologin\`
   - Kopieer de hele folder naar je gewenste locatie

2. **Maak een snelkoppeling:**
   - Rechtermuisknop op `SintMaartenCampusAutologin.exe`
   - Kies "Create shortcut"
   - Sleep de snelkoppeling naar je Desktop of Start Menu

3. **Gebruik de snelkoppeling:**
   - Dubbelklik op de snelkoppeling om te starten
   - De applicatie werkt hetzelfde als een enkele .exe

**Voordeel:** Betrouwbaar, geen antivirus problemen, sneller opstarten.

## Optie 2: Build als Enkele .exe (Geavanceerd)

Als je echt een enkele .exe wilt, moet je eerst antivirus/Windows Defender uitschakelen:

### Stappen:

1. **Schakel Windows Defender tijdelijk uit:**
   - Open Windows Security
   - Ga naar "Virus & threat protection"
   - Klik op "Manage settings"
   - Schakel "Real-time protection" tijdelijk uit

2. **Build de executable:**
   ```bash
   pyinstaller SintMaartenCampusAutologin.spec --clean --noconfirm
   ```

3. **Schakel Windows Defender weer aan**

4. **Voeg uitzondering toe:**
   - Windows Security → Virus & threat protection → Manage settings
   - Scroll naar "Exclusions"
   - Voeg de .exe toe als uitzondering

**Let op:** Een enkele .exe is groter (~50-100 MB) en start langzamer omdat alles eerst uitgepakt moet worden.

## Aanbeveling

Gebruik **Optie 1** (directory-based). Dit is:
- ✅ Betrouwbaarder
- ✅ Sneller opstarten
- ✅ Minder antivirus problemen
- ✅ Makkelijker te debuggen

De gebruiker ziet alleen de snelkoppeling, dus het voelt hetzelfde als een enkele .exe!
