import logging
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
from src.auto_login.browser_session import open_url_for_service
from src.auto_login.input_utils import clear_and_type_verified
from src.auto_login.microsoft_account_switch import get_microsoft_email_input, prepare_microsoft_login_for_email
from src.auto_login.microsoft_site_data import clear_microsoft_site_data

DATA_DIR = get_data_dir()
CREDENTIALS_FILE = DATA_DIR / "credentials.json"
GOOGLE_ADMIN_URL = "https://admin.google.com"

logger = logging.getLogger(__name__)


def _log_flow(event: str, detail: str = "") -> None:
    message = f"{event} {detail}".strip()
    logger.info(message)
    print(message)


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


def _manual_intervention_detected(driver) -> bool:
    try:
        page = (driver.page_source or "").lower()
        url = (driver.current_url or "").lower()
    except Exception:
        page, url = "", ""

    indicators = [
        "captcha",
        "recaptcha",
        "unusual traffic",
        "ongebruikelijk verkeer",
        "ik ben geen robot",
        "verify you are human",
        "verify it's you",
        "help us protect your account",
        "approve sign in request",
        "enter code",
        "security code",
        "authenticator app",
        "multi-factor authentication",
        "two-step verification",
        "2-step verification",
        "mfa",
    ]
    return any(token in page or token in url for token in indicators)


def _wait_for_flow(driver, timeout: int = 30) -> str:
    def _detect(_driver):
        current_url = (_driver.current_url or "").lower()
        if "admin.google.com" in current_url:
            return "authenticated"
        if "accounts.google.com" in current_url:
            return "google"
        if "login.microsoftonline.com" in current_url:
            return "microsoft"
        if _manual_intervention_detected(_driver):
            return "manual"
        return False

    try:
        return WebDriverWait(driver, timeout).until(_detect)
    except TimeoutException:
        if _manual_intervention_detected(driver):
            return "manual"
        return "unknown"


def _find_first_present(wait: WebDriverWait, selectors):
    last_error = None
    for by, selector in selectors:
        try:
            return wait.until(EC.presence_of_element_located((by, selector)))
        except Exception as exc:
            last_error = exc
    if last_error:
        raise last_error
    raise TimeoutException("Geen selector opgegeven.")


def _find_first_clickable(driver, selectors, *, timeout: int = 30):
    last_error = None
    for by, selector in selectors:
        try:
            return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, selector)))
        except Exception as exc:
            last_error = exc
    if last_error:
        raise last_error
    raise TimeoutException("Geen selector opgegeven.")


def _click_google_next(driver, selectors, *, event: str, timeout: int = 30) -> None:
    button = _find_first_clickable(driver, selectors, timeout=timeout)
    try:
        button.click()
    except Exception:
        driver.execute_script("arguments[0].click();", button)
    _log_flow(event)


def _has_google_password_input(driver) -> bool:
    selectors = [
        (By.CSS_SELECTOR, 'input[type="password"]'),
        (By.NAME, "Passwd"),
        (By.CSS_SELECTOR, 'input[autocomplete="current-password"]'),
    ]
    for by, selector in selectors:
        try:
            elements = driver.find_elements(by, selector)
            if any(el.is_displayed() and el.is_enabled() for el in elements):
                return True
        except Exception:
            continue
    return False


def _run_google_flow(driver, wait: WebDriverWait, email: str, password: str) -> str:
    _log_flow("FLOW_GOOGLE")
    if "accounts.google.com" not in (driver.current_url or "").lower():
        return _wait_for_flow(driver, timeout=10)

    try:
        email_input = _find_first_clickable(
            driver,
            [
                (By.CSS_SELECTOR, 'input[type="email"]'),
                (By.CSS_SELECTOR, "input#identifierId"),
                (By.CSS_SELECTOR, 'input[name="identifier"]'),
                (By.CSS_SELECTOR, 'input[autocomplete="username"]'),
            ],
            timeout=30,
        )
    except TimeoutException:
        return "manual" if _manual_intervention_detected(driver) else "pending"

    _log_flow("GOOGLE_EMAIL_FIELD_FOUND")
    clear_and_type_verified(driver, email_input, email)
    _log_flow("GOOGLE_EMAIL_FILLED")

    try:
        _click_google_next(
            driver,
            [
                (By.CSS_SELECTOR, "#identifierNext button"),
                (By.CSS_SELECTOR, "div#identifierNext"),
                (By.XPATH, "//button[.//span[normalize-space()='Next'] or normalize-space()='Next']"),
                (By.XPATH, "//span[text()='Next']/ancestor::button"),
            ],
            event="GOOGLE_IDENTIFIER_NEXT_CLICKED",
            timeout=30,
        )
    except TimeoutException:
        return "manual" if _manual_intervention_detected(driver) else "pending"

    try:
        next_step = WebDriverWait(driver, 30).until(
            lambda d: (
                "authenticated"
                if "admin.google.com" in (d.current_url or "").lower()
                else "microsoft"
                if "login.microsoftonline.com" in (d.current_url or "").lower()
                else "manual"
                if _manual_intervention_detected(d)
                else "password"
                if _has_google_password_input(d)
                else False
            )
        )
    except TimeoutException:
        return "manual" if _manual_intervention_detected(driver) else "pending"

    if next_step != "password":
        return next_step

    try:
        password_input = _find_first_clickable(
            driver,
            [
                (By.CSS_SELECTOR, 'input[type="password"]'),
                (By.CSS_SELECTOR, 'input[name="Passwd"]'),
                (By.CSS_SELECTOR, 'input[autocomplete="current-password"]'),
            ],
            timeout=30,
        )
    except TimeoutException:
        return "manual" if _manual_intervention_detected(driver) else "pending"

    _log_flow("GOOGLE_PASSWORD_FIELD_FOUND")
    clear_and_type_verified(driver, password_input, password)
    _log_flow("GOOGLE_PASSWORD_FILLED")

    try:
        _click_google_next(
            driver,
            [
                (By.CSS_SELECTOR, "#passwordNext button"),
                (By.CSS_SELECTOR, "div#passwordNext"),
                (By.XPATH, "//span[text()='Next']/ancestor::button"),
            ],
            event="GOOGLE_PASSWORD_NEXT_CLICKED",
            timeout=30,
        )
    except TimeoutException:
        return "manual" if _manual_intervention_detected(driver) else "pending"

    try:
        return WebDriverWait(driver, 60).until(
            lambda d: (
                "authenticated"
                if "admin.google.com" in (d.current_url or "").lower()
                else "microsoft"
                if "login.microsoftonline.com" in (d.current_url or "").lower()
                else "manual"
                if _manual_intervention_detected(d)
                else False
            )
        )
    except TimeoutException:
        return "manual" if _manual_intervention_detected(driver) else "pending"


def _run_microsoft_flow(driver, wait: WebDriverWait, email: str, password: str) -> None:
    _log_flow("FLOW_MICROSOFT")
    clear_microsoft_site_data(driver)
    driver.get(driver.current_url)

    if not get_microsoft_email_input(driver, timeout=2):
        prepare_microsoft_login_for_email(driver, email, timeout=20, start_url=None)

    email_input = _find_first_present(
        wait,
        [
            (By.NAME, "loginfmt"),
            (By.ID, "i0116"),
            (By.CSS_SELECTOR, "input[type='email']"),
        ],
    )

    if (email_input.get_attribute("value") or "").strip() == "":
        clear_and_type_verified(driver, email_input, email)

    next_btn = wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
    next_btn.click()

    try:
        password_input = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.NAME, "passwd")))
    except TimeoutException:
        if _manual_intervention_detected(driver):
            _log_flow("FLOW_MANUAL_INTERVENTION", "Microsoft wacht op gebruikersactie.")
            return
        raise

    clear_and_type_verified(driver, password_input, password)

    signin_btn = wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
    signin_btn.click()

    try:
        no_btn = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.ID, "idBtn_Back")))
        no_btn.click()
    except Exception:
        pass

    try:
        WebDriverWait(driver, 60).until(
            lambda d: "admin.google.com" in (d.current_url or "").lower() or _manual_intervention_detected(d)
        )
    except TimeoutException:
        pass


def login_google_admin() -> None:
    load_dotenv()

    admin_url = GOOGLE_ADMIN_URL
    google_email = get_credential_or_fail("google_admin", "email")
    google_password = get_credential_or_fail("google_admin", "password")

    driver = open_url_for_service("google_admin", admin_url, new_tab=True, account_id=google_email)

    try:
        wait = WebDriverWait(driver, 30)
        driver.get(admin_url)

        flow = _wait_for_flow(driver, timeout=30)

        if flow == "manual" or _google_bot_warning_detected(driver):
            _log_flow("FLOW_MANUAL_INTERVENTION", "Google vraagt om captcha/verificatie.")
            print("Google bot/captcha waarschuwing gedetecteerd. Rond verificatie handmatig af in deze tab.")
            return

        if flow == "authenticated":
            _log_flow("FLOW_ALREADY_AUTHENTICATED")
            print("Google Admin lijkt al ingelogd.")
            return

        if flow == "google":
            google_result = _run_google_flow(driver, wait, google_email, google_password)
            if google_result == "authenticated" or "admin.google.com" in (driver.current_url or "").lower():
                _log_flow("FLOW_ALREADY_AUTHENTICATED")
                print("Google Admin login uitgevoerd in een herbruikbare incognito browser-sessie.")
                return
            if _manual_intervention_detected(driver) or google_result in {"manual", "pending"}:
                _log_flow("FLOW_MANUAL_INTERVENTION", "Google login wacht op gebruikersactie.")
                print("Google Admin wacht op handmatige verificatie in deze tab.")
                return
            flow = google_result if google_result == "microsoft" else _wait_for_flow(driver, timeout=20)

        if flow == "microsoft":
            _run_microsoft_flow(driver, wait, google_email, google_password)
            if _manual_intervention_detected(driver):
                _log_flow("FLOW_MANUAL_INTERVENTION", "Microsoft SSO wacht op gebruikersactie.")
                print("Google Admin via Microsoft SSO wacht op handmatige verificatie in deze tab.")
                return
            if "admin.google.com" in (driver.current_url or "").lower():
                _log_flow("FLOW_ALREADY_AUTHENTICATED")

        elif flow == "unknown":
            _log_flow("FLOW_MANUAL_INTERVENTION", f"Onbekende flow: {driver.current_url}")
            print("Google Admin login wacht op handmatige actie in deze tab.")
            return

        print("Google Admin login uitgevoerd in een herbruikbare incognito browser-sessie.")
        print("Als er 2FA vereist is, vul die nu handmatig in.")

    finally:
        pass


if __name__ == "__main__":
    login_google_admin()
