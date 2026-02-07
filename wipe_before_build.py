"""
Wis credentials en servergegevens vóór het bouwen van een distribueerbare .exe.
Zo komt er geen gevoelige data in de build of op andere devices.

- In ontwikkelmodus: wist bestanden in src/core (credentials.json, rdp_servers.json, etc.)
- Optioneel: wist ook AppData\\Local\\SintMaartenCampusAutologin (--appdata)
"""
import os
import sys
from pathlib import Path

# Project root = map van dit script
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

# Data-dir in dev = src/core (zelfde als credentials_manager wanneer niet frozen)
DEV_DATA_DIR = SCRIPTS_DIR / "src" / "core"
APP_DATA_NAME = "SintMaartenCampusAutologin"

FILES_TO_WIPE = [
    "credentials.json",
    "rdp_servers.json",
    "ssh_servers.json",
    ".env",
    ".credentials_key",
]


def wipe_dir(data_dir: Path, label: str) -> int:
    """Verwijder gevoelige bestanden in data_dir. Retourneert aantal verwijderde bestanden."""
    if not data_dir.is_dir():
        return 0
    removed = 0
    for name in FILES_TO_WIPE:
        path = data_dir / name
        if path.exists():
            try:
                path.unlink()
                print(f"  Verwijderd: {path}")
                removed += 1
            except Exception as e:
                print(f"  Fout bij verwijderen {path}: {e}")
    return removed


def main():
    wipe_appdata = "--appdata" in sys.argv or "-a" in sys.argv
    total = 0

    # 1) Dev-datamap (src/core)
    print("Wissen van ontwikkel-datamap (src/core)...")
    total += wipe_dir(DEV_DATA_DIR, "dev")

    # 2) Optioneel: AppData (gebruikersdata van eerder geïnstalleerde .exe)
    if wipe_appdata:
        if os.name != "nt":
            appdata_dir = Path.home() / ".config" / APP_DATA_NAME
        else:
            appdata_dir = Path(os.environ.get("LOCALAPPDATA", Path.home())) / APP_DATA_NAME
        print("Wissen van AppData (gebruikersdata)...")
        total += wipe_dir(appdata_dir, "AppData")
    else:
        print("Tip: gebruik --appdata om ook AppData\\SintMaartenCampusAutologin te wissen.")

    print(f"Klaar. {total} bestand(en) verwijderd.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
