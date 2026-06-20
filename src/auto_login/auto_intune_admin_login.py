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
from src.core.security_utils import canonical_service_url
from src.auto_login.browser_session import open_url_for_service
from src.auto_login.input_utils import clear_and_type_verified
from src.auto_login.microsoft_account_switch import get_microsoft_email_input, prepare_microsoft_login_for_email
from src.auto_login.microsoft_site_data import clear_microsoft_site_data

DATA_DIR = get_data_dir()
CREDENTIALS_FILE = DATA_DIR / "credentials.json"


def get_credential_or_fail(service: str, field: str) -> str:
    value = get_credential(service, field, DATA_DIR, CREDENTIALS_FILE)
    if not value or value.strip() == "":
        raise RuntimeError(
            f"Credentials ontbreken: {field} voor {service} is niet ingevuld.\n"
            "Ga naar de web interface (http://127.0.0.1:5000/credentials) om je credentials in te stellen."
        )
    return value


def login_intune_admin() -> None:
    load_dotenv()

    admin_url = canonical_service_url("intune_admin")
    admin_email = get_credential_or_fail("intune_admin", "email")
    admin_password = get_credential_or_fail("intune_admin", "password")

    driver = open_url_for_service("intune_admin", admin_url, new_tab=True, account_id=admin_email)

    try:
        wait = WebDriverWait(driver, 30)
        driver.get(admin_url)

        fast_email_input = get_microsoft_email_input(driver, timeout=1.0)
        if not fast_email_input:
            clear_microsoft_site_data(driver)
            driver.get(admin_url)
            try:
                prepare_microsoft_login_for_email(driver, admin_email, timeout=20, start_url=admin_url)
            except TimeoutException:
                if "intune.microsoft.com" in driver.current_url and "permission" not in (driver.page_source or "").lower():
                    print("Intune Admin lijkt al ingelogd met actief account.")
                    return

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
        if (email_input.get_attribute("value") or "").strip() == "":
            clear_and_type_verified(driver, email_input, admin_email)

        next_btn = wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
        next_btn.click()

        password_input = wait.until(EC.element_to_be_clickable((By.NAME, "passwd")))
        clear_and_type_verified(driver, password_input, admin_password)

        signin_btn = wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
        signin_btn.click()

        try:
            no_btn = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.ID, "idBtn_Back")))
            no_btn.click()
        except Exception:
            pass

        try:
            WebDriverWait(driver, 60).until(
                lambda d: "intune.microsoft.com" in d.current_url or "microsoft.com" in d.current_url
            )
        except Exception:
            pass

        try:
            if "intune.microsoft.com" not in driver.current_url:
                driver.get(admin_url)
        except Exception:
            pass

        print("Intune Admin login uitgevoerd in een herbruikbare incognito browser-sessie.")
        print("Als er 2FA vereist is, vul die nu handmatig in.")
    finally:
        pass


if __name__ == "__main__":
    login_intune_admin()
