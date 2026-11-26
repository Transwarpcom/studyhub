import SwiftUI

// MARK: - 今日（复习 / 错题 / 每日一练）

struct TodayView: View {
    @EnvironmentObject var store: Store

    @State private var session: QuizSession?
    @State private var busy = false
    @State private var toast: String?

    var body: some View {
        NavigationStack {
            List {
                Section {
                    HStack(spacing: 18) {
                        stat("连续", "\(store.streakDays) 天")
                        stat("今日", "\(store.todayStat.answered) 题")
                        stat("正确率", rateText)
                        Spacer()
                    }
                    .padding(.vertical, 6)
                }

                Section("开始") {
                    Button {
                        startReview()
                    } label: {
                        row(icon: "clock.arrow.circlepath", title: "待复习",
                            detail: "\(store.dueReviews.count) 题到期", color: .orange)
                    }
                    .disabled(busy)

                    Button {
                        startWrong()
                    } label: {
                        row(icon: "exclamationmark.circle.fill", title: "错题重练",
                            detail: "\(store.wrongs.count) 道", color: .red)
                    }
                    .disabled(busy || store.wrongs.isEmpty)

                    Button {
                        startDaily()
                    } label: {
                        row(icon: "bolt.fill", title: "每日一练",
                            detail: "10 题，约 3 分钟", color: .blue)
                    }
                    .disabled(busy)

                    NavigationLink {
                        ChapterQuizPicker()
                    } label: {
                        row(icon: "list.bullet.rectangle", title: "章节测验",
                            detail: "挑一章整套做", color: .purple)
                    }

                    NavigationLink {
                        ChapterStatsView()
                    } label: {
                        row(icon: "chart.bar.xaxis", title: "各章掌握度",
                            detail: "哪章欠得多", color: .teal)
                    }
                }

                if busy {
                    Section {
                        HStack { Spacer(); ProgressView("抽题中…"); Spacer() }
                            .padding(.vertical, 10)
                    }
                }

                if let toast {
                    Section { Text(toast).font(.footnote).foregroundColor(.secondary) }
                }

                Section("错题分布") {
                    if store.wrongs.isEmpty {
                        Text("还没有错题").foregroundColor(.secondary)
                    } else {
                        NavigationLink {
                            WrongBookView().environmentObject(store)
                        } label: {
                            HStack {
                                Label("错题本", systemImage: "book.closed.fill")
                                Spacer()
                                Text("\(store.wrongs.count) 道").font(.caption).foregroundColor(.secondary)
                                Image(systemName: "chevron.right").font(.caption2).foregroundColor(.secondary)
                            }
                        }
                        ForEach(wrongGroups, id: \.key) { g in
                            HStack {
                                Text(g.title).font(.subheadline).lineLimit(1)
                                Spacer()
                                Text("\(g.count) 道")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }
                        }
                    }
                }
            }
            .listStyle(.insetGrouped)
            .navigationTitle("今日")
            .sheet(item: $session) { s in
                QuizView(session: s).environmentObject(store)
            }
        }
    }

    private var rateText: String {
        let a = store.totalAnswered
        guard a > 0 else { return "—" }
        return "\(store.totalCorrect * 100 / a)%"
    }

    private var wrongGroups: [(key: String, title: String, count: Int)] {
        var d: [String: (String, Int)] = [:]
        for w in store.wrongs {
            let cur = d[w.lessonId] ?? (w.lessonTitle, 0)
            d[w.lessonId] = (cur.0, cur.1 + 1)
        }
        return d.map { (key: $0.key, title: $0.value.0, count: $0.value.1) }
            .sorted { $0.count > $1.count }
    }

    private func stat(_ k: String, _ v: String) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(v).font(.system(.headline, design: .rounded))
            Text(k).font(.caption2).foregroundColor(.secondary)
        }
    }

    private func row(icon: String, title: String, detail: String, color: Color) -> some View {
        HStack(spacing: 12) {
            Image(systemName: icon)
                .font(.system(size: 17))
                .foregroundColor(color)
                .frame(width: 26)
            VStack(alignment: .leading, spacing: 1) {
                Text(title).foregroundColor(.primary)
                Text(detail).font(.caption).foregroundColor(.secondary)
            }
            Spacer()
            Image(systemName: "chevron.right")
                .font(.caption.weight(.semibold))
                .foregroundColor(Color.secondary.opacity(0.4))
        }
    }

    // MARK: 动作

    private func startReview() {
        busy = true
        Task {
            let q = await store.reviewQuestions()
            await MainActor.run {
                busy = false
                if q.isEmpty {
                    toast = "暂时没有到期的复习题。做几道新题后，系统会按 1/2/4/7/15 天排期。"
                } else {
                    session = QuizSession(title: "待复习", items: q, exam: false, limitSeconds: 0)
                }
            }
        }
    }

    private func startWrong() {
        let q = store.wrongQuestions()
        if q.isEmpty {
            toast = "错题本里的题还没缓存，先去设置页下载全部内容。"
        } else {
            session = QuizSession(title: "错题重练", items: q, exam: false, limitSeconds: 0)
        }
    }

    private func startDaily() {
        busy = true
        Task {
            let q = await store.pickQuestions(count: 10)
            await MainActor.run {
                busy = false
                if q.isEmpty {
                    toast = "抽不到题，检查一下是否已下载内容。"
                } else {
                    session = QuizSession(title: "每日一练", items: q, exam: false, limitSeconds: 0)
                }
            }
        }
    }
}

// MARK: - 章节测验选择
//
// 结构：List > Section（= 二级目录，例如「第六章 定积分的应用」）
//                行 = 下面每一个具体的节（「6.2 定积分在几何学上的应用」）
//                外加一行「整章随机 15 题」，把整章当整体抽题
// 这样「章检测题（作业册）」下面就是六个独立入口，点一次做一整份卷子。

struct ChapterQuizPicker: View {
    @EnvironmentObject var store: Store
    @State private var session: QuizSession?
    @State private var busyLabel: String?

    var body: some View {
        List {
            if let m = store.manifest {
                ForEach(m.tree) { root in
                    ForEach(root.children ?? []) { ch in
                        Section {
                            if Self.lessonCount(ch) > 1 {
                                Button {
                                    makeQuiz(ch, exam: true)
                                } label: {
                                    HStack(spacing: 8) {
                                        Image(systemName: "timer")
                                            .foregroundColor(.orange)
                                        Text("模拟考 · 限时 40 分钟")
                                        Spacer()
                                        Text("\(Self.lessonCount(ch)) 节")
                                            .font(.caption)
                                            .foregroundColor(.secondary)
                                    }
                                }
                                .disabled(busyLabel != nil)

                                Button {
                                    makeQuiz(ch)
                                } label: {
                                    HStack(spacing: 8) {
                                        Image(systemName: "shuffle")
                                            .foregroundColor(.accentColor)
                                        Text("整章随机 15 题")
                                        Spacer()
                                        Text("\(Self.lessonCount(ch)) 节")
                                            .font(.caption)
                                            .foregroundColor(.secondary)
                                    }
                                }
                                .disabled(busyLabel != nil)
                            }
                            ForEach(Self.lessons(in: ch)) { leaf in
                                Button {
                                    makeQuiz(leaf)
                                } label: {
                                    HStack(spacing: 8) {
                                        Image(systemName: "doc.text")
                                            .foregroundColor(.secondary)
                                        Text(Self.shortTitle(leaf.title))
                                            .lineLimit(1)
                                        Spacer()
                                        Image(systemName: "chevron.right")
                                            .font(.caption)
                                            .foregroundColor(.secondary)
                                    }
                                }
                                .disabled(busyLabel != nil)
                            }
                        } header: {
                            Text(ch.title)
                        }
                    }
                }
            }
            if let label = busyLabel {
                Section {
                    HStack {
                        Spacer()
                        ProgressView("组卷中：\(label)")
                        Spacer()
                    }
                    .padding(.vertical, 10)
                }
            }
        }
        .listStyle(.insetGrouped)
        .navigationTitle("章节测验")
        .navigationBarTitleDisplayMode(.inline)
        .sheet(item: $session) { s in
            QuizView(session: s).environmentObject(store)
        }
    }

    // MARK: - 组卷

    private func makeQuiz(_ node: Node, exam: Bool = false) {
        busyLabel = node.title
        Task {
            let all = await store.questions(in: node)
            await MainActor.run {
                busyLabel = nil
                if all.isEmpty { return }
                let items = exam ? all : Array(all.shuffled().prefix(15))
                session = QuizSession(title: exam ? "模拟考 · \(node.title)" : node.title,
                                      items: items,
                                      exam: exam,
                                      limitSeconds: exam ? 40 * 60 : 0)
            }
        }
    }

    // MARK: - 目录工具

    /// 递归收集节点下面所有的 lesson（节点自己是 lesson 就返回它自己）
    static func lessons(in node: Node) -> [Node] {
        if node.kind == "lesson" { return [node] }
        var out: [Node] = []
        for c in node.children ?? [] {
            out.append(contentsOf: lessons(in: c))
        }
        return out
    }

    static func lessonCount(_ node: Node) -> Int {
        lessons(in: node).count
    }

    /// 「作业册 · 6.2 几何应用（二）体积」→「6.2 几何应用（二）体积」
    static func shortTitle(_ t: String) -> String {
        let prefix = "作业册 · "
        if t.hasPrefix(prefix) { return String(t.dropFirst(prefix.count)) }
        return t
    }
}
