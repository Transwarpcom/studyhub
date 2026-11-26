import SwiftUI
import WebKit
import UIKit

// MARK: - 单题渲染（复用 reader.html）

struct QuizCardView: UIViewRepresentable {
    let item: QuizItem
    let fontSize: Double
    var allowPeek: Bool = true
    var onAnswer: (Bool, Bool) -> Void

    func makeCoordinator() -> Coord {
        Coord(item: item, fontSize: fontSize, allowPeek: allowPeek, onAnswer: onAnswer)
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
        let allowPeek: Bool
        let onAnswer: (Bool, Bool) -> Void
        weak var webView: WKWebView?
        private var ready = false
        private var pushed = false

        init(item: QuizItem, fontSize: Double, allowPeek: Bool,
             onAnswer: @escaping (Bool, Bool) -> Void) {
            self.item = item
            self.fontSize = fontSize
            self.allowPeek = allowPeek
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
                                        theme: UserDefaults.standard.string(forKey: "hub.theme") ?? "auto",
                                        allowPeek: allowPeek)
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
                let peeked = body["peeked"] as? Bool ?? false
                onAnswer(ok, peeked)
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
    @State private var peekedThis = false
    @State private var peekedCount = 0
    @State private var finished = false
    @AppStorage("hub.allowPeek") private var allowPeek = true
    @State private var wrongList: [QuizItem] = []

    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                if finished {
                    resultView
                } else {
                    header
                    QuizCardView(item: session.items[index],
                                  fontSize: store.fontSize,
                                  allowPeek: allowPeek) { ok, peeked in
                        handle(ok, peeked)
                    }
                    .id(index)

                    if peekedThis {
                        Button {
                            advance()
                        } label: {
                            Text(index + 1 < session.items.count ? "下一题" : "看成绩")
                                .frame(maxWidth: .infinity)
                        }
                        .buttonStyle(.borderedProminent)
                        .padding(.horizontal, 16)
                        .padding(.bottom, 10)
                    }
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
                    Text("\(rightCount) / \(answeredTotal)")
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
                    peekedThis = false; peekedCount = 0
                    wrongList = []; finished = false
                }
                Button("退出") { dismiss() }
            }
        }
        .listStyle(.insetGrouped)
    }

    /// 真正作答的题数：看过解析的不算分母
    private var answeredTotal: Int {
        let n = session.items.count - peekedCount
        return n > 0 ? n : 1
    }

    private var rateText: String {
        guard session.items.count > peekedCount else { return "全部看过解析" }
        return "正确率 \(rightCount * 100 / answeredTotal)%"
    }

    /// peeked=true 表示「提交前看了解析」：不算答对，记入待复习，停在这一题等用户点下一题
    private func handle(_ ok: Bool, peeked: Bool) {
        guard !answeredThis else { return }
        answeredThis = true
        peekedThis = peeked

        let it = session.items[index]
        if peeked {
            peekedCount += 1
            if !wrongList.contains(where: { $0.id == it.id }) { wrongList.append(it) }
        } else if ok {
            rightCount += 1
        } else {
            wrongList.append(it)
        }

        // 记进度 + 错题本 + 每日统计 + 复习排期
        store.record(lessonId: it.lessonId, lessonTitle: it.lessonTitle,
                     cardId: it.card.id, correct: ok, preview: previewText(it))

        if peeked { return }   // 看完了自己点「下一题」，不自动跳
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.4) {
            advance()
        }
    }

    private func advance() {
        let nextIndex = index + 1
        if nextIndex < session.items.count {
            index = nextIndex
            answeredThis = false
            peekedThis = false
        } else {
            finished = true
        }
    }

    private func previewText(_ it: QuizItem) -> String {
        let raw = it.card.question ?? it.card.md ?? ""
        let t = raw.replacingOccurrences(of: "$", with: "")
            .replacingOccurrences(of: "\n", with: " ")
        return String(t.prefix(60))
    }
}
