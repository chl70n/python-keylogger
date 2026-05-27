import queue
from datetime import datetime
from pynput import keyboard as kb
from src.events import KeyEvent

# Maps pynput special keys to readable labels
SPECIAL_KEY_MAP: dict = {
    kb.Key.enter:      "[ENTER]",
    kb.Key.space:      "[SPACE]",
    kb.Key.backspace:  "[BACKSPACE]",
    kb.Key.tab:        "[TAB]",
    kb.Key.ctrl_l:     "[CTRL]",
    kb.Key.ctrl_r:     "[CTRL]",
    kb.Key.alt_l:      "[ALT]",
    kb.Key.alt_r:      "[ALT]",
    kb.Key.alt_gr:     "[ALT]",
    kb.Key.shift:      "[SHIFT]",
    kb.Key.shift_r:    "[SHIFT]",
    kb.Key.caps_lock:  "[CAPS]",
    kb.Key.delete:     "[DEL]",
    kb.Key.esc:        "[ESC]",
    kb.Key.up:         "[UP]",
    kb.Key.down:       "[DOWN]",
    kb.Key.left:       "[LEFT]",
    kb.Key.right:      "[RIGHT]",
    kb.Key.home:       "[HOME]",
    kb.Key.end:        "[END]",
    kb.Key.page_up:    "[PGUP]",
    kb.Key.page_down:  "[PGDN]",
    kb.Key.insert:     "[INS]",
    kb.Key.print_screen: "[PRTSC]",
}


def format_key(key: kb.Key | kb.KeyCode) -> str:
    """Convert a pynput key object to a human-readable string.

    - Printable characters  → the character itself (e.g. "a", "A", "5", "!")
    - Known special keys    → bracketed label from SPECIAL_KEY_MAP
    - Unknown special keys  → "[KEY_NAME]" using key.name in uppercase
    """
    if isinstance(key, kb.KeyCode):
        return key.char if key.char else f"[{key.vk}]"
    return SPECIAL_KEY_MAP.get(key, f"[{key.name.upper()}]")


class KeyboardListener:
    """Wraps pynput.keyboard.Listener and pushes KeyEvent items onto a queue."""

    MAX_RESTARTS = 3

    def __init__(self, event_queue: queue.Queue):
        self._queue = event_queue
        self._listener: kb.Listener | None = None
        self._restart_count = 0

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def start(self) -> None:
        self._restart_count = 0
        self._launch()

    def stop(self) -> None:
        if self._listener:
            self._listener.stop()
            self._listener = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _launch(self) -> None:
        self._listener = kb.Listener(
            on_press=self._on_press,
            on_error=self._on_error,
        )
        self._listener.start()

    def _on_error(self, exc: Exception) -> None:
        """Called by pynput when the listener encounters an unhandled exception.

        Auto-restarts up to MAX_RESTARTS times.
        """
        if self._restart_count < self.MAX_RESTARTS:
            self._restart_count += 1
            print(
                f"[listener] restart {self._restart_count}/{self.MAX_RESTARTS} after error: {exc}",
                file=__import__("sys").stderr,
            )
            self._launch()
        else:
            print(
                f"[listener] max restarts ({self.MAX_RESTARTS}) reached — listener stopped.",
                file=__import__("sys").stderr,
            )

    def _on_press(self, key) -> None:
        try:
            key_str = format_key(key)
        except Exception:
            key_str = "[?]"
        timestamp = datetime.now().strftime("%H:%M:%S")
        self._queue.put(KeyEvent(key=key_str, timestamp=timestamp))
