"""
Helpers voor stabielere input in login flows.
"""
import os
import random
import time


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
