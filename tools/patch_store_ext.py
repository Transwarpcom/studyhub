# -*- coding: utf-8 -*-
"""Store 扩展：章掌握度、题目全库搜索、日志、Widget 共享"""
import io

P = r"C:/Users/chong/Documents/studyhub/Sources/Store.swift"
s = io.open(P, encoding="utf-8").read()


def sub(old, new, tag):
    global s
    n = s.count(old)
    assert n == 1, "%s 命中 %d" % (tag, n)
    s = s.replace(old, new)
    print("  ok", tag)


# ---------- 1. 章掌握度 + 全库搜题 ----------
sub("""    // MARK: 统计

    var totalAnswered: Int { progress.count }""",
    """    // MARK: 章掌握度

    /// 按课程树的二级节点（一章）统计
    func chapterStats() async -> [ChapterStat] {
        guard let m = manifest else { return [] }
        var out: [ChapterStat] = []
        for root in m.tree {
            for ch in root.children ?? [] {
                let mine = allLessonNodes.filter { $0.id == ch.id || $0.id.hasPrefix(ch.id + "/") }
                var total = 0, answered = 0, correct = 0, wrong = 0
                for n in mine {
                    let l = cachedLesson(node: n) ?? (try? await loadLesson(node: n))
                    guard let l else { continue }
                    for c in l.cards where c.type != "lecture" {
                        total += 1
                        let key = "\\(l.id)|\\(c.id)"
                        if let p = progress[key] {
                            answered += 1
                            if p { correct += 1 }
                        }
                        if wrongs.contains(where: { $0.id == key }) { wrong += 1 }
                    }
                }
                let ids = Set(mine.map { $0.id })
                let now = Date()
                let due = reviews.values.filter { ids.contains($0.lessonId) && $0.due <= now }.count
                out.append(ChapterStat(id: ch.id, title: ch.title, total: total,
                                       answered: answered, correct: correct,
                                       due: due, wrong: wrong))
            }
        }
        return out
    }

    // MARK: 全库搜题

    /// 在所有节的题干/讲义/解析里找关键词（先命中先返回，最多 60 条）
    func searchQuestions(_ query: String) async -> [QuizItem] {
        let q = query.trimmingCharacters(in: .whitespaces).lowercased()
        guard q.count >= 1 else { return [] }
        var out: [QuizItem] = []
        for n in allLessonNodes {
            let l = cachedLesson(node: n) ?? (try? await loadLesson(node: n))
            guard let l else { continue }
            for c in l.cards where c.type != "lecture" {
                let hay = ((c.question ?? "") + " " + (c.md ?? "") + " " + (c.explain ?? "")).lowercased()
                if hay.contains(q) {
                    out.append(QuizItem(id: "\\(l.id)|\\(c.id)", lessonId: l.id,
                                        lessonTitle: l.title, card: c))
                }
                if out.count >= 60 { return out }
            }
        }
        return out
    }

    // MARK: 统计

    var totalAnswered: Int { progress.count }""", "章统计+搜题")

# ---------- 2. record 末尾同步 Widget ----------
sub("""        // 艾宾浩斯排期
        recordReview(key: key, lessonId: lessonId, lessonTitle: lessonTitle, correct: correct)
    }""",
    """        // 艾宾浩斯排期
        recordReview(key: key, lessonId: lessonId, lessonTitle: lessonTitle, correct: correct)

        // 同步给锁屏小组件
        Shared.publish(due: dueReviews.count,
                       today: todayStat.answered,
                       wrong: wrongs.count,
                       streak: streakDays)
    }""", "record 同步 widget")

# ---------- 3. 刷新失败写日志 ----------
sub("""    func refresh() async {""",
    """    func refresh() async {
        defer { Shared.publish(due: dueReviews.count, today: todayStat.answered,
                               wrong: wrongs.count, streak: streakDays) }""", "refresh 同步 widget")

io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("written Store.swift")
