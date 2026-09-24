"""TV14, the tile board: the deployed layout carrying the live wiring.

Two things get tested here that a screenshot cannot catch. First, that the
DESIGN-LOCK skin survived the move (TV14 took index.html's tiles, so every
locked token must still be the locked value, not a lookalike). Second, that
the honesty rules survived: money that goes stale must stop being shown, and
a bank that needs signing in must not be able to render as a normal number.
"""
from pathlib import Path


BOARD = Path(__file__).resolve().parents[1] / "TV14-board.html"
DEPLOYED = Path(__file__).resolve().parents[1] / "index.html"


def source():
    return BOARD.read_text(encoding="utf-8")


# ------------------------------------------------------------- the skin

def test_locked_noir_tokens_are_preserved():
    html = source()
    for token in (
        "--ground:#100e0c",
        "--tile:#1a1512",
        "--tile2:#211b16",
        "--line:#2a241d",
        "--bone:#f1ebdf",
        "--dim:#8a8073",
        "--accent:#c9a96a",
        "--alert:#d0402e",
        "--ok:#7e9b7a",
    ):
        assert token in html, f"DESIGN-LOCK token missing: {token}"


def test_the_skin_matches_the_board_it_was_taken_from():
    """TV14 is the deployed layout. If noir ever drifts, it drifts in both."""
    noir = "--ground:#100e0c; --tile:#1a1512; --tile2:#211b16; --line:#2a241d;"
    assert noir in source()
    assert noir in DEPLOYED.read_text(encoding="utf-8")


def test_browser_does_not_request_a_missing_favicon():
    """A 404 on every load is noise in the console the contract watches."""
    assert '<link rel="icon" href="data:,">' in source()


def test_font_is_the_locked_one():
    assert "Plus+Jakarta+Sans" in source()


def test_no_em_dashes_in_surface_copy():
    html = source()
    assert "—" not in html
    assert "&mdash;" not in html


# ------------------------------------------------------------- the layout

def test_every_zone_from_the_live_board_survived_the_move():
    html = source()
    for tile in ("tNeed", "tConn", "tSpend", "tSys", "tMoney", "tToday", "tAlerts"):
        assert f'id="{tile}"' in html, f"zone lost in the reskin: {tile}"


def test_the_gold_tile_carries_one_thing_not_a_list():
    """A list of urgent things is not an urgent thing. It renders one."""
    html = source()
    assert "function renderNeedsYou" in html
    body = html[html.index("function renderNeedsYou"):]
    body = body[:body.index("\nfunction ")]
    # every branch assigns a single headline, none of them loops
    assert ".forEach" not in body
    assert "worstConn.headline" in body


def test_a_dead_credential_outranks_a_struggling_system():
    html = source()
    body = html[html.index("function renderNeedsYou"):]
    body = body[:body.index("\nfunction ")]
    assert body.index("if (worstConn)") < body.index("if (down.length)")


# ------------------------------------------------------------- honesty

def test_stale_money_renders_nothing_rather_than_old_numbers():
    html = source()
    body = html[html.index("function renderMoney"):]
    body = body[:body.index("\nfunction ")]
    stale = body[body.index("m.state === 'stale'"):]
    stale = stale[:stale.index("// spend tile")]
    assert "not re-checked, so not shown" in stale
    assert "m.spent" not in stale


def test_a_bank_needing_sign_in_makes_the_money_tile_loud():
    html = source()
    assert "m.needs_you && m.needs_you.length" in html
    assert "' hot'" in html


def test_an_unreachable_board_stops_claiming_the_connections_are_fresh():
    html = source()
    assert "function markConnectionsUnreachable" in html
    assert "board unreachable, last read" in html


def test_alerts_wrap_instead_of_being_cut_mid_word():
    """An ellipsed alert is an unread alert. TV13 learned this the hard way."""
    html = source()
    assert "row.wrap" in html
    assert "-webkit-line-clamp:2" in html


def test_board_payload_never_reaches_inner_html():
    """Every live value goes through textContent, so a merchant name cannot
    become markup. The only innerHTML writes are fixed strings we authored."""
    html = source()
    js = html[html.index("<script>"):]
    for line in js.split("\n"):
        if ".innerHTML" not in line or "=" not in line:
            continue
        value = line.split("=", 1)[1].strip()
        assert value.startswith(("'", '"', "''")), f"dynamic innerHTML: {line.strip()}"


# ------------------------------------------------------------- money privacy

def test_money_can_be_hidden_without_collapsing_the_tile():
    """The TV is in a room he films in. Privacy hides amounts, not structure."""
    html = source()
    assert "body.privacy .privhide{display:none}" in html
    assert 'class="st privhide"' in html or "'st privhide'" in html
    assert "amounts hidden" in html


def test_privacy_leaves_the_merchant_names_readable():
    html = source()
    body = html[html.index("function renderMoney"):]
    body = body[:body.index("\nfunction ")]
    # the name span is never given the privhide class, only the amount is
    assert "nm.className = 'nm'" in body
    assert "nm.className = 'nm privhide'" not in body


def test_privacy_survives_a_reload():
    assert "samuel-hq-privacy-v1" in source()


def test_storage_failures_cannot_blank_the_board():
    """A private window throws on localStorage. The board must still render."""
    html = source()
    js = html[html.index("<script>"):]
    for key in ("samuel-hq-privacy-v1", "samuel-hq-theme-v1"):
        idx = js.index(key)
        window = js[max(0, idx - 400):idx + 400]
        assert "try {" in window and "catch" in window


# ------------------------------------------------------------- monday

def test_monday_can_be_closed_and_muted_from_the_board():
    html = source()
    assert 'id="wakeClose"' in html
    assert 'id="wakeMute"' in html
    assert "type: 'cancel'" in html
    assert "type: 'mute'" in html


def test_the_veil_restores_pointer_events_when_shown():
    """Without this the X is painted but unclickable. Found in a real browser."""
    assert ".veil.show{opacity:1;pointer-events:auto}" in source()


def test_monday_controls_do_not_move_while_she_talks():
    """The transcript grows; the button he reaches for must not slide with it."""
    html = source()
    assert "min-height:min(38vh,340px)" in html
    assert "margin-top:auto" in html
    assert "-webkit-line-clamp:3" in html


# ------------------------------------------------------------- the app

APP = Path(__file__).resolve().parents[1] / "app-bundle" / "SamuelHQ.swift"


def app_source():
    return APP.read_text(encoding="utf-8")


def test_the_app_is_a_one_display_kiosk_not_a_fullscreen_app():
    """Native fullscreen makes a Space, and a Space takes the whole Mac. He
    asked for a board on one monitor while he keeps using the other."""
    swift = app_source()
    assert ".fullScreenNone" in swift
    assert ".canJoinAllSpaces" in swift
    assert ".stationary" in swift
    assert "styleMask: [.borderless]" in swift
    assert "toggleFullScreen" not in swift


def test_the_board_keeps_drawing_while_he_works_on_the_other_screen():
    assert "hidesOnDeactivate = false" in app_source()


def test_a_borderless_window_can_still_take_the_keyboard():
    """Without this Cmd+Q dies and the alarm never gets its unlock gesture."""
    swift = app_source()
    assert "override var canBecomeKey: Bool { true }" in swift


def test_there_is_always_a_way_out_of_a_window_with_no_title_bar():
    swift = app_source()
    assert "NSStatusBar.system.statusItem" in swift
    assert "Quit Samuel HQ" in swift


def test_the_chosen_display_survives_a_reboot_and_a_replug():
    swift = app_source()
    assert "SamuelHQChosenScreen" in swift
    assert "didChangeScreenParametersNotification" in swift
    # display IDs are not stable everywhere, so the name is the second chance
    assert "SamuelHQChosenScreenName" in swift


def test_it_defaults_to_the_external_display():
    """The built in screen is the computer he is trying to keep using."""
    swift = app_source()
    body = swift[swift.index("private func targetScreen()"):]
    body = body[:body.index("\n    private func placeOnScreen")]
    assert "$0 != NSScreen.main" in body


def test_mirrored_displays_are_reported_rather_than_faked():
    """The one setup the app cannot satisfy. It says so instead of covering
    both screens with the same picture and calling it done."""
    swift = app_source()
    assert "CGDisplayIsInMirrorSet(displayID) != 0" in swift
    # the master of a mirror set mirrors nobody, so this extra clause was a bug
    assert "CGDisplayIsInMirrorSet(displayID) != 0 && CGDisplayMirrorsDisplay" not in swift
    assert "mirrored" in swift.lower()
