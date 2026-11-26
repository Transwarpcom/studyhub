# -*- coding: utf-8 -*-
"""把 TodayView 里的 ChapterQuizPicker 换成两级结构：Section=二级目录，行=具体一节"""
import io

P = r"C:/Users/chong/Documents/studyhub/Sources/TodayView.swift"
src = io.open(P, encoding="utf-8").read()

MARK = "// MARK: - 章节测验选择"
i = src.index(MARK)
head = src[:i]

NEW = r'''// MARK: - 章节测验选择
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
                                            .foregroundColor(.tertiary)
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

    private func makeQuiz(_ node: Node) {
        busyLabel = node.title
        Task {
            let all = await store.questions(in: node)
            await MainActor.run {
                busyLabel = nil
                if all.isEmpty { return }
                let items = Array(all.shuffled().prefix(15))
                session = QuizSession(title: node.title, items: items, exam: false, limitSeconds: 0)
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
'''

io.open(P, "w", encoding="utf-8").write(head + NEW)
print("rewrote", P)
print("lines:", (head + NEW).count("\n") + 1)
