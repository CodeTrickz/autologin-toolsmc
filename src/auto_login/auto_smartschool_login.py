import os
import time
from pathlib import Path

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
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


def create_driver() -> webdriver.Chrome:
    # Gebruikt de ingebouwde Selenium manager om automatisch Chromedriver te vinden/downloaden
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    # Comment de volgende regel uit als je de browser niet zichtbaar wilt:
    # options.add_argument("--headless=new")

    driver = webdriver.Chrome(options=options, service=ChromeService())
    return driver


def login_smartschool_via_microsoft() -> None:
    load_dotenv()

    ms_email = get_credential_or_fail("smartschool", "email")
    ms_password = get_credential_or_fail("smartschool", "password")

    driver = create_driver()

    try:
        wait = WebDriverWait(driver, 30)

        # 1. Ga naar Smartschool loginpagina
        driver.get(SMARTSCHOOL_URL)

        # 2. Klik op "Microsoft" login knop
        # Probeer verschillende selectors (kan afhankelijk zijn van de HTML)
        microsoft_button = None
        selector_attempts = [
            (By.XPATH, "//a[contains(., 'Microsoft')]"),
            (By.XPATH, "//button[contains(., 'Microsoft')]"),
            (By.XPATH, "//*[contains(., 'Microsoft') and (self::a or self::button)]"),
        ]

        for by, selector in selector_attempts:
            try:
                microsoft_button = wait.until(
                    EC.element_to_be_clickable((by, selector))
                )
                break
            except Exception:
                continue

        if not microsoft_button:
            raise RuntimeError(
                "Kon de Microsoft-aanmeldknop op Smartschool niet vinden."
            )

        microsoft_button.click()

        # 3. Microsoft login: e‑mail invullen
        # Wacht tot het veld echt klikbaar is (niet alleen "aanwezig") om InvalidElementState te vermijden
        email_input = wait.until(
            EC.element_to_be_clickable((By.NAME, "loginfmt"))
        )
        email_input.send_keys(ms_email)

        next_btn = wait.until(
            EC.element_to_be_clickable((By.ID, "idSIButton9"))
        )
        next_btn.click()

        # 4. Wacht op wachtwoordveld
        password_input = wait.until(
            EC.element_to_be_clickable((By.NAME, "passwd"))
        )
        password_input.send_keys(ms_password)

        signin_btn = wait.until(
            EC.element_to_be_clickable((By.ID, "idSIButton9"))
        )
        signin_btn.click()

        # 5. Eventueel 'Blijf aangemeld?' bevestigen (dit mag nog automatisch)
        try:
            stay_signed_in_btn = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.ID, "idBtn_Back"))
            )
            # Probeer eerst "Ja" (idSIButton9); als dat niet lukt, klik "Nee" (idBtn_Back)
            try:
                yes_btn = driver.find_element(By.ID, "idSIButton9")
                if yes_btn.is_displayed() and yes_btn.is_enabled():
                    yes_btn.click()
                else:
                    stay_signed_in_btn.click()
            except Exception:
                stay_signed_in_btn.click()
        except Exception:
            # Geen 'Blijf aangemeld?'-scherm, ga verder
            pass

        # 6. Wacht tot je terug op Smartschool zit (2FA-scherm)
        try:
            WebDriverWait(driver, 60).until(
                EC.url_contains("smartschool.be")
            )
        except Exception:
            # Ook als we de URL niet goed kunnen detecteren, de browser blijft toch open
            pass

        # 7. Houd het script actief zodat de browser niet automatisch wordt gesloten.
        print("Smartschool/Microsoft login voltooid. Browser blijft open; sluit dit venster of stop het script om ook de browser te sluiten.")
        while True:
            time.sleep(3600)

    finally:
        # Laat de browser open staan zodat je ingelogd blijft.
        # Comment de volgende regel uit als je de browser automatisch wilt sluiten:
        # driver.quit()
        pass


if __name__ == "__main__":
    login_smartschool_via_microsoft()

