import os
import time
from pathlib import Path

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from credentials_manager import get_credential, get_data_dir

DATA_DIR = get_data_dir()
CREDENTIALS_FILE = DATA_DIR / "credentials.json"


def get_credential_or_fail(service: str, field: str) -> str:
    """Haal credential op uit encrypted storage (gebruikt persistente datamap bij .exe)."""
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


def login_microsoft_admin() -> None:
    """
    Log automatisch in op Microsoft 365 Admin Center.

    Config in .env:
    MS_ADMIN_URL=https://admin.microsoft.com (of andere URL)
    MS_ADMIN_EMAIL=jouw.admin@example.com
    MS_ADMIN_PASSWORD=JOUW_WACHTWOORD
    """
    load_dotenv()

    admin_url = get_credential_or_fail("microsoft_admin", "url") or "https://admin.microsoft.com"
    ms_email = get_credential_or_fail("microsoft_admin", "email")
    ms_password = get_credential_or_fail("microsoft_admin", "password")

    driver = create_driver()

    try:
        wait = WebDriverWait(driver, 30)

        # 1. Ga naar Microsoft Admin Center (of andere URL uit .env)
        driver.get(admin_url)

        # 2. Microsoft login: e‑mail invullen
        # Wacht tot het veld echt klikbaar is (niet alleen "aanwezig") om InvalidElementState te vermijden
        email_input = wait.until(
            EC.element_to_be_clickable((By.NAME, "loginfmt"))
        )
        email_input.send_keys(ms_email)

        next_btn = wait.until(
            EC.element_to_be_clickable((By.ID, "idSIButton9"))
        )
        next_btn.click()

        # 3. Wacht op wachtwoordveld
        password_input = wait.until(
            EC.element_to_be_clickable((By.NAME, "passwd"))
        )
        password_input.send_keys(ms_password)

        signin_btn = wait.until(
            EC.element_to_be_clickable((By.ID, "idSIButton9"))
        )
        signin_btn.click()

        # 4. Eventueel 'Blijf aangemeld?' bevestigen
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

        # 5. Wacht tot je op admin.microsoft.com bent (of 2FA-scherm)
        try:
            WebDriverWait(driver, 60).until(
                lambda d: "admin.microsoft.com" in d.current_url or "microsoft.com" in d.current_url
            )
        except Exception:
            # Ook als we de URL niet goed kunnen detecteren, de browser blijft toch open
            pass

        # 6. Houd het script actief zodat de browser niet automatisch wordt gesloten.
        print("Microsoft Admin login voltooid. Browser blijft open; sluit dit venster of stop het script om ook de browser te sluiten.")
        print("Als er 2FA vereist is, vul die nu handmatig in.")
        while True:
            time.sleep(3600)

    finally:
        # Laat de browser open staan zodat je ingelogd blijft.
        # Comment de volgende regel uit als je de browser automatisch wilt sluiten:
        # driver.quit()
        pass


if __name__ == "__main__":
    login_microsoft_admin()
