"""
Script om bestaande credentials op te schonen.
Verwijdert alle wachtwoorden uit .env en credentials.json.
Gebruikt dezelfde datamap als de app (get_data_dir) zodat het ook werkt vanuit de .exe.
"""
import os
import json
from pathlib import Path

import sys
from pathlib import Path

# Add parent directory to path for imports
SCRIPTS_DIR = Path(__file__).parent.parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from src.core.credentials_manager import get_data_dir

# Zelfde mappen als de app (bij .exe: AppData\Local\SintMaartenCampusAutologin)
DATA_DIR = get_data_dir()
SCRIPTS_DIR = Path(__file__).parent  # alleen nog voor fallback key-locatie

ENV_FILE = DATA_DIR / ".env"
CREDENTIALS_FILE = DATA_DIR / "credentials.json"
RDP_SERVERS_FILE = DATA_DIR / "rdp_servers.json"
SSH_SERVERS_FILE = DATA_DIR / "ssh_servers.json"
# Encryptie key: nieuwe locatie in datamap, plus oude locatie voor compatibiliteit
CREDENTIALS_KEY_FILE_NEW = DATA_DIR / ".credentials_key"
CREDENTIALS_KEY_FILE_OLD = SCRIPTS_DIR / ".credentials_key"

def clean_env_file():
    """Verwijder alle credential regels uit .env. Retourneert resultaat dict."""
    result = {"success": False, "message": "", "removed": 0}
    if not ENV_FILE.exists():
        result["message"] = "Geen .env bestand gevonden."
        return result
    
    cred_keys = [
        "MS_EMAIL", "MS_PASSWORD",
        "MS_ADMIN_URL", "MS_ADMIN_EMAIL", "MS_ADMIN_PASSWORD",
        "GOOGLE_ADMIN_URL", "GOOGLE_ADMIN_EMAIL", "GOOGLE_ADMIN_PASSWORD",
        "EASY4U_URL", "EASY4U_EMAIL", "EASY4U_PASSWORD",
    ]
    
    try:
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        cleaned_lines = []
        for line in lines:
            # Check of de regel een credential bevat
            is_credential = any(line.strip().startswith(key + "=") for key in cred_keys)
            if not is_credential:
                cleaned_lines.append(line)
        
        removed_count = len(lines) - len(cleaned_lines)
        
        with open(ENV_FILE, "w", encoding="utf-8") as f:
            f.writelines(cleaned_lines)
        
        result["success"] = True
        result["message"] = f".env bestand opgeschoond. {removed_count} credential regels verwijderd."
        result["removed"] = removed_count
    except Exception as e:
        result["message"] = f"Fout bij opschonen .env: {e}"
    
    return result


def clean_credentials_json():
    """Verwijder credentials.json als die bestaat. Retourneert resultaat dict."""
    result = {"success": False, "message": ""}
    if CREDENTIALS_FILE.exists():
        try:
            CREDENTIALS_FILE.unlink()
            result["success"] = True
            result["message"] = "credentials.json verwijderd."
        except Exception as e:
            result["message"] = f"Fout bij verwijderen credentials.json: {e}"
    else:
        result["message"] = "Geen credentials.json bestand gevonden."
    
    return result


def clean_rdp_servers():
    """Verwijder wachtwoorden uit RDP servers. Retourneert resultaat dict."""
    result = {"success": False, "message": "", "servers_cleaned": 0}
    rdp_file = RDP_SERVERS_FILE
    if rdp_file.exists():
        try:
            with open(rdp_file, "r", encoding="utf-8") as f:
                servers = json.load(f)
            
            # Verwijder wachtwoorden
            cleaned_servers = []
            for server in servers:
                cleaned_server = server.copy()
                if "password" in cleaned_server:
                    cleaned_server["password"] = ""
                cleaned_servers.append(cleaned_server)
            
            with open(rdp_file, "w", encoding="utf-8") as f:
                json.dump(cleaned_servers, f, indent=2, ensure_ascii=False)
            
            result["success"] = True
            result["message"] = f"RDP servers opgeschoond. Wachtwoorden verwijderd uit {len(servers)} servers."
            result["servers_cleaned"] = len(servers)
        except Exception as e:
            result["message"] = f"Fout bij opschonen RDP servers: {e}"
    else:
        result["message"] = "Geen rdp_servers.json bestand gevonden."
    
    return result


def clean_ssh_servers():
    """Verwijder wachtwoorden uit SSH servers. Retourneert resultaat dict."""
    result = {"success": False, "message": "", "servers_cleaned": 0}
    ssh_file = SSH_SERVERS_FILE
    if ssh_file.exists():
        try:
            with open(ssh_file, "r", encoding="utf-8") as f:
                servers = json.load(f)
            
            # Verwijder wachtwoorden
            cleaned_servers = []
            for server in servers:
                cleaned_server = server.copy()
                if "password" in cleaned_server:
                    cleaned_server["password"] = ""
                cleaned_servers.append(cleaned_server)
            
            with open(ssh_file, "w", encoding="utf-8") as f:
                json.dump(cleaned_servers, f, indent=2, ensure_ascii=False)
            
            result["success"] = True
            result["message"] = f"SSH servers opgeschoond. Wachtwoorden verwijderd uit {len(servers)} servers."
            result["servers_cleaned"] = len(servers)
        except Exception as e:
            result["message"] = f"Fout bij opschonen SSH servers: {e}"
    else:
        result["message"] = "Geen ssh_servers.json bestand gevonden."
    
    return result


def clean_key_file():
    """Verwijder encryptie key file(s) – zowel in datamap als oude locatie. Retourneert resultaat dict."""
    result = {"success": False, "message": "", "removed": 0}
    removed = 0
    for key_file in (CREDENTIALS_KEY_FILE_NEW, CREDENTIALS_KEY_FILE_OLD):
        if key_file.exists():
            try:
                key_file.unlink()
                removed += 1
            except Exception as e:
                result["message"] = (result["message"] or "") + f" Fout bij {key_file.name}: {e}. "
    if removed > 0:
        result["success"] = True
        result["message"] = (result["message"] or "") + f".credentials_key verwijderd ({removed} bestand(en))."
        result["removed"] = removed
    else:
        result["message"] = (result["message"] or "Geen .credentials_key bestand gevonden.")
    return result


def run_clean_all():
    """Voer alle clean functies uit en retourneer resultaten."""
    results = []
    results.append(("Clean .env", clean_env_file()))
    results.append(("Clean credentials.json", clean_credentials_json()))
    results.append(("Clean RDP servers", clean_rdp_servers()))
    results.append(("Clean SSH servers", clean_ssh_servers()))
    results.append(("Clean key file", clean_key_file()))
    return results


if __name__ == "__main__":
    import sys
    # Fix encoding voor Windows console
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("Opschonen van credentials...")
    print("-" * 50)
    results = run_clean_all()
    for name, result in results:
        icon = "✅" if result["success"] else "❌"
        print(f"{icon} {name}: {result['message']}")
    print("-" * 50)
    print("Klaar! Alle credentials zijn verwijderd.")
    print("Gebruik de web interface om nieuwe credentials veilig in te voeren.")
