import os
import subprocess
from pathlib import Path


def _ssh_target(host: str, user: str | None) -> str:
    return f"{user}@{host}" if user else host


def _openssh_available() -> bool:
    try:
        result = subprocess.run(
            ["ssh", "-V"],
            capture_output=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        stdout = result.stdout.decode(errors="ignore")
        stderr = result.stderr.decode(errors="ignore")
        return result.returncode == 0 or "OpenSSH" in stdout or "OpenSSH" in stderr
    except FileNotFoundError:
        return False


def _find_putty_tools() -> tuple[str | None, str | None]:
    putty_paths = [
        r"C:\Program Files\PuTTY\putty.exe",
        r"C:\Program Files (x86)\PuTTY\putty.exe",
        os.path.expanduser(r"~\AppData\Local\Programs\PuTTY\putty.exe"),
    ]

    for path in putty_paths:
        if Path(path).exists():
            putty_dir = Path(path).parent
            plink_path = putty_dir / "plink.exe"
            return path, str(plink_path) if plink_path.exists() else None
    return None, None


def _existing_key_file(key_file: str | None) -> str | None:
    if key_file and Path(key_file).exists():
        return str(Path(key_file))
    return None


def _build_windows_command(host: str, user: str | None, port: int, key_file: str | None, password: str | None) -> list[str]:
    target = _ssh_target(host, user)
    key_path = _existing_key_file(key_file)

    if _openssh_available():
        command = ["ssh"]
        if port != 22:
            command.extend(["-p", str(port)])
        if key_path:
            command.extend(["-i", key_path])
        command.append(target)
        # OpenSSH ondersteunt bewust geen wachtwoord via command line.
        return command

    putty_exe, plink_exe = _find_putty_tools()
    if password and plink_exe and not key_path:
        command = [plink_exe]
        if port != 22:
            command.extend(["-P", str(port)])
        command.extend([target, "-pw", password])
        return command

    if putty_exe:
        command = [putty_exe]
        if port != 22:
            command.extend(["-P", str(port)])
        if key_path:
            command.extend(["-i", key_path])
        command.append(target)
        return command

    command = ["ssh"]
    if port != 22:
        command.extend(["-p", str(port)])
    if key_path:
        command.extend(["-i", key_path])
    command.append(target)
    return command


def _start_single_ssh(host: str, user: str | None, port: int = 22, key_file: str | None = None, password: str | None = None) -> None:
    """
    Start één SSH-sessie in een CMD prompt venster.

    Args:
        host: Hostname of IP-adres
        user: Gebruikersnaam (optioneel)
        port: SSH poort (standaard 22)
        key_file: Pad naar private key bestand (optioneel)
        password: Wachtwoord (optioneel, wordt gebruikt als key_file niet is opgegeven)
    """
    try:
        if os.name == "nt":  # Windows
            subprocess.Popen(
                _build_windows_command(host, user, port, key_file, password),
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                shell=False,
            )
        else:  # Linux/macOS
            command = _build_windows_command(host, user, port, key_file, password)
            subprocess.Popen(["xterm", "-e", *command])
    except Exception as e:
        raise RuntimeError(f"Kon SSH verbinding naar {host} niet starten: {e}")


def start_ssh_connection(host: str, user: str | None = None, port: int = 22, key_file: str | None = None, password: str | None = None) -> None:
    """
    Start een SSH verbinding naar een server.
    
    Args:
        host: Hostname of IP-adres
        user: Gebruikersnaam (optioneel)
        port: SSH poort (standaard 22)
        key_file: Pad naar private key bestand (optioneel)
        password: Wachtwoord (optioneel, wordt gebruikt als key_file niet is opgegeven)
    """
    _start_single_ssh(host, user, port, key_file, password)
