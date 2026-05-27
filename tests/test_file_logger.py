import pytest
import time
from pathlib import Path
from src.events import KeyEvent, WindowEvent
from src.file_logger import FileLogger, LogWriteError


@pytest.fixture
def logger(tmp_path):
    return FileLogger(logs_dir=str(tmp_path / "logs"))


def test_logs_dir_created_automatically(tmp_path):
    logs_dir = tmp_path / "logs"
    assert not logs_dir.exists()
    FileLogger(logs_dir=str(logs_dir))
    assert logs_dir.exists()


def test_format_key_event(logger):
    event = KeyEvent(key="a", timestamp="12:00:00")
    assert logger._format_event(event) == "[12:00:00] a"


def test_format_special_key_event(logger):
    event = KeyEvent(key="[ENTER]", timestamp="12:00:01")
    assert logger._format_event(event) == "[12:00:01] [ENTER]"


def test_format_window_event(logger):
    event = WindowEvent(title="Notepad", timestamp="12:00:02")
    result = logger._format_event(event)
    assert "--- [Notepad] @ 12:00:02 ---" in result


def test_session_header_written_on_start(logger, tmp_path):
    logger.start_session()
    logger.end_session()
    log_files = list((tmp_path / "logs").glob("keylog_*.log"))
    assert len(log_files) == 1
    content = log_files[0].read_text(encoding="utf-8")
    assert "Session started" in content
    assert "Session ended" in content


def test_key_event_written_to_file(logger, tmp_path):
    logger.start_session()
    logger.write_event(KeyEvent(key="x", timestamp="10:00:00"))
    logger.end_session()
    content = list((tmp_path / "logs").glob("keylog_*.log"))[0].read_text(encoding="utf-8")
    assert "[10:00:00] x" in content


def test_window_event_written_to_file(logger, tmp_path):
    logger.start_session()
    logger.write_event(WindowEvent(title="TestWindow", timestamp="10:00:01"))
    logger.end_session()
    content = list((tmp_path / "logs").glob("keylog_*.log"))[0].read_text(encoding="utf-8")
    assert "--- [TestWindow] @ 10:00:01 ---" in content


def test_appends_across_two_sessions(tmp_path):
    logs_dir = str(tmp_path / "logs")
    logger1 = FileLogger(logs_dir=logs_dir)
    logger1.start_session()
    logger1.write_event(KeyEvent(key="a", timestamp="10:00:00"))
    logger1.end_session()

    logger2 = FileLogger(logs_dir=logs_dir)
    logger2.start_session()
    logger2.write_event(KeyEvent(key="b", timestamp="10:00:01"))
    logger2.end_session()

    log_files = list((tmp_path / "logs").glob("keylog_*.log"))
    assert len(log_files) == 1
    content = log_files[0].read_text(encoding="utf-8")
    assert "[10:00:00] a" in content
    assert "[10:00:01] b" in content
