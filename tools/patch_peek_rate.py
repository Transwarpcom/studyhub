# -*- coding: utf-8 -*-
"""正确率分母排除「看了解析」的题"""
import io

P = r"C:/Users/chong/Documents/studyhub/Sources/QuizView.swift"
s = io.open(P, encoding="utf-8").read()


def sub(old, new, tag):
    global s
    n = s.count(old)
    assert n == 1, "%s 命中 %d" % (tag, n)
    s = s.replace(old, new)
    print("  ok", tag)


sub("    @State private var peekedThis = false",
    "    @State private var peekedThis = false\n    @State private var peekedCount = 0",
    "状态 peekedCount")

sub("""                    Text("\\(rightCount) / \\(session.items.count)")""",
    """                    Text("\\(rightCount) / \\(answeredTotal)")""",
    "结果页分子分母")

sub("""        if peeked {
            if !wrongList.contains(where: { $0.id == it.id }) { wrongList.append(it) }
        } else if ok {""",
    """        if peeked {
            peekedCount += 1
            if !wrongList.contains(where: { $0.id == it.id }) { wrongList.append(it) }
        } else if ok {""",
    "handle 计数")

sub("""    private var rateText: String {
        let n = session.items.count
        guard n > 0 else { return "" }
        return "正确率 \\(rightCount * 100 / n)%"
    }""",
    """    /// 真正作答的题数：看过解析的不算分母
    private var answeredTotal: Int {
        let n = session.items.count - peekedCount
        return n > 0 ? n : 1
    }

    private var rateText: String {
        guard session.items.count > peekedCount else { return "全部看过解析" }
        return "正确率 \\(rightCount * 100 / answeredTotal)%"
    }""",
    "rateText")

sub("""                    index = 0; rightCount = 0; answeredThis = false
                    peekedThis = false; wrongList = []; finished = false""",
    """                    index = 0; rightCount = 0; answeredThis = false
                    peekedThis = false; peekedCount = 0
                    wrongList = []; finished = false""",
    "再来一轮重置")

io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("written", P)
