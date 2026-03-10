import time
import sys
from pathlib import Path

from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
    value = get_credential(service, field, DATA_DIR, CREDENTIALS_FILE)
    if not value or value.strip() == "":
        raise RuntimeError(
            f"Credentials ontbreken: {field} voor {service} is niet ingevuld.\n"
            "Ga naar de web interface (http://127.0.0.1:5000/credentials) om je credentials in te stellen."
        )
    return value


def _google_bot_warning_detected(driver) -> bool:
    try:
        page = (driver.page_source or "").lower()
    except Exception:
        page = ""
    indicators = ["unusual traffic", "ongebruikelijk verkeer", "ik ben geen robot", "recaptcha", "verify you are human"]
    return any(token in page for token in indicators)


def login_google_admin() -> None:
    load_dotenv()

    admin_url = get_credential_or_fail("google_admin", "url") or "https://admin.google.com"
    google_email = get_credential_or_fail("google_admin", "email")
    google_password = get_credential_or_fail("google_admin", "password")

    driver = open_url_for_service("google_admin", admin_url, new_tab=True, account_id=google_email)

    try:
        wait = WebDriverWait(driver, 30)
        clear_microsoft_site_data(driver)
        driver.get(admin_url)
        time.sleep(1)

        if _google_bot_warning_detected(driver):
            print("Google bot/captcha waarschuwing gedetecteerd. Rond verificatie handmatig af in deze tab.")
            return

        current_url = driver.current_url

        if "accounts.google.com" in current_url or "google.com" in current_url:
            email_input = None
            for by, selector in [
                (By.ID, "identifierId"),
                (By.NAME, "identifier"),
                (By.XPATH, "//input[@type='email']"),
            ]:
                try:
                    email_input = wait.until(EC.presence_of_element_located((by, selector)))
                    break
                except Exception:
                    continue

            if email_input:
                clear_and_human_type(email_input, google_email)
                next_btn = wait.until(EC.element_to_be_clickable((By.ID, "identifierNext")))
                next_btn.click()
                time.sleep(1)
                current_url = driver.current_url

        if "microsoftonline.com" in current_url or "login.microsoftonline.com" in current_url or "microsoft.com" in current_url:
            if not get_microsoft_email_input(driver, timeout=0.8):
                prepare_microsoft_login_for_email(driver, google_email, timeout=20, start_url=None)

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
                raise RuntimeError("Kon het Microsoft e-mail veld niet vinden.")

            if (email_input.get_attribute("value") or "").strip() == "":
                clear_and_human_type(email_input, google_email)

            next_btn = wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
            next_btn.click()

            password_input = wait.until(EC.element_to_be_clickable((By.NAME, "passwd")))
            clear_and_human_type(password_input, google_password)

            signin_btn = wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
            signin_btn.click()

            try:
                no_btn = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.ID, "idBtn_Back")))
                no_btn.click()
            except Exception:
                pass

            try:
                WebDriverWait(driver, 60).until(
                    lambda d: "admin.google.com" in d.current_url or "google.com" in d.current_url
                )
            except Exception:
                pass

        print("Google Admin login uitgevoerd in gedeelde browser-sessie (tab blijft open).")
        print("Als er 2FA vereist is, vul die nu handmatig in.")

    finally:
        pass


if __name__ == "__main__":
    login_google_admin()