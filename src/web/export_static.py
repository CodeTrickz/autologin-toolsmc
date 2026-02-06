"""
Exporteert Flask-templates naar statische HTML voor standalone desktop-modus.
Gebruik: python export_static.py
Output: static_export/ met index.html, credentials.html, etc.
Documentatie wordt direct meegenomen (geen laadstap).
"""
import sys
import html as html_module
from pathlib import Path

# Add parent directory to path for imports
SCRIPTS_DIR = Path(__file__).parent.parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from src.web.web_interface import app, APP_VERSION

# Output directory moet in project root zijn, niet in src/web/
OUTPUT_DIR = SCRIPTS_DIR / "static_export"


def _render_documentation_html():
    """Lees README.md en converteer naar HTML (zelfde logica als web_interface)."""
    try:
        import markdown
        readme_path = SCRIPTS_DIR / "README.md"
        if not readme_path.exists():
            return """<p><strong>README.md niet gevonden.</strong></p>"""
        with open(readme_path, "r", encoding="utf-8") as f:
            md = f.read()
        ext = ["fenced_code", "tables", "nl2br"]
        try:
            from markdown.extensions import codehilite
            ext.append("codehilite")
            cfg = {"codehilite": {"css_class": "highlight", "use_pygments": False}}
            return markdown.markdown(md, extensions=ext, extension_configs=cfg)
        except ImportError:
            return markdown.markdown(md, extensions=ext)
    except Exception as e:
        return f"<p><strong>Fout bij laden documentatie:</strong> {html_module.escape(str(e))}</p>"


LOADING_HTML = """<!DOCTYPE html><html lang="nl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<script>setTimeout(function(){ window.location.href = './index.html'; }, 500);</script>
</head><body style="margin:0;display:flex;align-items:center;justify-content:center;min-height:100vh;font-family:Segoe UI,sans-serif;background:linear-gradient(135deg,#4a90a4 0%,#5fb3a8 50%,#7bc4a0 100%);color:#fff;font-size:1.2em;">Applicatie laden...</body></html>"""


def export():
    OUTPUT_DIR.mkdir(exist_ok=True)
    (OUTPUT_DIR / "loading.html").write_text(LOADING_HTML, encoding="utf-8")
    documentation_html = _render_documentation_html()
    pages = [
        ("index.html", "index.html", {}),
        ("auto_login.html", "auto_login.html", {}),
        ("credentials.html", "credentials.html", {}),
        ("remote_connections.html", "remote_connections.html", {}),
        ("utilities.html", "utilities.html", {}),
        ("documentation.html", "documentation.html", {"documentation_html": documentation_html}),
    ]
    with app.app_context():
        for template_name, out_name, extra in pages:
            html = app.jinja_env.get_template(template_name).render(
                app_version=APP_VERSION,
                base_href="./",
                **extra
            )
            (OUTPUT_DIR / out_name).write_text(html, encoding="utf-8")
    return OUTPUT_DIR


if __name__ == "__main__":
    export()
    print("Static export klaar:", OUTPUT_DIR)
