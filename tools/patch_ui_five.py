# -*- coding: utf-8 -*-
"""四个界面入口：掌握度、题目搜索、错题导出、诊断日志"""
import io

ROOT = r"C:/Users/chong/Documents/studyhub/"


def sub(path, old, new, tag):
    p = ROOT + path
    s = io.open(p, encoding="utf-8").read()
    n = s.count(old)
    assert n == 1, "%s: %s 命中 %d" % (path, tag, n)
    io.open(p, "w", encoding="utf-8", newline="\n").write(s.replace(old, new))
    print("  ok", path, "|", tag)


# ---------- 1. TodayView：加「各章掌握度」入口 ----------
sub("Sources/TodayView.swift",
    """                    NavigationLink {
                        ChapterQuizPicker()
                    } label: {
                        row(icon: "list.bullet.rectangle", title: "章节测验",
                            detail: "挑一章整套做", color: .purple)
                    }""",
    """                    NavigationLink {
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
                    }""", "掌握度入口")

# ---------- 2. LibraryView：题目级搜索 ----------
sub("Sources/LibraryView.swift",
    """    @State private var query = \"\"""",
    """    @State private var query = ""
    @State private var cardHits: [QuizItem] = []
    @State private var searchingCards = false""", "搜索状态")

sub("Sources/LibraryView.swift",
    """                if !query.isEmpty {
                    Section("搜索结果（\\(results.count)）") {
                        if results.isEmpty {
                            Text("没有匹配的章节").foregroundColor(.secondary)
                        }
                        ForEach(results) { node in
                            NodeRow(node: node, path: $path)
                        }
                    }
                } else if let m = store.manifest {""",
    """                if !query.isEmpty {
                    Section("章节（\\(results.count)）") {
                        if results.isEmpty {
                            Text("没有匹配的章节").foregroundColor(.secondary)
                        }
                        ForEach(results) { node in
                            NodeRow(node: node, path: $path)
                        }
                    }
                    Section("题目里命中（\\(cardHits.count)）") {
                        if searchingCards && cardHits.isEmpty {
                            HStack(spacing: 8) {
                                ProgressView()
                                Text("正在检索全部题目…").font(.footnote).foregroundColor(.secondary)
                            }
                        } else if cardHits.isEmpty {
                            Text("题干、讲义、解析里都没有").foregroundColor(.secondary)
                        }
                        ForEach(cardHits) { it in
                            Button {
                                if let n = store.allLessonNodes.first(where: { $0.id == it.lessonId }) {
                                    path.append(n)
                                }
                            } label: {
                                VStack(alignment: .leading, spacing: 3) {
                                    Text(plain(it.card.question ?? it.card.md ?? it.card.id))
                                        .font(.subheadline)
                                        .lineLimit(2)
                                    Text(it.lessonTitle)
                                        .font(.caption2)
                                        .foregroundColor(.secondary)
                                }
                            }
                        }
                    }
                } else if let m = store.manifest {""", "题目搜索块")

sub("Sources/LibraryView.swift",
    """            .searchable(text: $query, placement: .navigationBarDrawer(displayMode: .always), prompt: "搜索章…")""",
    """            .searchable(text: $query, placement: .navigationBarDrawer(displayMode: .always), prompt: "搜索章节或题目…")
            .task(id: query) { await searchCards() }""", "搜索绑定")

sub("Sources/LibraryView.swift",
    """    var body: some View {""",
    """    private func plain(_ s: String) -> String {
        s.replacingOccurrences(of: "$", with: "")
            .replacingOccurrences(of: "\\n", with: " ")
    }

    private func searchCards() async {
        let q = query.trimmingCharacters(in: .whitespaces)
        guard q.count >= 2 else {
            cardHits = []
            return
        }
        // 打字停下 350ms 才真正查，避免每个键都扫全库
        try? await Task.sleep(nanoseconds: 350_000_000)
        if Task.isCancelled { return }
        await MainActor.run { searchingCards = true }
        let hits = await store.searchQuestions(q)
        if Task.isCancelled { return }
        await MainActor.run {
            cardHits = hits
            searchingCards = false
        }
    }

    var body: some View {""", "搜索函数")

# ---------- 3. WrongBookView：导出 ----------
sub("Sources/WrongBookView.swift",
    """                        HStack {
                            Text("共 \\(store.wrongs.count) 道").font(.headline)
                            Spacer()
                            Button("清空") {""",
    """                        HStack {
                            Text("共 \\(store.wrongs.count) 道").font(.headline)
                            Spacer()
                            ShareLink(item: exportText) {
                                Label("导出", systemImage: "square.and.arrow.up")
                                    .font(.footnote)
                            }
                            Button("清空") {""", "导出按钮")

sub("Sources/WrongBookView.swift",
    """    private func timeText(_ d: Date) -> String {""",
    """    /// 导出成一页文本：题号、所在节、题干、解析
    private var exportText: String {
        let f = DateFormatter()
        f.dateFormat = "yyyy-MM-dd HH:mm"
        var out = ["# 错题清单", "导出时间：\\(f.string(from: Date()))", "共 \\(store.wrongs.count) 道", ""]
        for (i, w) in store.wrongs.enumerated() {
            out.append("\\(i + 1). 【\\(w.lessonTitle)】")
            let q = w.preview.isEmpty ? w.cardId : w.preview
            out.append("   题干：\\(q)")
            out.append("")
        }
        return out.joined(separator: "\\n")
    }

    private func timeText(_ d: Date) -> String {""", "导出文本")

# ---------- 4. SettingsView：诊断 ----------
sub("Sources/SettingsView.swift",
    """                Section("关于") {""",
    """                Section {
                    NavigationLink {
                        ChapterStatsView()
                    } label: {
                        Label("各章掌握度", systemImage: "chart.bar.xaxis")
                    }
                    ShareLink(item: Log.text) {
                        Label("导出运行日志（\\(Log.lines.count) 条）", systemImage: "doc.text")
                    }
                    Button("清空日志") {
                        Log.clear()
                        hint = "日志已清空"
                    }
                    .foregroundColor(.red)
                } header: {
                    Text("诊断")
                }

                Section("关于") {""", "诊断区")

print("done")
