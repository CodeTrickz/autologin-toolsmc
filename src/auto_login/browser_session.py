"""
Selenium browser session management for auto-login scripts.

Normal logins reuse one Chrome session and open new tabs. Hardened admin
portals and account-sensitive flows use isolated Chrome sessions so cookies,
incognito state, and locked profiles cannot poison the next login attempt.
"""
from __future__ import annotations

import hashlib
import logging
import os
import threading
from pathlib import Path
from uuid import uuid4

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from src.core.credentials_manager import get_data_dir
from src.core.shutdown import register_shutdown_callback
from src.auto_login import browser_cleanup  # noqa: F401  (registers central shutdown cleanup)

logger = logging.getLogger(__name__)

_DRIVER_LOCK = threading.Lock()
_SHARED_DRIVER: webdriver.Chrome | None = None

_HARDENED_ADMIN_SERVICES = {
    "microsoft_admin",
    "intune_admin",
    "azure_admin",
    "google_admin",
}


def _is_truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _parse_csv_set(value: str | None) -> set[str]:
    if not value:
        return set()
    parts = [p.strip() for p in str(value).split(",")]
    return {p for p in parts if p}


def _default_user_data_dir() -> Path:
    data_dir = Path(get_data_dir())
    default_profile_dir = data_dir / "chrome_user_data"
    default_profile_dir.mkdir(parents=True, exist_ok=True)
    return default_profile_dir


def _isolated_user_data_dir(*, incognito: bool) -> Path:
    data_dir = Path(get_data_dir())
    base = data_dir / "chrome_user_data_isolated" / ("incognito" if incognito else "profile")
    base.mkdir(parents=True, exist_ok=True)
    path = base / uuid4().hex
    path.mkdir(parents=True, exist_ok=True)
    return path


def _account_profile_dir(service: str, account_id: str) -> Path:
    data_dir = Path(get_data_dir())
    base = data_dir / "chrome_profiles" / service
    base.mkdir(parents=True, exist_ok=True)
    key = (account_id or "").strip().lower().encode("utf-8")
    digest = hashlib.sha256(key).hexdigest()[:16]
    path = base / digest
    path.mkdir(parents=True, exist_ok=True)
    return path


def _build_options(
    *,
    incognito: bool = False,
    user_data_dir: str | None = None,
    profile_directory: str | None = None,
) -> webdriver.ChromeOptions:
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-sync")
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-component-update")
    options.add_argument("--disable-features=PasswordManagerOnboarding,PasswordImport,AutofillServerCommunication")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option(
        "prefs",
        {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "autofill.profile_enabled": False,
            "autofill.credit_card_enabled": False,
        },
    )

    if _is_truthy(os.environ.get("AUTO_LOGIN_DETACH")):
        options.add_experimental_option("detach", True)

    if user_data_dir is None:
        user_data_dir = (os.environ.get("AUTO_LOGIN_USER_DATA_DIR") or "").strip() or str(_default_user_data_dir())
    options.add_argument(f"--user-data-dir={user_data_dir}")

    if profile_directory is None:
        profile_directory = (os.environ.get("AUTO_LOGIN_PROFILE_DIRECTORY") or "").strip()
    if profile_directory:
        options.add_argument(f"--profile-directory={profile_directory}")

    if incognito:
        options.add_argument("--incognito")

    return options


def _driver_is_alive(driver: webdriver.Chrome | None) -> bool:
    if driver is None:
        return False
    try:
        handles = driver.window_handles
        if not handles:
            return False
        try:
            current_handle = driver.current_window_handle
        except Exception:
            current_handle = None
        if current_handle not in handles:
            driver.switch_to.window(handles[-1])
        _ = driver.current_url
        return True
    except Exception:
        return False


def _new_driver(*, incognito: bool = False, user_data_dir: str | None = None, profile_directory: str | None = None) -> webdriver.Chrome:
    service = ChromeService(executable_path=ChromeDriverManager().install())
    return webdriver.Chrome(
        options=_build_options(
            incognito=incognito,
            user_data_dir=user_data_dir,
            profile_directory=profile_directory,
        ),
        service=service,
    )


def _open_new_tab(driver: webdriver.Chrome, url: str) -> None:
    try:
        driver.switch_to.new_window("tab")
    except Exception:
        driver.execute_script("window.open('about:blank', '_blank');")
        driver.switch_to.window(driver.window_handles[-1])
    driver.get(url)


def _log_session_event(event: str, session_type: str) -> None:
    message = f"{event} {session_type}"
    logger.info(message)
    print(message)


def incognito_for_service(service: str) -> bool:
    if _is_truthy(os.environ.get("AUTO_LOGIN_INCOGNITO")):
        return True
    incognito = _parse_csv_set(os.environ.get("AUTO_LOGIN_INCOGNITO_SERVICES"))
    return service in incognito


def hardened_admin_session(service: str) -> bool:
    return service in _HARDENED_ADMIN_SERVICES and not _is_truthy(os.environ.get("AUTO_LOGIN_DISABLE_ADMIN_HARDENING"))


def get_shared_driver() -> webdriver.Chrome:
    """Return the reusable normal Chrome driver, creating it if needed."""
    global _SHARED_DRIVER
    with _DRIVER_LOCK:
        if _driver_is_alive(_SHARED_DRIVER):
            _log_session_event("SESSION_REUSED", "normal")
            return _SHARED_DRIVER

        try:
            _SHARED_DRIVER = _new_driver()
        except WebDriverException as e:
            raise RuntimeError(
                "Kon gedeelde Chrome-sessie niet starten (mogelijk profiel in gebruik). "
                "Sluit Chrome-vensters die door de tool zijn geopend en probeer opnieuw."
            ) from e

        _log_session_event("SESSION_CREATED", "normal")
        return _SHARED_DRIVER


def open_url_in_shared_session(url: str, *, new_tab: bool = True) -> webdriver.Chrome:
    """Open a URL in the reusable normal Chrome session."""
    driver = get_shared_driver()
    if new_tab and _driver_is_alive(driver):
        try:
            _open_new_tab(driver, url)
        except Exception:
            driver.get(url)
    else:
        driver.get(url)
    return driver


def open_url_in_isolated_session(url: str, *, incognito: bool = False) -> webdriver.Chrome:
    """Open a URL in a fresh isolated Chrome instance."""
    isolated_dir = _isolated_user_data_dir(incognito=incognito)
    driver = _new_driver(incognito=incognito, user_data_dir=str(isolated_dir), profile_directory="")
    _log_session_event("SESSION_CREATED", "isolated-incognito" if incognito else "isolated")
    driver.get(url)
    return driver


def open_url_in_account_session(service: str, url: str, account_id: str, *, incognito: bool = False) -> webdriver.Chrome:
    """Open a URL in a stable isolated Chrome profile for one account."""
    profile_dir = _account_profile_dir(service, account_id)
    driver = _new_driver(incognito=incognito, user_data_dir=str(profile_dir), profile_directory="")
    _log_session_event("SESSION_CREATED", f"account-{service}")
    driver.get(url)
    return driver


def _requires_account_isolation(service: str) -> bool:
    return service in {
        "smartschool",
        "smartschool_admin",
        "microsoft_admin",
        "google_admin",
        "intune_admin",
        "azure_admin",
    }


def open_url_for_service(
    service: str,
    url: str,
    *,
    new_tab: bool = True,
    account_id: str | None = None,
    incognito: bool | None = None,
) -> webdriver.Chrome:
    """
    Open a URL according to the service strategy.

    Admin portals default to fresh isolated incognito sessions. Account-sensitive
    services get per-account profiles when not using explicit incognito.
    """
    global _SHARED_DRIVER

    if hardened_admin_session(service):
        return open_url_in_isolated_session(url, incognito=True)

    use_incognito = incognito_for_service(service) if incognito is None else incognito
    if use_incognito:
        return open_url_in_isolated_session(url, incognito=True)

    if account_id and _requires_account_isolation(service):
        return open_url_in_account_session(service, url, account_id, incognito=False)

    try:
        return open_url_in_shared_session(url, new_tab=new_tab)
    except Exception:
        with _DRIVER_LOCK:
            _SHARED_DRIVER = None
        return open_url_in_shared_session(url, new_tab=new_tab)


def quit_all_sessions() -> None:
    global _SHARED_DRIVER
    with _DRIVER_LOCK:
        driver = _SHARED_DRIVER
        _SHARED_DRIVER = None
    if driver is not None:
        try:
            driver.quit()
            _log_session_event("SESSION_QUIT", "normal")
        except Exception:
            pass


register_shutdown_callback("browser_sessions", quit_all_sessions)
