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

struct ChapterQuizPicker: View {
    @EnvironmentObject var store: Store
    @State private var session: QuizSession?
    @State private var busy = false
    @State private var picked: Node?

    var body: some View {
        List {
            if let m = store.manifest {
                ForEach(m.tree) { root in
                    Section(root.title) {
                        ForEach(root.children ?? []) { ch in
                            Button {
                                makeQuiz(ch)
                            } label: {
                                HStack {
                                    Text(ch.title).lineLimit(1)
                                    Spacer()
                                    Text("\(ch.children?.count ?? 0) 节")
                                        .font(.caption)
                                        .foregroundColor(.secondary)
                                }
                            }
                        }
                    }
                }
            }
            if busy {
                HStack { Spacer(); ProgressView("组卷中…"); Spacer() }
            }
        }
        .listStyle(.insetGrouped)
        .navigationTitle("章节测验")
        .navigationBarTitleDisplayMode(.inline)
        .sheet(item: $session) { s in
            QuizView(session: s).environmentObject(store)
        }
    }

    private func makeQuiz(_ node: Node) {
        busy = true
        Task {
            let all = await store.questions(in: node)
            await MainActor.run {
                busy = false
                if all.isEmpty {
                    return
                }
                let items = Array(all.shuffled().prefix(15))
                session = QuizSession(title: node.title, items: items, exam: false, limitSeconds: 0)
            }
        }
    }
}
