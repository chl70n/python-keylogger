"""
Tkinter live-viewer dashboard for the educational keylogger.

Layout:
  ┌──────────────────────────────────────────────┐
  │  [▶ Start]  [■ Stop]  [📂 Open Logs]          │
  ├──────────────────────────────────────────────┤
  │  scrolled text area (dark theme, Consolas)    │
  ├──────────────────────────────────────────────┤
  │  ● Recording | Window: Notepad | Keys: 47    │
  └──────────────────────────────────────────────┘
"""
import os
import queue
import tkinter as tk
from tkinter import scrolledtext, messagebox
from pathlib import Path

from src.events import KeyEvent, WindowEvent
from src.file_logger import FileLogger, LogWriteError


class KeyloggerGUI:
    """Main application window. Must be instantiated on the main thread."""

    REFRESH_MS = 500  # queue poll interval in milliseconds

    def __init__(
        self,
        event_queue: queue.Queue,
        listener,
        window_tracker,
        file_logger: FileLogger,
        logs_dir: str = "logs",
    ):
        self._queue = event_queue
        self._listener = listener
        self._window_tracker = window_tracker
        self._file_logger = file_logger
        self._logs_dir = Path(logs_dir)

        self._keys_captured: int = 0
        self._is_recording: bool = False
        self._after_id: str | None = None
        self._current_window: str = "—"

        self._root = tk.Tk()
        self._root.title("Educational Keylogger")
        self._root.geometry("720x500")
        self._root.resizable(True, True)
        self._root.protocol("WM_DELETE_WINDOW", self._on_close)

        self._build_ui()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Start the Tkinter main loop (blocks until window closed)."""
        self._root.mainloop()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        self._build_toolbar()
        self._build_text_area()
        self._build_status_bar()

    def _build_toolbar(self) -> None:
        bar = tk.Frame(self._root, pady=6, padx=8)
        bar.pack(fill=tk.X)

        self._btn_start = tk.Button(
            bar, text="▶  Start", width=11,
            bg="#2d8a4e", fg="white", activebackground="#236b3c",
            font=("Segoe UI", 10, "bold"),
            command=self._start_recording,
        )
        self._btn_start.pack(side=tk.LEFT, padx=(0, 6))

        self._btn_stop = tk.Button(
            bar, text="■  Stop", width=11,
            bg="#c0392b", fg="white", activebackground="#922b21",
            font=("Segoe UI", 10, "bold"),
            state=tk.DISABLED,
            command=self._stop_recording,
        )
        self._btn_stop.pack(side=tk.LEFT, padx=(0, 6))

        tk.Button(
            bar, text="📂  Open Logs", width=13,
            font=("Segoe UI", 10),
            command=self._open_logs_folder,
        ).pack(side=tk.LEFT)

    def _build_text_area(self) -> None:
        self._text = scrolledtext.ScrolledText(
            self._root,
            wrap=tk.WORD,
            font=("Consolas", 10),
            state=tk.DISABLED,
            bg="#1e1e1e",
            fg="#d4d4d4",
            insertbackground="white",
            padx=6,
            pady=4,
        )
        self._text.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 4))

    def _build_status_bar(self) -> None:
        bar = tk.Frame(self._root, bd=1, relief=tk.SUNKEN)
        bar.pack(fill=tk.X, side=tk.BOTTOM)

        self._lbl_status = tk.Label(
            bar, text="■  Stopped", fg="#c0392b",
            anchor=tk.W, padx=10, font=("Segoe UI", 9),
        )
        self._lbl_status.pack(side=tk.LEFT)

        tk.Label(bar, text="│", fg="#555").pack(side=tk.LEFT)

        self._lbl_window = tk.Label(
            bar, text="Window: —",
            anchor=tk.W, padx=10, font=("Segoe UI", 9),
        )
        self._lbl_window.pack(side=tk.LEFT)

        tk.Label(bar, text="│", fg="#555").pack(side=tk.LEFT)

        self._lbl_keys = tk.Label(
            bar, text="Keys: 0",
            anchor=tk.W, padx=10, font=("Segoe UI", 9),
        )
        self._lbl_keys.pack(side=tk.LEFT)

    # ------------------------------------------------------------------
    # Recording control
    # ------------------------------------------------------------------

    def _start_recording(self) -> None:
        try:
            self._file_logger.start_session()
        except LogWriteError as exc:
            messagebox.showerror("Log Error", str(exc))
            return

        self._is_recording = True
        self._keys_captured = 0
        self._window_tracker.start()
        self._listener.start()

        self._btn_start.config(state=tk.DISABLED)
        self._btn_stop.config(state=tk.NORMAL)
        self._lbl_status.config(text="●  Recording", fg="#2d8a4e")

        self._append_text("=== Recording started ===\n\n")
        self._after_id = self._root.after(self.REFRESH_MS, self._refresh)

    def _stop_recording(self) -> None:
        self._is_recording = False
        if self._after_id is not None:
            self._root.after_cancel(self._after_id)
            self._after_id = None
        self._listener.stop()
        self._window_tracker.stop()
        try:
            self._file_logger.end_session()
        except LogWriteError as exc:
            messagebox.showerror("Log Error", str(exc))

        self._btn_start.config(state=tk.NORMAL)
        self._btn_stop.config(state=tk.DISABLED)
        self._lbl_status.config(text="■  Stopped", fg="#c0392b")
        self._append_text("\n=== Recording stopped ===\n")

    # ------------------------------------------------------------------
    # Queue drain (called every REFRESH_MS ms)
    # ------------------------------------------------------------------

    def _refresh(self) -> None:
        if not self._is_recording:
            return

        while True:
            try:
                event = self._queue.get_nowait()
            except queue.Empty:
                break

            # Write to disk
            try:
                self._file_logger.write_event(event)
            except LogWriteError as exc:
                messagebox.showerror("Log Error", str(exc))

            # Update GUI
            if isinstance(event, KeyEvent):
                self._keys_captured += 1
                self._append_text(f"[{event.timestamp}] {event.key}\n")
                self._lbl_keys.config(text=f"Keys: {self._keys_captured}")
            elif isinstance(event, WindowEvent):
                short_title = event.title[:35]
                self._current_window = short_title
                self._append_text(
                    f"\n--- [{event.title}] @ {event.timestamp} ---\n"
                )
                self._lbl_window.config(text=f"Window: {short_title}")

            self._queue.task_done()

        self._after_id = self._root.after(self.REFRESH_MS, self._refresh)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _append_text(self, text: str) -> None:
        self._text.config(state=tk.NORMAL)
        self._text.insert(tk.END, text)
        self._text.see(tk.END)
        self._text.config(state=tk.DISABLED)

    def _open_logs_folder(self) -> None:
        self._logs_dir.mkdir(parents=True, exist_ok=True)
        os.startfile(str(self._logs_dir.resolve()))

    def _on_close(self) -> None:
        if self._is_recording:
            self._stop_recording()
        self._root.destroy()
