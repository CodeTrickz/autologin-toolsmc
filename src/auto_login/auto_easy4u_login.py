"""
Automatische login voor Easy4U Nederland admin (easy4u.nl).
Gebruikt Selenium + Chrome (binnen en buiten de .exe).
Credentials komen uit de app (Credentials > Easy4U).
"""
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
SCRIPTS_DIR = Path(__file__).parent.parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from src.core.credentials_manager import get_credential, get_data_dir

DATA_DIR = get_data_dir()
CREDENTIALS_FILE = DATA_DIR / "credentials.json"

LOGIN_URL = "https://easy4u.nl/admin/login?referrer=%2Fadmin%2F"


def get_credential_or_fail(service: str, field: str) -> str:
    """Haal credential op uit encrypted storage."""
    value = get_credential(service, field, DATA_DIR, CREDENTIALS_FILE)
    if not value or value.strip() == "":
        raise RuntimeError(
            f"Credentials ontbreken: {field} voor {service} is niet ingevuld.\n"
            "Ga naar de web interface of desktop app om je credentials in te stellen."
        )
    return value


def _login_selenium_chrome() -> None:
    """
    Easy4U login met Selenium + Chrome.
    Werkt zowel in de .exe als wanneer je het script in Python draait.
    """
    from dotenv import load_dotenv

    env_path = DATA_DIR / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()

    email = get_credential_or_fail("easy4u", "email")
    password = get_credential_or_fail("easy4u", "password")

    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    driver = None
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        driver = webdriver.Chrome(options=options, service=ChromeService())
        wait = WebDriverWait(driver, 20)

        driver.get(LOGIN_URL)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input:not([type='password']):not([type='submit']):not([type='hidden'])")))

        email_input = driver.find_element(
            By.CSS_SELECTOR,
            "input:not([type='password']):not([type='submit']):not([type='hidden'])",
        )
        email_input.clear()
        email_input.send_keys(email)

        pwd_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        pwd_input.clear()
        pwd_input.send_keys(password)

        try:
            login_btn = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
        except Exception:
            login_btn = driver.find_element(
                By.XPATH,
                "//button[contains(translate(., 'INLOGGEN', 'inloggen'), 'inloggen')]",
            )
        login_btn.click()

        WebDriverWait(driver, 15).until(
            lambda d: "/login" not in d.current_url or "admin" in d.current_url
        )
        url = driver.current_url
        if "/admin" in url and "/login" not in url:
            pass
        else:
            try:
                err = driver.find_element(By.CSS_SELECTOR, "[class*='error'], .alert-danger, #errorsDiv")
                if err.is_displayed():
                    print("Login mislukt:", err.text)
            except Exception:
                print("Pagina na login:", url)

        if sys.stdin.isatty() and not getattr(sys, "frozen", False):
            input("Druk op Enter om de browser te sluiten...")
    finally:
        if driver:
            driver.quit()


def login_easy4u() -> None:
    """
    Log automatisch in op Easy4U: https://easy4u.nl/admin/
    Gebruikt Selenium + Chrome. Credentials uit de app (Credentials > Easy4U).
    """
    try:
        _login_selenium_chrome()
    except RuntimeError:
        raise
    except Exception as e:
        print("Fout bij Easy4U login:", e)
        raise


if __name__ == "__main__":
    login_easy4u()
