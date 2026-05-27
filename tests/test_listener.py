import pytest
from pynput import keyboard
from src.listener import format_key


def test_lowercase_alpha():
    key = keyboard.KeyCode.from_char("a")
    assert format_key(key) == "a"


def test_uppercase_alpha():
    key = keyboard.KeyCode.from_char("A")
    assert format_key(key) == "A"


def test_digit():
    key = keyboard.KeyCode.from_char("5")
    assert format_key(key) == "5"


def test_symbol():
    key = keyboard.KeyCode.from_char("!")
    assert format_key(key) == "!"


def test_enter():
    assert format_key(keyboard.Key.enter) == "[ENTER]"


def test_space():
    assert format_key(keyboard.Key.space) == "[SPACE]"


def test_backspace():
    assert format_key(keyboard.Key.backspace) == "[BACKSPACE]"


def test_tab():
    assert format_key(keyboard.Key.tab) == "[TAB]"


def test_ctrl_left():
    assert format_key(keyboard.Key.ctrl_l) == "[CTRL]"


def test_ctrl_right():
    assert format_key(keyboard.Key.ctrl_r) == "[CTRL]"


def test_alt_left():
    assert format_key(keyboard.Key.alt_l) == "[ALT]"


def test_alt_right():
    assert format_key(keyboard.Key.alt_r) == "[ALT]"


def test_shift_left():
    assert format_key(keyboard.Key.shift) == "[SHIFT]"


def test_shift_right():
    assert format_key(keyboard.Key.shift_r) == "[SHIFT]"


def test_caps_lock():
    assert format_key(keyboard.Key.caps_lock) == "[CAPS]"


def test_delete():
    assert format_key(keyboard.Key.delete) == "[DEL]"


def test_escape():
    assert format_key(keyboard.Key.esc) == "[ESC]"


def test_arrow_up():
    assert format_key(keyboard.Key.up) == "[UP]"


def test_arrow_down():
    assert format_key(keyboard.Key.down) == "[DOWN]"


def test_f1_key():
    # F-keys fall back to name.upper() pattern
    assert format_key(keyboard.Key.f1) == "[F1]"


def test_f12_key():
    assert format_key(keyboard.Key.f12) == "[F12]"
