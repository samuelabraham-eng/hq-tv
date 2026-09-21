from pathlib import Path


BOARD = Path(__file__).resolve().parents[1] / "TV13-live-board.html"
LAUNCHER = Path(__file__).resolve().parents[1] / "app-bundle" / "SamuelHQ-launcher.sh"
APP_SOURCE = Path(__file__).resolve().parents[1] / "app-bundle" / "SamuelHQ.swift"


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


def test_live_board_restores_the_proven_alarm_wake_path():
    html = source()
    assert 'id="dawn"' in html
    assert 'id="wakeAlarm"' in html
    assert "function paintSunrise" in html
    assert "function checkAlarm" in html
    assert "function fireAlarm" in html
    assert "function startTone" in html
    assert '"pointerdown","keydown","touchstart"' in html
    assert "HOLD_MS = 1600" in html
    assert "MAX_SNOOZES = 3" in html


def test_alarm_firing_uses_the_clock_not_the_countdown_hint():
    html = source()
    check_alarm = html.split("function checkAlarm", 1)[1].split("function", 1)[0]
    assert "target.setHours" in check_alarm
    assert "now.getTime()" in check_alarm
    assert "fires_in_s" not in check_alarm


def test_alarm_countdown_cannot_render_sixty_minutes():
    html = source()
    assert "Math.ceil(a.fires_in_s / 60)" in html
    assert "totalMinutes % 60" in html


def test_alarm_runtime_survives_reload_and_has_a_small_missed_minute_window():
    html = source()
    assert "localStorage" in html
    assert "ALARM_RUNTIME_KEY" in html
    assert "CATCH_UP_MS" in html
    assert "persistAlarmRuntime" in html


def test_disabled_alarm_is_checked_before_a_pending_snooze():
    html = source()
    check_alarm = html.split("function checkAlarm", 1)[1].split("function", 1)[0]
    assert check_alarm.index("alarmParts()") < check_alarm.index("snoozeUntil")


def test_alarm_state_rejects_older_updated_at_values():
    html = source()
    assert "function adoptAlarm" in html
    assert "updated_at" in html
    assert "incomingEpoch < acceptedAlarmEpoch" in html


def test_mac_app_launches_monday_without_a_duplicate_board_and_allows_alarm_audio():
    launcher = LAUNCHER.read_text(encoding="utf-8")
    assert "--args --background" in launcher
    assert "--autoplay-policy=no-user-gesture-required" in launcher
    app = APP_SOURCE.read_text(encoding="utf-8")
    assert 'configuration.arguments = ["--background"]' in app
    assert "mediaTypesRequiringUserActionForPlayback = []" in app
    assert 'window.title = "Samuel HQ"' in app


def test_board_surfaces_microphone_permission_and_hides_inactive_alarm_dialog():
    html = source()
    assert "microphone permission needed" in html
    assert "micAvailable !== true" in html
    assert "checking microphone" in html
    assert 'id="wakeAlarm" role="dialog"' in html
    assert 'aria-hidden="true"' in html
    assert "setAttribute('aria-hidden', 'false')" in html


# ---- connections strip: the credential layer (Sept 21 2026) ----------------
# Samuel: "if it cant ping the turo system or school system say it needs to sing
# in this live app needs to be connected to everything and acc work correctly or
# its useles". These lock the behaviour that makes that true.

def test_connections_strip_exists_and_reads_the_board_payload():
    html = source()
    assert 'id="conn"' in html
    assert "function renderConnections" in html
    assert "renderConnections(d.connections)" in html


def test_connection_action_text_is_never_truncated():
    """The half of the line that tells him what to do is the half that got cut."""
    html = source()
    conn_css = html.split(".cc .ca{")[1].split("}")[0]
    assert "text-overflow" not in conn_css
    assert "white-space:nowrap" not in conn_css
    assert "line-height" in conn_css


def test_sign_in_states_are_loud_and_the_calm_state_is_quiet():
    html = source()
    assert "CONN_BAD = ['needs_sign_in', 'needs_approval', 'offline']" in html
    assert "'1 thing needs you'" in html
    assert "'everything is connected'" in html
    assert ".conn.needs{border-color:var(--red)}" in html


def test_connections_never_claim_a_verdict_nobody_rechecked():
    html = source()
    assert "'never checked'" in html
    assert "'connection probe has not run'" in html


def test_systems_detail_wraps_instead_of_ellipsing():
    html = source()
    sys_css = html.split(".s .d{")[1].split("}")[0]
    assert "text-overflow:ellipsis" not in sys_css
    assert "-webkit-line-clamp:2" in sys_css


# ---- monday dismiss (Sept 21 2026) ----------------------------------------
# "neesd an X button the monday stuff when monday doesnt work correctly and i
# dont want to say close out"

def test_monday_card_has_a_real_close_button():
    html = source()
    assert 'id="wakeClose"' in html
    assert 'aria-label="close monday"' in html
    assert "$('wakeClose').addEventListener('click', closeWake)" in html


def test_closing_cancels_her_turn_instead_of_only_hiding_the_card():
    html = source()
    assert "sendMonday({ type: 'cancel' })" in html
    assert "suppressVeilUntil" in html


def test_escape_key_closes_the_card_too():
    html = source()
    assert "event.key === 'Escape'" in html


def test_mute_and_unmute_are_buttons_not_voice_only():
    html = source()
    assert 'id="wakeMute"' in html
    assert 'id="mUnmute"' in html
    assert "sendMonday({ type: 'mute', minutes: minutes })" in html
    assert "monday is muted for" in html


def test_close_targets_meet_the_44px_touch_rule():
    html = source()
    wx = html.split(".wx{")[1].split("}")[0]
    assert "width:46px" in wx and "height:46px" in wx
    mute = html.split(".wmute{")[1].split("}")[0]
    assert "min-height:44px" in mute


def test_the_card_accepts_clicks_when_it_is_shown():
    """It rendered perfectly and swallowed every click: .veil.show never restored
    pointer-events, so the X was decorative until a real browser test found it."""
    html = source()
    assert ".veil.show{opacity:1;pointer-events:auto}" in html
