import os
import time
from pathlib import Path

from dotenv import load_dotenv
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


def _google_bot_warning_detected(driver) -> bool:
    """Detecteer bekende Google bot/captcha waarschuwingen."""
    try:
        page = (driver.page_source or "").lower()
    except Exception:
        page = ""
    indicators = [
        "unusual traffic",
        "ongebruikelijk verkeer",
        "ik ben geen robot",
        "reCAPTCHA".lower(),
        "verify you are human",
    ]
    return any(token in page for token in indicators)


def login_google_admin() -> None:
    """
    Log automatisch in op Google Workspace Admin Console (admin.google.com).

    Config in .env:
    GOOGLE_ADMIN_URL=https://admin.google.com (of andere URL)
    GOOGLE_ADMIN_EMAIL=jouw.admin@example.com
    GOOGLE_ADMIN_PASSWORD=JOUW_WACHTWOORD
    """
    load_dotenv()

    admin_url = get_credential_or_fail("google_admin", "url") or "https://admin.google.com"
    google_email = get_credential_or_fail("google_admin", "email")
    google_password = get_credential_or_fail("google_admin", "password")

    driver = open_url_for_service("google_admin", admin_url, new_tab=True, account_id=google_email)

    try:
        wait = WebDriverWait(driver, 30)
        # Voorkom Microsoft SSO account-conflict met eerdere logins.
        clear_microsoft_site_data(driver)
        driver.get(admin_url)
        time.sleep(3)  # Wacht op pagina laden

        current_url = driver.current_url

        if _google_bot_warning_detected(driver):
            print("Google bot/captcha waarschuwing gedetecteerd. Rond verificatie handmatig af in deze tab.")
            return
        
        # 2. EERSTE PAGINA: Google login (accounts.google.com)
        if "accounts.google.com" in current_url or "google.com" in current_url:
            print("Google login pagina gedetecteerd. Vul e-mail in...")
            
            # Google login: e‑mail invullen
            email_input = None
            email_selectors = [
                (By.ID, "identifierId"),
                (By.NAME, "identifier"),
                (By.XPATH, "//input[@type='email']"),
                (By.XPATH, "//input[@name='Email']"),
                (By.XPATH, "//input[contains(@aria-label, 'email') or contains(@aria-label, 'Email')]"),
            ]
            
            for by, selector in email_selectors:
                try:
                    email_input = wait.until(EC.presence_of_element_located((by, selector)))
                    break
                except Exception:
                    continue
            
            if not email_input:
                raise RuntimeError("Kon het e-mail veld op de Google login pagina niet vinden.")
            
            email_input.click()
            time.sleep(0.5)
            clear_and_human_type(email_input, google_email)
            time.sleep(1)

            # Klik op "Next" knop (Google)
            next_btn = None
            next_selectors = [
                (By.ID, "identifierNext"),
                (By.XPATH, "//button[@id='identifierNext']"),
                (By.XPATH, "//button[.//span[contains(text(), 'Next')]]"),
                (By.XPATH, "//button[contains(., 'Next')]"),
            ]
            
            for by, selector in next_selectors:
                try:
                    next_btn = wait.until(EC.element_to_be_clickable((by, selector)))
                    break
                except Exception:
                    continue
            
            if not next_btn:
                raise RuntimeError("Kon de 'Next' knop op de Google login pagina niet vinden.")
            
            next_btn.click()
            time.sleep(3)  # Wacht op redirect naar Microsoft
            current_url = driver.current_url

        # 3. TWEEDE PAGINA: Microsoft login (microsoftonline.com)
        if "microsoftonline.com" in current_url or "login.microsoftonline.com" in current_url or "microsoft.com" in current_url:
            print("Microsoft login pagina gedetecteerd. Vul e-mail in...")
            if not get_microsoft_email_input(driver, timeout=0.8):
                prepare_microsoft_login_for_email(driver, google_email, timeout=20, start_url=None)
            
            # Microsoft login: e‑mail invullen (tweede pagina)
            # Probeer verschillende selectors voor het e-mail veld
            email_input = None
            email_selectors = [
                (By.NAME, "loginfmt"),
                (By.ID, "i0116"),
                (By.XPATH, "//input[@type='email']"),
                (By.XPATH, "//input[@name='loginfmt']"),
                (By.XPATH, "//input[contains(@placeholder, 'Email') or contains(@placeholder, 'email')]"),
            ]
            
            for by, selector in email_selectors:
                try:
                    email_input = wait.until(EC.element_to_be_clickable((by, selector)))
                    break
                except Exception:
                    continue
            
            if not email_input:
                raise RuntimeError("Kon het e-mail veld op de Microsoft login pagina niet vinden.")
            
            email_input.click()
            time.sleep(0.5)
            clear_and_human_type(email_input, google_email)
            time.sleep(1)

            # Klik op "Next" knop
            next_btn = None
            next_selectors = [
                (By.ID, "idSIButton9"),
                (By.XPATH, "//input[@type='submit' and @value='Next']"),
                (By.XPATH, "//button[contains(., 'Next')]"),
                (By.XPATH, "//input[@id='idSIButton9']"),
            ]
            
            for by, selector in next_selectors:
                try:
                    next_btn = wait.until(EC.element_to_be_clickable((by, selector)))
                    break
                except Exception:
                    continue
            
            if not next_btn:
                raise RuntimeError("Kon de 'Next' knop op de Microsoft login pagina niet vinden.")
            
            next_btn.click()
            time.sleep(3)  # Wacht op volgende pagina (kan wachtwoord of opnieuw e-mail zijn)

            # Check of er op de tweede pagina ook een e-mail veld is (soms vraagt Microsoft dit opnieuw)
            email_input_2 = None
            try:
                email_selectors_2 = [
                    (By.NAME, "loginfmt"),
                    (By.ID, "i0116"),
                    (By.XPATH, "//input[@type='email']"),
                    (By.XPATH, "//input[@name='loginfmt']"),
                    (By.XPATH, "//input[contains(@placeholder, 'Email') or contains(@placeholder, 'email')]"),
                ]
                
                for by, selector in email_selectors_2:
                    try:
                        email_input_2 = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((by, selector))
                        )
                        # Check of het veld leeg is of niet
                        if email_input_2.get_attribute("value") == "" or email_input_2.get_attribute("value") is None:
                            print("E-mail veld gevonden op tweede pagina, invullen...")
                            email_input_2.click()
                            time.sleep(0.5)
                            clear_and_human_type(email_input_2, google_email)
                            time.sleep(1)
                            
                            # Klik opnieuw op Next
                            next_btn_2 = None
                            next_selectors_2 = [
                                (By.ID, "idSIButton9"),
                                (By.XPATH, "//input[@type='submit' and @value='Next']"),
                                (By.XPATH, "//button[contains(., 'Next')]"),
                                (By.XPATH, "//input[@id='idSIButton9']"),
                            ]
                            
                            for by2, selector2 in next_selectors_2:
                                try:
                                    next_btn_2 = WebDriverWait(driver, 10).until(
                                        EC.element_to_be_clickable((by2, selector2))
                                    )
                                    break
                                except Exception:
                                    continue
                            
                            if next_btn_2:
                                next_btn_2.click()
                                time.sleep(2)  # Wacht op wachtwoordscherm
                        break
                    except Exception:
                        continue
            except Exception:
                # Geen tweede e-mail veld, ga verder naar wachtwoord
                pass

            # DERDE PAGINA: Wacht op wachtwoordveld
            print("Wacht op wachtwoord veld (derde pagina)...")
            password_input = None
            password_selectors = [
                (By.NAME, "passwd"),
                (By.ID, "i0118"),
                (By.XPATH, "//input[@type='password']"),
                (By.XPATH, "//input[@name='passwd']"),
                (By.XPATH, "//input[contains(@aria-label, 'Password') or contains(@aria-label, 'password')]"),
            ]
            
            for by, selector in password_selectors:
                try:
                    password_input = WebDriverWait(driver, 30).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    break
                except Exception:
                    continue
            
            if not password_input:
                raise RuntimeError("Kon het wachtwoord veld op de Microsoft login pagina niet vinden.")
            
            print("Vul wachtwoord in...")
            password_input.click()
            time.sleep(0.5)
            clear_and_human_type(password_input, google_password)
            time.sleep(1)

            # Klik op "Sign in" knop (derde pagina - wachtwoord)
            signin_btn = None
            signin_selectors = [
                (By.ID, "idSIButton9"),
                (By.XPATH, "//input[@type='submit' and @value='Sign in']"),
                (By.XPATH, "//button[contains(., 'Sign in')]"),
                (By.XPATH, "//input[@id='idSIButton9']"),
                (By.XPATH, "//button[@id='idSIButton9']"),
                (By.XPATH, "//input[@type='submit']"),
                (By.XPATH, "//button[.//text()='Sign in']"),
                (By.XPATH, "//button[contains(text(), 'Sign in')]"),
            ]
            
            for by, selector in signin_selectors:
                try:
                    signin_btn = WebDriverWait(driver, 30).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    break
                except Exception:
                    continue
            
            if not signin_btn:
                raise RuntimeError("Kon de 'Sign in' knop op de Microsoft login pagina niet vinden.")
            
            print("Klik op 'Sign in' knop...")
            signin_btn.click()
            time.sleep(3)  # Wacht op volgende stap (redirect of "Blijf aangemeld")

            # Eventueel 'Blijf aangemeld?' bevestigen
            try:
                no_btn = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.ID, "idBtn_Back"))
                )
                no_btn.click()
            except Exception:
                pass

            # Wacht op redirect terug naar Google Admin
            try:
                WebDriverWait(driver, 60).until(
                    lambda d: "admin.google.com" in d.current_url
                    or "google.com" in d.current_url
                )
                print("Terug geredirect naar Google Admin.")
            except Exception:
                pass

            print("Google Admin login (via Microsoft SAML/SSO) uitgevoerd in gedeelde browser-sessie (tab blijft open).")
            print("Als er 2FA vereist is, vul die nu handmatig in.")
            return

        # 2. Google login: e‑mail invullen (als er geen Microsoft redirect is)
        # Probeer verschillende selectors voor het e-mail veld
        email_input = None
        email_selectors = [
            (By.ID, "identifierId"),
            (By.NAME, "identifier"),
            (By.XPATH, "//input[@type='email']"),
            (By.XPATH, "//input[@name='Email']"),
            (By.XPATH, "//input[@aria-label*='email' or @aria-label*='Email' or @aria-label*='e-mail']"),
        ]

        for by, selector in email_selectors:
            try:
                email_input = wait.until(EC.presence_of_element_located((by, selector)))
                # Wacht extra tot het echt klikbaar is
                WebDriverWait(driver, 5).until(EC.element_to_be_clickable((by, selector)))
                email_input = driver.find_element(by, selector)
                break
            except Exception:
                continue

        if not email_input:
            raise RuntimeError("Kon het e-mail veld op de Google login pagina niet vinden.")

        # Klik eerst op het veld om focus te krijgen
        email_input.click()
        time.sleep(0.5)
        clear_and_human_type(email_input, google_email)
        time.sleep(1)  # Wacht even zodat Google de input kan verwerken

        # 3. Klik op "Volgende" na e-mail
        next_btn = None
        next_selectors = [
            (By.ID, "identifierNext"),
            (By.XPATH, "//button[@id='identifierNext']"),
            (By.XPATH, "//button[.//span[contains(text(), 'Volgende')]]"),
            (By.XPATH, "//button[.//span[contains(text(), 'Next')]]"),
            (By.XPATH, "//button[contains(., 'Volgende')]"),
            (By.XPATH, "//button[contains(., 'Next')]"),
            (By.XPATH, "//div[@id='identifierNext']"),
        ]

        for by, selector in next_selectors:
            try:
                next_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((by, selector))
                )
                break
            except Exception:
                continue

        if not next_btn:
            raise RuntimeError("Kon de 'Volgende' knop na e-mail niet vinden.")
        
        next_btn.click()
        time.sleep(2)  # Wacht op wachtwoordscherm

        # 4. Wacht op wachtwoordveld
        password_input = None
        password_selectors = [
            (By.NAME, "password"),
            (By.NAME, "Passwd"),
            (By.XPATH, "//input[@type='password']"),
            (By.XPATH, "//input[@name='Passwd']"),
            (By.ID, "password"),
            (By.XPATH, "//input[@aria-label*='password' or @aria-label*='Password' or @aria-label*='wachtwoord']"),
        ]

        for by, selector in password_selectors:
            try:
                password_input = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((by, selector))
                )
                # Wacht extra tot het echt klikbaar is
                WebDriverWait(driver, 5).until(EC.element_to_be_clickable((by, selector)))
                password_input = driver.find_element(by, selector)
                break
            except Exception:
                continue

        if not password_input:
            raise RuntimeError("Kon het wachtwoord veld niet vinden.")

        # Klik eerst op het veld om focus te krijgen
        password_input.click()
        time.sleep(0.5)
        clear_and_human_type(password_input, google_password)
        time.sleep(1)  # Wacht even zodat Google de input kan verwerken

        # 5. Klik op "Volgende" na wachtwoord
        password_next_btn = None
        password_next_selectors = [
            (By.ID, "passwordNext"),
            (By.XPATH, "//button[@id='passwordNext']"),
            (By.XPATH, "//button[.//span[contains(text(), 'Volgende')]]"),
            (By.XPATH, "//button[.//span[contains(text(), 'Next')]]"),
            (By.XPATH, "//button[contains(., 'Volgende')]"),
            (By.XPATH, "//button[contains(., 'Next')]"),
            (By.XPATH, "//div[@id='passwordNext']"),
        ]

        for by, selector in password_next_selectors:
            try:
                password_next_btn = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((by, selector))
                )
                break
            except Exception:
                continue

        if not password_next_btn:
            raise RuntimeError("Kon de 'Volgende' knop na wachtwoord niet vinden.")
        
        password_next_btn.click()
        time.sleep(2)  # Wacht op volgende stap (2FA of admin console)

        # 6. Wacht tot je op admin.google.com bent (of 2FA-scherm)
        try:
            WebDriverWait(driver, 60).until(
                lambda d: "admin.google.com" in d.current_url
                or "accounts.google.com" in d.current_url
                or "google.com" in d.current_url
            )
        except Exception:
            # Ook als we de URL niet goed kunnen detecteren, de browser blijft toch open
            pass

        print("Google Admin login uitgevoerd in gedeelde browser-sessie (tab blijft open).")
        print("Als er 2FA vereist is, vul die nu handmatig in.")

    finally:
        # Browser blijft bewust open voor sessiebehoud.
        pass


if __name__ == "__main__":
    login_google_admin()
