import os
from pathlib import Path

from dotenv import load_dotenv
from selenium.common.exceptions import TimeoutException
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
from src.auto_login.browser_session import open_url_for_service
from src.auto_login.input_utils import clear_and_human_type
from src.auto_login.microsoft_account_switch import get_microsoft_email_input, prepare_microsoft_login_for_email
from src.auto_login.microsoft_site_data import clear_microsoft_site_data

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

    driver = open_url_for_service("microsoft_admin", admin_url, new_tab=True, account_id=ms_email)

    try:
        wait = WebDriverWait(driver, 30)
        driver.get(admin_url)

        # Fast path: als Microsoft loginveld al klaarstaat, meteen typen.
        fast_email_input = get_microsoft_email_input(driver, timeout=1.0)
        if not fast_email_input:
            # Alleen als we niet meteen kunnen typen, doen we de zwaardere cleanup/account-switch.
            clear_microsoft_site_data(driver)
            driver.get(admin_url)
            try:
                prepare_microsoft_login_for_email(driver, ms_email, timeout=20, start_url=admin_url)
            except TimeoutException:
                # Als er geen loginveld verschijnt, kunnen we al in admin zitten met juiste account.
                if "admin.microsoft.com" in driver.current_url and "permission" not in (driver.page_source or "").lower():
                    print("Microsoft Admin lijkt al ingelogd met actief account.")
                    return

        # 2. Microsoft login: e‑mail invullen
        # Sneller: wacht enkel tot het veld aanwezig is (klikbaar kan later worden).
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
            raise RuntimeError("Kon Microsoft e-mail veld niet vinden (loginfmt/i0116).")
        # Als fast path al getypt heeft, laten we de value staan.
        if (email_input.get_attribute("value") or "").strip() == "":
            clear_and_human_type(email_input, ms_email)

        next_btn = wait.until(
            EC.element_to_be_clickable((By.ID, "idSIButton9"))
        )
        next_btn.click()

        # 3. Wacht op wachtwoordveld
        password_input = wait.until(
            EC.element_to_be_clickable((By.NAME, "passwd"))
        )
        clear_and_human_type(password_input, ms_password)

        signin_btn = wait.until(
            EC.element_to_be_clickable((By.ID, "idSIButton9"))
        )
        signin_btn.click()

        # 4. Eventueel 'Blijf aangemeld?' altijd op "Nee" zetten
        try:
            no_btn = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.ID, "idBtn_Back"))
            )
            no_btn.click()
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

        # Navigeer na succesvolle auth naar de admin portal.
        # Dit voorkomt dat we blijven hangen op login.microsoftonline.com.
        try:
            if "admin.microsoft.com" not in driver.current_url:
                driver.get(admin_url)
        except Exception:
            pass

        print("Microsoft Admin login uitgevoerd in gedeelde browser-sessie (tab blijft open).")
        print("Als er 2FA vereist is, vul die nu handmatig in.")

    finally:
        # Laat de browser open staan zodat je ingelogd blijft.
        # Comment de volgende regel uit als je de browser automatisch wilt sluiten:
        # driver.quit()
        pass


if __name__ == "__main__":
    login_microsoft_admin()
