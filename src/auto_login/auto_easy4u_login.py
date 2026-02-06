"""
Automatische login voor Easy4U Nederland admin (easy4u.nl).
Gebruikt Playwright voor betrouwbare invulling en klik op de loginpagina.
Credentials komen uit de app (Credentials > Easy4U).
"""
import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
SCRIPTS_DIR = Path(__file__).parent.parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from src.core.credentials_manager import get_credential, get_data_dir

DATA_DIR = get_data_dir()
CREDENTIALS_FILE = DATA_DIR / "credentials.json"

LOGIN_URL = "https://easy4u.nl/admin/login?referrer=%2Fadmin%2F"


def get_credential_or_fail(service: str, field: str) -> str:
    """Haal credential op uit encrypted storage."""
    value = get_credential(service, field, DATA_DIR, CREDENTIALS_FILE)
    if not value or value.strip() == "":
        raise RuntimeError(
            f"Credentials ontbreken: {field} voor {service} is niet ingevuld.\n"
            "Ga naar de web interface of desktop app om je credentials in te stellen."
        )
    return value


async def _login_async(headed: bool = True) -> None:
    """Playwright-based login (async)."""
    from dotenv import load_dotenv
    env_path = DATA_DIR / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()

    email = get_credential_or_fail("easy4u", "email")
    password = get_credential_or_fail("easy4u", "password")

    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=not headed,
            slow_mo=80 if headed else 0,
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720},
        )
        page = await context.new_page()

        try:
            print("Openen loginpagina...")
            await page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=20000)
            await page.wait_for_load_state("networkidle", timeout=10000)

            email_input = page.locator(
                "input:not([type='password']):not([type='submit']):not([type='hidden'])"
            ).first
            await email_input.wait_for(state="visible", timeout=15000)
            await email_input.fill(email)

            pwd_input = page.locator("input[type='password']").first
            await pwd_input.wait_for(state="visible", timeout=5000)
            await pwd_input.fill(password)

            login_btn = (
                page.get_by_role("button", name="inloggen")
                .or_(page.locator("input[type='submit']"))
                .or_(page.get_by_role("button", name="Inloggen"))
                .first
            )
            await login_btn.click()

            await page.wait_for_load_state("networkidle", timeout=15000)

            url = page.url
            if "/admin" in url and "/login" not in url:
                print("Succesvol ingelogd op Easy4U.")
            else:
                error_el = page.locator("[class*='error'], .alert-danger, #errorsDiv").first
                if await error_el.is_visible():
                    print("Login mislukt:", await error_el.text_content())
                else:
                    print("Pagina na login:", url)

            if headed:
                input("Druk op Enter om de browser te sluiten...")
        except Exception as e:
            print("Fout:", e)
        finally:
            await browser.close()


def login_easy4u() -> None:
    """
    Log automatisch in op Easy4U: https://easy4u.nl/admin/
    Gebruikt Playwright. Credentials uit de app (Credentials > Easy4U).
    """
    try:
        asyncio.run(_login_async(headed=True))
    except RuntimeError:
        raise
    except Exception as e:
        print("Fout bij Easy4U login:", e)
        raise


if __name__ == "__main__":
    login_easy4u()
