import os
import subprocess
from dotenv import load_dotenv


def _get_env_or_none(key: str) -> str | None:
    value = os.environ.get(key)
    if value is None or not str(value).strip():
        return None
    return value.strip()


def _start_single_rdp(host: str, user: str | None, password: str | None) -> None:
    """
    Start één RDP-sessie. Als user & password zijn meegegeven,
    worden deze eerst via cmdkey opgeslagen voor deze host.
    """
    # Eerst optioneel credentials registreren
    if user and password:
        try:
            # TERMSRV/host is de target voor RDP-credentials
            subprocess.run(
                [
                    "cmdkey",
                    "/generic:TERMSRV/" + host,
                    "/user:" + user,
                    "/pass:" + password,
                ],
                check=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
        except Exception as e:
            print(f"Waarschuwing: kon credentials voor {host} niet instellen via cmdkey: {e}")

    # Daarna mstsc starten
    try:
        subprocess.Popen(["mstsc", f"/v:{host}"])
    except FileNotFoundError:
        print(
            "Kon 'mstsc' niet vinden. Controleer of je Remote Desktop Client "
            "op deze Windows-machine geïnstalleerd is."
        )
    except Exception as e:
        print(f"Kon RDP naar {host} niet starten: {e}")


def start_rdp_sessions() -> None:
    """
    Start meerdere RDP-sessies via mstsc.

    Config in .env, per server eigen login:

    RDP_SESSIONS=2

    RDP_1_HOST=server1.of.ip
    RDP_1_USER=DOMAIN1\\user1
    RDP_1_PASS=wachtwoord1

    RDP_2_HOST=server2.of.ip:3390
    RDP_2_USER=DOMAIN2\\user2
    RDP_2_PASS=wachtwoord2

    Uitbreiden = RDP_SESSIONS ophogen en extra blok RDP_3_*, RDP_4_*, ...

    Als RDP_SESSIONS niet gezet is, valt het script terug op de oude
    RDP_SERVERS (zonder per-server login).
    """
    load_dotenv()

    sessions_raw = _get_env_or_none("RDP_SESSIONS")
    if sessions_raw:
        try:
            count = int(sessions_raw)
        except ValueError:
            print("RDP_SESSIONS moet een getal zijn, bv. 2")
            return

        if count <= 0:
            print("RDP_SESSIONS is 0 of negatief, er worden geen sessies gestart.")
            return

        print(f"Start {count} RDP-sessies volgens .env-configuratie:")
        for i in range(1, count + 1):
            host = _get_env_or_none(f"RDP_{i}_HOST")
            user = _get_env_or_none(f"RDP_{i}_USER")
            password = _get_env_or_none(f"RDP_{i}_PASS")

            if not host:
                print(f"- RDP_{i}_HOST ontbreekt, sessie {i} wordt overgeslagen.")
                continue

            print(f"- Sessie {i}: host={host}, user={user or '[Windows opgeslagen]'}")
            _start_single_rdp(host, user, password)

        return

    # Fallback: oude manier met alleen RDP_SERVERS (zonder logins)
    servers_raw = _get_env_or_none("RDP_SERVERS")
    if not servers_raw:
        print(
            "Geen RDP_SESSIONS of RDP_SERVERS gevonden in .env.\n"
            "Nieuwe manier (met logins), voorbeeld:\n"
            "  RDP_SESSIONS=2\n"
            "  RDP_1_HOST=server1.of.ip\n"
            "  RDP_1_USER=DOMAIN1\\user1\n"
            "  RDP_1_PASS=wachtwoord1\n"
            "  RDP_2_HOST=server2.of.ip\n"
            "  RDP_2_USER=DOMAIN2\\user2\n"
            "  RDP_2_PASS=wachtwoord2\n"
        )
        return

    servers = [s.strip() for s in servers_raw.split(",") if s.strip()]
    if not servers:
        print("RDP_SERVERS is leeg na parsen. Controleer je .env.")
        return

    print("Start RDP-sessies naar de volgende servers (zonder aparte logins):")
    for s in servers:
        print(f" - {s}")
        _start_single_rdp(s, None, None)


if __name__ == "__main__":
    start_rdp_sessions()


