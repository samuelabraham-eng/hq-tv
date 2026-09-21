import Cocoa
import WebKit

final class AppDelegate: NSObject, NSApplicationDelegate, WKNavigationDelegate {
    private var window: NSWindow!
    private var webView: WKWebView!
    private let boardURL = URL(string: "http://127.0.0.1:9770/")!
    private let alarmURL = URL(string: "http://127.0.0.1:9770/api/alarm")!
    private var attempts = 0

    func applicationDidFinishLaunching(_ notification: Notification) {
        NSApp.setActivationPolicy(.regular)
        buildWindow()
        startServices()
        waitForBoard()
    }

    private func buildWindow() {
        let configuration = WKWebViewConfiguration()
        configuration.websiteDataStore = .default()
        configuration.mediaTypesRequiringUserActionForPlayback = []
        configuration.allowsAirPlayForMediaPlayback = true

        webView = WKWebView(frame: .zero, configuration: configuration)
        webView.navigationDelegate = self

        let frame = NSRect(x: 0, y: 0, width: 1600, height: 980)
        window = NSWindow(
            contentRect: frame,
            styleMask: [.titled, .closable, .miniaturizable, .resizable, .fullSizeContentView],
            backing: .buffered,
            defer: false
        )
        window.title = "Samuel HQ"
        window.titleVisibility = .hidden
        window.titlebarAppearsTransparent = true
        window.minSize = NSSize(width: 960, height: 640)
        window.contentView = webView
        window.center()
        window.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)
    }

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
                    self.webView.load(URLRequest(
                        url: self.boardURL,
                        cachePolicy: .reloadIgnoringLocalCacheData,
                        timeoutInterval: 5
                    ))
                    return
                }
                self.attempts += 1
                if self.attempts == 10 { self.showStartingState() }
                DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
                    self.waitForBoard()
                }
            }
        }.resume()
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
