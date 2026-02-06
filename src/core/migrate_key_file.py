"""
Migratie script om de encryptie key file te verplaatsen naar een veiligere locatie.
Dit script moet worden uitgevoerd als je een upgrade doet naar de nieuwe versie.
"""
import os
import sys
import shutil
from pathlib import Path

# Add parent directory to path for imports
SCRIPTS_DIR = Path(__file__).parent.parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

# Oude locatie: in project root
OLD_KEY_FILE = SCRIPTS_DIR / ".credentials_key"

if os.name == "nt":  # Windows
    appdata_dir = Path(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")))
    secure_dir = appdata_dir / "SintMaartenCampusAutologin"
    secure_dir.mkdir(exist_ok=True, mode=0o700)
    NEW_KEY_FILE = secure_dir / ".credentials_key"
else:  # Unix/Linux
    config_dir = Path.home() / ".config" / "sintmaartencampus-autologin"
    config_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    NEW_KEY_FILE = config_dir / ".credentials_key"

def migrate_key_file():
    """Migreer de key file van de oude locatie naar de nieuwe veilige locatie. Retourneert resultaat dict."""
    result = {"success": False, "message": "", "old_path": str(OLD_KEY_FILE), "new_path": str(NEW_KEY_FILE)}
    
    if not OLD_KEY_FILE.exists():
        result["message"] = "Geen oude key file gevonden. Geen migratie nodig."
        return result
    
    if NEW_KEY_FILE.exists():
        result["message"] = f"Key file bestaat al op nieuwe locatie: {NEW_KEY_FILE}. Oude key file wordt niet gemigreerd om conflicten te voorkomen."
        return result
    
    try:
        # Kopieer key file naar nieuwe locatie
        shutil.copy2(OLD_KEY_FILE, NEW_KEY_FILE)
        
        # Zet bestandspermissies
        if os.name != "nt":  # Unix/Linux
            os.chmod(NEW_KEY_FILE, 0o600)
        else:  # Windows
            import stat
            os.chmod(NEW_KEY_FILE, stat.S_IREAD | stat.S_IWRITE)
            try:
                import ctypes
                ctypes.windll.kernel32.SetFileAttributesW(str(NEW_KEY_FILE), 2)  # Hidden
            except Exception:
                pass
        
        result["success"] = True
        result["message"] = f"Key file succesvol gemigreerd naar: {NEW_KEY_FILE}. Oude key file blijft staan op: {OLD_KEY_FILE}. Je kunt deze handmatig verwijderen na verificatie."
        
    except Exception as e:
        result["message"] = f"Fout bij migreren key file: {e}. De oude key file blijft op zijn plaats."
    
    return result

if __name__ == "__main__":
    migrate_key_file()
