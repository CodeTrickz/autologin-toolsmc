import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Add parent directory to path for imports
SCRIPTS_DIR = Path(__file__).parent.parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from src.core.credentials_manager import get_credential, get_data_dir
from src.auto_login.browser_session import open_url_for_service, open_url_in_isolated_session
from src.auto_login.input_utils import clear_and_human_type
from src.auto_login.microsoft_account_switch import get_microsoft_email_input, prepare_microsoft_login_for_email
from src.auto_login.microsoft_site_data import clear_microsoft_site_data

DATA_DIR = get_data_dir()
CREDENTIALS_FILE = DATA_DIR / "credentials.json"

SMARTSCHOOL_URL = os.environ.get(
    "SMARTSCHOOL_URL",
    "https://sintmaartencampus.smartschool.be/login",
)


def get_credential_or_fail(service: str, field: str) -> str:
    """Haal credential op uit encrypted storage."""
    value = get_credential(service, field, DATA_DIR, CREDENTIALS_FILE)
    if not value or value.strip() == "":
        raise RuntimeError(
            f"Credentials ontbreken: {field} voor {service} is niet ingevuld.\n"
            "Ga naar de web interface (http://127.0.0.1:5000/credentials) om je credentials in te stellen."
        )
    return value


def _first_visible(elements):
    for el in elements:
        try:
            if el.is_displayed() and el.is_enabled():
                return el
        except Exception:
            continue
    return None


def _find_first_visible(driver, selectors, *, timeout: int = 8):
    """
    Vind het eerste zichtbare element dat matcht met een van de selectors.
    `selectors`: list[tuple[By, selector]]
    """
    def _try_find(_driver):
        for by, sel in selectors:
            try:
                els = _driver.find_elements(by, sel)
                el = _first_visible(els)
                if el:
                    return el
            except Exception:
                continue
        return False

    return WebDriverWait(driver, timeout).until(_try_find)


def _try_direct_smartschool_login(driver, wait: WebDriverWait, username: str, password: str) -> bool:
    """Probeer eerst Smartschool standaardlogin (gebruikersnaam + wachtwoord)."""
    username_selectors = [
        (By.CSS_SELECTOR, "input[placeholder*='Gebruikersnaam']"),
        (By.CSS_SELECTOR, "input[aria-label*='Gebruikersnaam']"),
        (By.NAME, "login"),
        (By.NAME, "username"),
        (By.NAME, "user"),
        (By.ID, "login"),
        (By.ID, "username"),
        # Fallback: enige zichtbare tekst input in login form
        (By.CSS_SELECTOR, "form input[type='text']"),
    ]
    try:
        username_input = _find_first_visible(driver, username_selectors, timeout=8)
    except TimeoutException:
        return False

    password_selectors = [
        (By.CSS_SELECTOR, "input[placeholder*='Wachtwoord']"),
        (By.CSS_SELECTOR, "input[aria-label*='Wachtwoord']"),
        (By.NAME, "password"),
        (By.NAME, "passwd"),
        (By.ID, "password"),
        (By.CSS_SELECTOR, "form input[type='password']"),
    ]
    try:
        pwd_input = _find_first_visible(driver, password_selectors, timeout=8)
    except TimeoutException:
        return False

    clear_and_human_type(username_input, username)
    clear_and_human_type(pwd_input, password)

    submit_selectors = [
        (By.CSS_SELECTOR, "input[type='submit']"),
        (By.CSS_SELECTOR, "button[type='submit']"),
        (By.XPATH, "//button[contains(translate(., 'AANMELDENINLOGGENLOGIN', 'aanmeldeninloggenlogin'), 'aanmelden') or contains(translate(., 'AANMELDENINLOGGENLOGIN', 'aanmeldeninloggenlogin'), 'inloggen') or contains(translate(., 'AANMELDENINLOGGENLOGIN', 'aanmeldeninloggenlogin'), 'login')]"),
        (By.XPATH, "//input[@type='submit' and (contains(@value,'Aanmelden') or contains(@value,'Inloggen') or contains(@value,'Login'))]"),
    ]

    try:
        submit_btn = _find_first_visible(driver, submit_selectors, timeout=8)
    except TimeoutException:
        return False

    submit_btn.click()
    return True


def _try_smartschool_microsoft_login(driver, wait: WebDriverWait, account_email: str, password: str) -> bool:
    """Probeer Smartschool login via Microsoft-knop met e-mail + wachtwoord."""
    microsoft_button = None
    selector_attempts = [
        (By.XPATH, "//a[contains(., 'Microsoft')]"),
        (By.XPATH, "//button[contains(., 'Microsoft')]"),
        (By.XPATH, "//*[contains(., 'Microsoft') and (self::a or self::button)]"),
    ]
    for by, selector in selector_attempts:
        try:
            microsoft_button = wait.until(EC.element_to_be_clickable((by, selector)))
            break
        except Exception:
            continue
    if not microsoft_button:
        return False

    microsoft_button.click()
    # Fast path: als het Microsoft e-mailveld al klaar is, meteen invullen.
    if not get_microsoft_email_input(driver, timeout=0.8):
        prepare_microsoft_login_for_email(driver, account_email, timeout=20, start_url=None)

    email_input = None
    for by, selector in [
        (By.NAME, "loginfmt"),
        (By.ID, "i0116"),
        (By.CSS_SELECTOR, "input[type='email']"),
    ]:
        try:
            email_input = wait.until(EC.presence_of_element_located((by, selector)))
            break
        except Exception:
            continue
    if not email_input:
        return False
    clear_and_human_type(email_input, account_email)

    next_btn = wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
    next_btn.click()

    password_input = wait.until(EC.element_to_be_clickable((By.NAME, "passwd")))
    clear_and_human_type(password_input, password)

    signin_btn = wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
    signin_btn.click()

    # Optioneel "Blijf aangemeld?" dialoog altijd op "Nee" zetten.
    try:
        no_btn = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.ID, "idBtn_Back"))
        )
        no_btn.click()
    except Exception:
        pass

    return True


def _looks_like_email(value: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value or ""))


def _do_smartschool_login(account_id: str, account_password: str) -> None:
    """Voer Smartschool login uit: e-mail via Microsoft, username via standaard login."""
    load_dotenv()
    account_id = (account_id or "").strip()
    # Voor username-login willen we cookie-isolatie zodat je 2 accounts tegelijk kan openhouden.
    # Incognito is per venster/proces (niet per tab), dus we starten hiervoor een aparte Chrome instance.
    if _looks_like_email(account_id):
        driver = open_url_for_service("smartschool", SMARTSCHOOL_URL, new_tab=True, account_id=account_id)
        # Wis enkel Microsoft site-data voor deze loginpoging om account-conflict te voorkomen.
        clear_microsoft_site_data(driver)
        driver.get(SMARTSCHOOL_URL)
    else:
        driver = open_url_in_isolated_session(SMARTSCHOOL_URL, incognito=True)

    try:
        wait = WebDriverWait(driver, 30)
        if _looks_like_email(account_id):
            used_microsoft_login = _try_smartschool_microsoft_login(driver, wait, account_id, account_password)
            if used_microsoft_login:
                print("Smartschool login via Microsoft uitgevoerd in gedeelde browser-sessie (tab blijft open).")
                return
            raise RuntimeError(
                "E-mail login vereist Microsoft-knop, maar Microsoft-flow kon niet worden gestart."
            )

        used_direct_login = _try_direct_smartschool_login(driver, wait, account_id, account_password)
        if used_direct_login:
            print("Smartschool standaardlogin (gebruikersnaam) uitgevoerd in incognito sessie (venster blijft open).")
            return

        raise RuntimeError(
            "Kon de Smartschool standaardlogin velden niet vinden. "
            "Controleer de loginpagina of pas selectors aan."
        )

    finally:
        pass


def login_smartschool_via_microsoft() -> None:
    """Log in op Smartschool met standaard credentials (gebruikersnaam of e-mail veld)."""
    account_id = get_credential("smartschool", "username", DATA_DIR, CREDENTIALS_FILE) or get_credential_or_fail("smartschool", "email")
    account_password = get_credential_or_fail("smartschool", "password")
    _do_smartschool_login(account_id, account_password)


def login_smartschool_admin_via_microsoft() -> None:
    """Log in op Smartschool admin met beheerderscredentials (gebruikersnaam of e-mail veld)."""
    account_id = get_credential("smartschool_admin", "username", DATA_DIR, CREDENTIALS_FILE) or get_credential_or_fail("smartschool_admin", "email")
    account_password = get_credential_or_fail("smartschool_admin", "password")
    _do_smartschool_login(account_id, account_password)


if __name__ == "__main__":
    login_smartschool_via_microsoft()

