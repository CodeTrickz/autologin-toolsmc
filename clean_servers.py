"""
Script om volledige RDP en SSH servers uit de applicatie te verwijderen.
Verwijdert alle servers uit de JSON bestanden.
Gebruikt dezelfde datamap als de applicatie (get_data_dir), zodat het
ook werkt voor de gebundelde .exe (AppData\Local\SintMaartenCampusAutologin).
"""
import json
import sys
from pathlib import Path

from credentials_manager import get_data_dir

DATA_DIR = get_data_dir()
SCRIPTS_DIR = Path(__file__).parent  # alleen nog voor backwards compatibility indien nodig
RDP_SERVERS_FILE = DATA_DIR / "rdp_servers.json"
SSH_SERVERS_FILE = DATA_DIR / "ssh_servers.json"


def clean_rdp_servers():
    """Verwijder alle RDP servers uit de applicatie. Retourneert resultaat dict."""
    result = {"success": False, "message": "", "servers_removed": 0}
    
    if not RDP_SERVERS_FILE.exists():
        result["message"] = "Geen rdp_servers.json bestand gevonden."
        result["success"] = True
        return result
    
    try:
        # Laad servers
        with open(RDP_SERVERS_FILE, "r", encoding="utf-8") as f:
            servers = json.load(f)
        
        servers_count = len(servers)
        
        # Verwijder alle servers (maak lege lijst)
        with open(RDP_SERVERS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2, ensure_ascii=False)
        
        # Zet bestandspermissies (alleen eigenaar kan lezen)
        import os
        if os.name != "nt":  # Unix/Linux
            os.chmod(RDP_SERVERS_FILE, 0o600)
        
        result["success"] = True
        if servers_count > 0:
            result["message"] = f"Alle RDP servers verwijderd. {servers_count} server(s) verwijderd uit de applicatie."
        else:
            result["message"] = f"Geen RDP servers gevonden om te verwijderen."
        result["servers_removed"] = servers_count
    except Exception as e:
        result["message"] = f"Fout bij verwijderen RDP servers: {e}"
    
    return result


def clean_ssh_servers():
    """Verwijder alle SSH servers uit de applicatie. Retourneert resultaat dict."""
    result = {"success": False, "message": "", "servers_removed": 0}
    
    if not SSH_SERVERS_FILE.exists():
        result["message"] = "Geen ssh_servers.json bestand gevonden."
        result["success"] = True
        return result
    
    try:
        # Laad servers
        with open(SSH_SERVERS_FILE, "r", encoding="utf-8") as f:
            servers = json.load(f)
        
        servers_count = len(servers)
        
        # Verwijder alle servers (maak lege lijst)
        with open(SSH_SERVERS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2, ensure_ascii=False)
        
        # Zet bestandspermissies (alleen eigenaar kan lezen)
        import os
        if os.name != "nt":  # Unix/Linux
            os.chmod(SSH_SERVERS_FILE, 0o600)
        
        result["success"] = True
        if servers_count > 0:
            result["message"] = f"Alle SSH servers verwijderd. {servers_count} server(s) verwijderd uit de applicatie."
        else:
            result["message"] = f"Geen SSH servers gevonden om te verwijderen."
        result["servers_removed"] = servers_count
    except Exception as e:
        result["message"] = f"Fout bij verwijderen SSH servers: {e}"
    
    return result


def clean_all_servers():
    """Verwijder alle RDP en SSH servers uit de applicatie. Retourneert resultaten dict."""
    results = {
        "rdp": clean_rdp_servers(),
        "ssh": clean_ssh_servers()
    }
    
    total_removed = results["rdp"].get("servers_removed", 0) + results["ssh"].get("servers_removed", 0)
    all_success = results["rdp"]["success"] and results["ssh"]["success"]
    
    if total_removed > 0:
        message = f"Alle servers verwijderd. {total_removed} server(s) verwijderd uit de applicatie."
    else:
        message = f"Geen servers gevonden om te verwijderen."
    
    return {
        "success": all_success,
        "message": message,
        "rdp": results["rdp"],
        "ssh": results["ssh"],
        "total_removed": total_removed
    }


if __name__ == "__main__":
    # Fix encoding voor Windows console
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("Verwijderen van alle RDP en SSH servers...")
    print("-" * 50)
    
    rdp_result = clean_rdp_servers()
    ssh_result = clean_ssh_servers()
    
    icon_rdp = "OK" if rdp_result["success"] else "FOUT"
    icon_ssh = "OK" if ssh_result["success"] else "FOUT"
    
    print(f"[{icon_rdp}] RDP Servers: {rdp_result['message']}")
    print(f"[{icon_ssh}] SSH Servers: {ssh_result['message']}")
    
    print("-" * 50)
    total = rdp_result.get("servers_removed", 0) + ssh_result.get("servers_removed", 0)
    print(f"Klaar! {total} server(s) verwijderd uit de applicatie.")
    print("Gebruik de web interface om nieuwe servers toe te voegen.")
