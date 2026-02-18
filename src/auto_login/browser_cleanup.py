"""
Browser cleanup voor de auto-login tool.

Doel:
- Wis tool-profielen/cookies bij afsluiten van de applicatie.
- Ook als er nog Chrome vensters open staan die door de tool zijn gestart.

Veiligheid:
- We raken enkel profielen aan onder de tool DATA_DIR (chrome_user_data*).
- We proberen enkel chrome.exe processen te sluiten waarvan de CommandLine
  een van onze tool-profielpaden bevat.
"""
from __future__ import annotations

import atexit
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from src.core.credentials_manager import get_data_dir


def _is_truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _data_dir() -> Path:
    return Path(get_data_dir())


def _candidate_profile_dirs() -> list[Path]:
    d = _data_dir()
    # Alles wat we zelf kunnen hebben aangemaakt.
    dirs = []
    dirs.extend([p for p in d.glob("chrome_user_data*") if p.exists() and p.is_dir()])
    dirs.extend([p for p in d.glob("chrome_profiles*") if p.exists() and p.is_dir()])
    # Sorteer: eerst nested dirs (zodat rmtree in parent later kan).
    dirs.sort(key=lambda p: len(str(p)), reverse=True)
    return dirs


def _powershell_json(command: str) -> object:
    out = subprocess.check_output(
        ["powershell", "-NoProfile", "-Command", command],
        stderr=subprocess.DEVNULL,
        text=True,
        encoding="utf-8",
    )
    out = out.strip()
    if not out:
        return []
    return json.loads(out)


def _kill_tool_chrome_processes(profile_dirs: list[Path]) -> int:
    """
    Kill enkel chrome.exe processen die een tool user-data-dir bevatten.
    """
    if sys.platform != "win32":
        return 0

    needles = {str(p).lower() for p in profile_dirs}
    if not needles:
        return 0

    procs = _powershell_json(
        "Get-CimInstance Win32_Process -Filter \"Name='chrome.exe'\" "
        "| Select-Object ProcessId,CommandLine "
        "| ConvertTo-Json -Compress"
    )
    if isinstance(procs, dict):
        procs = [procs]
    if not isinstance(procs, list):
        return 0

    killed = 0
    for p in procs:
        try:
            pid = int(p.get("ProcessId"))
            cmd = str(p.get("CommandLine") or "").lower()
            if not cmd:
                continue
            if any(needle in cmd for needle in needles):
                subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], check=False)
                killed += 1
        except Exception:
            continue

    return killed


def clear_browser_data(*, force_kill: bool = True) -> dict:
    """
    Wis alle tool browserprofielen.
    """
    profile_dirs = _candidate_profile_dirs()
    if not profile_dirs:
        return {"success": True, "message": "Geen tool browserprofielen gevonden om te wissen.", "deleted": 0, "killed": 0}

    killed = 0
    if force_kill:
        killed = _kill_tool_chrome_processes(profile_dirs)

    deleted = 0
    failed: list[str] = []
    for p in profile_dirs:
        try:
            shutil.rmtree(p)
            deleted += 1
        except Exception:
            failed.append(str(p))

    success = len(failed) == 0
    msg = f"Browser cookies/profielen gewist: {deleted} map(pen)."
    if force_kill and killed:
        msg += f" Chrome processen gesloten: {killed}."
    if failed:
        msg += f" Niet gelukt: {len(failed)} (mogelijk nog gelocked)."

    return {
        "success": success,
        "message": msg,
        "deleted": deleted,
        "killed": killed,
        "failed": failed,
    }


def _cleanup_on_exit() -> None:
    # Default: altijd wissen bij exit, tenzij expliciet uitgeschakeld.
    if _is_truthy(os.environ.get("AUTO_LOGIN_PERSIST_PROFILE")):
        return
    try:
        clear_browser_data(force_kill=True)
    except Exception:
        # No hard-fail on exit.
        pass


atexit.register(_cleanup_on_exit)

