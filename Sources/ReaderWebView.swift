import SwiftUI
import WebKit
import UIKit

struct RenderPayload: Codable {
    var lessonId: String
    var title: String
    var subtitle: String
    var cards: [Card]
    var progress: [String: Bool]
    var fontSize: Double
    var scrollY: Double
    var theme: String
}

struct ReaderWebView: UIViewRepresentable {
    let lesson: Lesson
    var scrollY: Double = 0
    var onScroll: ((Double) -> Void)? = nil
    var onCopyTex: ((String) -> Void)? = nil
    @EnvironmentObject var store: Store

    func makeCoordinator() -> Coordinator {
        Coordinator(lesson: lesson, scrollY: scrollY, onScroll: onScroll, onCopyTex: onCopyTex)
    }

    func makeUIView(context: Context) -> WKWebView {
        let conf = WKWebViewConfiguration()
        conf.allowsInlineMediaPlayback = true
        conf.userContentController.add(context.coordinator, name: "hub")

        let wv = WKWebView(frame: .zero, configuration: conf)
        wv.isOpaque = false
        wv.backgroundColor = .clear
        wv.scrollView.backgroundColor = .clear
        wv.navigationDelegate = context.coordinator
        wv.allowsBackForwardNavigationGestures = false
        context.coordinator.webView = wv

        if let url = Bundle.main.url(forResource: "reader", withExtension: "html", subdirectory: "web") {
            wv.loadFileURL(url, allowingReadAccessTo: url.deletingLastPathComponent())
        } else {
            wv.loadHTMLString("<meta name='viewport' content='width=device-width'><h3 style='font-family:-apple-system;padding:24px'>reader.html 没有打进包里</h3>", baseURL: nil)
        }
        return wv
    }

    func updateUIView(_ uiView: WKWebView, context: Context) {
        context.coordinator.update(lesson: lesson,
                                   progress: store.progressDict(lesson: lesson),
                                   fontSize: store.fontSize,
                                   theme: store.theme)
    }

    static func dismantleUIView(_ uiView: WKWebView, coordinator: Coordinator) {
        uiView.configuration.userContentController.removeScriptMessageHandler(forName: "hub")
    }

    final class Coordinator: NSObject, WKScriptMessageHandler, WKNavigationDelegate {
        var lesson: Lesson
        var progress: [String: Bool] = [:]
        var fontSize: Double = 17
        var scrollY: Double = 0
        var theme: String = "auto"
        var onScroll: ((Double) -> Void)?
        var onCopyTex: ((String) -> Void)?
        weak var webView: WKWebView?
        private var ready = false
        private var lastJSON = ""

        init(lesson: Lesson, scrollY: Double = 0,
             onScroll: ((Double) -> Void)? = nil,
             onCopyTex: ((String) -> Void)? = nil) {
            self.lesson = lesson
            self.scrollY = scrollY
            self.onScroll = onScroll
            self.onCopyTex = onCopyTex
        }

        func update(lesson: Lesson, progress: [String: Bool], fontSize: Double, theme: String) {
            self.lesson = lesson
            self.progress = progress
            self.fontSize = fontSize
            self.theme = theme
            push()
        }

        func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
            ready = true
            push(force: true)
        }

        func push(force: Bool = false) {
            guard ready, let wv = webView else { return }
            let payload = RenderPayload(lessonId: lesson.id,
                                        title: lesson.title,
                                        subtitle: lesson.subtitle ?? "",
                                        cards: lesson.cards,
                                        progress: progress,
                                        fontSize: fontSize,
                                        scrollY: scrollY,
                                        theme: theme)
            guard let data = try? JSONEncoder().encode(payload),
                  var json = String(data: data, encoding: .utf8) else { return }
            json = json.replacingOccurrences(of: "\u{2028}", with: "\\u2028")
                       .replacingOccurrences(of: "\u{2029}", with: "\\u2029")
            guard force || json != lastJSON else { return }
            lastJSON = json
            wv.evaluateJavaScript("window.renderStudyHub(\(json));", completionHandler: nil)
        }

        func userContentController(_ userContentController: WKUserContentController,
                                   didReceive message: WKScriptMessage) {
            guard message.name == "hub", let body = message.body as? [String: Any] else { return }
            let type = body["type"] as? String ?? ""

            if type == "answer" {
                let cardId = body["cardId"] as? String ?? ""
                let correct = body["correct"] as? Bool ?? false
                let preview = body["preview"] as? String ?? ""
                let lessonId = lesson.id
                let lessonTitle = lesson.title
                let store = StoreLocator.shared.store
                Task { @MainActor in
                    store?.record(lessonId: lessonId, lessonTitle: lessonTitle,
                                  cardId: cardId, correct: correct, preview: preview)
                }
            } else if type == "ready" {
                push(force: true)
            } else if type == "scroll" {
                if let y = body["y"] as? Double {
                    onScroll?(y)
                }
            } else if type == "copy", let tex = body["tex"] as? String {
                onCopyTex?(tex)
            } else if type == "openURL", let s = body["url"] as? String, let u = URL(string: s) {
                UIApplication.shared.open(u)
            } else if type == "haptic" {
                let g = UIImpactFeedbackGenerator(style: .light)
                g.impactOccurred()
            }
        }
    }
}

// 用弱引用把 Store 交给 Coordinator，避免非隔离上下文访问 @MainActor 属性
final class StoreLocator {
    static let shared = StoreLocator()
    weak var store: Store?
}
