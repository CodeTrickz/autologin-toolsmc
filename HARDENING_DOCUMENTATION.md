# Hardening Documentation

Dit document bundelt alle hardening-documentatie van de applicatie in één plaats.
Per maatregel staat hieronder:

- wat er is gehardend;
- hoe het technisch is geïmplementeerd;
- waarom dit nodig was;
- waarom dit de applicatie veiliger maakt.

Dit document is bedoeld als volledig overzicht voor beheer, review en toekomstig onderhoud.

## Scope

De hardening richt zich op de belangrijkste risico's in deze applicatie:

- diefstal van opgeslagen credentials;
- lekken van secrets naar de UI of API;
- misbruik van de lokale web-API;
- phishing of misconfiguratie via foutieve admin-URL's;
- command injection bij externe connecties;
- onnodig persistente browserprofielen en sessies;
- onveilige opslag van gevoelige data in de projectmap.

## Algemeen beveiligingsmodel

De applicatie is een lokale desktop/webtool die:

- credentials bewaart;
- admin-portals automatisch opent;
- browserautomatisering gebruikt;
- lokaal een web/API-laag aanbiedt;
- RDP- en SSH-connecties kan starten.

Daarom is de hardening opgebouwd rond drie principes:

1. secrets blijven zoveel mogelijk aan de Python/OS-kant;
2. gevoelige paden worden beperkt tot officiële en gecontroleerde inputs;
3. browser- en API-oppervlakken worden actief verkleind.

## 1. Secrets worden niet meer teruggestuurd naar de UI

### Wat is gehardend

- Opgeslagen wachtwoorden worden niet meer als plaintext teruggegeven aan de frontend.
- De credentials-API en serverlijsten sturen alleen nog een `has_password` indicatie.
- De desktop bridge gebruikt dezelfde redactie.

### Hoe dit technisch is gedaan

Bestanden:

- `src/web/web_interface.py`
- `src/web/desktop_api.py`

Techniek:

- De helper `_redact_credentials_for_response()` vervangt `password` door `has_password`.
- De helper `_redact_servers_for_response()` verwijdert wachtwoorden uit RDP/SSH responses.
- Zowel Flask-routes als de `pywebview` desktop API gebruiken deze redactie voordat data naar de UI gaat.

### Waarom dit nodig was

In de eerdere situatie konden opgeslagen secrets opnieuw zichtbaar worden in:

- browser devtools;
- frontend state;
- JavaScript foutenlogs;
- eventuele XSS-contexten;
- responses van localhost API-calls.

### Waarom dit de applicatie veiliger maakt

Een aanvaller of ongewenste scriptcontext kan een reeds opgeslagen wachtwoord niet meer simpel terug opvragen via de UI-laag. Daardoor daalt het risico op credential-exfiltratie via frontend, browser debugging of lokale API-inspectie.

## 2. Verbindingen starten server-side via `server_id`

### Wat is gehardend

- RDP en SSH kunnen nu gestart worden op basis van een `server_id`.
- De frontend hoeft daarvoor geen opgeslagen wachtwoorden meer eerst op te halen.

### Hoe dit technisch is gedaan

Bestanden:

- `src/web/web_interface.py`
- `src/web/desktop_api.py`
- `templates/remote_connections.html`

Techniek:

- De UI stuurt alleen `server_id` naar `/api/rdp/connect` en `/api/ssh/connect`.
- De backend zoekt de serverdefinitie op, leest het wachtwoord lokaal in en start pas daarna de connectie.
- De browser krijgt het geheime veld nooit meer te zien.

### Waarom dit nodig was

Eerder moest de browserlaag weten welk wachtwoord bij een opgeslagen server hoorde om een verbinding te starten. Dat is onnodig risicovol.

### Waarom dit de applicatie veiliger maakt

Secrets blijven binnen de backendlogica en komen niet meer terecht in UI-requests, JSON-objecten of browser state. Dit verkleint de attack surface aanzienlijk.

## 3. Lokale API is beschermd met locality checks en CSRF

### Wat is gehardend

- API-verkeer wordt beperkt tot lokale requests.
- Schrijfacties vereisen een CSRF-token.
- Origin/Referer worden gecontroleerd als extra controlelaag.

### Hoe dit technisch is gedaan

Bestanden:

- `src/web/web_interface.py`
- `templates/base.html`

Techniek:

- `protect_local_api()` controleert of requests alleen van `127.0.0.1` of equivalente localhost-adressen komen.
- Voor `POST`, `PUT`, `PATCH` en `DELETE` is een geldig `X-App-CSRF-Token` vereist.
- Het CSRF-token wordt per sessie opgeslagen en via de templates beschikbaar gemaakt.
- De frontend bridge bouwt fetch-headers centraal op en stuurt het token automatisch mee.

### Waarom dit nodig was

Een localhost API is veiliger dan een publiek luisterende service, maar zonder extra checks blijft misbruik door lokale processen of ongewenste browsercontexten mogelijk.

### Waarom dit de applicatie veiliger maakt

Deze laag maakt onbedoelde of kwaadaardige requests tegen de API moeilijker. Vooral state-changing acties zijn nu niet meer vrij uitvoerbaar zonder geldige sessiecontext.

## 4. Flask secret key is niet meer voorspelbaar

### Wat is gehardend

- De applicatie gebruikt geen vaste development fallback secret key meer als operationele sleutel.
- Er wordt automatisch een persistente geheime sleutel aangemaakt in een gebruikersspecifieke locatie.

### Hoe dit technisch is gedaan

Bestanden:

- `src/web/web_interface.py`
- `src/web/desktop_app.py`

Techniek:

- `get_flask_secret_key()` gebruikt eerst `FLASK_SECRET_KEY` als override.
- Als die niet gezet is, wordt lokaal een persistente random secret aangemaakt.
- De oude runtime-logica die terugviel op een voorspelbare standaard is verwijderd uit het hoofdpad.

### Waarom dit nodig was

Een voorspelbare of bekende secret key ondermijnt:

- sessiebeveiliging;
- CSRF-bescherming;
- integriteit van session cookies.

### Waarom dit de applicatie veiliger maakt

Een unieke, niet-voorspelbare secret key beschermt de sessielaag veel beter en voorkomt triviaal misbruik van Flask session signing.

## 5. Security headers zijn toegevoegd

### Wat is gehardend

De app zet nu standaard browser security headers:

- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `Referrer-Policy: no-referrer`
- `Permissions-Policy`
- `Content-Security-Policy`

### Hoe dit technisch is gedaan

Bestand:

- `src/web/web_interface.py`

Techniek:

- In `no_cache_html()` worden de headers aan responses toegevoegd.
- De CSP beperkt onder andere:
  - externe connecties;
  - framing;
  - base-uri;
  - form submits buiten de app-context.

### Waarom dit nodig was

Zonder deze headers is de browserlaag gevoeliger voor:

- clickjacking;
- MIME sniffing;
- ongewenste externe resource-loads;
- bredere script- en form-oppervlakken.

### Waarom dit de applicatie veiliger maakt

Deze headers verkleinen de kans dat de UI in een ongewenste browsercontext wordt misbruikt of dat browsergedrag te veel vrijheid krijgt.

## 6. SSH command injection is verwijderd

### Wat is gehardend

- SSH-commando's worden niet meer als shell-string samengesteld voor uitvoering.
- `shell=True` is verwijderd uit het relevante Windows-pad.

### Hoe dit technisch is gedaan

Bestand:

- `src/auto_login/auto_ssh_connect.py`

Techniek:

- Commando's worden opgebouwd als argumentlijsten.
- `subprocess.Popen()` draait met `shell=False`.
- Host, user, poort en key-path worden als afzonderlijke argumenten doorgegeven.

### Waarom dit nodig was

Als invoer in een shell-string terechtkomt, kunnen speciale tekens of manipulaties leiden tot command injection.

### Waarom dit de applicatie veiliger maakt

De shell interpreteert invoer niet meer als uitvoerbare tekst. Daardoor daalt het risico dat een hostnaam, username of pad een extra command uitvoert.

## 7. Credential-opslag is versterkt met DPAPI op Windows

### Wat is gehardend

- De Fernet-sleutel wordt op Windows nu DPAPI-beschermd opgeslagen.
- De sleutel is daarmee gebonden aan de ingelogde Windows-gebruiker.
- Oude sleutelbestanden worden gemigreerd naar het nieuwe model.

### Hoe dit technisch is gedaan

Bestand:

- `src/core/credentials_manager.py`

Techniek:

- Via `ctypes` worden `CryptProtectData` en `CryptUnprotectData` gebruikt.
- De nieuwe sleutel wordt opgeslagen als `.credentials_key.dpapi`.
- Oude raw keyfiles in AppData of projectlocaties worden compatibel overgezet.

### Waarom dit nodig was

Een los onbeschermd key-bestand op dezelfde machine is voor administratorgebruik te zwak. Iemand met toegang tot bestanden kan dan zowel data als sleutel buitmaken.

### Waarom dit de applicatie veiliger maakt

DPAPI koppelt de decryptie aan het Windows-account. Dat maakt offline misbruik, bestandsdiefstal en eenvoudig kopiëren van de sleutel aanzienlijk lastiger.

## 8. Gevoelige app-data staat niet meer standaard in de projectmap

### Wat is gehardend

- De standaard datamap staat nu buiten de broncode.
- Oude data uit de legacy projectlocatie kan automatisch worden gemigreerd.

### Hoe dit technisch is gedaan

Bestand:

- `src/core/credentials_manager.py`

Techniek:

- Op Windows wordt standaard `LOCALAPPDATA/SintMaartenCampusAutologin` gebruikt.
- Op niet-Windows systemen wordt een configuratiemap onder de gebruiker gebruikt.
- Alleen bij expliciete override `AUTOLOGIN_USE_PROJECT_DATA_DIR=true` wordt nog de projectmap gebruikt.

### Waarom dit nodig was

Gevoelige bestanden in een projectmap verhogen het risico op:

- onbedoeld committen;
- backuppen naar verkeerde locaties;
- delen van secrets via zip, sync of version control;
- vermenging van code en data.

### Waarom dit de applicatie veiliger maakt

Gevoelige data wordt fysiek beter gescheiden van de codebase. Dat verkleint operationele fouten en beperkt blootstelling.

## 9. Admin-portals zijn gelockt op officiële URL's

### Wat is gehardend

- Voor admin-services worden alleen officiële, vertrouwde portal-URL's gebruikt.
- Die URLs zijn niet langer vrij instelbaar in de betekenisvolle zin.

### Hoe dit technisch is gedaan

Bestanden:

- `src/core/security_utils.py`
- `src/web/web_interface.py`
- `src/web/desktop_api.py`
- `templates/credentials.html`
- `src/auto_login/auto_microsoft_admin_login.py`
- `src/auto_login/auto_intune_admin_login.py`
- `src/auto_login/auto_azure_admin_login.py`
- `src/auto_login/auto_google_admin_login.py`

Techniek:

- `CANONICAL_SERVICE_URLS` definieert de officiële URLs.
- `normalize_service_url()` forceert voor gelockte services de canonical URL.
- De UI toont deze velden read-only.
- De backend slaat alleen de genormaliseerde/vertrouwde URL op.
- De login-scripts gebruiken rechtstreeks de canonical URL.

### Waarom dit nodig was

Vrij instelbare admin-URL's kunnen leiden tot:

- phishing-achtige misconfiguraties;
- typo-domains;
- ongewenste redirects;
- verkeerd geopende of kwaadaardige portalen.

### Waarom dit de applicatie veiliger maakt

De tool kan admin-credentials niet zomaar naar een willekeurige URL leiden. Daardoor wordt het risico op misbruik via verkeerde portal-configuratie sterk verkleind.

## 10. Bestaande wachtwoorden blijven behouden zonder ze opnieuw te tonen

### Wat is gehardend

- Een gebruiker kan credentials wijzigen zonder het opgeslagen wachtwoord terug te zien of opnieuw in te voeren.

### Hoe dit technisch is gedaan

Bestanden:

- `src/core/security_utils.py`
- `src/web/web_interface.py`
- `src/web/desktop_api.py`
- `templates/credentials.html`

Techniek:

- `preserve_existing_secret()` behoudt het bestaande wachtwoord wanneer er geen nieuw wachtwoord wordt ingestuurd.
- Het wachtwoordveld wordt bewust leeg weergegeven.
- De UI toont alleen dat er al een wachtwoord aanwezig is.

### Waarom dit nodig was

Zonder deze logica zou men gedwongen worden:

- wachtwoorden opnieuw zichtbaar te maken;
- wachtwoorden opnieuw in de UI te laden;
- of credentials per ongeluk kwijt te raken.

### Waarom dit de applicatie veiliger maakt

Deze aanpak voorkomt zowel secret-lekken als onnodige operationele fouten, terwijl de beheerervaring werkbaar blijft.

## 11. Admin-browser sessies zijn strakker gehard

### Wat is gehardend

- Admin-logins draaien standaard in tijdelijke, geïsoleerde incognito sessies.
- De gedeelde tabsessie wordt voor admin-portals overgeslagen.
- Sync, wachtwoordmanager en autofill zijn uitgeschakeld.
- Browserprofielen van de tool worden standaard opgeschoond bij afsluiten.

### Hoe dit technisch is gedaan

Bestanden:

- `src/auto_login/browser_session.py`
- `src/auto_login/browser_cleanup.py`
- `src/auto_login/auto_microsoft_admin_login.py`
- `src/auto_login/auto_intune_admin_login.py`
- `src/auto_login/auto_azure_admin_login.py`
- `src/auto_login/auto_google_admin_login.py`

Techniek:

- `hardened_admin_session()` forceert voor admin-services geïsoleerde incognito sessies.
- Chrome options schakelen sync, password manager en autofill-gerelateerde functies uit.
- Browserprofielen onder de tool-datamap worden op exit verwijderd, tenzij expliciet uitgeschakeld.

### Waarom dit nodig was

Admin-cookies en sessies zijn een hoogwaardig doelwit. Persistente browserprofielen vergroten het risico op:

- sessiehergebruik;
- cookie-diefstal;
- kruisbesmetting tussen accounts;
- achterblijvende admin-logincontexten.

### Waarom dit de applicatie veiliger maakt

De levensduur en herbruikbaarheid van admin-sessies wordt beperkt. Dat verlaagt het risico dat een achtergebleven profiel of cookie later opnieuw misbruikt wordt.

## 12. Oude onveilige statische exports zijn vervangen

### Wat is gehardend

- De actuele statische export is opnieuw opgebouwd vanuit de geharde templates.
- Oude dubbele of verouderde exports zijn opgeschoond.

### Hoe dit technisch is gedaan

Bestanden:

- `src/web/export_static.py`
- `static_export/*`

Techniek:

- De export is opnieuw gegenereerd na de hardening.
- Oude ongebruikte HTML-kopieën onder de oude exportlocatie zijn verwijderd.

### Waarom dit nodig was

Een standalone of desktopvariant mag geen oude frontendcode blijven bevatten als daar nog zwakkere beveiligingslogica in zit.

### Waarom dit de applicatie veiliger maakt

Alle runtimes gebruiken nu dezelfde geharde UI-logica, in plaats van een mix van nieuwe en oude beveiligingsniveaus.

## 13. Credential utilities zijn bijgewerkt op het nieuwe model

### Wat is gehardend

- Hulpscripts voor migratie, cleanup en validatie zijn aangepast aan de nieuwe hardening.

### Hoe dit technisch is gedaan

Bestanden:

- `src/core/migrate_key_file.py`
- `src/core/clean_credentials.py`
- `src/core/security_test.py`

Techniek:

- Migratie gebruikt nu het actuele sleutelmodel.
- Cleanup verwijdert ook de nieuwe DPAPI-sleutelvarianten.
- Security tests zijn aangepast op de nieuwe secret-logica.

### Waarom dit nodig was

Als hulpscripts nog oude aannames volgen, ontstaat er een verschil tussen de werkelijke beveiliging en de onderhoudspaden.

### Waarom dit de applicatie veiliger maakt

Beheer en onderhoud blijven consistent met de nieuwe beveiligingsarchitectuur. Dat voorkomt regressies en foutieve schoonmaak of migratie.

## Wat deze hardening concreet veiliger maakt

Door deze maatregelen samen:

- zijn opgeslagen secrets minder goed uitleesbaar;
- kunnen credentials minder makkelijk via de UI worden buitgemaakt;
- worden admin-accounts minder makkelijk naar verkeerde portals gestuurd;
- zijn lokale requests minder vrij misbruikbaar;
- zijn browser- en shell-oppervlakken kleiner;
- is de opslagarchitectuur geschikter voor administratorgebruik.

Met andere woorden: de hardening verlaagt zowel het risico op technische aanvalspaden als het risico op operationele fouten.

## Grenzen van deze beveiliging

Deze applicatie is nu veel beter gehard, maar niet absoluut onkwetsbaar.

Belangrijke resterende grenzen:

- Malware op dezelfde Windows-gebruiker kan nog steeds ingevoerde data of actieve sessies proberen te onderscheppen.
- DPAPI helpt sterk, maar beschermt niet tegen een volledig gecompromitteerd ingelogd account.
- Browserautomatisering blijft gevoeliger dan een enterprise vault of privileged workstation oplossing.
- Een lokale tool met admin-accounts blijft afhankelijk van de veiligheid van de beheer-pc zelf.

## Waarom de applicatie nu als "secure" kan gelden

Binnen de context van een lokale beheerapp geldt de applicatie nu als goed gehard omdat:

- credentials niet meer vrij door de frontend circuleren;
- admin-URL's zijn afgedwongen;
- de lokale API beschermd is;
- shell injection risico's zijn verwijderd;
- browserpersistentie voor admin-sessies is verkleind;
- opslag is verplaatst en versterkt;
- onderhoudspaden en exports zijn meegehard.

Dat betekent niet "onhackbaar", maar wel dat de belangrijkste realistische risico's in deze architectuur doelgericht zijn beperkt.

## Aanbevolen gebruik voor maximale veiligheid

Gebruik de applicatie alleen:

- op een vertrouwde beheer-pc;
- met MFA op alle admin-accounts;
- zonder onnodige browser-extensies;
- met actuele Windows-, browser- en driver-updates;
- zonder gevoelige projectdata nog in de oude projectmap te laten staan.

## Gerelateerde documenten

- `ADMIN_HARDENING.md`
- `SECURITY_HARDENING.md`

Dit bestand is het complete, samengevoegde overzicht. De andere documenten kunnen blijven dienen als kortere samenvatting of historisch logboek.
