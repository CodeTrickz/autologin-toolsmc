"""
Migratie script om de encryptie key file te verplaatsen naar een veiligere locatie.
Dit script moet worden uitgevoerd als je een upgrade doet naar de nieuwe versie.
"""
import os
import sys
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
    NEW_KEY_FILE = secure_dir / ".credentials_key.dpapi"
else:  # Unix/Linux
    config_dir = Path.home() / ".config" / "sintmaartencampus-autologin"
    config_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    NEW_KEY_FILE = config_dir / ".credentials_key"

def migrate_key_file():
    """Migreer de key file van de oude locatie naar de nieuwe veilige locatie. Retourneert resultaat dict."""
    result = {"success": False, "message": "", "old_path": str(OLD_KEY_FILE), "new_path": str(NEW_KEY_FILE)}

    try:
        from src.core.credentials_manager import get_encryption_key

        key = get_encryption_key(SCRIPTS_DIR)
        if not key:
            result["message"] = "Kon geen encryptiesleutel laden of migreren."
            return result

        result["success"] = True
        result["message"] = f"Encryptiesleutel gecontroleerd/gemigreerd naar: {NEW_KEY_FILE}."
    except Exception as e:
        result["message"] = f"Fout bij migreren key file: {e}."

    return result

if __name__ == "__main__":
    migrate_key_file()
