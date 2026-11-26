# -*- coding: utf-8 -*-
"""补漏：网页版 --sub 变量、模拟考入口、考试模式随时交卷"""
import io

ROOT = r"C:/Users/chong/Documents/studyhub/"
OK, FAIL = [], []


def sub(path, old, new, tag):
    p = ROOT + path
    s = io.open(p, encoding="utf-8").read()
    n = s.count(old)
    if n != 1:
        FAIL.append("%s: %s 命中 %d" % (path, tag, n))
        print("  !!", path, "|", tag, n)
        return
    io.open(p, "w", encoding="utf-8", newline="\n").write(s.replace(old, new))
    OK.append(tag)
    print("  ok", path, "|", tag)


# ---------- 1. 网页版补 --sub（图的标注/辅助线颜色） ----------
sub("web/app.css",
    """  --text-2:    #4a5160;""",
    """  --text-2:    #4a5160;
  --sub:       #6b7280;""", "亮色 --sub")

sub("web/app.css",
    """    --text-2:    #a8b1c0;""",
    """    --text-2:    #a8b1c0;
    --sub:       #9aa3b2;""", "深色 --sub")

# ---------- 2. 章节测验：加「模拟考 · 限时 40 分钟」 ----------
sub("Sources/TodayView.swift",
    """                            if Self.lessonCount(ch) > 1 {
                                Button {
                                    makeQuiz(ch)
                                } label: {""",
    """                            if Self.lessonCount(ch) > 1 {
                                Button {
                                    makeQuiz(ch, exam: true)
                                } label: {
                                    HStack(spacing: 8) {
                                        Image(systemName: "timer")
                                            .foregroundColor(.orange)
                                        Text("模拟考 · 限时 40 分钟")
                                        Spacer()
                                        Text("\\(Self.lessonCount(ch)) 节")
                                            .font(.caption)
                                            .foregroundColor(.secondary)
                                    }
                                }
                                .disabled(busyLabel != nil)

                                Button {
                                    makeQuiz(ch)
                                } label: {""", "模拟考入口")

sub("Sources/TodayView.swift",
    """    private func makeQuiz(_ node: Node) {
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
    }""",
    """    private func makeQuiz(_ node: Node, exam: Bool = false) {
        busyLabel = node.title
        Task {
            let all = await store.questions(in: node)
            await MainActor.run {
                busyLabel = nil
                if all.isEmpty { return }
                let items = exam ? all : Array(all.shuffled().prefix(15))
                session = QuizSession(title: exam ? "模拟考 · \\(node.title)" : node.title,
                                      items: items,
                                      exam: exam,
                                      limitSeconds: exam ? 40 * 60 : 0)
            }
        }
    }""", "makeQuiz exam")

# ---------- 3. 考试模式：顶部随时可交卷 ----------
sub("Sources/QuizView.swift",
    """            if isExam && doneIdx.count == session.items.count {
                Button {
                    submitExam()
                } label: {
                    Text("交卷").frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)
                .padding(.top, 2)
            }""",
    """            if isExam {
                Button {
                    submitExam()
                } label: {
                    Text(doneIdx.count == session.items.count
                         ? "交卷（已答完）"
                         : "交卷（已答 \\(doneIdx.count)/\\(session.items.count)）")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)
                .tint(doneIdx.count == session.items.count ? .green : .orange)
                .padding(.top, 2)
            }""", "随时交卷")

print("\n成功 %d，失败 %d" % (len(OK), len(FAIL)))
for f in FAIL:
    print("  ", f)
