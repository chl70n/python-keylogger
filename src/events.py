from dataclasses import dataclass


@dataclass
class KeyEvent:
    """A single keystroke captured by the listener."""
    key: str        # Human-readable key string, e.g. "a", "[ENTER]", "[CTRL]"
    timestamp: str  # HH:MM:SS format


@dataclass
class WindowEvent:
    """Active window title changed."""
    title: str      # Window title text
    timestamp: str  # HH:MM:SS format
