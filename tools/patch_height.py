# -*- coding: utf-8 -*-
"""答题页高度自适应：webview 上报内容高度，外层整页滚动"""
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


# ---------- reader.js：渲染完上报内容高度 ----------
sub("Resources/web/reader.js",
    """  window.renderStudyHub = function (payload) {""",
    """  // 渲染完成后把内容高度报给原生（答题页按内容撑开，避免内部滚动藏住按钮）
  function postHeight() {
    try {
      var h = Math.ceil(document.documentElement.scrollHeight || document.body.scrollHeight || 0);
      if (h > 0) post({ type: 'height', h: h });
    } catch (e) {}
  }

  window.renderStudyHub = function (payload) {""", "postHeight")

sub("Resources/web/reader.js",
    """    build(payload);
  };""",
    """    build(payload);
    setTimeout(postHeight, 80);
    setTimeout(postHeight, 400);
  };""", "渲染后上报")

# ---------- ReaderWebView（阅读页）忽略 height，无需改 ----------

# ---------- QuizView：高度状态 + 外层滚动 ----------
sub("Sources/QuizView.swift",
    """    var exam: Bool = false
    var onAnswer: (Bool, Bool) -> Void = { _, _ in }
    var onPick: ([String]) -> Void = { _ in }""",
    """    var exam: Bool = false
    var onAnswer: (Bool, Bool) -> Void = { _, _ in }
    var onPick: ([String]) -> Void = { _ in }
    var onHeight: (CGFloat) -> Void = { _ in }""", "QuizCardView 回调")

sub("Sources/QuizView.swift",
    """        Coord(item: item, fontSize: fontSize, allowPeek: allowPeek, exam: exam,
              onAnswer: onAnswer, onPick: onPick)""",
    """        Coord(item: item, fontSize: fontSize, allowPeek: allowPeek, exam: exam,
              onAnswer: onAnswer, onPick: onPick, onHeight: onHeight)""", "makeCoordinator")

sub("Sources/QuizView.swift",
    """        let onAnswer: (Bool, Bool) -> Void
        let onPick: ([String]) -> Void""",
    """        let onAnswer: (Bool, Bool) -> Void
        let onPick: ([String]) -> Void
        let onHeight: (CGFloat) -> Void""", "Coord 属性")

sub("Sources/QuizView.swift",
    """        init(item: QuizItem, fontSize: Double, allowPeek: Bool, exam: Bool,
             onAnswer: @escaping (Bool, Bool) -> Void,
             onPick: @escaping ([String]) -> Void) {
            self.item = item
            self.fontSize = fontSize
            self.allowPeek = allowPeek
            self.exam = exam
            self.onAnswer = onAnswer
            self.onPick = onPick
        }""",
    """        init(item: QuizItem, fontSize: Double, allowPeek: Bool, exam: Bool,
             onAnswer: @escaping (Bool, Bool) -> Void,
             onPick: @escaping ([String]) -> Void,
             onHeight: @escaping (CGFloat) -> Void) {
            self.item = item
            self.fontSize = fontSize
            self.allowPeek = allowPeek
            self.exam = exam
            self.onAnswer = onAnswer
            self.onPick = onPick
            self.onHeight = onHeight
        }""", "Coord init")

sub("Sources/QuizView.swift",
    """            } else if type == "pick" {
                let picked = (body["picked"] as? [String]) ?? []
                onPick(picked)
            }""",
    """            } else if type == "pick" {
                let picked = (body["picked"] as? [String]) ?? []
                onPick(picked)
            } else if type == "height" {
                let h = (body["h"] as? NSNumber)?.doubleValue ?? 0
                if h > 40 { onHeight(CGFloat(h)) }
            }""", "height 分支")

# webview 自身不滚动
sub("Sources/QuizView.swift",
    """        wv.isOpaque = false
        wv.backgroundColor = .clear
        wv.scrollView.backgroundColor = .clear""",
    """        wv.isOpaque = false
        wv.backgroundColor = .clear
        wv.scrollView.backgroundColor = .clear
        wv.scrollView.isScrollEnabled = false
        wv.scrollView.bounces = false""", "禁用内部滚动")

sub("Sources/QuizView.swift",
    """    @AppStorage("hub.allowPeek") private var allowPeek = true""",
    """    @AppStorage("hub.allowPeek") private var allowPeek = true
    @State private var cardHeight: CGFloat = 380""", "高度状态")

sub("Sources/QuizView.swift",
    """                    QuizCardView(item: session.items[index],
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
                    .id(index)""",
    """                    ScrollView {
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
                                      },
                                      onHeight: { h in
                                          cardHeight = min(max(h, 300), 4000)
                                      })
                        .frame(height: cardHeight)
                        .id(index)
                    }""", "外层 ScrollView")

print("\n成功 %d，失败 %d" % (len(OK), len(FAIL)))
for f in FAIL:
    print("  ", f)
