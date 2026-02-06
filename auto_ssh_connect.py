import os
import subprocess
from pathlib import Path


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
    # Gebruik altijd OpenSSH (standaard SSH client op Windows 10+)
    # Check of OpenSSH beschikbaar is
    ssh_available = False
    try:
        result = subprocess.run(
            ["ssh", "-V"],
            capture_output=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        if result.returncode == 0 or "OpenSSH" in result.stderr.decode() or "OpenSSH" in result.stdout.decode():
            ssh_available = True
    except FileNotFoundError:
        pass
    
    if ssh_available:
        # Gebruik OpenSSH (normale SSH emulator)
        if user:
            ssh_target = f"{user}@{host}"
        else:
            ssh_target = host
        
        ssh_command = f"ssh {ssh_target}"
        
        if port != 22:
            ssh_command += f" -p {port}"
        
        if key_file and Path(key_file).exists():
            ssh_command += f" -i \"{key_file}\""
        
        # OpenSSH ondersteunt geen wachtwoord via command line (veiligheid)
        # Wachtwoord moet handmatig worden ingevoerd in de CMD prompt
        # Dit is de normale en veilige manier om SSH te gebruiken
    else:
        # OpenSSH niet beschikbaar, probeer PuTTY als fallback
        putty_paths = [
            r"C:\Program Files\PuTTY\putty.exe",
            r"C:\Program Files (x86)\PuTTY\putty.exe",
            os.path.expanduser(r"~\AppData\Local\Programs\PuTTY\putty.exe"),
        ]
        
        putty_dir = None
        putty_exe = None
        plink_exe = None
        for path in putty_paths:
            if Path(path).exists():
                putty_exe = path
                putty_dir = Path(path).parent
                if (putty_dir / "plink.exe").exists():
                    plink_exe = str(putty_dir / "plink.exe")
                break
        
        # Als er een wachtwoord is en plink beschikbaar, gebruik plink
        if password and plink_exe:
            if user:
                ssh_target = f"{user}@{host}"
            else:
                ssh_target = host
            
            ssh_command = f'"{plink_exe}" {ssh_target}'
            
            if port != 22:
                ssh_command += f" -P {port}"
            
            if key_file and Path(key_file).exists():
                ssh_command += f' -i "{key_file}"'
            else:
                ssh_command += f' -pw "{password}"'
        elif putty_exe:
            # Gebruik PuTTY GUI
            if user:
                ssh_target = f"{user}@{host}"
            else:
                ssh_target = host
            
            ssh_command = f'"{putty_exe}" {ssh_target}'
            
            if port != 22:
                ssh_command += f" -P {port}"
            
            if key_file and Path(key_file).exists():
                ssh_command += f' -i "{key_file}"'
        else:
            # Fallback: probeer gewoon ssh.exe
            ssh_command = f"ssh {user + '@' if user else ''}{host}"
            if port != 22:
                ssh_command += f" -p {port}"
    
    # Start CMD prompt met SSH commando
    try:
        # Start een nieuwe CMD prompt venster en voer het SSH commando direct uit
        # /k houdt het venster open na het commando
        if os.name == "nt":  # Windows
            # Gebruik start cmd om een nieuw venster te openen
            # /k houdt het venster open, /c voert het commando uit
            subprocess.Popen(
                f'start "SSH - {host}" cmd /k "{ssh_command}"',
                shell=True
            )
        else:  # Linux/macOS
            subprocess.Popen(["xterm", "-e", ssh_command] + [";", "bash"])
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
