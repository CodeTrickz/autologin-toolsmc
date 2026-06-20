"""
Central application shutdown coordination.
"""
from __future__ import annotations

import atexit
import signal
import threading
from collections.abc import Callable

from src.core.process_cleanup import kill_child_process_tree

shutdown_event = threading.Event()

_lock = threading.RLock()
_threads: list[threading.Thread] = []
_callbacks: list[tuple[str, Callable[[], None]]] = []
_handler_registered = False
_signals_registered = False
_shutdown_started = False


def register_shutdown_handler() -> None:
    """Register the single process-level shutdown handler."""
    global _handler_registered, _signals_registered
    with _lock:
        if _handler_registered:
            return
        if not _handler_registered:
            atexit.register(shutdown_application)
            _handler_registered = True
        if not _signals_registered:
            for sig_name in ("SIGINT", "SIGTERM"):
                sig = getattr(signal, sig_name, None)
                if sig is None:
                    continue
                try:
                    signal.signal(sig, _handle_signal)
                except Exception:
                    continue
            _signals_registered = True


def _handle_signal(signum, frame) -> None:
    shutdown_application()


def register_thread(thread: threading.Thread) -> threading.Thread:
    with _lock:
        if thread not in _threads:
            _threads.append(thread)
    return thread


def start_thread(thread: threading.Thread) -> threading.Thread:
    register_thread(thread)
    thread.start()
    return thread


def register_shutdown_callback(name: str, callback: Callable[[], None]) -> None:
    with _lock:
        if any(existing_name == name for existing_name, _ in _callbacks):
            return
        _callbacks.append((name, callback))


def request_shutdown() -> None:
    shutdown_event.set()


def join_threads(timeout_per_thread: float = 5.0) -> None:
    current = threading.current_thread()
    with _lock:
        threads = list(_threads)

    for thread in threads:
        if thread is current or not thread.is_alive():
            continue
        try:
            thread.join(timeout=timeout_per_thread)
        except RuntimeError:
            continue


def shutdown_application() -> None:
    """Stop workers, servers, browsers, and registered background threads."""
    global _shutdown_started
    with _lock:
        if _shutdown_started:
            return
        _shutdown_started = True
        callbacks = list(reversed(_callbacks))

    shutdown_event.set()

    for name, callback in callbacks:
        try:
            callback()
        except Exception as exc:
            try:
                print(f"Fout bij shutdown stap {name}: {exc}")
            except Exception:
                pass

    join_threads()
    kill_child_process_tree()


register_shutdown_handler()
