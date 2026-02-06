import os
import subprocess
import time
from pathlib import Path

import pyautogui
from dotenv import load_dotenv


def main() -> None:
    """
    Start WatchGuard Mobile VPN with SSL automatisch.

    Config in .env:

    WG_SSLVPN_EXE="C:\\Program Files (x86)\\WatchGuard\\Mobile VPN with SSL\\wgsslvpnc.exe"
    WG_SSLVPN_ARGS=-connect

    - EXE: pad naar de WatchGuard VPN client.
    - ARGS (optioneel): extra argumenten zoals -connect of een profielnaam.
      Laat leeg als je gewoon de GUI wilt laten starten en zelf op 'Connect' klikt.
    """
    load_dotenv()

    exe = os.environ.get(
        "WG_SSLVPN_EXE",
        r"C:\Program Files (x86)\WatchGuard\Mobile VPN with SSL\wgsslvpnc.exe",
    )
    args = os.environ.get("WG_SSLVPN_ARGS", "").strip()

    exe_path = Path(exe)
    if not exe_path.exists():
        print(
            f"WatchGuard executable niet gevonden op {exe_path}.\n"
            "Pas WG_SSLVPN_EXE in je .env aan naar het juiste pad, "
            "bijvoorbeeld door in Verkenner naar het programma te navigeren en het pad te kopiëren."
        )
        return

    # Als er een .lnk is opgegeven, start deze via 'start' zodat Windows de snelkoppeling afhandelt.
    is_lnk = exe_path.suffix.lower() == ".lnk"

    if is_lnk:
        cmd = [
            "cmd",
            "/c",
            "start",
            "",
            str(exe_path),
        ]
        # Argumenten aan een .lnk meegeven werkt meestal niet; die moeten in de snelkoppeling zelf staan.
        print(f"Start WatchGuard Mobile VPN with SSL via snelkoppeling: {exe_path}")
    else:
        cmd = [str(exe_path)]
        if args:
            # Splits eenvoudig op spaties; als je meer complexe args hebt kun je WG_SSLVPN_ARGS zelf juist quoten
            cmd.extend(args.split())
        print(f"Start WatchGuard Mobile VPN with SSL: {' '.join(cmd)}")

    try:
        # Laat de VPN-client gewoon draaien; geen wacht op exit.
        subprocess.Popen(cmd)

        # Als -connect niets doet, kunnen we optioneel de Connect-knop simuleren.
        # Zet in .env: WG_SSLVPN_AUTO_GUI_CONNECT=1 om dit aan te zetten.
        auto_gui = os.environ.get("WG_SSLVPN_AUTO_GUI_CONNECT", "0").strip() == "1"
        if auto_gui:
            # Even ruimer wachten tot het venster in beeld is
            time.sleep(5)

            # Probeer eerst het WatchGuard-venster naar voren te brengen
            try:
                # pygetwindow wordt intern door pyautogui gebruikt
                import pygetwindow as gw  # type: ignore

                candidates = [
                    w
                    for w in gw.getAllWindows()
                    if "mobile vpn with ssl" in w.title.lower()
                    or "watchguard" in w.title.lower()
                ]
                if candidates:
                    candidates[0].activate()
                    time.sleep(1)
            except Exception:
                # Als dit mislukt, proberen we alsnog gewoon de toetsen te sturen
                pass

            # Probeer eerst Alt+C (sneltoets voor Connect in veel Engelse/Nederlandse builds)
            try:
                pyautogui.hotkey("alt", "c")
            except Exception:
                pass
            # En stuur daarna nog een Enter als fallback op de default button
            try:
                time.sleep(1)
                pyautogui.press("enter")
            except Exception:
                pass
    except Exception as e:
        print(f"Kon WatchGuard VPN niet starten: {e}")


if __name__ == "__main__":
    main()

