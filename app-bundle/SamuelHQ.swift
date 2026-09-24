import Cocoa
import WebKit

// Samuel HQ.app
//
// Samuel, Sept 24 2026: "similar to how for fortnite i can put my fortnite on one
// monitor and fullscreen it and still use my computer on the other".
//
// So this is a KIOSK ON ONE DISPLAY, not a fullscreen app. The difference matters:
// macOS native fullscreen creates its own Space, and a Space steals the whole Mac
// the moment he clicks the other monitor. Instead the window is borderless, sized
// to the chosen screen's frame, joins every Space, and never hides when it loses
// focus. He clicks the laptop, the board just keeps running over there, exactly
// like a game on a second monitor.

private let boardURL = URL(string: "http://127.0.0.1:9770/")!
private let alarmURL = URL(string: "http://127.0.0.1:9770/api/alarm")!
private let screenKey = "SamuelHQChosenScreen"
private let screenNameKey = "SamuelHQChosenScreenName"
private let onTopKey = "SamuelHQKeepOnTop"

/// A borderless window still has to take the keyboard, or Cmd+Q dies with it and
/// the alarm never gets its "press any button once" gesture.
final class KioskWindow: NSWindow {
    override var canBecomeKey: Bool { true }
    override var canBecomeMain: Bool { true }
}

extension NSScreen {
    var displayID: CGDirectDisplayID {
        let key = NSDeviceDescriptionKey("NSScreenNumber")
        return (deviceDescription[key] as? NSNumber)?.uint32Value ?? 0
    }

    /// True when this screen is a mirror of another one. Mirrored displays are a
    /// single logical screen to AppKit, so "put it on the other monitor" is not
    /// something the app can do until he turns mirroring off himself.
    /// CGDisplayIsInMirrorSet alone is the right test. The extra
    /// CGDisplayMirrorsDisplay check that was here first missed his actual setup:
    /// the LG is the MASTER of the mirror set, so it mirrors nobody and reported
    /// 0, and the warning never fired on the one machine it was written for.
    var isMirrored: Bool {
        CGDisplayIsInMirrorSet(displayID) != 0
    }
}

final class AppDelegate: NSObject, NSApplicationDelegate, WKNavigationDelegate {
    private var window: KioskWindow!
    private var webView: WKWebView!
    private var statusItem: NSStatusItem!
    private var attempts = 0
    private var boardLoaded = false

    func applicationDidFinishLaunching(_ notification: Notification) {
        NSApp.setActivationPolicy(.regular)
        buildWindow()
        buildMenu()
        buildStatusItem()
        startServices()
        waitForBoard()

        // A monitor being unplugged, replugged, or rearranged must not strand the
        // board off screen or leave it sized for a display that is gone.
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(screensChanged),
            name: NSApplication.didChangeScreenParametersNotification,
            object: nil
        )
    }

    // MARK: - which display

    /// His chosen screen if it is still attached, otherwise the biggest external
    /// one, otherwise whatever there is. Never returns nil while a screen exists.
    private func targetScreen() -> NSScreen? {
        let screens = NSScreen.screens
        guard !screens.isEmpty else { return nil }

        let saved = CGDirectDisplayID(UserDefaults.standard.integer(forKey: screenKey))
        if saved != 0, let match = screens.first(where: { $0.displayID == saved }) {
            return match
        }
        // displayIDs are not stable across reboots on every Mac, so the name is a
        // second chance before we fall back to guessing.
        if let name = UserDefaults.standard.string(forKey: screenNameKey),
           let match = screens.first(where: { $0.localizedName == name }) {
            return match
        }
        // Default: the external display, because the built in one is the computer
        // he is trying to keep using.
        let external = screens.filter { $0 != NSScreen.main }
        return external.max(by: { $0.frame.width < $1.frame.width }) ?? screens.first
    }

    private func placeOnScreen(_ screen: NSScreen) {
        window.setFrame(screen.frame, display: true)
        UserDefaults.standard.set(Int(screen.displayID), forKey: screenKey)
        UserDefaults.standard.set(screen.localizedName, forKey: screenNameKey)
        applyLevel()
        window.makeKeyAndOrderFront(nil)
    }

    private func applyLevel() {
        let onTop = UserDefaults.standard.bool(forKey: onTopKey)
        // .normal lets him drop a window on that display when he wants to. The
        // "keep on top" toggle is for when the board is the only thing allowed
        // there, and it covers the menu bar too.
        window.level = onTop ? NSWindow.Level(Int(CGWindowLevelForKey(.mainMenuWindow)) + 1)
                             : .normal
    }

    @objc private func screensChanged() {
        guard let screen = targetScreen() else { return }
        placeOnScreen(screen)
        buildStatusMenu()
        if boardLoaded { reportMirroring() }
    }

    // MARK: - window

    private func buildWindow() {
        let configuration = WKWebViewConfiguration()
        configuration.websiteDataStore = .default()
        configuration.mediaTypesRequiringUserActionForPlayback = []
        configuration.allowsAirPlayForMediaPlayback = true

        webView = WKWebView(frame: .zero, configuration: configuration)
        webView.navigationDelegate = self
        webView.setValue(false, forKey: "drawsBackground")

        let screen = targetScreen()
        window = KioskWindow(
            contentRect: screen?.frame ?? NSRect(x: 0, y: 0, width: 1600, height: 980),
            styleMask: [.borderless],
            backing: .buffered,
            defer: false
        )
        window.title = "Samuel HQ"
        window.contentView = webView
        window.backgroundColor = NSColor(red: 0.063, green: 0.055, blue: 0.047, alpha: 1)
        window.isOpaque = true
        window.hasShadow = false

        // The three behaviours that make it a second monitor board rather than a
        // fullscreen app: it shows on every Space, it does not travel between
        // them, and it refuses native fullscreen entirely.
        window.collectionBehavior = [.canJoinAllSpaces, .stationary, .fullScreenNone]
        window.hidesOnDeactivate = false
        window.isMovableByWindowBackground = false

        if let screen { placeOnScreen(screen) } else { window.center() }
        window.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)
    }

    // MARK: - menus, the only way out of a borderless window

    private func buildMenu() {
        let main = NSMenu()
        let appItem = NSMenuItem()
        let appMenu = NSMenu()
        appMenu.addItem(withTitle: "Reload the board",
                        action: #selector(reloadBoard), keyEquivalent: "r")
        appMenu.addItem(NSMenuItem.separator())
        appMenu.addItem(withTitle: "Hide Samuel HQ",
                        action: #selector(NSApplication.hide(_:)), keyEquivalent: "h")
        appMenu.addItem(withTitle: "Quit Samuel HQ",
                        action: #selector(NSApplication.terminate(_:)), keyEquivalent: "q")
        appItem.submenu = appMenu
        main.addItem(appItem)
        NSApp.mainMenu = main
    }

    private func buildStatusItem() {
        statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.squareLength)
        statusItem.button?.title = "\u{25A0}"
        statusItem.button?.toolTip = "Samuel HQ"
        buildStatusMenu()
    }

    /// Rebuilt whenever the displays change, so the list is never a lie.
    private func buildStatusMenu() {
        let menu = NSMenu()
        let screens = NSScreen.screens

        if screens.count == 1 && screens[0].isMirrored {
            let item = NSMenuItem(title: "Displays are mirrored", action: nil, keyEquivalent: "")
            item.isEnabled = false
            menu.addItem(item)
            let fix = NSMenuItem(title: "Open Display settings",
                                 action: #selector(openDisplaySettings), keyEquivalent: "")
            fix.target = self
            menu.addItem(fix)
        } else {
            let header = NSMenuItem(title: "Show the board on", action: nil, keyEquivalent: "")
            header.isEnabled = false
            menu.addItem(header)
            let current = targetScreen()?.displayID
            for screen in screens {
                let builtIn = screen == screens.first && screens.count == 1
                let label = screen.localizedName
                    + (screen == NSScreen.main && !builtIn ? " (main)" : "")
                let item = NSMenuItem(title: label,
                                      action: #selector(chooseScreen(_:)), keyEquivalent: "")
                item.target = self
                item.tag = Int(screen.displayID)
                item.state = screen.displayID == current ? .on : .off
                menu.addItem(item)
            }
        }

        menu.addItem(NSMenuItem.separator())
        let onTop = NSMenuItem(title: "Keep on top of that display",
                               action: #selector(toggleOnTop), keyEquivalent: "")
        onTop.target = self
        onTop.state = UserDefaults.standard.bool(forKey: onTopKey) ? .on : .off
        menu.addItem(onTop)

        let reload = NSMenuItem(title: "Reload the board",
                                action: #selector(reloadBoard), keyEquivalent: "")
        reload.target = self
        menu.addItem(reload)

        menu.addItem(NSMenuItem.separator())
        let quit = NSMenuItem(title: "Quit Samuel HQ",
                              action: #selector(NSApplication.terminate(_:)), keyEquivalent: "")
        menu.addItem(quit)
        statusItem.menu = menu
    }

    @objc private func chooseScreen(_ sender: NSMenuItem) {
        guard let screen = NSScreen.screens.first(where: { Int($0.displayID) == sender.tag })
        else { return }
        placeOnScreen(screen)
        buildStatusMenu()
        reportMirroring()
    }

    @objc private func toggleOnTop() {
        let next = !UserDefaults.standard.bool(forKey: onTopKey)
        UserDefaults.standard.set(next, forKey: onTopKey)
        applyLevel()
        buildStatusMenu()
    }

    @objc private func reloadBoard() {
        attempts = 0
        boardLoaded = false
        waitForBoard()
    }

    @objc private func openDisplaySettings() {
        if let url = URL(string: "x-apple.systempreferences:com.apple.Displays-Settings.extension") {
            NSWorkspace.shared.open(url)
        }
    }

    // MARK: - services

    private func startServices() {
        let board = Process()
        board.executableURL = URL(fileURLWithPath: "/bin/launchctl")
        board.arguments = ["kickstart", "-k", "gui/\(getuid())/com.samuel.boardd"]
        try? board.run()

        let mondayURL = FileManager.default.homeDirectoryForCurrentUser
            .appendingPathComponent("Applications/Monday.app")
        guard FileManager.default.fileExists(atPath: mondayURL.path) else { return }
        let configuration = NSWorkspace.OpenConfiguration()
        configuration.arguments = ["--background"]
        configuration.activates = false
        NSWorkspace.shared.openApplication(
            at: mondayURL,
            configuration: configuration,
            completionHandler: nil
        )
    }

    private func waitForBoard() {
        var request = URLRequest(url: alarmURL)
        request.timeoutInterval = 1
        URLSession.shared.dataTask(with: request) { [weak self] _, response, _ in
            guard let self else { return }
            let ready = (response as? HTTPURLResponse)?.statusCode == 200
            DispatchQueue.main.async {
                if ready {
                    self.boardLoaded = true
                    self.webView.load(URLRequest(
                        url: boardURL,
                        cachePolicy: .reloadIgnoringLocalCacheData,
                        timeoutInterval: 5
                    ))
                    return
                }
                self.attempts += 1
                if self.attempts == 10 { self.showStartingState() }
                DispatchQueue.main.asyncAfter(deadline: .now() + 1) { self.waitForBoard() }
            }
        }.resume()
    }

    /// Mirroring is the one setup where the app cannot do what he asked, and the
    /// honest move is to say so on the board rather than silently covering both
    /// screens with the same picture and calling it done.
    private func reportMirroring() {
        let mirrored = NSScreen.screens.count == 1 && NSScreen.screens[0].isMirrored
        let js = """
        (function(){
          var id='hq-mirror-note', old=document.getElementById(id);
          if(!\(mirrored)){ if(old) old.remove(); return; }
          if(old) return;
          var n=document.createElement('div'); n.id=id;
          n.style.cssText='position:fixed;left:0;right:0;bottom:0;z-index:99;'+
            'background:#1a1512;border-top:2px solid #d0402e;color:#f1ebdf;'+
            'font:500 15px/1.5 -apple-system,sans-serif;padding:12px 22px';
          n.textContent='Your displays are mirrored, so both screens show this. '+
            'Turn mirroring off in System Settings, Displays, then pick a screen '+
            'from the HQ icon in the menu bar.';
          document.body.appendChild(n);
        })();
        """
        webView.evaluateJavaScript(js, completionHandler: nil)
    }

    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation?) {
        reportMirroring()
    }

    private func showStartingState() {
        webView.loadHTMLString("""
        <!doctype html><meta charset="utf-8">
        <style>
        html,body{height:100%;margin:0;background:#100e0c;color:#f1ebdf}
        body{display:grid;place-items:center;font:600 16px/1.5 -apple-system,sans-serif}
        main{text-align:center}h1{color:#c9a96a;font-size:34px;margin:0 0 10px}
        p{color:#9f9588}
        </style>
        <main><h1>samuel hq</h1><p>starting the live board...</p></main>
        """, baseURL: nil)
    }

    func webView(
        _ webView: WKWebView,
        didFailProvisionalNavigation navigation: WKNavigation?,
        withError error: Error
    ) {
        attempts = 10
        boardLoaded = false
        showStartingState()
        DispatchQueue.main.asyncAfter(deadline: .now() + 1) { self.waitForBoard() }
    }

    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
        true
    }
}

let application = NSApplication.shared
let delegate = AppDelegate()
application.delegate = delegate
application.run()
