import os
import time
from pathlib import Path

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import sys
from pathlib import Path

# Add parent directory to path for imports
SCRIPTS_DIR = Path(__file__).parent.parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from src.core.credentials_manager import get_credential, get_data_dir

DATA_DIR = get_data_dir()
CREDENTIALS_FILE = DATA_DIR / "credentials.json"


def get_credential_or_fail(service: str, field: str) -> str:
    """Haal credential op uit encrypted storage (gebruikt persistente datamap bij .exe)."""
    value = get_credential(service, field, DATA_DIR, CREDENTIALS_FILE)
    if not value or value.strip() == "":
        raise RuntimeError(
            f"Credentials ontbreken: {field} voor {service} is niet ingevuld.\n"
            "Ga naar de web interface of desktop app om je credentials in te stellen."
        )
    return value


def create_driver() -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    driver = webdriver.Chrome(options=options, service=ChromeService())
    return driver


def _is_visible(driver, element) -> bool:
    """Check of element zichtbaar en bruikbaar is (niet hidden)."""
    try:
        if not element.is_displayed():
            return False
        if element.get_attribute("type") == "hidden":
            return False
        return True
    except Exception:
        return False


def _find_email_input(driver):
    """Vind het e-mail/gebruikersnaam veld (Portal Easy4u: 'Gebruikersnaam')."""
    wait = WebDriverWait(driver, 15)
    # 1) Portal Easy4u (my.easy4u.be/nl/login): placeholder "Vul hier je gebruikersnaam in"
    for by, sel in [
        (By.XPATH, "//input[contains(@placeholder, 'gebruikersnaam') or contains(@placeholder, 'Gebruikersnaam')]"),
        (By.XPATH, "//label[contains(., 'Gebruikersnaam')]/following-sibling::input"),
        (By.XPATH, "//input[contains(@placeholder, 'Vul hier') and not(@type='password')]"),
        (By.NAME, "gebruikersnaam"),
        (By.ID, "gebruikersnaam"),
        (By.CSS_SELECTOR, "input[type='email']"),
        (By.NAME, "email"),
        (By.ID, "email"),
        (By.NAME, "username"),
        (By.ID, "username"),
        (By.CSS_SELECTOR, "input[autocomplete='email']"),
    ]:
        try:
            el = wait.until(EC.presence_of_element_located((by, sel)))
            if _is_visible(driver, el):
                return el
        except Exception:
            continue
    # 2) Eerste zichtbare input die type=text of type=email is (geen password)
    try:
        inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='email']")
        for inp in inputs:
            if _is_visible(driver, inp) and inp.get_attribute("type") != "password":
                return inp
    except Exception:
        pass
    return None


def _find_password_input(driver):
    """Vind het wachtwoord veld (Portal Easy4u: placeholder 'Vul hier je wachtwoord in')."""
    wait = WebDriverWait(driver, 10)
    for by, sel in [
        (By.XPATH, "//input[@type='password' and (contains(@placeholder, 'wachtwoord') or contains(@placeholder, 'Wachtwoord'))]"),
        (By.XPATH, "//input[contains(@placeholder, 'wachtwoord')]"),
        (By.XPATH, "//label[contains(., 'Wachtwoord')]/following-sibling::*//input[@type='password']"),
        (By.CSS_SELECTOR, "input[type='password']"),
        (By.NAME, "password"),
        (By.ID, "password"),
        (By.NAME, "passwd"),
        (By.ID, "passwd"),
    ]:
        try:
            el = wait.until(EC.presence_of_element_located((by, sel)))
            if _is_visible(driver, el):
                return el
        except Exception:
            continue
    try:
        for inp in driver.find_elements(By.CSS_SELECTOR, "input[type='password']"):
            if _is_visible(driver, inp):
                return inp
    except Exception:
        pass
    return None


def _find_submit_or_login_button(driver):
    """Vind login/submit knop (Portal Easy4u: knop met tekst 'Inloggen')."""
    wait = WebDriverWait(driver, 10)
    for by, sel in [
        (By.XPATH, "//button[normalize-space(.)='Inloggen']"),
        (By.XPATH, "//*[@type='submit' and normalize-space(.)='Inloggen']"),
        (By.XPATH, "//input[@type='submit' and (@value='Inloggen' or normalize-space(@value)='Inloggen')]"),
        (By.XPATH, "//button[contains(., 'Inloggen')]"),
        (By.XPATH, "//a[contains(@class, 'btn') and contains(., 'Inloggen')]"),
        (By.CSS_SELECTOR, "button[type='submit']"),
        (By.CSS_SELECTOR, "input[type='submit']"),
        (By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'inloggen')]"),
        (By.ID, "login-btn"),
        (By.ID, "submit"),
        (By.NAME, "submit"),
    ]:
        try:
            el = wait.until(EC.element_to_be_clickable((by, sel)))
            if _is_visible(driver, el):
                return ("click", el)
        except Exception:
            continue
    # Fallback: zoek formulier en return dat (submit via Enter of form.submit())
    try:
        form = driver.find_element(By.TAG_NAME, "form")
        if form and _is_visible(driver, form):
            return ("form", form)
    except Exception:
        pass
    return None


def _try_switch_to_login_iframe(driver):
    """Probeer te wisselen naar een iframe dat de login bevat (bijv. sommige portalen)."""
    try:
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for iframe in iframes:
            try:
                driver.switch_to.frame(iframe)
                if _find_email_input(driver) and _find_password_input(driver):
                    return True
            except Exception:
                pass
            finally:
                driver.switch_to.default_content()
    except Exception:
        pass
    return False


def login_easy4u() -> None:
    """
    Log automatisch in op Portal Easy4u: https://my.easy4u.be/nl/login
    Velden: Gebruikersnaam, Wachtwoord, knop Inloggen.
    Gebruikt credentials uit de app (Credentials > Easy4U: URL, e-mail/gebruikersnaam, wachtwoord).
    """
    env_path = DATA_DIR / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()

    easy4u_url = (get_credential_or_fail("easy4u", "url") or "").strip() or "https://my.easy4u.be/nl/login"
    # Bij Portal Easy4u is dit veld "Gebruikersnaam" (kan e-mail of gebruikersnaam zijn)
    easy4u_email = get_credential_or_fail("easy4u", "email")
    easy4u_password = get_credential_or_fail("easy4u", "password")

    driver = create_driver()

    try:
        print(f"Ga naar {easy4u_url}...")
        driver.get(easy4u_url)

        WebDriverWait(driver, 15).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(3)
        # Portal Easy4u kan dynamisch laden; wacht op eerste zichtbare input
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text'], input[type='email'], input[placeholder*='gebruikersnaam'], input[placeholder*='Gebruikersnaam']"))
            )
            time.sleep(1)
        except Exception:
            pass

        # Optioneel: als er een login-iframe is, daarnaar wisselen
        if not _find_email_input(driver):
            _try_switch_to_login_iframe(driver)

        email_input = _find_email_input(driver)
        if not email_input:
            try:
                all_in = driver.find_elements(By.TAG_NAME, "input")
                print("Debug inputs:", [(i.get_attribute("type"), i.get_attribute("name"), i.get_attribute("id")) for i in all_in[:15]])
            except Exception:
                pass
            raise RuntimeError("E-mail/gebruikersnaam veld op de Easy4U loginpagina niet gevonden. Controleer de URL en of de pagina geladen is.")

        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", email_input)
        time.sleep(0.3)
        email_input.click()
        email_input.clear()
        email_input.send_keys(easy4u_email)

        password_input = _find_password_input(driver)
        if not password_input:
            raise RuntimeError("Wachtwoordveld op de Easy4U loginpagina niet gevonden.")

        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", password_input)
        time.sleep(0.3)
        password_input.click()
        password_input.clear()
        password_input.send_keys(easy4u_password)

        submit = _find_submit_or_login_button(driver)
        if not submit:
            # Laatste poging: Enter in wachtwoordveld
            password_input.send_keys(Keys.RETURN)
            time.sleep(2)
        elif submit[0] == "click":
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", submit[1])
            time.sleep(0.2)
            try:
                submit[1].click()
            except Exception:
                driver.execute_script("arguments[0].click();", submit[1])
            time.sleep(2)
        else:
            try:
                driver.execute_script("arguments[0].submit();", submit[1])
            except Exception:
                password_input.send_keys(Keys.RETURN)
            time.sleep(2)

        try:
            WebDriverWait(driver, 25).until(
                lambda d: "my.easy4u.be" in d.current_url and "/login" not in d.current_url
            )
            print("Succesvol ingelogd op Easy4U.")
        except Exception:
            print("Login uitgevoerd. Controleer of je bent ingelogd.")

        print("Browser blijft open. Sluit dit venster om af te sluiten.")
        while True:
            time.sleep(3600)

    finally:
        pass


if __name__ == "__main__":
    login_easy4u()
