"""
Helpers om Microsoft login account-keuze te forceren in gedeelde browser-sessies.
"""
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def _click_first_clickable(driver, selectors, timeout=4) -> bool:
    for by, selector in selectors:
        try:
            el = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, selector)))
            el.click()
            return True
        except Exception:
            # JS fallback voor overlays/rare state
            try:
                el = _find_visible(driver, [(by, selector)])
                if el:
                    driver.execute_script("arguments[0].click();", el)
                    return True
            except Exception:
                pass
            continue
    return False


def _find_visible(driver, selectors):
    for by, selector in selectors:
        try:
            elements = driver.find_elements(by, selector)
            for el in elements:
                if el.is_displayed() and el.is_enabled():
                    return el
        except Exception:
            continue
    return None


def get_microsoft_email_input(driver, timeout: float = 1.2):
    """
    Snelle check of Microsoft e-mailveld al beschikbaar is.
    Retourneert element of None.
    """
    deadline = time.time() + max(0.2, float(timeout))
    selectors = [
        (By.NAME, "loginfmt"),
        (By.ID, "i0116"),
        (By.CSS_SELECTOR, "input[type='email']"),
    ]
    while time.time() < deadline:
        el = _find_visible(driver, selectors)
        if el:
            return el
        time.sleep(0.1)
    return None


def prepare_microsoft_login_for_email(driver, desired_email: str, timeout: int = 30, start_url: str | None = None) -> None:
    """
    Zorg dat loginflow niet stil een eerder account hergebruikt.
    - Klik indien aanwezig op "Sign out & switch"
    - Kies "Use another account" op account-picker
    """
    deadline = time.time() + timeout
    poll = 0.25  # sneller respons zonder "bot-instant" te zijn
    login_input_selectors = [
        (By.NAME, "loginfmt"),
        (By.ID, "i0116"),
        (By.CSS_SELECTOR, "input[type='email']"),
    ]

    while time.time() < deadline:
        # Als we op een logout bevestigingspagina zitten, terug naar start.
        try:
            url = (driver.current_url or "").lower()
            page = (driver.page_source or "").lower()
        except Exception:
            url, page = "", ""

        if start_url and ("logout" in url or "signed out of your account" in page):
            try:
                driver.get(start_url)
            except Exception:
                pass
            time.sleep(0.3)

        # Als loginveld beschikbaar is, zijn we klaar.
        if _find_visible(driver, login_input_selectors):
            return

        # 1) Als we op een pagina zitten met "Sign out & switch", forceer die.
        # Alleen doen als we een start_url hebben om terug naartoe te gaan.
        if start_url:
            did_signout = _click_first_clickable(
                driver,
                [
                    (By.XPATH, "//*[normalize-space()='Sign out & switch']"),
                    (By.XPATH, "//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'sign out & switch')]"),
                    (By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'sign out & switch')]"),
                    (By.XPATH, "//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'afmelden') and contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'wissel')]"),
                    (By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'afmelden') and contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'wissel')]"),
                ],
                timeout=1,
            )
            if did_signout:
                time.sleep(0.3)
                try:
                    driver.get(start_url)
                except Exception:
                    pass
                time.sleep(0.3)

        # 2) Op account picker: kies expliciet "Use another account".
        _click_first_clickable(
            driver,
            [
                (By.XPATH, "//*[contains(normalize-space(),'Use another account')]"),
                (By.XPATH, "//div[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'use another account')]"),
                (By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'use another account')]"),
                (By.XPATH, "//div[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'ander account')]"),
                (By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'ander account')]"),
            ],
            timeout=1,
        )

        # 3) Soms toont MS een tegel met reeds gekende accounts; klik desnoods gewenste mail.
        if desired_email:
            _click_first_clickable(
                driver,
                [
                    (
                        By.XPATH,
                        f"//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{desired_email.lower()}')]",
                    ),
                ],
                timeout=1,
            )

        time.sleep(poll)

    raise TimeoutException("Microsoft loginveld (loginfmt) niet bereikt na account-switch.")
