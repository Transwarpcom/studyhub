# -*- coding: utf-8 -*-
"""修：看过解析的题不该进「今日答题数/正确率」统计"""
import io


def sub(path, old, new, tag):
    p = r"C:/Users/chong/Documents/studyhub/" + path
    s = io.open(p, encoding="utf-8").read()
    n = s.count(old)
    assert n == 1, "%s: %s 命中 %d" % (path, tag, n)
    io.open(p, "w", encoding="utf-8", newline="\n").write(s.replace(old, new))
    print("  ok", path, "|", tag)


# 1) Store.record 增加 peeked 参数：peeked 只记进度/错题/复习，不进每日统计
sub("Sources/Store.swift",
    """    func record(lessonId: String, lessonTitle: String, cardId: String,
                correct: Bool, preview: String) {""",
    """    /// peeked = 提交前看过解析：不算作答，不写「每日答题/正确率」统计，
    /// 但仍然记进度、进错题本、排进复习队列（该复习的还是要复习）
    func record(lessonId: String, lessonTitle: String, cardId: String,
                correct: Bool, preview: String, peeked: Bool = false) {""",
    "record 签名")

sub("Sources/Store.swift",
    """        // 按天统计
        let f = DateFormatter()
        f.dateFormat = "yyyy-MM-dd"
        let day = f.string(from: Date())
        var st = days[day] ?? DayStat(day: day, answered: 0, correct: 0)
        st.answered += 1
        if correct { st.correct += 1 }
        days[day] = st
        saveDays()""",
    """        // 按天统计（看过解析的题不算作答，避免把正确率统计搞脏）
        if !peeked {
            let f = DateFormatter()
            f.dateFormat = "yyyy-MM-dd"
            let day = f.string(from: Date())
            var st = days[day] ?? DayStat(day: day, answered: 0, correct: 0)
            st.answered += 1
            if correct { st.correct += 1 }
            days[day] = st
            saveDays()
        }""",
    "每日统计跳过 peeked")

# 2) QuizView 传 peeked
sub("Sources/QuizView.swift",
    """        store.record(lessonId: it.lessonId, lessonTitle: it.lessonTitle,
                     cardId: it.card.id, correct: ok, preview: previewText(it))""",
    """        store.record(lessonId: it.lessonId, lessonTitle: it.lessonTitle,
                     cardId: it.card.id, correct: ok, preview: previewText(it),
                     peeked: peeked)""",
    "QuizView 传 peeked")

# 3) ReaderWebView 桥接传 peeked
sub("Sources/ReaderWebView.swift",
    """                let cardId = body["cardId"] as? String ?? ""
                let correct = body["correct"] as? Bool ?? false
                let preview = body["preview"] as? String ?? ""
                let lessonId = lesson.id
                let lessonTitle = lesson.title
                let store = StoreLocator.shared.store
                Task { @MainActor in
                    store?.record(lessonId: lessonId, lessonTitle: lessonTitle,
                                  cardId: cardId, correct: correct, preview: preview)
                }""",
    """                let cardId = body["cardId"] as? String ?? ""
                let correct = body["correct"] as? Bool ?? false
                let peeked = body["peeked"] as? Bool ?? false
                let preview = body["preview"] as? String ?? ""
                let lessonId = lesson.id
                let lessonTitle = lesson.title
                let store = StoreLocator.shared.store
                Task { @MainActor in
                    store?.record(lessonId: lessonId, lessonTitle: lessonTitle,
                                  cardId: cardId, correct: correct, preview: preview,
                                  peeked: peeked)
                }""",
    "ReaderWebView 传 peeked")

print("done")
