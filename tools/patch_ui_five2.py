# -*- coding: utf-8 -*-
"""继续：搜索绑定/函数、错题导出、诊断区（各步独立，不因一处失败中断）"""
import io

ROOT = r"C:/Users/chong/Documents/studyhub/"
OK, FAIL = [], []


def sub(path, old, new, tag):
    p = ROOT + path
    s = io.open(p, encoding="utf-8").read()
    n = s.count(old)
    if n != 1:
        FAIL.append("%s: %s 命中 %d" % (path, tag, n))
        print("  !!", path, "|", tag, "命中", n)
        return
    io.open(p, "w", encoding="utf-8", newline="\n").write(s.replace(old, new))
    OK.append(tag)
    print("  ok", path, "|", tag)


# ---------- LibraryView：搜索框 + 搜索函数 ----------
sub("Sources/LibraryView.swift",
    '            .searchable(text: $query, placement: .navigationBarDrawer(displayMode: .always), prompt: "搜索章节")',
    '            .searchable(text: $query, placement: .navigationBarDrawer(displayMode: .always), prompt: "搜索章节或题目…")\n'
    '            .task(id: query) { await searchCards() }',
    "搜索绑定")

sub("Sources/LibraryView.swift",
    "    var body: some View {",
    """    private func plain(_ s: String) -> String {
        s.replacingOccurrences(of: "$", with: "")
            .replacingOccurrences(of: "\\n", with: " ")
    }

    private func searchCards() async {
        let q = query.trimmingCharacters(in: .whitespaces)
        guard q.count >= 2 else {
            cardHits = []
            searchingCards = false
            return
        }
        // 打字停下 350ms 才扫全库，避免每个键都查一遍
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

# ---------- WrongBookView：导出 ----------
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
    "    private func timeText(_ d: Date) -> String {",
    """    /// 导出成一页文本：序号、所在节、题干
    private var exportText: String {
        let f = DateFormatter()
        f.dateFormat = "yyyy-MM-dd HH:mm"
        var out = ["# 错题清单", "导出时间：\\(f.string(from: Date()))", "共 \\(store.wrongs.count) 道", ""]
        for (i, w) in store.wrongs.enumerated() {
            out.append("\\(i + 1). 【\\(w.lessonTitle)】")
            out.append("   题干：\\(w.preview.isEmpty ? w.cardId : w.preview)")
            out.append("")
        }
        return out.joined(separator: "\\n")
    }

    private func timeText(_ d: Date) -> String {""", "导出文本")

# ---------- SettingsView：诊断 ----------
sub("Sources/SettingsView.swift",
    '                Section("关于") {',
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

print("\n成功 %d 项，失败 %d 项" % (len(OK), len(FAIL)))
for f in FAIL:
    print("  失败:", f)
