# Educational Keylogger

> ⚠️ **For authorized educational and research use only.**
> See [DISCLAIMER.txt](DISCLAIMER.txt) for full terms.

A Python keylogger built for learning how keystroke capture, threading,
and GUI design work. Built with `pynput`, `pywin32`, and `Tkinter`.

## Features
- Real-time keystroke capture with timestamps
- Active window title context (switches log section on window change)
- Daily rotating log file in `logs/`
- Tkinter live-viewer dashboard with Start / Stop controls

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run

```powershell
python main.py
```

## Run Tests

```powershell
pytest tests/ -v
```

## Log Format

```
=== Session started: 2026-05-27 14:30:00 ===

--- [Notepad - Untitled] @ 14:30:05 ---
[14:30:06] H
[14:30:06] e
[14:30:06] l

--- [Google Chrome] @ 14:30:15 ---
[14:30:16] s

=== Session ended: 2026-05-27 14:31:00 ===
```

## How to Detect a Keylogger on Your Machine

- **Task Manager / Process Explorer** — Look for unfamiliar Python processes
- **Autoruns (Sysinternals)** — Check startup entries for unknown scripts
- **Wireshark** — Watch for unexpected outbound traffic from Python
- **Anti-malware scan** — Windows Defender or Malwarebytes
- **Audit log files** — Check `%TEMP%` and `AppData` for unexpected `.log` files
