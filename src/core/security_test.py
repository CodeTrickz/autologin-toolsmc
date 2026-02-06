"""
Security Test Script voor Sint Maarten Campus Autologin Tool
Controleert op beveiligingsproblemen en best practices.
"""
import os
import sys
import json
import stat
from pathlib import Path
from cryptography.fernet import Fernet

# Add parent directory to path for imports
SCRIPTS_DIR = Path(__file__).parent.parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

# Use get_data_dir for file paths (works for both dev and .exe)
from src.core.credentials_manager import get_data_dir
DATA_DIR = get_data_dir()

CREDENTIALS_FILE = DATA_DIR / "credentials.json"
RDP_SERVERS_FILE = DATA_DIR / "rdp_servers.json"
SSH_SERVERS_FILE = DATA_DIR / "ssh_servers.json"
ENV_FILE = DATA_DIR / ".env"
KEY_FILE_OLD = SCRIPTS_DIR / ".credentials_key"

# Nieuwe key file locaties
if os.name == "nt":  # Windows
    appdata_dir = Path(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")))
    KEY_FILE_NEW = appdata_dir / "SintMaartenCampusAutologin" / ".credentials_key"
else:
    KEY_FILE_NEW = Path.home() / ".config" / "sintmaartencampus-autologin" / ".credentials_key"

class SecurityTest:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.passed = []
        
        # Zorg dat sys.path correct is ingesteld voor imports
        if str(SCRIPTS_DIR) not in sys.path:
            sys.path.insert(0, str(SCRIPTS_DIR))
        
        # Debug: log sys.path voor troubleshooting
        if hasattr(self, '_debug') and self._debug:
            print(f"SecurityTest initialized, SCRIPTS_DIR: {SCRIPTS_DIR}")
            print(f"sys.path (first 3): {sys.path[:3]}")
    
    def add_issue(self, severity, category, message, recommendation=""):
        if severity == "CRITICAL":
            self.issues.append({
                "severity": severity,
                "category": category,
                "message": message,
                "recommendation": recommendation
            })
        else:
            self.warnings.append({
                "severity": severity,
                "category": category,
                "message": message,
                "recommendation": recommendation
            })
    
    def add_pass(self, category, message):
        self.passed.append({
            "category": category,
            "message": message
        })
    
    def test_1_plaintext_passwords(self):
        """Test 1: Controleer op plaintext wachtwoorden in bestanden"""
        print("\n[TEST 1] Controleer op plaintext wachtwoorden...")
        
        # Check .env file
        if ENV_FILE.exists():
            with open(ENV_FILE, "r", encoding="utf-8") as f:
                content = f.read().lower()
                if "password" in content or "wachtwoord" in content:
                    self.add_issue(
                        "CRITICAL",
                        "Plaintext Passwords",
                        f"Gevoelige data gevonden in {ENV_FILE}",
                        "Verwijder alle wachtwoorden uit .env. Gebruik alleen encrypted credentials.json"
                    )
                else:
                    self.add_pass("Plaintext Passwords", ".env bevat geen wachtwoorden")
        
        # Check credentials.json voor plaintext
        if CREDENTIALS_FILE.exists():
            try:
                with open(CREDENTIALS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for service, creds in data.items():
                        if isinstance(creds, dict) and "password" in creds:
                            pwd = creds["password"]
                            # Check of het encrypted is (base64 encoded encrypted data)
                            if not pwd.startswith("gAAAA") and len(pwd) > 20:
                                # Fernet encrypted data begint meestal met gAAAA
                                # Maar base64 encoded kan ook, check of het decryptbaar is
                                try:
                                    # Probeer te decoderen als base64
                                    import base64
                                    decoded = base64.b64decode(pwd)
                                    # Als het decryptbaar is zonder key, is het niet encrypted
                                    if len(decoded) < 32:  # Fernet tokens zijn minimaal 32 bytes
                                        self.add_issue(
                                            "CRITICAL",
                                            "Plaintext Passwords",
                                            f"Wachtwoord in {service} lijkt niet encrypted",
                                            "Zorg dat alle wachtwoorden encrypted zijn opgeslagen"
                                        )
                                    else:
                                        self.add_pass("Plaintext Passwords", f"Wachtwoord in {service} is encrypted")
                                except:
                                    # Als het niet base64 is, is het waarschijnlijk plaintext
                                    if not pwd.startswith("gAAAA"):
                                        self.add_issue(
                                            "CRITICAL",
                                            "Plaintext Passwords",
                                            f"Wachtwoord in {service} lijkt plaintext",
                                            "Encrypt alle wachtwoorden voordat je ze opslaat"
                                        )
            except Exception as e:
                self.add_issue(
                    "WARNING",
                    "File Access",
                    f"Kon {CREDENTIALS_FILE} niet lezen: {e}",
                    "Controleer bestandspermissies"
                )
    
    def test_2_file_permissions(self):
        """Test 2: Controleer bestandspermissies"""
        print("\n[TEST 2] Controleer bestandspermissies...")
        
        files_to_check = [
            (CREDENTIALS_FILE, "credentials.json"),
            (RDP_SERVERS_FILE, "rdp_servers.json"),
            (SSH_SERVERS_FILE, "ssh_servers.json"),
            (KEY_FILE_OLD, ".credentials_key (oud)"),
            (KEY_FILE_NEW, ".credentials_key (nieuw)"),
        ]
        
        for file_path, name in files_to_check:
            if file_path.exists():
                try:
                    if os.name != "nt":  # Unix/Linux
                        file_stat = os.stat(file_path)
                        mode = file_stat.st_mode
                        # Check of alleen eigenaar kan lezen (600 of 700)
                        if (mode & stat.S_IRWXG) or (mode & stat.S_IRWXO):
                            self.add_issue(
                                "CRITICAL",
                                "File Permissions",
                                f"{name} heeft te open permissies (anderen kunnen lezen)",
                                f"Zet permissies met: chmod 600 {file_path}"
                            )
                        else:
                            self.add_pass("File Permissions", f"{name} heeft correcte permissies")
                    else:  # Windows
                        # Op Windows zijn permissies complexer, maar we kunnen checken of het hidden is
                        if file_path.name.startswith("."):
                            self.add_pass("File Permissions", f"{name} is hidden op Windows")
                except Exception as e:
                    self.add_issue(
                        "WARNING",
                        "File Permissions",
                        f"Kon permissies van {name} niet controleren: {e}",
                        ""
                    )
    
    def test_3_key_file_security(self):
        """Test 3: Controleer encryptie key file beveiliging"""
        print("\n[TEST 3] Controleer encryptie key file...")
        
        key_files = [KEY_FILE_OLD, KEY_FILE_NEW]
        key_found = False
        
        for key_file in key_files:
            if key_file.exists():
                key_found = True
                # Check of key file niet te groot is (moet 44 bytes zijn voor Fernet)
                try:
                    size = key_file.stat().st_size
                    if size != 44:
                        self.add_issue(
                            "WARNING",
                            "Key File",
                            f"Key file {key_file} heeft onverwachte grootte ({size} bytes)",
                            "Fernet keys moeten 44 bytes zijn (32 bytes key + base64 encoding)"
                        )
                    else:
                        self.add_pass("Key File", f"Key file {key_file} heeft correcte grootte")
                    
                    # Check permissies
                    if os.name != "nt":
                        file_stat = os.stat(key_file)
                        mode = file_stat.st_mode
                        if (mode & stat.S_IRWXG) or (mode & stat.S_IRWXO):
                            self.add_issue(
                                "CRITICAL",
                                "Key File",
                                f"Key file {key_file} heeft te open permissies",
                                f"Zet permissies met: chmod 600 {key_file}"
                            )
                except Exception as e:
                    self.add_issue(
                        "WARNING",
                        "Key File",
                        f"Kon key file {key_file} niet controleren: {e}",
                        ""
                    )
        
        if not key_found:
            self.add_issue(
                "WARNING",
                "Key File",
                "Geen encryptie key file gevonden",
                "Er wordt mogelijk een master password gebruikt of key wordt bij eerste gebruik aangemaakt"
            )
    
    def test_4_encryption_implementation(self):
        """Test 4: Controleer encryptie implementatie"""
        print("\n[TEST 4] Controleer encryptie implementatie...")
        
        try:
            # Probeer verschillende import methoden
            try:
                from src.core.credentials_manager import get_encryption_key, encrypt_password, decrypt_password
            except ImportError:
                # Fallback: probeer direct import
                try:
                    from credentials_manager import get_encryption_key, encrypt_password, decrypt_password
                except ImportError:
                    # Laatste fallback: import module en gebruik attributen
                    import importlib
                    try:
                        cm_module = importlib.import_module('src.core.credentials_manager')
                        get_encryption_key = cm_module.get_encryption_key
                        encrypt_password = cm_module.encrypt_password
                        decrypt_password = cm_module.decrypt_password
                    except Exception as import_err:
                        raise ImportError(f"Kon credentials_manager niet importeren: {import_err}")
            
            # Test encryptie/decryptie
            test_password = "test_password_123"
            scripts_dir = SCRIPTS_DIR
            
            encrypted = encrypt_password(test_password, scripts_dir)
            if not encrypted:
                self.add_issue(
                    "CRITICAL",
                    "Encryption",
                    "Encryptie functie werkt niet",
                    "Controleer credentials_manager.py"
                )
                return
            
            decrypted = decrypt_password(encrypted, scripts_dir)
            if decrypted != test_password:
                self.add_issue(
                    "CRITICAL",
                    "Encryption",
                    "Decryptie werkt niet correct",
                    "Controleer encryptie/decryptie logica"
                )
            else:
                self.add_pass("Encryption", "Encryptie/decryptie werkt correct")
            
            # Check of encrypted data base64 is
            try:
                import base64
                base64.b64decode(encrypted)
                self.add_pass("Encryption", "Encrypted data is correct base64 encoded")
            except:
                self.add_issue(
                    "WARNING",
                    "Encryption",
                    "Encrypted data is geen geldige base64",
                    "Controleer encryptie implementatie"
                )
                
        except ImportError as e:
            # Meer gedetailleerde error message
            import traceback
            error_details = str(e)
            if "credentials_manager" in error_details.lower():
                self.add_issue(
                    "CRITICAL",
                    "Encryption",
                    f"Kon encryptie modules niet importeren: {e}",
                    f"Controleer sys.path: {sys.path[:3]}... Controleer of src/core/credentials_manager.py bestaat."
                )
            else:
                self.add_issue(
                    "CRITICAL",
                    "Encryption",
                    f"Kon encryptie modules niet importeren: {e}",
                    "Installeer cryptography: pip install cryptography"
                )
        except Exception as e:
            import traceback
            self.add_issue(
                "WARNING",
                "Encryption",
                f"Fout bij testen encryptie: {e}",
                f"Controleer credentials_manager.py. Traceback: {traceback.format_exc()[:200]}"
            )
    
    def test_5_web_security(self):
        """Test 5: Controleer web interface beveiliging"""
        print("\n[TEST 5] Controleer web interface beveiliging...")
        
        # Check of Flask secret key is ingesteld (geen default in productie)
        try:
            from src.web.web_interface import app
            default_keys = ("dev-secret-key", "dev-secret-key-change-in-production")
            if not app.secret_key or (app.secret_key in default_keys):
                self.add_issue(
                    "WARNING",
                    "Web Security",
                    "Flask secret key niet ingesteld of gebruikt default",
                    "Zet FLASK_SECRET_KEY in .env of environment in productie"
                )
            else:
                self.add_pass("Web Security", "Flask secret key is ingesteld")
        except:
            self.add_issue(
                "WARNING",
                "Web Security",
                "Kon Flask app niet controleren",
                ""
            )
        
        # Check of er input validatie is
        try:
            # Probeer verschillende import methoden
            try:
                from src.core.security_utils import (
                    sanitize_string,
                    validate_email,
                    validate_url,
                    validate_hostname,
                )
            except ImportError:
                # Fallback: probeer direct import
                try:
                    from security_utils import (
                        sanitize_string,
                        validate_email,
                        validate_url,
                        validate_hostname,
                    )
                except ImportError:
                    # Laatste fallback: import module en gebruik attributen
                    import importlib
                    su_module = importlib.import_module('src.core.security_utils')
                    sanitize_string = su_module.sanitize_string
                    validate_email = su_module.validate_email
                    validate_url = su_module.validate_url
                    validate_hostname = su_module.validate_hostname
            
            self.add_pass("Web Security", "Input validatie en sanitization modules aanwezig")
        except ImportError as e:
            self.add_issue(
                "WARNING",
                "Web Security",
                f"Security utilities module niet gevonden: {e}",
                f"Zorg dat src/core/security_utils.py bestaat. sys.path: {sys.path[:3]}..."
            )
        except Exception as e:
            self.add_issue(
                "WARNING",
                "Web Security",
                f"Fout bij importeren security_utils: {e}",
                "Controleer of src/core/security_utils.py bestaat en correct is"
            )
        
        # Check of security utils worden gebruikt in web_interface (alleen als bronbestand bestaat, niet in gebundelde app)
        web_interface_path = SCRIPTS_DIR / "src" / "web" / "web_interface.py"
        if web_interface_path.exists():
            try:
                with open(web_interface_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if "from src.core.security_utils import" in content or "from security_utils import" in content:
                        self.add_pass("Web Security", "Security utilities worden gebruikt in web_interface")
                    else:
                        self.add_issue(
                            "WARNING",
                            "Web Security",
                            "Security utilities worden mogelijk niet gebruikt",
                            "Importeer en gebruik security_utils in web_interface.py"
                        )
            except Exception as e:
                self.add_issue(
                    "WARNING",
                    "Web Security",
                    f"Kon web_interface.py niet controleren: {e}",
                    ""
                )
        else:
            # Gebundelde/geïnstalleerde versie: geen bronbestand, controle niet van toepassing
            self.add_pass("Web Security", "Security utilities beschikbaar (geïnstalleerde versie)")
    
    def _is_bundled_or_installed(self):
        """True als we draaien vanuit gebundelde .exe of installatiemap (geen broncode-omgeving)."""
        scripts_str = str(SCRIPTS_DIR).lower()
        return (
            getattr(sys, "frozen", False)
            or "_internal" in scripts_str
            or "dist" in scripts_str
            or "program files" in scripts_str
            or not (SCRIPTS_DIR / "src" / "web" / "web_interface.py").exists()
        )

    def test_6_sensitive_data_exposure(self):
        """Test 6: Controleer op blootstelling van gevoelige data"""
        print("\n[TEST 6] Controleer op blootstelling van gevoelige data...")
        
        # In gebundelde/geïnstalleerde app is .gitignore niet van toepassing
        if self._is_bundled_or_installed():
            self.add_pass("Git Security", ".gitignore niet van toepassing (geïnstalleerde versie)")
            return

        # Check of er geen credentials in git (alleen in ontwikkelomgeving)
        gitignore = SCRIPTS_DIR / ".gitignore"
        if gitignore.exists():
            with open(gitignore, "r", encoding="utf-8") as f:
                content = f.read()
                required_ignores = [
                    "credentials.json",
                    ".credentials_key",
                    ".env",
                    "rdp_servers.json",
                    "ssh_servers.json"
                ]
                missing = [item for item in required_ignores if item not in content]
                if missing:
                    self.add_issue(
                        "CRITICAL",
                        "Git Security",
                        f"Ontbrekende entries in .gitignore: {', '.join(missing)}",
                        f"Voeg toe aan .gitignore: {', '.join(missing)}"
                    )
                else:
                    self.add_pass("Git Security", ".gitignore bevat alle gevoelige bestanden")
        else:
            self.add_issue(
                "CRITICAL",
                "Git Security",
                ".gitignore bestand ontbreekt",
                "Maak .gitignore aan en voeg alle gevoelige bestanden toe"
            )
    
    def run_all_tests(self):
        """Voer alle security tests uit"""
        self.test_1_plaintext_passwords()
        self.test_2_file_permissions()
        self.test_3_key_file_security()
        self.test_4_encryption_implementation()
        self.test_5_web_security()
        self.test_6_sensitive_data_exposure()
    
    def get_results(self):
        """Retourneer test resultaten als dict."""
        total_issues = len(self.issues) + len(self.warnings)
        return {
            "passed": self.passed,
            "warnings": self.warnings,
            "issues": self.issues,
            "total_passed": len(self.passed),
            "total_warnings": len(self.warnings),
            "total_issues": len(self.issues),
            "total_problems": total_issues,
            "all_passed": total_issues == 0
        }
    
    def print_results(self):
        """Print test resultaten"""
        print("=" * 60)
        print("SECURITY TEST - Sint Maarten Campus Autologin Tool")
        print("=" * 60)
        
        print(f"\n[PASSED] {len(self.passed)}")
        for item in self.passed:
            print(f"  [OK] {item['category']}: {item['message']}")
        
        print(f"\n[WARNINGS] {len(self.warnings)}")
        for item in self.warnings:
            print(f"  [!] {item['severity']} - {item['category']}: {item['message']}")
            if item['recommendation']:
                print(f"    -> {item['recommendation']}")
        
        print(f"\n[CRITICAL ISSUES] {len(self.issues)}")
        for item in self.issues:
            print(f"  [X] {item['severity']} - {item['category']}: {item['message']}")
            if item['recommendation']:
                print(f"    -> {item['recommendation']}")
        
        print("\n" + "=" * 60)
        total_issues = len(self.issues) + len(self.warnings)
        if total_issues == 0:
            print("[SUCCESS] ALLE TESTS GESLAAGD - Geen beveiligingsproblemen gevonden!")
        else:
            print(f"[WARNING] {total_issues} beveiligingsproblemen gevonden")
        print("=" * 60)

if __name__ == "__main__":
    test = SecurityTest()
    test.run_all_tests()
