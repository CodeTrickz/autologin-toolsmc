"""
Helpers voor stabielere input in login flows.
"""
import os
import random
import time

from selenium.webdriver.common.keys import Keys


def _get_float_env(name: str, default: float) -> float:
    try:
        v = float(os.environ.get(name, "").strip())
        return v
    except Exception:
        return default


def clear_and_human_type(element, text: str, min_delay: float | None = None, max_delay: float | None = None) -> None:
    """
    Typ tekst karakter per karakter met kleine willekeurige pauzes.
    """
    # Sneller maar nog "menselijk": standaard ~40-120ms per karakter.
    if min_delay is None:
        min_delay = _get_float_env("AUTO_LOGIN_TYPE_DELAY_MIN", 0.04)
    if max_delay is None:
        max_delay = _get_float_env("AUTO_LOGIN_TYPE_DELAY_MAX", 0.12)

    # Safety: zorg dat ranges kloppen
    min_delay = max(0.0, float(min_delay))
    max_delay = max(min_delay, float(max_delay))

    element.clear()
    for i, ch in enumerate(str(text or "")):
        element.send_keys(ch)
        time.sleep(random.uniform(min_delay, max_delay))
        # Mini-pauze af en toe (zoals nadenken/handpositie)
        if i > 0 and i % random.randint(6, 12) == 0:
            time.sleep(random.uniform(0.12, 0.35))


def clear_and_type_verified(driver, element, text: str, min_delay: float | None = None, max_delay: float | None = None) -> None:
    """
    Vul een input in en controleer of de browser de waarde echt heeft aangenomen.
    Sommige moderne loginformulieren negeren .clear() of losse send_keys events.
    """
    text = str(text or "")

    try:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    except Exception:
        pass

    try:
        element.click()
        element.send_keys(Keys.CONTROL, "a")
        element.send_keys(Keys.BACKSPACE)
        clear_and_human_type(element, text, min_delay=min_delay, max_delay=max_delay)
    except Exception:
        pass

    try:
        if (element.get_attribute("value") or "") == text:
            return
    except Exception:
        pass

    driver.execute_script(
        """
        const el = arguments[0];
        const value = arguments[1];
        el.focus();
        const setter = Object.getOwnPropertyDescriptor(el.__proto__, 'value')?.set
            || Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
        setter.call(el, '');
        el.dispatchEvent(new Event('input', { bubbles: true }));
        setter.call(el, value);
        el.dispatchEvent(new Event('input', { bubbles: true }));
        el.dispatchEvent(new Event('change', { bubbles: true }));
        """,
        element,
        text,
    )

    if (element.get_attribute("value") or "") != text:
        raise RuntimeError("Inputveld kon niet betrouwbaar worden ingevuld.")
