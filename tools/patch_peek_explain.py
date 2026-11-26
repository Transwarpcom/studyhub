# -*- coding: utf-8 -*-
"""答题前可看解析：reader.js + 三处 Swift + 样式"""
import io

ROOT = r"C:/Users/chong/Documents/studyhub/"


def patch(path, pairs):
    p = ROOT + path
    s = io.open(p, encoding="utf-8").read()
    for old, new, tag in pairs:
        n = s.count(old)
        assert n == 1, "%s: %s 命中 %d 次（应为 1）" % (path, tag, n)
        s = s.replace(old, new)
        print("  ok", path, "|", tag)
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)
    print("written", path)


# ---------------- 1. reader.html：加样式 ----------------
patch("Resources/web/reader.html", [
    (""".verdict.ok{color:var(--ok)}
  .verdict.bad{color:var(--bad)}""",
     """.verdict.ok{color:var(--ok)}
  .verdict.bad{color:var(--bad)}
  .verdict.peek{color:#b8860b}""", "verdict.peek"),
])

# ---------------- 2. reader.js ----------------
patch("Resources/web/reader.js", [
    # S 增加 allowPeek
    ("""    answered: {},   // cardId -> {correct, picked, inputs}""",
     """    answered: {},   // cardId -> {correct, picked, peeked}
    allowPeek: true,""", "S.allowPeek"),

    # build 时读取开关
    ("""    S.payload = payload;
    S.lessonId = payload.lessonId;""",
     """    S.payload = payload;
    S.lessonId = payload.lessonId;
    S.allowPeek = payload.allowPeek !== false;""", "读 allowPeek"),

    # 单选/多选：加「先看解析」按钮
    ("""    h += '<div class="btn-row"><button class="btn submit" disabled>提交答案</button></div>';
    h += '<div class="verdict"></div><div class="explain" style="display:none"></div>';""",
     """    h += '<div class="btn-row"><button class="btn submit" disabled>提交答案</button>' +
         (S.allowPeek ? '<button class="btn ghost small peek">先看解析</button>' : '') +
         '</div>';
    h += '<div class="verdict"></div><div class="explain" style="display:none"></div>';""", "choice 按钮"),

    ("""    var picked = [];
    var opts = el.querySelectorAll('.opt');
    var submit = el.querySelector('.submit');""",
     """    var picked = [];
    var opts = el.querySelectorAll('.opt');
    var submit = el.querySelector('.submit');
    var peekBtn = el.querySelector('.peek');""", "choice peekBtn"),

    ("""    submit.addEventListener('click', function () {
      evaluateChoice(el, card, picked);
    });""",
     """    submit.addEventListener('click', function () {
      evaluateChoice(el, card, picked);
    });

    if (peekBtn) {
      peekBtn.addEventListener('click', function () {
        if (el.dataset.locked === '1') return;
        peekAnswer(el, card, { picked: picked });
      });
    }""", "choice peek 事件"),

    # 填空：加按钮 + 事件
    ("""    h += '<div class="btn-row"><button class="btn submit">提交答案</button></div>';
    h += '<div class="verdict"></div><div class="explain" style="display:none"></div>';
    el.innerHTML = h;

    el.querySelector('.submit').addEventListener('click', function () {""",
     """    h += '<div class="btn-row"><button class="btn submit">提交答案</button>' +
         (S.allowPeek ? '<button class="btn ghost small peek">先看解析</button>' : '') +
         '</div>';
    h += '<div class="verdict"></div><div class="explain" style="display:none"></div>';
    el.innerHTML = h;

    var peekBtn = el.querySelector('.peek');
    if (peekBtn) {
      peekBtn.addEventListener('click', function () {
        if (el.dataset.locked === '1') return;
        var picked = [];
        el.querySelectorAll('.blank-input').forEach(function (inp) { picked.push(inp.value); });
        peekAnswer(el, card, { picked: picked });
      });
    }

    el.querySelector('.submit').addEventListener('click', function () {""", "blank 按钮"),

    # showResult 支持 peeked
    ("""  function showResult(el, card, correct, info) {
    var v = el.querySelector('.verdict');
    if (v) {
      v.textContent = correct ? '✓ 答对了' : '✗ 再想想';
      v.className = 'verdict ' + (correct ? 'ok' : 'bad');
    }""",
     """  function showResult(el, card, correct, info) {
    var peeked = !!(info && info.peeked);
    var v = el.querySelector('.verdict');
    if (v) {
      if (peeked) {
        v.textContent = '👀 已看解析 · 记入待复习';
        v.className = 'verdict peek';
      } else {
        v.textContent = correct ? '✓ 答对了' : '✗ 再想想';
        v.className = 'verdict ' + (correct ? 'ok' : 'bad');
      }
    }""", "showResult peeked"),

    # record 支持 peeked
    ("""  function record(cardId, correct, info, preview) {
    S.answered[cardId] = { correct: correct, picked: info.picked || [] };
    post({ type: 'answer', cardId: cardId, correct: !!correct, preview: preview || '' });
    updateProgress();
  }""",
     """  function record(cardId, correct, info, preview) {
    var peeked = !!(info && info.peeked);
    S.answered[cardId] = { correct: correct, picked: info.picked || [], peeked: peeked };
    post({ type: 'answer', cardId: cardId, correct: !!correct,
           peeked: peeked, preview: preview || '' });
    updateProgress();
  }

  // 提交前看解析：不判对错，只把题标成「已看」，记入待复习
  function peekAnswer(el, card, info) {
    el.dataset.locked = '1';
    var picked = (info && info.picked) || [];
    var sub = el.querySelector('.submit');
    if (sub) sub.style.display = 'none';
    var pk = el.querySelector('.peek');
    if (pk) pk.style.display = 'none';
    el.querySelectorAll('.opt').forEach(function (b) { b.classList.add('locked'); });
    el.querySelectorAll('.blank-input').forEach(function (i) { i.readOnly = true; });
    showResult(el, card, false, { picked: picked, peeked: true });
    record(card.id, false, { picked: picked, peeked: true }, previewOf(card));
  }""", "record + peekAnswer"),
])

# ---------------- 3. ReaderWebView.swift ----------------
patch("Sources/ReaderWebView.swift", [
    ("""    var scrollY: Double
    var theme: String
}""",
     """    var scrollY: Double
    var theme: String
    var allowPeek: Bool?
}""", "RenderPayload.allowPeek"),

    ("""                                        scrollY: scrollY,
                                        theme: theme)""",
     """                                        scrollY: scrollY,
                                        theme: theme,
                                        allowPeek: UserDefaults.standard.object(forKey: "hub.allowPeek") as? Bool)""",
     "构造 allowPeek"),

    ("""            if type == "answer" {
                let cardId = body["cardId"] as? String ?? ""
                let correct = body["correct"] as? Bool ?? false
                let preview = body["preview"] as? String ?? ""
                let lessonId = lesson.id
                let lessonTitle = lesson.title
                let store = StoreLocator.shared.store
                Task { @MainActor in
                    store?.record(lessonId: lessonId, lessonTitle: lessonTitle,
                                  cardId: cardId, correct: correct, preview: preview)
                }""",
     """            if type == "answer" {
                let cardId = body["cardId"] as? String ?? ""
                let correct = body["correct"] as? Bool ?? false
                let preview = body["preview"] as? String ?? ""
                let lessonId = lesson.id
                let lessonTitle = lesson.title
                let store = StoreLocator.shared.store
                Task { @MainActor in
                    store?.record(lessonId: lessonId, lessonTitle: lessonTitle,
                                  cardId: cardId, correct: correct, preview: preview)
                }""", "阅读页桥接（不变，仅确认）"),
])

# ---------------- 4. QuizView.swift ----------------
patch("Sources/QuizView.swift", [
    ("""struct QuizCardView: UIViewRepresentable {
    let item: QuizItem
    let fontSize: Double
    var onAnswer: (Bool) -> Void""",
     """struct QuizCardView: UIViewRepresentable {
    let item: QuizItem
    let fontSize: Double
    var allowPeek: Bool = true
    var onAnswer: (Bool, Bool) -> Void""", "QuizCardView 签名"),

    ("""    func makeCoordinator() -> Coord {
        Coord(item: item, fontSize: fontSize, onAnswer: onAnswer)
    }""",
     """    func makeCoordinator() -> Coord {
        Coord(item: item, fontSize: fontSize, allowPeek: allowPeek, onAnswer: onAnswer)
    }""", "makeCoordinator"),

    ("""        let item: QuizItem
        let fontSize: Double
        let onAnswer: (Bool) -> Void""",
     """        let item: QuizItem
        let fontSize: Double
        let allowPeek: Bool
        let onAnswer: (Bool, Bool) -> Void""", "Coord 属性"),

    ("""        init(item: QuizItem, fontSize: Double, onAnswer: @escaping (Bool) -> Void) {
            self.item = item
            self.fontSize = fontSize
            self.onAnswer = onAnswer
        }""",
     """        init(item: QuizItem, fontSize: Double, allowPeek: Bool,
             onAnswer: @escaping (Bool, Bool) -> Void) {
            self.item = item
            self.fontSize = fontSize
            self.allowPeek = allowPeek
            self.onAnswer = onAnswer
        }""", "Coord init"),

    ("""                                        scrollY: 0,
                                        theme: UserDefaults.standard.string(forKey: "hub.theme") ?? "auto")""",
     """                                        scrollY: 0,
                                        theme: UserDefaults.standard.string(forKey: "hub.theme") ?? "auto",
                                        allowPeek: allowPeek)""", "payload allowPeek"),

    ("""            if (body["type"] as? String) == "answer" {
                let ok = body["correct"] as? Bool ?? false
                onAnswer(ok)
            }""",
     """            if (body["type"] as? String) == "answer" {
                let ok = body["correct"] as? Bool ?? false
                let peeked = body["peeked"] as? Bool ?? false
                onAnswer(ok, peeked)
            }""", "桥接 peeked"),

    ("""    @State private var answeredThis = false
    @State private var finished = false""",
     """    @State private var answeredThis = false
    @State private var peekedThis = false
    @State private var finished = false
    @AppStorage("hub.allowPeek") private var allowPeek = true""", "QuizView 状态"),

    ("""                    QuizCardView(item: session.items[index], fontSize: store.fontSize) { ok in
                        handle(ok)
                    }
                    .id(index)""",
     """                    QuizCardView(item: session.items[index],
                                  fontSize: store.fontSize,
                                  allowPeek: allowPeek) { ok, peeked in
                        handle(ok, peeked)
                    }
                    .id(index)

                    if peekedThis {
                        Button {
                            advance()
                        } label: {
                            Text(index + 1 < session.items.count ? "下一题" : "看成绩")
                                .frame(maxWidth: .infinity)
                        }
                        .buttonStyle(.borderedProminent)
                        .padding(.horizontal, 16)
                        .padding(.bottom, 10)
                    }""", "QuizCardView 调用"),

    ("""                Button("再来一轮") {
                    index = 0; rightCount = 0; answeredThis = false
                    wrongList = []; finished = false
                }""",
     """                Button("再来一轮") {
                    index = 0; rightCount = 0; answeredThis = false
                    peekedThis = false; wrongList = []; finished = false
                }""", "再来一轮重置"),

    ("""    private func handle(_ ok: Bool) {
        guard !answeredThis else { return }
        answeredThis = true
        if ok { rightCount += 1 } else { wrongList.append(session.items[index]) }

        let it = session.items[index]
        // 记进度 + 错题本 + 每日统计 + 复习排期
        store.record(lessonId: it.lessonId, lessonTitle: it.lessonTitle,
                     cardId: it.card.id, correct: ok, preview: previewText(it))

        let nextIndex = index + 1
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.4) {
            if nextIndex < session.items.count {
                index = nextIndex
                answeredThis = false
            } else {
                finished = true
            }
        }
    }""",
     """    /// peeked=true 表示「提交前看了解析」：不算答对，记入待复习，停在这一题等用户点下一题
    private func handle(_ ok: Bool, peeked: Bool) {
        guard !answeredThis else { return }
        answeredThis = true
        peekedThis = peeked

        let it = session.items[index]
        if peeked {
            if !wrongList.contains(where: { $0.id == it.id }) { wrongList.append(it) }
        } else if ok {
            rightCount += 1
        } else {
            wrongList.append(it)
        }

        // 记进度 + 错题本 + 每日统计 + 复习排期
        store.record(lessonId: it.lessonId, lessonTitle: it.lessonTitle,
                     cardId: it.card.id, correct: ok, preview: previewText(it))

        if peeked { return }   // 看完了自己点「下一题」，不自动跳
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.4) {
            advance()
        }
    }

    private func advance() {
        let nextIndex = index + 1
        if nextIndex < session.items.count {
            index = nextIndex
            answeredThis = false
            peekedThis = false
        } else {
            finished = true
        }
    }""", "handle 改造"),
])

print("all patched")
