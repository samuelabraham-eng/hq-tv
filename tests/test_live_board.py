from pathlib import Path


BOARD = Path(__file__).resolve().parents[1] / "TV13-live-board.html"


def source():
    return BOARD.read_text(encoding="utf-8")


def test_locked_noir_tokens_are_preserved():
    html = source()
    for token in (
        "--ground:#100e0c",
        "--tile:#1a1512",
        "--tile2:#211b16",
        "--bone:#f1ebdf",
        "--gold:#c9a96a",
        "--red:#d0402e",
        "--green:#7e9b7a",
    ):
        assert token in html


def test_live_board_has_no_forbidden_surface_copy():
    html = source()
    assert "\u2014" not in html
    assert "&mdash;" not in html
    assert "🚨" not in html
    assert "📌" not in html


def test_alarm_failure_is_visible_and_distinct_from_no_alarm():
    html = source()
    assert "function renderAlarmUnavailable" in html
    assert "alarm status unavailable" in html
    assert "none set" in html


def test_alarm_payload_never_enters_inner_html():
    html = source()
    assert "$('alarmMeta').innerHTML" not in html
    assert "function setAlarmMeta" in html


def test_board_refresh_failure_labels_last_known_content():
    html = source()
    assert "refresh failed, showing last update" in html
    assert "lastBoardUpdate" in html


def test_alerts_use_semantic_severity():
    html = source()
    assert "a.severity" in html
    assert "r.className = 'al ' + severity" in html
    assert ".al.critical" in html
    assert ".al.attention" in html
    assert "a.tier" not in html


def test_reduced_motion_disables_pulse_and_overlay_movement():
    html = source()
    assert "@media (prefers-reduced-motion: reduce)" in html
    assert "animation:none" in html
    assert "transition:none" in html


def test_api_fetches_reject_non_success_responses():
    html = source()
    assert "function expectJson" in html
    assert "if (!r.ok)" in html


def test_browser_does_not_request_a_missing_favicon():
    assert '<link rel="icon" href="data:,">' in source()
