import SwiftUI
import WebKit
import UIKit

// MARK: - 单题渲染（复用 reader.html）

struct QuizCardView: UIViewRepresentable {
    let item: QuizItem
    let fontSize: Double
    var allowPeek: Bool = true
    var exam: Bool = false
    var onAnswer: (Bool, Bool) -> Void = { _, _ in }
    var onPick: ([String]) -> Void = { _ in }

    func makeCoordinator() -> Coord {
        Coord(item: item, fontSize: fontSize, allowPeek: allowPeek, exam: exam,
              onAnswer: onAnswer, onPick: onPick)
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
        let exam: Bool
        let onAnswer: (Bool, Bool) -> Void
        let onPick: ([String]) -> Void
        weak var webView: WKWebView?
        private var ready = false
        private var pushed = false

        init(item: QuizItem, fontSize: Double, allowPeek: Bool, exam: Bool,
             onAnswer: @escaping (Bool, Bool) -> Void,
             onPick: @escaping ([String]) -> Void) {
            self.item = item
            self.fontSize = fontSize
            self.allowPeek = allowPeek
            self.exam = exam
            self.onAnswer = onAnswer
            self.onPick = onPick
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
                                        allowPeek: allowPeek,
                                        exam: exam)
            guard let data = try? JSONEncoder().encode(payload),
                  var json = String(data: data, encoding: .utf8) else { return }
            json = json.replacingOccurrences(of: "\u{2028}", with: "\\u2028")
                       .replacingOccurrences(of: "\u{2029}", with: "\\u2029")
            pushed = true
            wv.evaluateJavaScript("window.renderStudyHub(\(json));", completionHandler: nil)
        }

        func userContentController(_ uc: WKUserContentController, didReceive message: WKScriptMessage) {
            guard message.name == "hub", let body = message.body as? [String: Any] else { return }
            let type = body["type"] as? String ?? ""
            if type == "answer" {
                let ok = body["correct"] as? Bool ?? false
                let peeked = body["peeked"] as? Bool ?? false
                onAnswer(ok, peeked)
            } else if type == "pick" {
                let picked = (body["picked"] as? [String]) ?? []
                onPick(picked)
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
    @State private var allowPeek = true

    // 答题卡
    @State private var showCard = false
    @State private var doneIdx: Set<Int> = []
    @State private var wrongIdx: Set<Int> = []

    // 限时交卷
    @State private var picks: [String: [String]] = [:]
    @State private var leftSeconds = 0
    @State private var started = false

    private var isExam: Bool { session.exam }

    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                if finished {
                    resultView
                } else {
                    header
                    QuizCardView(item: session.items[index],
                                  fontSize: store.fontSize,
                                  allowPeek: allowPeek,
                                  exam: isExam,
                                  onAnswer: { ok, peeked in
                                      handle(ok, peeked)
                                  },
                                  onPick: { picked in
                                      picks[session.items[index].id] = picked
                                      answeredThis = true
                                  })
                    .id(index)
                }
            }
            .navigationTitle(session.title)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("退出") { dismiss() }
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button {
                        showCard = true
                    } label: {
                        Image(systemName: "square.grid.3x3.fill")
                    }
                    .disabled(finished)
                }
            }
            .sheet(isPresented: $showCard) {
                answerCard
            }
        }
        .onAppear(perform: startIfNeeded)
    }

    // MARK: - 顶部：进度 / 倒计时 / 上一题 / 交卷

    private var header: some View {
        VStack(spacing: 6) {
            HStack(spacing: 10) {
                Button {
                    go(index - 1)
                } label: {
                    Image(systemName: "chevron.left")
                }
                .disabled(index == 0)

                Text("第 \(index + 1) / \(session.items.count) 题")
                    .font(.footnote.weight(.semibold))

                Spacer()

                if isExam {
                    Text(timeText)
                        .font(.footnote.monospacedDigit())
                        .foregroundColor(leftSeconds <= 60 ? .red : .secondary)
                } else {
                    Text("正确 \(rightCount)")
                        .font(.footnote)
                        .foregroundColor(.secondary)
                }

                Button {
                    go(index + 1)
                } label: {
                    Image(systemName: "chevron.right")
                }
                .disabled(index + 1 >= session.items.count)
            }
            ProgressView(value: Double(index + (answeredThis ? 1 : 0)),
                         total: Double(session.items.count))

            if isExam && doneIdx.count == session.items.count {
                Button {
                    submitExam()
                } label: {
                    Text("交卷").frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)
                .padding(.top, 2)
            }
        }
        .padding(.horizontal, 16)
        .padding(.top, 8)
        .padding(.bottom, 6)
    }

    private var timeText: String {
        let m = max(0, leftSeconds) / 60
        let s = max(0, leftSeconds) % 60
        return String(format: "%02d:%02d", m, s)
    }

    // MARK: - 答题卡

    private var answerCard: some View {
        NavigationStack {
            ScrollView {
                LazyVGrid(columns: Array(repeating: GridItem(.flexible(), spacing: 10), count: 5),
                          spacing: 10) {
                    ForEach(Array(session.items.enumerated()), id: \.offset) { _, it in
                        Button {
                            go(i)
                            showCard = false
                        } label: {
                            Text("\(i + 1)")
                                .font(.subheadline.weight(.semibold))
                                .frame(maxWidth: .infinity, minHeight: 42)
                                .background(cardColor(i))
                                .foregroundColor(.white)
                                .clipShape(RoundedRectangle(cornerRadius: 8, style: .continuous))
                        }
                    }
                }
                .padding(16)

                HStack(spacing: 16) {
                    legend(.green, "答对")
                    legend(.red, "答错")
                    legend(.gray.opacity(0.45), "没做")
                    legend(.blue, "当前")
                }
                .font(.caption)
                .padding(.bottom, 20)
            }
            .navigationTitle("答题卡")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("关闭") { showCard = false }
                }
                if isExam {
                    ToolbarItem(placement: .bottomBar) {
                        Button("交卷") { submitExam() }
                    }
                }
            }
        }
    }

    private func legend(_ color: Color, _ text: String) -> some View {
        HStack(spacing: 4) {
            RoundedRectangle(cornerRadius: 3).fill(color).frame(width: 12, height: 12)
            Text(text)
        }
    }

    private func cardColor(_ i: Int) -> Color {
        if i == index { return .blue }
        if wrongIdx.contains(i) { return .red }
        if doneIdx.contains(i) { return .green }
        return .gray.opacity(0.45)
    }

    // MARK: - 结果页

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
                    doneIdx = []; wrongIdx = []; picks = [:]
                    leftSeconds = session.limitSeconds
                }
                Button("错题再看一遍") {
                    let items = wrongList
                    if !items.isEmpty {
                        wrongList = []
                        index = 0; rightCount = 0; answeredThis = false
                        finished = false; doneIdx = []; wrongIdx = []; picks = [:]
                    }
                }
                .disabled(wrongList.isEmpty)
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

    // MARK: - 流程

    private func startIfNeeded() {
        guard !started else { return }
        started = true
        leftSeconds = session.limitSeconds
        if isExam && session.limitSeconds > 0 {
            Task { await tick() }
        }
    }

    private func tick() async {
        while leftSeconds > 0 && !finished {
            try? await Task.sleep(nanoseconds: 1_000_000_000)
            if finished { return }
            leftSeconds -= 1
            if leftSeconds == 0 {
                submitExam()
                return
            }
        }
    }

    private func go(_ i: Int) {
        guard i >= 0, i < session.items.count, i != index else { return }
        index = i
        answeredThis = doneIdx.contains(i)
    }

    private func handle(_ ok: Bool, _ peeked: Bool) {
        guard !answeredThis else { return }
        answeredThis = true

        let it = session.items[index]
        doneIdx.insert(index)
        if ok { rightCount += 1 } else { wrongIdx.insert(index); wrongList.append(it) }

        store.record(lessonId: it.lessonId, lessonTitle: it.lessonTitle,
                     cardId: it.card.id, correct: ok, preview: previewText(it))

        DispatchQueue.main.asyncAfter(deadline: .now() + 1.4) {
            self.advance()
        }
    }

    private func advance() {
        let next = index + 1
        if next < session.items.count {
            index = next
            answeredThis = doneIdx.contains(next)
        } else if isExam {
            // 考试模式：停在最后一题，等交卷
            return
        } else {
            finished = true
        }
    }

    /// 交卷：按 picks 逐题判分
    private func submitExam() {
        guard !finished else { return }
        var right = 0
        var wrong: [QuizItem] = []
        for (i, it) in session.items.enumerated() {
            let picked = picks[it.id] ?? []
            let ok = judge(it.card, picked)
            if ok {
                right += 1
            } else {
                wrong.append(it)
            }
            store.record(lessonId: it.lessonId, lessonTitle: it.lessonTitle,
                         cardId: it.card.id, correct: ok, preview: previewText(it))
        }
        rightCount = right
        wrongList = wrong
        wrongIdx = Set(wrong.compactMap { w in session.items.firstIndex(of: w) })
        doneIdx = Set(0..<session.items.count)
        finished = true
    }

    private func judge(_ card: Card, _ picked: [String]) -> Bool {
        switch card.type {
        case "choice", "multi", "judge":
            let ans = (card.answer ?? []).sorted()
            let got = picked.compactMap { Int($0) }.sorted()
            return !ans.isEmpty && ans == got
        case "blank":
            let blanks = card.blanks ?? []
            guard !blanks.isEmpty else { return false }
            for (i, accepted) in blanks.enumerated() {
                let v = i < picked.count ? norm(picked[i]) : ""
                if !accepted.contains(where: { norm($0) == v }) { return false }
            }
            return true
        default:
            return false
        }
    }

    private func norm(_ s: String) -> String {
        s.trimmingCharacters(in: .whitespacesAndNewlines)
            .lowercased()
            .replacingOccurrences(of: " ", with: "")
    }

    private func previewText(_ it: QuizItem) -> String {
        let raw = it.card.question ?? it.card.md ?? ""
        let t = raw.replacingOccurrences(of: "$", with: "")
            .replacingOccurrences(of: "\n", with: " ")
        return String(t.prefix(60))
    }
}
