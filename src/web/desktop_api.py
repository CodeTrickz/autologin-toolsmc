"""
Python API voor standalone desktop-modus (zonder Flask/localhost).
Wordt via pywebview js_api aan de frontend geëxposeerd.
Alle methodes retourneren dezelfde structuur als de Flask API (dict).
"""
import json
import sys
import threading
from pathlib import Path

# Add parent directory to path for imports
SCRIPTS_DIR = Path(__file__).parent.parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

# Import gedeelde logica uit web_interface (zonder Flask app te starten)
from src.web.web_interface import (
    APP_VERSION,
    SCRIPTS_DIR,
    load_rdp_servers,
    save_rdp_servers,
    load_ssh_servers,
    save_ssh_servers,
    load_credentials,
    save_credentials,
)
from src.core.security_utils import (
    sanitize_string,
    validate_email,
    validate_url,
    validate_hostname,
    validate_port,
    sanitize_file_path,
    validate_service_name,
)


class DesktopAPI:
    """API voor de frontend in standalone-modus (pywebview)."""

    def get_version(self):
        return {"version": APP_VERSION}

    def get_credentials(self):
        creds = load_credentials()
        return {"success": True, "credentials": creds}

    def save_credentials(self, service, data):
        if not validate_service_name(service):
            return {"success": False, "error": "Onbekende service"}
        if not data or not isinstance(data, dict):
            return {"success": False, "error": "Ongeldige input"}

        credentials = load_credentials()

        if service == "smartschool":
            username = sanitize_string(data.get("username", "") or data.get("email", ""))
            password = data.get("password", "")
            if not username:
                return {"success": False, "error": "Gebruikersnaam is verplicht"}
            if not password:
                return {"success": False, "error": "Wachtwoord is verplicht"}
            credentials["smartschool"] = {"username": username, "email": username, "password": password}
        elif service == "smartschool_admin":
            username = sanitize_string(data.get("username", "") or data.get("email", ""))
            password = data.get("password", "")
            if not username:
                return {"success": False, "error": "Gebruikersnaam is verplicht"}
            if not password:
                return {"success": False, "error": "Wachtwoord is verplicht"}
            credentials["smartschool_admin"] = {"username": username, "email": username, "password": password}
        elif service == "microsoft_admin":
            url = sanitize_string(data.get("url", "https://admin.microsoft.com"))
            email = sanitize_string(data.get("email", ""))
            password = data.get("password", "")
            if not validate_url(url):
                return {"success": False, "error": "Ongeldige URL"}
            if not email:
                return {"success": False, "error": "E-mail is verplicht"}
            if not validate_email(email):
                return {"success": False, "error": "Ongeldig e-mail adres"}
            if not password:
                return {"success": False, "error": "Wachtwoord is verplicht"}
            credentials["microsoft_admin"] = {"url": url, "email": email, "password": password}
        elif service == "google_admin":
            url = sanitize_string(data.get("url", "https://admin.google.com"))
            email = sanitize_string(data.get("email", ""))
            password = data.get("password", "")
            if not validate_url(url):
                return {"success": False, "error": "Ongeldige URL"}
            if not email:
                return {"success": False, "error": "E-mail is verplicht"}
            if not validate_email(email):
                return {"success": False, "error": "Ongeldig e-mail adres"}
            if not password:
                return {"success": False, "error": "Wachtwoord is verplicht"}
            credentials["google_admin"] = {"url": url, "email": email, "password": password}
        elif service == "easy4u":
            # Altijd de officiële Nederlandse login-URL gebruiken (niet my.easy4u.be)
            url = "https://easy4u.nl/admin/"
            email = sanitize_string(data.get("email", ""))
            password = data.get("password", "")
            if not validate_url(url):
                return {"success": False, "error": "Ongeldige URL"}
            if not email:
                return {"success": False, "error": "E-mail is verplicht"}
            if not validate_email(email):
                return {"success": False, "error": "Ongeldig e-mail adres"}
            if not password:
                return {"success": False, "error": "Wachtwoord is verplicht"}
            credentials["easy4u"] = {"url": url, "email": email, "password": password}
        else:
            return {"success": False, "error": "Onbekende service"}

        if save_credentials(credentials):
            return {"success": True, "message": f"{service} credentials opgeslagen"}
        return {"success": False, "error": "Kon credentials niet opslaan"}

    def get_rdp_servers(self):
        servers = load_rdp_servers()
        return {"success": True, "servers": servers}

    def add_rdp_server(self, data):
        if not data or not isinstance(data, dict):
            return {"success": False, "error": "Ongeldige input"}
        host = sanitize_string(data.get("host", ""))
        user = sanitize_string(data.get("user", ""))
        password = data.get("password", "")
        name = sanitize_string(data.get("name", "")) or host
        if not host:
            return {"success": False, "error": "Host is verplicht"}
        if not validate_hostname(host):
            return {"success": False, "error": "Ongeldig hostname of IP adres"}
        servers = load_rdp_servers()
        if any(s.get("host") == host for s in servers):
            return {"success": False, "error": "Server met deze host bestaat al"}
        new_server = {
            "id": len(servers) + 1,
            "name": name,
            "host": host,
            "user": user,
            "password": password,
        }
        servers.append(new_server)
        if save_rdp_servers(servers):
            return {"success": True, "message": "Server toegevoegd", "server": new_server}
        return {"success": False, "error": "Kon server niet opslaan"}

    def delete_rdp_server(self, server_id):
        servers = load_rdp_servers()
        servers = [s for s in servers if s.get("id") != server_id]
        if save_rdp_servers(servers):
            return {"success": True, "message": "Server verwijderd"}
        return {"success": False, "error": "Kon server niet verwijderen"}

    def connect_rdp(self, data):
        host = data.get("host")
        user = data.get("user") or ""
        password = data.get("password") or ""
        if not host:
            return {"success": False, "error": "Host is verplicht"}
        try:
            from src.auto_login.auto_rdp_sessions import _start_single_rdp
            _start_single_rdp(host, user, password)
            return {"success": True, "message": f"RDP connectie naar {host} gestart"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_ssh_servers(self):
        servers = load_ssh_servers()
        return {"success": True, "servers": servers}

    def add_ssh_server(self, data):
        if not data or not isinstance(data, dict):
            return {"success": False, "error": "Ongeldige input"}
        host = sanitize_string(data.get("host", ""))
        user = sanitize_string(data.get("user", ""))
        port = data.get("port", 22)
        key_file = sanitize_file_path(data.get("key_file", ""))
        password = data.get("password", "")
        name = sanitize_string(data.get("name", "")) or host
        if not host:
            return {"success": False, "error": "Host is verplicht"}
        if not validate_hostname(host):
            return {"success": False, "error": "Ongeldig hostname of IP adres"}
        if not validate_port(port):
            return {"success": False, "error": "Ongeldig poort nummer (1-65535)"}
        try:
            port = int(port)
        except (ValueError, TypeError):
            port = 22
        servers = load_ssh_servers()
        if any(s.get("host") == host and s.get("port", 22) == port for s in servers):
            return {"success": False, "error": "Server met deze host en poort bestaat al"}
        new_server = {
            "id": len(servers) + 1,
            "name": name,
            "host": host,
            "user": user,
            "port": port,
            "key_file": key_file,
            "password": password,
        }
        servers.append(new_server)
        if save_ssh_servers(servers):
            return {"success": True, "message": "Server toegevoegd", "server": new_server}
        return {"success": False, "error": "Kon server niet opslaan"}

    def delete_ssh_server(self, server_id):
        servers = load_ssh_servers()
        servers = [s for s in servers if s.get("id") != server_id]
        if save_ssh_servers(servers):
            return {"success": True, "message": "Server verwijderd"}
        return {"success": False, "error": "Kon server niet verwijderen"}

    def connect_ssh(self, data):
        host = data.get("host")
        user = data.get("user") or ""
        port = data.get("port", 22)
        key_file = data.get("key_file") or ""
        password = data.get("password") or ""
        if not host:
            return {"success": False, "error": "Host is verplicht"}
        try:
            from src.auto_login.auto_ssh_connect import start_ssh_connection
            start_ssh_connection(host, user, port, key_file, password)
            return {"success": True, "message": f"SSH verbinding naar {host} gestart"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def login(self, service):
        valid = ["smartschool", "smartschool_admin", "microsoft_admin", "google_admin", "easy4u"]
        if service not in valid:
            return {"success": False, "error": "Onbekende service"}
        try:
            from src.auto_login.auto_smartschool_login import login_smartschool_via_microsoft, login_smartschool_admin_via_microsoft
            from src.auto_login.auto_microsoft_admin_login import login_microsoft_admin
            from src.auto_login.auto_google_admin_login import login_google_admin
            from src.auto_login.auto_easy4u_login import login_easy4u
            funcs = {
                "smartschool": login_smartschool_via_microsoft,
                "smartschool_admin": login_smartschool_admin_via_microsoft,
                "microsoft_admin": login_microsoft_admin,
                "google_admin": login_google_admin,
                "easy4u": login_easy4u,
            }
            thread = threading.Thread(target=funcs[service], daemon=True)
            thread.start()
            return {"success": True, "message": f"{service} login gestart"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def run_utility(self, utility):
        valid = ["clean_credentials", "migrate_key", "security_test", "clean_servers", "clear_browser_data"]
        if utility not in valid:
            return {"success": False, "error": "Onbekende utility"}
        try:
            if utility == "clean_credentials":
                from src.core.clean_credentials import run_clean_all
                results = run_clean_all()
                return {"success": True, "message": "Credentials opgeschoond", "utility": utility, "results": results}
            elif utility == "migrate_key":
                from src.core.migrate_key_file import migrate_key_file
                result = migrate_key_file()
                return {"success": result.get("success", False), "message": result.get("message", "Migratie voltooid"), "utility": utility, "result": result}
            elif utility == "security_test":
                from src.core.security_test import SecurityTest
                test = SecurityTest()
                test.run_all_tests()
                results = test.get_results()
                return {"success": True, "message": f"Security test voltooid: {results['total_passed']} geslaagd, {results['total_problems']} problemen gevonden", "utility": utility, "results": results}
            elif utility == "clean_servers":
                from src.core.clean_servers import clean_all_servers
                result = clean_all_servers()
                return {"success": result.get("success", False), "message": result.get("message", "Servers opgeschoond"), "utility": utility, "result": result}
            elif utility == "clear_browser_data":
                from src.auto_login.browser_cleanup import clear_browser_data
                result = clear_browser_data(force_kill=True)
                return {"success": result.get("success", False), "message": result.get("message", "Browser data gewist"), "utility": utility, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e), "utility": utility}

    def get_documentation_html(self):
        """Retourneer README als HTML (voor documentatiepagina in standalone)."""
        try:
            import markdown
            readme_path = SCRIPTS_DIR / "README.md"
            if not readme_path.exists():
                return "<p><strong>README.md niet gevonden.</strong></p>"
            with open(readme_path, "r", encoding="utf-8") as f:
                md = f.read()
            ext = ["fenced_code", "tables", "nl2br"]
            try:
                from markdown.extensions import codehilite
                ext.append("codehilite")
                cfg = {"codehilite": {"css_class": "highlight", "use_pygments": False}}
                html_content = markdown.markdown(md, extensions=ext, extension_configs=cfg)
            except ImportError:
                html_content = markdown.markdown(md, extensions=ext)
            return html_content
        except Exception as e:
            return f"<p><strong>Fout bij laden documentatie:</strong> {e!s}</p>"
