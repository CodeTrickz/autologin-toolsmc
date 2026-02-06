"""
Credentials Manager met encryptie voor veilige opslag van wachtwoorden.
"""
import os
import sys
import json
import base64
from pathlib import Path
from cryptography.fernet import Fernet


def get_data_dir() -> Path:
    """
    Directory voor credentials en server-bestanden (persistent).
    Bij gebundelde .exe: AppData/Local/SintMaartenCampusAutologin.
    Anders: map van dit bestand (projectmap).
    """
    if getattr(sys, "frozen", False):
        if os.name == "nt":
            base = Path(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")))
        else:
            base = Path.home() / ".config"
        data_dir = base / "SintMaartenCampusAutologin"
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir
    return Path(__file__).parent
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def get_or_create_key(key_file: Path) -> bytes:
    """
    Genereer of laad een encryptie key.
    Als de key file niet bestaat, wordt er een nieuwe gegenereerd.
    """
    if key_file.exists():
        with open(key_file, "rb") as f:
            return f.read()
    else:
        # Genereer nieuwe key
        key = Fernet.generate_key()
        with open(key_file, "wb") as f:
            f.write(key)
        # Zet bestandspermissies (alleen eigenaar kan lezen)
        if os.name != "nt":  # Unix/Linux
            os.chmod(key_file, 0o600)
        else:  # Windows
            # Op Windows: zet bestand attributen (hidden + read-only voor anderen)
            try:
                import stat
                # Alleen eigenaar kan lezen/schrijven
                os.chmod(key_file, stat.S_IREAD | stat.S_IWRITE)
                # Maak bestand hidden
                import ctypes
                ctypes.windll.kernel32.SetFileAttributesW(str(key_file), 2)  # FILE_ATTRIBUTE_HIDDEN
            except Exception:
                pass  # Als het niet lukt, ga door
        return key


def get_encryption_key(scripts_dir: Path) -> bytes:
    """
    Haal de encryptie key op. Gebruikt een master password of genereert een key file.
    De key file wordt opgeslagen in een veilige locatie (gebruikers AppData op Windows).
    """
    # Gebruik master password uit environment als die bestaat
    master_password = os.environ.get("CREDENTIALS_MASTER_PASSWORD")
    
    if master_password:
        # Gebruik master password om key te genereren
        salt = b"credentials_salt_v1"  # Vaste salt voor consistentie
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
        return key
    else:
        # Gebruik key file - plaats in veilige locatie
        if os.name == "nt":  # Windows
            # Gebruik AppData\Local voor betere beveiliging
            appdata_dir = Path(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")))
            secure_dir = appdata_dir / "SintMaartenCampusAutologin"
            secure_dir.mkdir(exist_ok=True, mode=0o700)
            key_file = secure_dir / ".credentials_key"
            # Fallback naar oude locatie voor backward compatibility
            old_key_file = scripts_dir / ".credentials_key"
        else:  # Unix/Linux
            # Gebruik .config directory in home
            config_dir = Path.home() / ".config" / "sintmaartencampus-autologin"
            config_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
            key_file = config_dir / ".credentials_key"
            # Fallback naar oude locatie voor backward compatibility
            old_key_file = scripts_dir / ".credentials_key"
        
        # Probeer eerst nieuwe locatie, anders oude locatie (backward compatibility)
        if key_file.exists():
            return get_or_create_key(key_file)
        elif old_key_file.exists():
            # Migreer automatisch van oude naar nieuwe locatie
            try:
                import shutil
                shutil.copy2(old_key_file, key_file)
                # Zet permissies
                if os.name != "nt":
                    os.chmod(key_file, 0o600)
                else:
                    import stat
                    os.chmod(key_file, stat.S_IREAD | stat.S_IWRITE)
                    try:
                        import ctypes
                        ctypes.windll.kernel32.SetFileAttributesW(str(key_file), 2)
                    except Exception:
                        pass
                print(f"Key file automatisch gemigreerd naar: {key_file}")
            except Exception as e:
                print(f"Waarschuwing: kon key file niet migreren: {e}")
                # Gebruik oude locatie als fallback
                return get_or_create_key(old_key_file)
            return get_or_create_key(key_file)
        else:
            # Maak nieuwe key file op veilige locatie
            return get_or_create_key(key_file)


def encrypt_credentials(credentials: dict, scripts_dir: Path) -> dict:
    """
    Encrypt credentials dictionary. Alleen wachtwoorden worden geëncrypteerd.
    Werkt ook voor RDP servers (waar password direct in dict staat).
    """
    key = get_encryption_key(scripts_dir)
    fernet = Fernet(key)
    
    encrypted = {}
    for service, creds in credentials.items():
        encrypted[service] = {}
        for field, value in creds.items():
            if field == "password" and value:
                # Encrypt wachtwoord
                encrypted_value = fernet.encrypt(value.encode())
                encrypted[service][field] = base64.b64encode(encrypted_value).decode()
            else:
                # Andere velden niet encrypten
                encrypted[service][field] = value
    
    return encrypted


def encrypt_password(password: str, scripts_dir: Path) -> str:
    """
    Encrypt een enkel wachtwoord. Handig voor RDP servers.
    """
    if not password:
        return ""
    
    key = get_encryption_key(scripts_dir)
    fernet = Fernet(key)
    encrypted_value = fernet.encrypt(password.encode())
    return base64.b64encode(encrypted_value).decode()


def decrypt_password(encrypted_password: str, scripts_dir: Path) -> str:
    """
    Decrypt een enkel wachtwoord. Handig voor RDP servers.
    """
    if not encrypted_password:
        return ""
    
    try:
        key = get_encryption_key(scripts_dir)
        fernet = Fernet(key)
        encrypted_bytes = base64.b64decode(encrypted_password.encode())
        decrypted_value = fernet.decrypt(encrypted_bytes)
        return decrypted_value.decode()
    except Exception:
        return ""


def decrypt_credentials(encrypted_credentials: dict, scripts_dir: Path) -> dict:
    """
    Decrypt credentials dictionary.
    """
    try:
        key = get_encryption_key(scripts_dir)
        fernet = Fernet(key)
        
        decrypted = {}
        for service, creds in encrypted_credentials.items():
            decrypted[service] = {}
            for field, value in creds.items():
                if field == "password" and value:
                    try:
                        # Decrypt wachtwoord
                        encrypted_bytes = base64.b64decode(value.encode())
                        decrypted_value = fernet.decrypt(encrypted_bytes)
                        decrypted[service][field] = decrypted_value.decode()
                    except Exception:
                        # Als decryptie mislukt, return lege string
                        decrypted[service][field] = ""
                else:
                    decrypted[service][field] = value
        
        return decrypted
    except Exception as e:
        # Als er een fout is, return lege dict
        print(f"Fout bij decrypten credentials: {e}")
        return {}


def load_encrypted_credentials(credentials_file: Path, scripts_dir: Path) -> dict:
    """
    Laad en decrypt credentials uit bestand.
    """
    if not credentials_file.exists():
        return {}
    
    try:
        with open(credentials_file, "r", encoding="utf-8") as f:
            encrypted_data = json.load(f)
        
        return decrypt_credentials(encrypted_data, scripts_dir)
    except Exception as e:
        print(f"Fout bij laden credentials: {e}")
        return {}


def save_encrypted_credentials(credentials: dict, credentials_file: Path, scripts_dir: Path) -> bool:
    """
    Encrypt en sla credentials op in bestand met beveiligde permissies.
    """
    try:
        encrypted = encrypt_credentials(credentials, scripts_dir)
        
        with open(credentials_file, "w", encoding="utf-8") as f:
            json.dump(encrypted, f, indent=2, ensure_ascii=False)
        
        # Zet bestandspermissies (alleen eigenaar kan lezen)
        if os.name != "nt":  # Unix/Linux
            os.chmod(credentials_file, 0o600)
        else:  # Windows
            # Op Windows: zet bestand attributen (hidden + read-only voor anderen)
            try:
                import stat
                # Alleen eigenaar kan lezen/schrijven
                os.chmod(credentials_file, stat.S_IREAD | stat.S_IWRITE)
                # Maak bestand hidden (optioneel, kan worden uitgeschakeld)
                # import ctypes
                # ctypes.windll.kernel32.SetFileAttributesW(str(credentials_file), 2)  # FILE_ATTRIBUTE_HIDDEN
            except Exception:
                pass  # Als het niet lukt, ga door
        
        return True
    except Exception as e:
        print(f"Fout bij opslaan credentials: {e}")
        return False


def sync_to_env(credentials: dict, env_file: Path, scripts_dir: Path) -> bool:
    """
    Sync alleen niet-gevoelige gegevens naar .env bestand (GEEN wachtwoorden).
    Wachtwoorden blijven alleen in encrypted credentials.json.
    """
    try:
        env_lines = []
        
        # Lees bestaande .env als die bestaat
        if env_file.exists():
            with open(env_file, "r", encoding="utf-8") as f:
                env_lines = f.readlines()
        
        # Verwijder ALLE oude credentials (ook wachtwoorden)
        cred_keys = [
            "MS_EMAIL", "MS_PASSWORD",
            "MS_ADMIN_URL", "MS_ADMIN_EMAIL", "MS_ADMIN_PASSWORD",
            "GOOGLE_ADMIN_URL", "GOOGLE_ADMIN_EMAIL", "GOOGLE_ADMIN_PASSWORD",
            "EASY4U_URL", "EASY4U_EMAIL", "EASY4U_PASSWORD",
        ]
        
        env_lines = [line for line in env_lines if not any(line.strip().startswith(key + "=") for key in cred_keys)]
        
        # Voeg ALLEEN niet-gevoelige gegevens toe (GEEN wachtwoorden)
        # Alleen URL's en emails voor referentie, maar modules lezen direct uit encrypted credentials
        if "microsoft_admin" in credentials:
            env_lines.append(f"MS_ADMIN_URL={credentials['microsoft_admin'].get('url', 'https://admin.microsoft.com')}\n")
        
        if "google_admin" in credentials:
            env_lines.append(f"GOOGLE_ADMIN_URL={credentials['google_admin'].get('url', 'https://admin.google.com')}\n")
        
        if "easy4u" in credentials:
            env_lines.append(f"EASY4U_URL={credentials['easy4u'].get('url', 'https://easy4u.nl/admin/')}\n")
        
        # Schrijf .env terug (ZONDER wachtwoorden)
        with open(env_file, "w", encoding="utf-8") as f:
            f.writelines(env_lines)
        
        return True
    except Exception as e:
        print(f"Fout bij sync naar .env: {e}")
        return False


def get_credential(service: str, field: str, scripts_dir: Path, credentials_file: Path) -> str:
    """
    Haal een specifieke credential op uit encrypted storage.
    Dit is de veilige manier om credentials te lezen.
    """
    credentials = load_encrypted_credentials(credentials_file, scripts_dir)
    if service in credentials:
        return credentials[service].get(field, "")
    return ""
