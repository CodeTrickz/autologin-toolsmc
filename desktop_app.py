"""
Sint Maarten Campus Autologin Tool - Desktop GUI Applicatie
- Standalone-modus (geen Flask): zelfde HTML/CSS, geen localhost in browser.
- Of: Flask in achtergrond + embedded window (geen aparte browser).
"""
import os
import sys
import threading
import webbrowser
import time
import socket
import requests
import http.server
from pathlib import Path
from dotenv import load_dotenv

# Fix encoding voor Windows (voorkom UnicodeEncodeError bij .exe zonder console)
if sys.platform == 'win32':
    try:
        import codecs
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'replace')
    except Exception:
        pass

# Import Flask app en versie
from web_interface import app, APP_VERSION

# Pad naar de scripts directory
SCRIPTS_DIR = Path(__file__).parent

# Laad .env
load_dotenv()

# Maak templates directory aan als die niet bestaat
templates_dir = SCRIPTS_DIR / "templates"
templates_dir.mkdir(exist_ok=True)

# Probeer webview te gebruiken voor embedded browser
try:
    import webview
    WEBVIEW_AVAILABLE = True
except ImportError:
    WEBVIEW_AVAILABLE = False
    try:
        print("webview niet beschikbaar. Installeer met: pip install pywebview")
        print("Gebruik standaard browser in plaats daarvan.")
    except:
        pass


def is_port_in_use(port):
    """Check of een poort in gebruik is"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0


def wait_for_server(url, max_wait=10):
    """Wacht tot de Flask server klaar is"""
    for i in range(max_wait):
        try:
            response = requests.get(url, timeout=1)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(0.5)
    return False


def start_flask_server(port):
    """Start Flask server in achtergrond thread"""
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    if not debug_mode and app.secret_key == "dev-secret-key-change-in-production":
        import secrets
        app.secret_key = secrets.token_hex(32)
    app.run(host="127.0.0.1", port=port, debug=debug_mode, use_reloader=False)


def run_static_server(port, directory):
    """Start een eenvoudige bestandsserver voor static_export (geen Flask)."""
    os.chdir(directory)
    handler = http.server.SimpleHTTPRequestHandler
    server = http.server.HTTPServer(("127.0.0.1", port), handler)
    server.serve_forever()


def main():
    """Start de desktop applicatie."""
    use_standalone = os.environ.get("STANDALONE", "").lower() in ("1", "true", "yes")
    if "--standalone" in sys.argv:
        use_standalone = True
    # Gebundelde .exe: standaard standalone (geen Flask/localhost in browser)
    if not use_standalone and getattr(sys, "frozen", False):
        use_standalone = True
    if "--no-standalone" in sys.argv:
        use_standalone = False

    title = f"Sint Maarten Campus Autologin Tool v{APP_VERSION}"

    if use_standalone and WEBVIEW_AVAILABLE:
        # Standalone: geen Flask, alleen bestandsserver + Python-API (geen localhost in browser)
        static_export = SCRIPTS_DIR / "static_export"
        if not (static_export / "index.html").exists():
            try:
                from export_static import export
                export()
            except Exception as e:
                try:
                    print(f"Export mislukt: {e}. Start zonder --standalone.")
                except Exception:
                    pass
                use_standalone = False
        if use_standalone and (static_export / "index.html").exists():
            server_port = 0
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", 0))
                server_port = s.getsockname()[1]
            server_thread = threading.Thread(
                target=run_static_server,
                args=(server_port, str(static_export)),
                daemon=True,
            )
            server_thread.start()
            url = f"http://127.0.0.1:{server_port}/index.html"
            time.sleep(0.3)
            from desktop_api import DesktopAPI
            api = DesktopAPI()
            window = webview.create_window(
                title,
                url,
                width=1200,
                height=800,
                min_size=(900, 600),
                resizable=True,
                js_api=api,
            )
            webview.start(debug=False)
            return

    # Normale modus: Flask op localhost + webview (geen aparte browser)
    port = int(os.environ.get("FLASK_PORT", "5000"))
    url = f"http://127.0.0.1:{port}"

    if is_port_in_use(port):
        if WEBVIEW_AVAILABLE:
            try:
                window = webview.create_window(
                    title, url, width=1200, height=800,
                    min_size=(900, 600), resizable=True
                )
                webview.start(debug=False)
                return
            except Exception as e:
                try:
                    print(f"Fout bij starten webview: {e}")
                except Exception:
                    pass
                webbrowser.open(url)
                return
        else:
            webbrowser.open(url)
            return

    flask_thread = threading.Thread(target=start_flask_server, args=(port,), daemon=True)
    flask_thread.start()
    if not wait_for_server(url, max_wait=15):
        return

    if WEBVIEW_AVAILABLE:
        try:
            window = webview.create_window(
                title, url, width=1200, height=800,
                min_size=(900, 600), resizable=True
            )
            webview.start(debug=False)
        except Exception as e:
            try:
                print(f"Fout bij starten webview: {e}")
            except Exception:
                pass
            webbrowser.open(url)
            while True:
                time.sleep(1)
    else:
        webbrowser.open(url)
        while True:
            time.sleep(1)


if __name__ == "__main__":
    main()
