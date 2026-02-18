"""
Wis Microsoft site-data (cookies + storage) zonder hele browserreset.
"""
from __future__ import annotations

from selenium.webdriver.remote.webdriver import WebDriver

MS_DOMAINS = [
    "login.microsoftonline.com",
    "microsoftonline.com",
    "microsoft.com",
    "admin.microsoft.com",
    "office.com",
    "live.com",
]


def _domain_matches(candidate: str, target: str) -> bool:
    c = (candidate or "").lstrip(".").lower()
    t = target.lower()
    return c == t or c.endswith("." + t)


def _clear_storage_on_current_origin(driver: WebDriver) -> None:
    driver.execute_script(
        """
        try { localStorage.clear(); } catch (e) {}
        try { sessionStorage.clear(); } catch (e) {}
        try {
          if (window.indexedDB && indexedDB.databases) {
            indexedDB.databases().then(dbs => {
              (dbs || []).forEach(db => { if (db && db.name) indexedDB.deleteDatabase(db.name); });
            });
          }
        } catch (e) {}
        try {
          if (window.caches && caches.keys) {
            caches.keys().then(keys => keys.forEach(k => caches.delete(k)));
          }
        } catch (e) {}
        """
    )


def clear_microsoft_site_data(driver: WebDriver) -> None:
    """
    Wis enkel Microsoft-gerelateerde cookies + web storage.
    """
    # Storage per origin wissen via CDP (zonder visuele navigatie/redirects).
    # Dit wist ook cookies voor die origin en is veel sneller dan alle cookies ophalen.
    for domain in MS_DOMAINS:
        try:
            driver.execute_cdp_cmd(
                "Storage.clearDataForOrigin",
                {"origin": f"https://{domain}", "storageTypes": "all"},
            )
        except Exception:
            continue
