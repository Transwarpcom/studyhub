import SwiftUI
import WebKit
import UIKit

// MARK: - 单题渲染（复用 reader.html）

struct QuizCardView: UIViewRepresentable {
    let item: QuizItem
    let fontSize: Double
    var onAnswer: (Bool) -> Void

    func makeCoordinator() -> Coord {
        Coord(item: item, fontSize: fontSize, onAnswer: onAnswer)
    }

    func makeUIView(context: Context) -> WKWebView {
        let conf = WKWebViewConfiguration()
        conf.userContentController.add(context.coordinator, name: "hub")
        let wv = WKWebView(frame: .zero, configuration: conf)
        wv.isOpaque = false
        wv.backgroundColor = .clear
        wv.scrollView.backgroundColor = .clear
        wv.navigationDelegate = context.coordinator
        context.coordinator.webView = wv
        if let url = Bundle.main.url(forResource: "reader", withExtension: "html", subdirectory: "web") {
            wv.loadFileURL(url, allowingReadAccessTo: url.deletingLastPathComponent())
        }
        return wv
    }

    func updateUIView(_ uiView: WKWebView, context: Context) {
        context.coordinator.push()
    }

    static func dismantleUIView(_ uiView: WKWebView, coordinator: Coord) {
        uiView.configuration.userContentController.removeScriptMessageHandler(forName: "hub")
    }

    final class Coord: NSObject, WKScriptMessageHandler, WKNavigationDelegate {
        let item: QuizItem
        let fontSize: Double
        let onAnswer: (Bool) -> Void
        weak var webView: WKWebView?
        private var ready = false
        private var pushed = false

        init(item: QuizItem, fontSize: Double, onAnswer: @escaping (Bool) -> Void) {
            self.item = item
            self.fontSize = fontSize
            self.onAnswer = onAnswer
        }

        func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
            ready = true
            push()
        }

        func push() {
            guard ready, !pushed, let wv = webView else { return }
            let payload = RenderPayload(lessonId: item.lessonId,
                                        title: item.lessonTitle,
                                        subtitle: "",
                                        cards: [item.card],
                                        progress: [:],
                                        fontSize: fontSize,
                                        scrollY: 0,
                                        theme: UserDefaults.standard.string(forKey: "hub.theme") ?? "auto")
            guard let data = try? JSONEncoder().encode(payload),
                  var json = String(data: data, encoding: .utf8) else { return }
            json = json.replacingOccurrences(of: "\u{2028}", with: "\\u2028")
                       .replacingOccurrences(of: "\u{2029}", with: "\\u2029")
            pushed = true
            wv.evaluateJavaScript("window.renderStudyHub(\(json));", completionHandler: nil)
        }

        func userContentController(_ uc: WKUserContentController, didReceive message: WKScriptMessage) {
            guard message.name == "hub", let body = message.body as? [String: Any] else { return }
            if (body["type"] as? String) == "answer" {
                let ok = body["correct"] as? Bool ?? false
                onAnswer(ok)
            }
        }
    }
}

// MARK: - 练习/测验

struct QuizView: View {
    let session: QuizSession
    @EnvironmentObject var store: Store
    @Environment(\.dismiss) private var dismiss

    @State private var index = 0
    @State private var rightCount = 0
    @State private var answeredThis = false
    @State private var finished = false
    @State private var wrongList: [QuizItem] = []

    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                if finished {
                    resultView
                } else {
                    header
                    QuizCardView(item: session.items[index], fontSize: store.fontSize) { ok in
                        handle(ok)
                    }
                    .id(index)
                }
            }
            .navigationTitle(session.title)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("退出") { dismiss() }
                }
            }
        }
    }

    private var header: some View {
        VStack(spacing: 6) {
            HStack {
                Text("第 \(index + 1) / \(session.items.count) 题")
                    .font(.footnote.weight(.semibold))
                Spacer()
                Text("正确 \(rightCount)")
                    .font(.footnote)
                    .foregroundColor(.secondary)
            }
            ProgressView(value: Double(index + (answeredThis ? 1 : 0)),
                         total: Double(session.items.count))
        }
        .padding(.horizontal, 16)
        .padding(.top, 8)
        .padding(.bottom, 4)
    }

    private var resultView: some View {
        List {
            Section {
                VStack(spacing: 8) {
                    Text("\(rightCount) / \(session.items.count)")
                        .font(.system(size: 44, weight: .bold, design: .rounded))
                    Text(rateText)
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }
                .frame(maxWidth: .infinity)
                .padding(.vertical, 20)
            }
            if !wrongList.isEmpty {
                Section("这轮错的题（\(wrongList.count)）") {
                    ForEach(wrongList) { it in
                        VStack(alignment: .leading, spacing: 2) {
                            Text(it.card.question?.replacingOccurrences(of: "$", with: "") ?? it.card.id)
                                .font(.subheadline)
                                .lineLimit(2)
                            Text(it.lessonTitle)
                                .font(.caption2)
                                .foregroundColor(.secondary)
                        }
                    }
                }
            }
            Section {
                Button("再来一轮") {
                    index = 0; rightCount = 0; answeredThis = false
                    wrongList = []; finished = false
                }
                Button("退出") { dismiss() }
            }
        }
        .listStyle(.insetGrouped)
    }

    private var rateText: String {
        let n = session.items.count
        guard n > 0 else { return "" }
        return "正确率 \(rightCount * 100 / n)%"
    }

    private func handle(_ ok: Bool) {
        guard !answeredThis else { return }
        answeredThis = true
        if ok { rightCount += 1 } else { wrongList.append(session.items[index]) }

        let it = session.items[index]
        // 记进度 + 错题本 + 每日统计 + 复习排期
        store.record(lessonId: it.lessonId, lessonTitle: it.lessonTitle,
                     cardId: it.card.id, correct: ok, preview: previewText(it))

        let nextIndex = index + 1
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.4) {
            if nextIndex < session.items.count {
                index = nextIndex
                answeredThis = false
            } else {
                finished = true
            }
        }
    }

    private func previewText(_ it: QuizItem) -> String {
        let raw = it.card.question ?? it.card.md ?? ""
        let t = raw.replacingOccurrences(of: "$", with: "")
            .replacingOccurrences(of: "\n", with: " ")
        return String(t.prefix(60))
    }
}
