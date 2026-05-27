import queue
import time
import pytest
from src.events import WindowEvent
from src.window_tracker import WindowTracker


@pytest.fixture
def make_tracker():
    """Factory: returns (tracker, queue). Override _get_active_window_title before calling start()."""
    trackers = []

    def factory():
        q = queue.Queue()
        t = WindowTracker(q)
        t.POLL_INTERVAL = 0.05  # Fast polling for tests
        trackers.append(t)
        return t, q

    yield factory

    for t in trackers:
        t.stop()


def test_emits_event_on_first_non_empty_window(make_tracker):
    tracker, q = make_tracker()
    tracker._get_active_window_title = lambda: "Notepad"
    tracker.start()
    time.sleep(0.2)
    tracker.stop()

    events = list(q.queue)
    titles = [e.title for e in events if isinstance(e, WindowEvent)]
    assert "Notepad" in titles


def test_emits_event_when_window_changes(make_tracker):
    tracker, q = make_tracker()
    call_count = [0]

    def titles():
        call_count[0] += 1
        return "Notepad" if call_count[0] <= 3 else "Chrome"

    tracker._get_active_window_title = titles
    tracker.start()
    time.sleep(0.5)
    tracker.stop()

    events = list(q.queue)
    titles_seen = [e.title for e in events if isinstance(e, WindowEvent)]
    assert "Notepad" in titles_seen
    assert "Chrome" in titles_seen


def test_no_duplicate_events_for_same_window(make_tracker):
    tracker, q = make_tracker()
    tracker._get_active_window_title = lambda: "Notepad"
    tracker.start()
    time.sleep(0.3)
    tracker.stop()

    events = list(q.queue)
    window_events = [e for e in events if isinstance(e, WindowEvent)]
    assert len(window_events) == 1


def test_empty_title_does_not_emit(make_tracker):
    tracker, q = make_tracker()
    tracker._get_active_window_title = lambda: ""
    tracker.start()
    time.sleep(0.2)
    tracker.stop()

    assert q.empty()


def test_exception_in_get_title_does_not_crash_tracker(make_tracker):
    tracker, q = make_tracker()

    def raise_error():
        raise OSError("access denied")

    tracker._get_active_window_title = raise_error
    tracker.start()
    time.sleep(0.2)
    tracker.stop()  # Must not raise

    assert q.empty()
