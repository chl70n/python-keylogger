import queue
import threading
import time
from datetime import datetime
from src.events import WindowEvent

try:
    import win32gui
    _WIN32_AVAILABLE = True
except ImportError:
    _WIN32_AVAILABLE = False


class WindowTracker:
    """Polls the active window title and emits WindowEvent on change."""

    POLL_INTERVAL: float = 2.0  # seconds; override in tests

    def __init__(self, event_queue: queue.Queue):
        self._queue = event_queue
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._last_title: str = ""

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            raise RuntimeError("WindowTracker already running. Call stop() first.")
        self._stop_event.clear()
        self._last_title = ""
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=3)
            self._thread = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_active_window_title(self) -> str:
        """Return the current foreground window title, or '' on any error."""
        if not _WIN32_AVAILABLE:
            return ""
        try:
            hwnd = win32gui.GetForegroundWindow()
            return win32gui.GetWindowText(hwnd)
        except Exception:
            return ""

    def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                title = self._get_active_window_title()
            except Exception:
                title = ""
            if title and title != self._last_title:
                self._last_title = title
                timestamp = datetime.now().strftime("%H:%M:%S")
                self._queue.put(WindowEvent(title=title, timestamp=timestamp))
            time.sleep(self.POLL_INTERVAL)
