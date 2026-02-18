"""
Gedeeld browser-sessiebeheer voor alle Selenium auto-login scripts.

Doelen:
- Hergebruik 1 Chrome instance binnen dezelfde app-run.
- Open elke login in een nieuw tabblad i.p.v. een nieuw browservenster.
- Optionele incognito modus via AUTO_LOGIN_INCOGNITO=true.
"""
import os
import threading
from pathlib import Path
from uuid import uuid4
import hashlib

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.service import Service as ChromeService

from src.core.credentials_manager import get_data_dir
from src.auto_login import browser_cleanup  # noqa: F401  (registers atexit cleanup)

_DRIVER_LOCK = threading.Lock()
_SHARED_DRIVER = None


def _is_truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _parse_csv_set(value: str | None) -> set[str]:
    if not value:
        return set()
    parts = [p.strip() for p in str(value).split(",")]
    return {p for p in parts if p}


def _tabs_only_mode() -> bool:
    """
    Standaard tabs-only: geen aparte browser instances.
    Zet AUTO_LOGIN_ALLOW_SEPARATE_INSTANCES=true om dit expliciet toe te laten.
    """
    return not _is_truthy(os.environ.get("AUTO_LOGIN_ALLOW_SEPARATE_INSTANCES"))


def should_isolate_service(service: str) -> bool:
    """
    Bepaal of een service in een aparte Chrome instance moet openen.

    Env:
    - AUTO_LOGIN_ISOLATE_ALL=true
    - AUTO_LOGIN_ISOLATE_SERVICES="smartschool,google_admin,microsoft_admin,easy4u"
    """
    if _is_truthy(os.environ.get("AUTO_LOGIN_ISOLATE_ALL")):
        return True
    isolate = _parse_csv_set(os.environ.get("AUTO_LOGIN_ISOLATE_SERVICES"))
    return service in isolate


def _default_isolate_by_account_services() -> set[str]:
    # Services waar je vaak met meerdere accounts tegelijk werkt.
    return {"microsoft_admin", "google_admin", "smartschool", "smartschool_admin"}


def should_isolate_by_account(service: str) -> bool:
    """
    Open een service in een apart profiel per account/e-mail.

    Env:
    - AUTO_LOGIN_ISOLATE_BY_ACCOUNT_ALL=true
    - AUTO_LOGIN_ISOLATE_BY_ACCOUNT_SERVICES="microsoft_admin,google_admin,smartschool"
    - AUTO_LOGIN_DISABLE_ISOLATE_BY_ACCOUNT=true  (alles uit)
    """
    if _is_truthy(os.environ.get("AUTO_LOGIN_DISABLE_ISOLATE_BY_ACCOUNT")):
        return False
    if _is_truthy(os.environ.get("AUTO_LOGIN_ISOLATE_BY_ACCOUNT_ALL")):
        return True
    cfg = _parse_csv_set(os.environ.get("AUTO_LOGIN_ISOLATE_BY_ACCOUNT_SERVICES"))
    # Default: UIT. Alleen actief als expliciet ingesteld.
    return service in cfg


def _requires_account_isolation(service: str) -> bool:
    """
    Services die via Microsoft-accountcookies snel conflicteren tussen accounts.
    Voor deze services isoleren we standaard per account-id.
    """
    return service in {"smartschool", "smartschool_admin", "microsoft_admin", "google_admin"}


def incognito_for_service(service: str) -> bool:
    """
    Bepaal of een service incognito moet draaien (meestal enkel relevant bij isolated sessions).

    Env:
    - AUTO_LOGIN_INCOGNITO=true (globaal)
    - AUTO_LOGIN_INCOGNITO_SERVICES="smartschool,google_admin"
    """
    if _is_truthy(os.environ.get("AUTO_LOGIN_INCOGNITO")):
        return True
    incognito = _parse_csv_set(os.environ.get("AUTO_LOGIN_INCOGNITO_SERVICES"))
    return service in incognito

def _default_user_data_dir() -> Path:
    data_dir = Path(get_data_dir())
    default_profile_dir = data_dir / "chrome_user_data"
    default_profile_dir.mkdir(parents=True, exist_ok=True)
    return default_profile_dir


def _isolated_user_data_dir(*, incognito: bool) -> Path:
    # Aparte user-data-dir is nodig om meerdere Chrome processen tegelijk te kunnen draaien.
    data_dir = Path(get_data_dir())
    base = data_dir / "chrome_user_data_isolated" / ("incognito" if incognito else "profile")
    base.mkdir(parents=True, exist_ok=True)
    path = base / uuid4().hex
    path.mkdir(parents=True, exist_ok=True)
    return path


def _account_profile_dir(service: str, account_id: str) -> Path:
    """
    Geef een stabiele profielmap terug per (service, account_id).
    Dit voorkomt dat cookies van een ander account 'meegenomen' worden.
    """
    data_dir = Path(get_data_dir())
    base = data_dir / "chrome_profiles" / service
    base.mkdir(parents=True, exist_ok=True)
    key = (account_id or "").strip().lower().encode("utf-8")
    digest = hashlib.sha256(key).hexdigest()[:16]
    p = base / digest
    p.mkdir(parents=True, exist_ok=True)
    return p


def _build_options(
    *,
    incognito: bool | None = None,
    user_data_dir: str | None = None,
    profile_directory: str | None = None,
) -> webdriver.ChromeOptions:
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    # In een desktop-app is "detach" meestal niet nodig: zolang de app draait
    # blijft de driver leven. Detach kan wel handig zijn, maar veroorzaakt vaak
    # "user data dir is already in use" bij een volgende app-run.
    if _is_truthy(os.environ.get("AUTO_LOGIN_DETACH")):
        options.add_experimental_option("detach", True)

    if user_data_dir is None:
        user_data_dir = (os.environ.get("AUTO_LOGIN_USER_DATA_DIR") or "").strip() or str(_default_user_data_dir())

    options.add_argument(f"--user-data-dir={user_data_dir}")

    if profile_directory is None:
        profile_directory = (os.environ.get("AUTO_LOGIN_PROFILE_DIRECTORY") or "").strip()
    if profile_directory:
        options.add_argument(f"--profile-directory={profile_directory}")

    if incognito is None:
        incognito = _is_truthy(os.environ.get("AUTO_LOGIN_INCOGNITO"))
    if incognito:
        options.add_argument("--incognito")

    return options


def _driver_is_alive(driver: webdriver.Chrome | None) -> bool:
    if not driver:
        return False
    try:
        _ = driver.current_url
        return True
    except Exception:
        return False


def get_shared_driver() -> webdriver.Chrome:
    """Geef een herbruikbare Chrome driver terug (maakt hem aan indien nodig)."""
    global _SHARED_DRIVER
    with _DRIVER_LOCK:
        if _driver_is_alive(_SHARED_DRIVER):
            return _SHARED_DRIVER

        try:
            _SHARED_DRIVER = webdriver.Chrome(options=_build_options(), service=ChromeService())
        except WebDriverException as e:
            # Meest voorkomende oorzaak: vaste user-data-dir is nog gelocked door een
            # achtergebleven Chrome instance van een vorige run.
            raise RuntimeError(
                "Kon gedeelde Chrome-sessie niet starten (mogelijk profiel in gebruik). "
                "Sluit alle Chrome-vensters die door de tool zijn geopend, of gebruik isolatie."
            ) from e
        return _SHARED_DRIVER


def open_url_in_shared_session(url: str, *, new_tab: bool = True) -> webdriver.Chrome:
    """
    Open URL in de gedeelde Chrome-sessie.
    Standaard opent dit in een nieuw tabblad.
    """
    driver = get_shared_driver()

    if new_tab and _driver_is_alive(driver):
        # Selenium 4: betrouwbaarder dan window.open (popup blockers / timing issues).
        try:
            driver.switch_to.new_window("tab")
            driver.get(url)
        except Exception:
            # Fallback: oudere selenium/chromedriver combinaties
            try:
                driver.execute_script("window.open('about:blank', '_blank');")
                driver.switch_to.window(driver.window_handles[-1])
                driver.get(url)
            except Exception:
                driver.get(url)
    else:
        driver.get(url)

    return driver


def open_url_in_isolated_session(url: str, *, incognito: bool = False) -> webdriver.Chrome:
    """
    Open URL in een aparte Chrome instance (met eigen user-data-dir).
    Handig voor cookie-isolatie (bv. tegelijk 2 accounts).
    """
    isolated_dir = _isolated_user_data_dir(incognito=incognito)
    driver = webdriver.Chrome(
        options=_build_options(user_data_dir=str(isolated_dir), incognito=incognito, profile_directory=""),
        service=ChromeService(),
    )
    driver.get(url)
    return driver


def open_url_in_account_session(service: str, url: str, account_id: str, *, incognito: bool = False) -> webdriver.Chrome:
    """
    Open URL in een aparte Chrome instance met een vaste profielmap per account.
    """
    profile_dir = _account_profile_dir(service, account_id)
    driver = webdriver.Chrome(
        options=_build_options(user_data_dir=str(profile_dir), incognito=incognito, profile_directory=""),
        service=ChromeService(),
    )
    driver.get(url)
    return driver


def open_url_for_service(service: str, url: str, *, new_tab: bool = True, account_id: str | None = None) -> webdriver.Chrome:
    """
    Open URL volgens sessie-strategie per service.
    - shared session: nieuw tabblad in 1 gedeelde Chrome
    - isolated session: aparte Chrome instance voor cookie-isolatie
    """
    global _SHARED_DRIVER

    if _tabs_only_mode():
        try:
            return open_url_in_shared_session(url, new_tab=new_tab)
        except Exception:
            with _DRIVER_LOCK:
                _SHARED_DRIVER = None
            return open_url_in_shared_session(url, new_tab=new_tab)

    if should_isolate_service(service):
        return open_url_in_isolated_session(url, incognito=incognito_for_service(service))
    if account_id and (_requires_account_isolation(service) or should_isolate_by_account(service)):
        # Vermijd account-cookie clashes (A wordt hergebruikt voor B).
        return open_url_in_account_session(service, url, account_id, incognito=False)

    # Niet-incognito services: altijd gedeelde sessie + extra tab.
    # Alleen als er nog geen sessie is, start get_shared_driver een nieuwe Chrome.
    if not incognito_for_service(service):
        try:
            return open_url_in_shared_session(url, new_tab=new_tab)
        except Exception:
            # Eén retry met een verse shared driver referentie.
            with _DRIVER_LOCK:
                _SHARED_DRIVER = None
            return open_url_in_shared_session(url, new_tab=new_tab)

    # Incognito services blijven geïsoleerd.
    if account_id and should_isolate_by_account(service):
        return open_url_in_account_session(service, url, account_id, incognito=True)
    return open_url_in_isolated_session(url, incognito=True)
