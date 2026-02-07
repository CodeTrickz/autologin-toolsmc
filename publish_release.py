"""
Publiceer SintMaartenCampusAutologin_Installatie.zip naar GitHub Releases.
Gebruikt GITHUB_TOKEN (env) of --token. Zonder token: toont instructies.

Voorbeelden:
  python publish_release.py
  python publish_release.py --token ghp_xxxx
"""
import os
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

REPO = "CodeTrickz/autologin-toolsmc"
ZIP_NAME = "SintMaartenCampusAutologin_Installatie.zip"


def get_version():
    from src.web.web_interface import APP_VERSION
    return APP_VERSION


def main():
    token = os.environ.get("GITHUB_TOKEN") or None
    if "--token" in sys.argv:
        i = sys.argv.index("--token")
        if i + 1 < len(sys.argv):
            token = sys.argv[i + 1]
    if not token:
        print("GITHUB_TOKEN is niet gezet. Zet een Personal Access Token (repo scope) of gebruik:")
        print("  python publish_release.py --token <JOUW_TOKEN>")
        print("Of: installeer GitHub CLI (gh) en run: scripts\\publish_release.bat")
        print("Token aanmaken: https://github.com/settings/tokens")
        return 1

    zip_path = SCRIPTS_DIR / ZIP_NAME
    if not zip_path.exists():
        print(f"Zip niet gevonden: {zip_path}")
        return 1

    version = get_version()
    tag = f"v{version}"
    zip_size = zip_path.stat().st_size

    # Create release
    url = f"https://api.github.com/repos/{REPO}/releases"
    data = {
        "tag_name": tag,
        "name": f"{tag} – Installatie voor andere PC's",
        "body": "Download de zip en voer op de doel-PC **install.bat** uit als administrator.\n\nGeen credentials of servergegevens in de zip.",
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode(),
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            release = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        if e.code == 422 and "already_exists" in body.lower():
            # Tag exists: get release by tag to get upload_url
            get_url = f"https://api.github.com/repos/{REPO}/releases/tags/{tag}"
            req2 = urllib.request.Request(
                get_url,
                headers={"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"},
            )
            try:
                with urllib.request.urlopen(req2) as resp:
                    release = json.loads(resp.read().decode())
            except urllib.error.HTTPError:
                print(f"Release {tag} bestaat maar kon niet worden opgehaald.")
                return 1
        else:
            print(f"Fout bij aanmaken release: {e.code} {body[:500]}")
            return 1

    upload_url = release.get("upload_url", "").split("{")[0]
    if not upload_url:
        print("Geen upload_url in response.")
        return 1

    # Upload zip
    upload_url = f"{upload_url}?name={ZIP_NAME}"
    with open(zip_path, "rb") as f:
        zip_data = f.read()

    req = urllib.request.Request(
        upload_url,
        data=zip_data,
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/zip",
            "Content-Length": str(len(zip_data)),
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            asset = json.loads(resp.read().decode())
        print(f"Release {tag} gepubliceerd.")
        print(f"Zip geüpload: {asset.get('name', ZIP_NAME)} ({zip_size // 1024 // 1024} MB)")
        print(f"Download: https://github.com/{REPO}/releases")
        return 0
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        if e.code == 422 and "already_exists" in body.lower():
            print(f"Asset {ZIP_NAME} bestaat al bij {tag}. Verwijder het bestaande bestand in de release en run opnieuw, of gebruik een nieuwe versie.")
        else:
            print(f"Fout bij upload: {e.code} {body[:500]}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
