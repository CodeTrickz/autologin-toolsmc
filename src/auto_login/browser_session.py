"""
Selenium browser session management for all auto-login scripts.

The application owns at most two Chrome instances during one run:
- normal_driver: regular Chrome profile
- incognito_driver: Chrome started with --incognito

Every login opens a new tab in the matching browser. Existing browsers are
reused while they respond, and are recreated only after the user has closed
that browser.
"""
from __future__ import annotations

import logging
import os
import threading
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from src.core.credentials_manager import get_data_dir
from src.core.shutdown import register_shutdown_callback
from src.auto_login import browser_cleanup  # noqa: F401  (registers central shutdown cleanup)

logger = logging.getLogger(__name__)

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


def _incognito_user_data_dir() -> Path:
    data_dir = Path(get_data_dir())
    incognito_profile_dir = data_dir / "chrome_user_data_incognito"
    incognito_profile_dir.mkdir(parents=True, exist_ok=True)
    return incognito_profile_dir


def _build_options(*, incognito: bool = False) -> webdriver.ChromeOptions:
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

    if incognito:
        user_data_dir = str(_incognito_user_data_dir())
        options.add_argument("--incognito")
    else:
        user_data_dir = (os.environ.get("AUTO_LOGIN_USER_DATA_DIR") or "").strip() or str(_default_user_data_dir())
        profile_directory = (os.environ.get("AUTO_LOGIN_PROFILE_DIRECTORY") or "").strip()
        if profile_directory:
            options.add_argument(f"--profile-directory={profile_directory}")

    options.add_argument(f"--user-data-dir={user_data_dir}")
    return options


def _log_session_event(event: str, session_type: str) -> None:
    message = f"{event} {session_type}"
    logger.info(message)
    print(message)


class SessionManager:
    """Owns the only Selenium Chrome instances started by this application."""

    def __init__(self) -> None:
        self.normal_driver: webdriver.Chrome | None = None
        self.incognito_driver: webdriver.Chrome | None = None
        self._lock = threading.Lock()

    def open_login_tab(self, url: str, *, incognito: bool = False) -> webdriver.Chrome:
        """
        Open a login URL in a new tab of the matching reusable browser session.
        """
        with self._lock:
            driver = self._get_or_create_driver(incognito=incognito)
            self._open_new_tab(driver, url, incognito=incognito)
            return driver

    def get_driver(self, *, incognito: bool = False) -> webdriver.Chrome:
        """Return the matching reusable driver, creating it when necessary."""
        with self._lock:
            return self._get_or_create_driver(incognito=incognito)

    def quit_all(self) -> None:
        """Quit both application-managed Chrome sessions."""
        with self._lock:
            drivers = [
                ("normal", self.normal_driver),
                ("incognito", self.incognito_driver),
            ]
            self.normal_driver = None
            self.incognito_driver = None

        for session_type, driver in drivers:
            if driver is None:
                continue
            try:
                driver.quit()
                _log_session_event("SESSION_QUIT", session_type)
            except Exception:
                pass

    def _get_or_create_driver(self, *, incognito: bool) -> webdriver.Chrome:
        attr = "incognito_driver" if incognito else "normal_driver"
        driver = getattr(self, attr)
        session_type = self._session_type(incognito)

        if self._driver_is_alive(driver):
            _log_session_event("SESSION_REUSED", session_type)
            return driver

        service = ChromeService(executable_path=ChromeDriverManager().install())
        try:
            driver = webdriver.Chrome(options=_build_options(incognito=incognito), service=service)
        except WebDriverException as e:
            raise RuntimeError(
                f"Kon Chrome-sessie niet starten ({session_type}; mogelijk profiel in gebruik). "
                "Sluit Chrome-vensters die door de tool zijn geopend en probeer opnieuw."
            ) from e

        setattr(self, attr, driver)
        _log_session_event("SESSION_CREATED", session_type)
        return driver

    def _driver_is_alive(self, driver: webdriver.Chrome | None) -> bool:
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

    def _open_new_tab(self, driver: webdriver.Chrome, url: str, *, incognito: bool) -> None:
        session_type = self._session_type(incognito)
        try:
            driver.switch_to.new_window("tab")
        except Exception:
            driver.execute_script("window.open('about:blank', '_blank');")
            driver.switch_to.window(driver.window_handles[-1])

        _log_session_event("NEW_TAB_CREATED", session_type)
        driver.get(url)

    @staticmethod
    def _session_type(incognito: bool) -> str:
        return "incognito" if incognito else "normal"


session_manager = SessionManager()
register_shutdown_callback("browser_sessions", session_manager.quit_all)


def incognito_for_service(service: str) -> bool:
    """
    Determine whether a service should use the reusable incognito browser.

    Admin portals keep their historical hardened behavior by using the single
    incognito browser instead of creating temporary isolated browsers.
    """
    if service in _HARDENED_ADMIN_SERVICES:
        return not _is_truthy(os.environ.get("AUTO_LOGIN_DISABLE_ADMIN_HARDENING"))
    if _is_truthy(os.environ.get("AUTO_LOGIN_INCOGNITO")):
        return True
    incognito = _parse_csv_set(os.environ.get("AUTO_LOGIN_INCOGNITO_SERVICES"))
    return service in incognito


def hardened_admin_session(service: str) -> bool:
    return service in _HARDENED_ADMIN_SERVICES and not _is_truthy(os.environ.get("AUTO_LOGIN_DISABLE_ADMIN_HARDENING"))


def get_shared_driver() -> webdriver.Chrome:
    """Backward-compatible normal-session driver accessor."""
    return session_manager.get_driver(incognito=False)


def open_url_in_shared_session(url: str, *, new_tab: bool = True) -> webdriver.Chrome:
    """Open URL in the reusable normal Chrome session."""
    if new_tab:
        return session_manager.open_login_tab(url, incognito=False)
    driver = session_manager.get_driver(incognito=False)
    driver.get(url)
    return driver


def open_url_in_isolated_session(url: str, *, incognito: bool = False) -> webdriver.Chrome:
    """
    Backward-compatible helper.

    The old implementation created a fresh browser. The new invariant allows
    only one normal and one incognito browser, so this opens a new tab in the
    matching reusable session.
    """
    return session_manager.open_login_tab(url, incognito=incognito)


def open_url_in_account_session(service: str, url: str, account_id: str, *, incognito: bool = False) -> webdriver.Chrome:
    """
    Backward-compatible helper for account-specific callers.

    Per-account Chrome instances are intentionally no longer created.
    """
    return session_manager.open_login_tab(url, incognito=incognito)


def open_url_for_service(
    service: str,
    url: str,
    *,
    new_tab: bool = True,
    account_id: str | None = None,
    incognito: bool | None = None,
) -> webdriver.Chrome:
    """
    Open URL in exactly one of the two reusable sessions.

    Service modules should use this function instead of constructing Selenium
    drivers themselves. The actual Chrome launch point remains SessionManager.
    """
    use_incognito = incognito_for_service(service) if incognito is None else incognito
    if new_tab:
        return session_manager.open_login_tab(url, incognito=use_incognito)

    driver = session_manager.get_driver(incognito=use_incognito)
    driver.get(url)
    return driver
