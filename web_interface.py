import os
import json
import html
import threading
from pathlib import Path
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv

# Import login modules
from auto_smartschool_login import login_smartschool_via_microsoft
from auto_microsoft_admin_login import login_microsoft_admin
from auto_google_admin_login import login_google_admin
from auto_easy4u_login import login_easy4u

# Import credentials manager
from credentials_manager import (
    get_data_dir,
    load_encrypted_credentials,
    save_encrypted_credentials,
    sync_to_env,
)

# Import security utilities
from security_utils import (
    sanitize_string,
    validate_email,
    validate_url,
    validate_hostname,
    validate_port,
    sanitize_file_path,
    validate_service_name,
    sanitize_json_input,
)

app = Flask(__name__)
# Secret key voor sessies en CSRF protection
# In productie: gebruik een sterke, willekeurige secret key
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")

# Applicatieversie (één plek; ook zichtbaar in webinterface en API)
APP_VERSION = "1.0.4"

# Pad: templates in bundel, data (credentials/servers) in persistente map
SCRIPTS_DIR = Path(__file__).parent
DATA_DIR = get_data_dir()
RDP_SERVERS_FILE = DATA_DIR / "rdp_servers.json"
SSH_SERVERS_FILE = DATA_DIR / "ssh_servers.json"
CREDENTIALS_FILE = DATA_DIR / "credentials.json"
ENV_FILE = DATA_DIR / ".env"

# Laad .env
load_dotenv()


@app.context_processor
def inject_version():
    """Maak applicatieversie beschikbaar in alle templates."""
    return {"app_version": APP_VERSION}


def load_rdp_servers():
    """Laad RDP servers uit encrypted JSON bestand."""
    if not RDP_SERVERS_FILE.exists():
        return []
    
    try:
        with open(RDP_SERVERS_FILE, "r", encoding="utf-8") as f:
            encrypted_data = json.load(f)
        
        # Decrypt wachtwoorden
        from credentials_manager import decrypt_password
        
        decrypted_servers = []
        for server in encrypted_data:
            decrypted_server = server.copy()
            if "password" in server and server["password"]:
                # Decrypt wachtwoord
                decrypted_server["password"] = decrypt_password(server["password"], SCRIPTS_DIR)
            decrypted_servers.append(decrypted_server)
        
        return decrypted_servers
    except Exception as e:
        print(f"Fout bij laden RDP servers: {e}")
        return []


def save_rdp_servers(servers):
    """Encrypt en sla RDP servers op in JSON bestand."""
    try:
        from credentials_manager import encrypt_password
        
        # Encrypt wachtwoorden
        encrypted_servers = []
        for server in servers:
            encrypted_server = server.copy()
            if "password" in server and server["password"]:
                # Encrypt wachtwoord
                encrypted_server["password"] = encrypt_password(server["password"], SCRIPTS_DIR)
            encrypted_servers.append(encrypted_server)
        
        with open(RDP_SERVERS_FILE, "w", encoding="utf-8") as f:
            json.dump(encrypted_servers, f, indent=2, ensure_ascii=False)
        
        # Zet bestandspermissies (alleen eigenaar kan lezen)
        if os.name != "nt":  # Unix/Linux
            os.chmod(RDP_SERVERS_FILE, 0o600)
        
        return True
    except Exception as e:
        print(f"Fout bij opslaan RDP servers: {e}")
        return False


def load_ssh_servers():
    """Laad SSH servers uit encrypted JSON bestand."""
    if not SSH_SERVERS_FILE.exists():
        return []
    
    try:
        with open(SSH_SERVERS_FILE, "r", encoding="utf-8") as f:
            encrypted_data = json.load(f)
        
        # Decrypt wachtwoorden
        from credentials_manager import decrypt_password
        
        decrypted_servers = []
        for server in encrypted_data:
            decrypted_server = server.copy()
            if "password" in server and server["password"]:
                try:
                    # Decrypt wachtwoord
                    decrypted_server["password"] = decrypt_password(server["password"], SCRIPTS_DIR)
                except Exception:
                    # Als decryptie faalt, laat leeg
                    decrypted_server["password"] = ""
            decrypted_servers.append(decrypted_server)
        
        return decrypted_servers
    except Exception as e:
        print(f"Fout bij laden SSH servers: {e}")
        return []


def save_ssh_servers(servers):
    """Encrypt en sla SSH servers op in JSON bestand."""
    try:
        from credentials_manager import encrypt_password
        
        # Encrypt wachtwoorden
        encrypted_servers = []
        for server in servers:
            encrypted_server = server.copy()
            if "password" in server and server["password"]:
                # Encrypt wachtwoord
                encrypted_server["password"] = encrypt_password(server["password"], SCRIPTS_DIR)
            encrypted_servers.append(encrypted_server)
        
        with open(SSH_SERVERS_FILE, "w", encoding="utf-8") as f:
            json.dump(encrypted_servers, f, indent=2, ensure_ascii=False)
        
        # Zet bestandspermissies (alleen eigenaar kan lezen)
        if os.name != "nt":  # Unix/Linux
            os.chmod(SSH_SERVERS_FILE, 0o600)
        
        return True
    except Exception as e:
        print(f"Fout bij opslaan SSH servers: {e}")
        return False


def load_credentials():
    """Laad credentials uit encrypted JSON bestand."""
    return load_encrypted_credentials(CREDENTIALS_FILE, SCRIPTS_DIR)


def save_credentials(creds):
    """Encrypt en sla credentials op in JSON bestand. GEEN wachtwoorden in .env."""
    try:
        # Sla encrypted op in JSON (wachtwoorden worden geëncrypteerd)
        if not save_encrypted_credentials(creds, CREDENTIALS_FILE, SCRIPTS_DIR):
            return False
        
        # Sync alleen URL's naar .env (GEEN wachtwoorden of emails)
        # Modules lezen nu direct uit encrypted credentials.json
        if not sync_to_env(creds, ENV_FILE, SCRIPTS_DIR):
            return False
        
        # Herlaad .env (maar wachtwoorden staan er niet meer in)
        load_dotenv(override=True)
        
        return True
    except Exception as e:
        print(f"Fout bij opslaan credentials: {e}")
        return False


@app.route("/")
def index():
    """Hoofdpagina - navigatie."""
    return render_template("index.html")


@app.route("/auto-login")
def auto_login():
    """Auto login pagina."""
    return render_template("auto_login.html")


@app.route("/credentials")
def credentials_page():
    """Credentials beheer pagina."""
    credentials = load_credentials()
    return render_template("credentials.html", credentials=credentials)


@app.route("/remote-connections")
def remote_connections():
    """Remote connections pagina (RDP + SSH)."""
    rdp_servers = load_rdp_servers()
    ssh_servers = load_ssh_servers()
    return render_template("remote_connections.html", rdp_servers=rdp_servers, ssh_servers=ssh_servers)


@app.route("/utilities")
def utilities():
    """Utilities pagina voor het uitvoeren van fix scripts."""
    return render_template("utilities.html")


@app.route("/api/version", methods=["GET"])
def api_version():
    """Geef de applicatieversie (voor desktop app of externe checks)."""
    return jsonify({"version": APP_VERSION})


@app.route("/api/utilities/<utility>", methods=["POST"])
def run_utility(utility):
    """Voer een utility script uit."""
    valid_utilities = ["clean_credentials", "migrate_key", "security_test", "clean_servers"]
    
    if utility not in valid_utilities:
        return jsonify({"success": False, "error": "Onbekende utility"}), 400
    
    try:
        if utility == "clean_credentials":
            from clean_credentials import run_clean_all
            results = run_clean_all()
            return jsonify({
                "success": True,
                "message": "Credentials opgeschoond",
                "utility": utility,
                "results": results
            })
        
        elif utility == "migrate_key":
            from migrate_key_file import migrate_key_file
            result = migrate_key_file()
            return jsonify({
                "success": result.get("success", False),
                "message": result.get("message", "Migratie voltooid"),
                "utility": utility,
                "result": result
            })
        
        elif utility == "security_test":
            from security_test import SecurityTest
            test = SecurityTest()
            test.run_all_tests()
            results = test.get_results()
            return jsonify({
                "success": True,
                "message": f"Security test voltooid: {results['total_passed']} geslaagd, {results['total_problems']} problemen gevonden",
                "utility": utility,
                "results": results
            })
        
        elif utility == "clean_servers":
            from clean_servers import clean_all_servers
            result = clean_all_servers()
            return jsonify({
                "success": result.get("success", False),
                "message": result.get("message", "Servers opgeschoond"),
                "utility": utility,
                "result": result
            })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "utility": utility
        }), 500


@app.route("/documentation")
def documentation():
    """Documentatie pagina - leest automatisch README.md."""
    try:
        import markdown
        
        # Lees README.md
        readme_path = SCRIPTS_DIR / "README.md"
        if readme_path.exists():
            with open(readme_path, "r", encoding="utf-8") as f:
                markdown_content = f.read()
            
            # Converteer markdown naar HTML met beschikbare extensions
            extensions = ['fenced_code', 'tables', 'nl2br']
            
            # Probeer codehilite toe te voegen als beschikbaar
            try:
                from markdown.extensions import codehilite
                extensions.append('codehilite')
                extension_configs = {
                    'codehilite': {
                        'css_class': 'highlight',
                        'use_pygments': False
                    }
                }
            except ImportError:
                extension_configs = {}
            
            # Converteer markdown naar HTML
            html_content = markdown.markdown(
                markdown_content,
                extensions=extensions,
                extension_configs=extension_configs
            )
        else:
            html_content = """
            <div style="background: #fff3cd; padding: 20px; border-radius: 8px; border-left: 4px solid #ffc107;">
                <p><strong>⚠️ README.md niet gevonden</strong></p>
                <p>Het README.md bestand kon niet worden gevonden. Zorg dat het bestand bestaat in de scripts directory.</p>
            </div>
            """
    except ImportError:
        # Fallback als markdown niet geïnstalleerd is
        html_content = """
        <div style="background: #fff3cd; padding: 20px; border-radius: 8px; border-left: 4px solid #ffc107;">
            <p><strong>⚠️ Markdown library niet geïnstalleerd</strong></p>
            <p>Installeer de markdown library om documentatie te kunnen weergeven:</p>
            <code style="background: #e9ecef; padding: 5px 10px; border-radius: 4px; display: block; margin-top: 10px;">
                pip install markdown
            </code>
        </div>
        """
    except Exception as e:
        html_content = f"""
        <div style="background: #f8d7da; padding: 20px; border-radius: 8px; border-left: 4px solid #dc3545;">
            <p><strong>❌ Fout bij laden documentatie</strong></p>
            <p>Er is een fout opgetreden bij het laden van de documentatie: {html.escape(str(e))}</p>
        </div>
        """
    
    return render_template("documentation.html", documentation_html=html_content)


@app.route("/api/login/<service>", methods=["POST"])
def start_login(service):
    """Start een login module voor een specifieke service."""
    # Valideer service naam
    if not validate_service_name(service):
        return jsonify({"success": False, "error": "Onbekende service"}), 400
    
    login_functions = {
        "smartschool": login_smartschool_via_microsoft,
        "microsoft_admin": login_microsoft_admin,
        "google_admin": login_google_admin,
        "easy4u": login_easy4u,
    }

    # Check of credentials zijn ingevuld
    credentials = load_credentials()
    
    required_fields = {
        "smartschool": ["email", "password"],
        "microsoft_admin": ["url", "email", "password"],
        "google_admin": ["url", "email", "password"],
        "easy4u": ["url", "email", "password"],
    }
    
    if service not in credentials:
        return jsonify({
            "success": False,
            "error": f"Credentials voor {service} zijn nog niet ingevuld. Ga naar de Credentials pagina om deze in te stellen."
        }), 400
    
    service_creds = credentials[service]
    missing_fields = []
    
    for field in required_fields.get(service, []):
        if not service_creds.get(field) or service_creds.get(field).strip() == "":
            missing_fields.append(field)
    
    if missing_fields:
        return jsonify({
            "success": False,
            "error": f"De volgende velden zijn niet ingevuld: {', '.join(missing_fields)}. Ga naar de Credentials pagina om deze in te stellen."
        }), 400

    try:
        # Start de login functie in een aparte thread (niet-blocking)
        login_func = login_functions[service]
        thread = threading.Thread(target=login_func, daemon=True)
        thread.start()
        
        return jsonify({"success": True, "message": f"{service} login gestart"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/rdp/connect", methods=["POST"])
def connect_rdp():
    """Start een RDP connectie naar een specifieke server."""
    data = request.get_json()
    host = data.get("host")
    user = data.get("user")
    password = data.get("password")

    if not host:
        return jsonify({"success": False, "error": "Host is verplicht"}), 400

    try:
        # Gebruik de functie uit auto_rdp_sessions.py
        from auto_rdp_sessions import _start_single_rdp

        _start_single_rdp(host, user, password)
        return jsonify({"success": True, "message": f"RDP connectie naar {host} gestart"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/rdp/servers", methods=["GET"])
def get_rdp_servers():
    """Haal alle RDP servers op."""
    servers = load_rdp_servers()
    return jsonify({"success": True, "servers": servers})


@app.route("/api/rdp/servers", methods=["POST"])
def add_rdp_server():
    """Voeg een nieuwe RDP server toe."""
    data = request.get_json()
    if not data or not isinstance(data, dict):
        return jsonify({"success": False, "error": "Ongeldige input"}), 400
    
    host = sanitize_string(data.get("host", ""))
    user = sanitize_string(data.get("user", ""))
    password = data.get("password", "")  # Wachtwoord niet sanitizen (wordt encrypted)
    name = sanitize_string(data.get("name", "")) or host

    if not host:
        return jsonify({"success": False, "error": "Host is verplicht"}), 400
    
    if not validate_hostname(host):
        return jsonify({"success": False, "error": "Ongeldig hostname of IP adres"}), 400

    servers = load_rdp_servers()

    # Check of host al bestaat
    if any(s.get("host") == host for s in servers):
        return jsonify({"success": False, "error": "Server met deze host bestaat al"}), 400

    new_server = {
        "id": len(servers) + 1,
        "name": name,
        "host": host,
        "user": user,
        "password": password,  # Wordt encrypted opgeslagen
    }

    servers.append(new_server)

    if save_rdp_servers(servers):
        return jsonify({"success": True, "message": "Server toegevoegd", "server": new_server})
    else:
        return jsonify({"success": False, "error": "Kon server niet opslaan"}), 500


@app.route("/api/rdp/servers/<int:server_id>", methods=["DELETE"])
def delete_rdp_server(server_id):
    """Verwijder een RDP server."""
    servers = load_rdp_servers()
    servers = [s for s in servers if s.get("id") != server_id]

    if save_rdp_servers(servers):
        return jsonify({"success": True, "message": "Server verwijderd"})
    else:
        return jsonify({"success": False, "error": "Kon server niet verwijderen"}), 500


@app.route("/api/ssh/connect", methods=["POST"])
def connect_ssh():
    """Start een SSH verbinding naar een specifieke server."""
    data = request.get_json()
    host = data.get("host")
    user = data.get("user")
    port = data.get("port", 22)
    key_file = data.get("key_file")
    password = data.get("password")

    if not host:
        return jsonify({"success": False, "error": "Host is verplicht"}), 400

    try:
        from auto_ssh_connect import start_ssh_connection

        start_ssh_connection(host, user, port, key_file, password)
        return jsonify({"success": True, "message": f"SSH verbinding naar {host} gestart"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/ssh/servers", methods=["GET"])
def get_ssh_servers():
    """Haal alle SSH servers op."""
    servers = load_ssh_servers()
    return jsonify({"success": True, "servers": servers})


@app.route("/api/ssh/servers", methods=["POST"])
def add_ssh_server():
    """Voeg een nieuwe SSH server toe."""
    data = request.get_json()
    if not data or not isinstance(data, dict):
        return jsonify({"success": False, "error": "Ongeldige input"}), 400
    
    host = sanitize_string(data.get("host", ""))
    user = sanitize_string(data.get("user", ""))
    port = data.get("port", 22)
    key_file = sanitize_file_path(data.get("key_file", ""))
    password = data.get("password", "")  # Wachtwoord niet sanitizen (wordt encrypted)
    name = sanitize_string(data.get("name", "")) or host

    if not host:
        return jsonify({"success": False, "error": "Host is verplicht"}), 400
    
    if not validate_hostname(host):
        return jsonify({"success": False, "error": "Ongeldig hostname of IP adres"}), 400

    if not validate_port(port):
        return jsonify({"success": False, "error": "Ongeldig poort nummer (1-65535)"}), 400
    
    try:
        port = int(port)
    except (ValueError, TypeError):
        port = 22

    servers = load_ssh_servers()

    # Check of host al bestaat
    if any(s.get("host") == host and s.get("port", 22) == port for s in servers):
        return jsonify({"success": False, "error": "Server met deze host en poort bestaat al"}), 400

    new_server = {
        "id": len(servers) + 1,
        "name": name,
        "host": host,
        "user": user,
        "port": port,
        "key_file": key_file,
        "password": password,  # Wordt encrypted opgeslagen
    }

    servers.append(new_server)

    if save_ssh_servers(servers):
        return jsonify({"success": True, "message": "Server toegevoegd", "server": new_server})
    else:
        return jsonify({"success": False, "error": "Kon server niet opslaan"}), 500


@app.route("/api/ssh/servers/<int:server_id>", methods=["DELETE"])
def delete_ssh_server(server_id):
    """Verwijder een SSH server."""
    servers = load_ssh_servers()
    servers = [s for s in servers if s.get("id") != server_id]

    if save_ssh_servers(servers):
        return jsonify({"success": True, "message": "Server verwijderd"})
    else:
        return jsonify({"success": False, "error": "Kon server niet verwijderen"}), 500


@app.route("/api/credentials", methods=["GET"])
def get_credentials():
    """Haal alle credentials op."""
    credentials = load_credentials()
    return jsonify({"success": True, "credentials": credentials})


@app.route("/api/credentials/<service>", methods=["POST"])
def save_service_credentials(service):
    """Sla credentials op voor een specifieke service."""
    # Valideer service naam
    if not validate_service_name(service):
        return jsonify({"success": False, "error": "Onbekende service"}), 400
    
    data = request.get_json()
    if not data or not isinstance(data, dict):
        return jsonify({"success": False, "error": "Ongeldige input"}), 400
    
    credentials = load_credentials()
    
    # Valideer en sanitize input
    if service == "smartschool":
        email = sanitize_string(data.get("email", ""))
        password = data.get("password", "")  # Wachtwoord niet sanitizen (wordt encrypted)
        
        if not email:
            return jsonify({"success": False, "error": "E-mail is verplicht"}), 400
        if not validate_email(email):
            return jsonify({"success": False, "error": "Ongeldig e-mail adres"}), 400
        if not password:
            return jsonify({"success": False, "error": "Wachtwoord is verplicht"}), 400
        
        credentials["smartschool"] = {
            "email": email,
            "password": password,
        }
    elif service == "microsoft_admin":
        url = sanitize_string(data.get("url", "https://admin.microsoft.com"))
        email = sanitize_string(data.get("email", ""))
        password = data.get("password", "")
        
        if not validate_url(url):
            return jsonify({"success": False, "error": "Ongeldige URL"}), 400
        if not email:
            return jsonify({"success": False, "error": "E-mail is verplicht"}), 400
        if not validate_email(email):
            return jsonify({"success": False, "error": "Ongeldig e-mail adres"}), 400
        if not password:
            return jsonify({"success": False, "error": "Wachtwoord is verplicht"}), 400
        
        credentials["microsoft_admin"] = {
            "url": url,
            "email": email,
            "password": password,
        }
    elif service == "google_admin":
        url = sanitize_string(data.get("url", "https://admin.google.com"))
        email = sanitize_string(data.get("email", ""))
        password = data.get("password", "")
        
        if not validate_url(url):
            return jsonify({"success": False, "error": "Ongeldige URL"}), 400
        if not email:
            return jsonify({"success": False, "error": "E-mail is verplicht"}), 400
        if not validate_email(email):
            return jsonify({"success": False, "error": "Ongeldig e-mail adres"}), 400
        if not password:
            return jsonify({"success": False, "error": "Wachtwoord is verplicht"}), 400
        
        credentials["google_admin"] = {
            "url": url,
            "email": email,
            "password": password,
        }
    elif service == "easy4u":
        url = sanitize_string(data.get("url", "https://my.easy4u.be/nl/login"))
        email = sanitize_string(data.get("email", ""))
        password = data.get("password", "")
        
        if not validate_url(url):
            return jsonify({"success": False, "error": "Ongeldige URL"}), 400
        if not email:
            return jsonify({"success": False, "error": "E-mail is verplicht"}), 400
        if not validate_email(email):
            return jsonify({"success": False, "error": "Ongeldig e-mail adres"}), 400
        if not password:
            return jsonify({"success": False, "error": "Wachtwoord is verplicht"}), 400
        
        credentials["easy4u"] = {
            "url": url,
            "email": email,
            "password": password,
        }
    
    if save_credentials(credentials):
        return jsonify({"success": True, "message": f"{service} credentials opgeslagen"})
    else:
        return jsonify({"success": False, "error": "Kon credentials niet opslaan"}), 500


if __name__ == "__main__":
    # Maak templates directory aan als die niet bestaat
    templates_dir = SCRIPTS_DIR / "templates"
    templates_dir.mkdir(exist_ok=True)

    # Productie vs Development mode
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    port = int(os.environ.get("FLASK_PORT", "5000"))
    
    # In productie: genereer een random secret key als die niet is ingesteld
    if not debug_mode and app.secret_key == "dev-secret-key-change-in-production":
        import secrets
        app.secret_key = secrets.token_hex(32)
        print("[!] WAARSCHUWING: FLASK_SECRET_KEY niet ingesteld. Gebruik een vaste secret key in productie!")
    
    # Start de Flask server
    app.run(host="127.0.0.1", port=port, debug=debug_mode)
