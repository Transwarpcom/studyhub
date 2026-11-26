# -*- coding: utf-8 -*-
"""改回语义：看解析只是看，不锁选项、不记录、不影响作答"""
import io

ROOT = r"C:/Users/chong/Documents/studyhub/"


def sub(path, old, new, tag):
    p = ROOT + path
    s = io.open(p, encoding="utf-8").read()
    n = s.count(old)
    assert n == 1, "%s: %s 命中 %d" % (path, tag, n)
    io.open(p, "w", encoding="utf-8", newline="\n").write(s.replace(old, new))
    print("  ok", path, "|", tag)


# ---------- 1. reader.js：peekAnswer → toggleExplain（纯查看，可收起） ----------
sub("Resources/web/reader.js",
    """    if (peekBtn) {
      peekBtn.addEventListener('click', function () {
        if (el.dataset.locked === '1') return;
        peekAnswer(el, card, { picked: picked }, resetUI);
      });
    }""",
    """    if (peekBtn) {
      peekBtn.addEventListener('click', function () {
        toggleExplain(el, card, peekBtn);
      });
    }""",
    "choice peek 事件")

sub("Resources/web/reader.js",
    """    if (peekBtn) {
      peekBtn.addEventListener('click', function () {
        if (el.dataset.locked === '1') return;
        var picked = [];
        el.querySelectorAll('.blank-input').forEach(function (inp) { picked.push(inp.value); });
        peekAnswer(el, card, { picked: picked }, resetUI);
      });
    }""",
    """    if (peekBtn) {
      peekBtn.addEventListener('click', function () {
        toggleExplain(el, card, peekBtn);
      });
    }""",
    "blank peek 事件")

sub("Resources/web/reader.js",
    """  // 提交前看解析：不判对错，只把题标成「已看」，记入待复习
  function peekAnswer(el, card, info, reset) {
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
    if (reset) el.appendChild(redoBar(card, reset));
  }""",
    """  // 看解析：只是看，不锁选项、不判分、不记录，可以随时收起继续做
  function toggleExplain(el, card, btn) {
    var box = el.querySelector('.explain');
    if (!box) return;
    var open = box.style.display === 'block';
    if (open) {
      box.style.display = 'none';
      box.innerHTML = '';
      if (btn) btn.textContent = '看解析';
      return;
    }
    box.style.display = 'block';
    box.innerHTML = '<div class="tag">解析</div><div class="md">' +
      mdToHtml(card.explain || '（暂无解析）') + '</div>';
    renderMath(box);
    if (btn) btn.textContent = '收起解析';
  }""",
    "toggleExplain")

# 已答状态恢复时，别把「看解析」按钮藏掉（答完也能回看解析）
sub("Resources/web/reader.js",
    """    el.querySelector('.submit').style.display = 'none';
    var pk = el.querySelector('.peek');
    if (pk) pk.style.display = 'none';""",
    """    el.querySelector('.submit').style.display = 'none';""",
    "restoreChoice 保留 peek")

sub("Resources/web/reader.js",
    """    if (prev) {
      if (peekBtn) peekBtn.style.display = 'none';
      el.querySelectorAll('.blank-input').forEach(function (inp, idx) {""",
    """    if (prev) {
      el.querySelectorAll('.blank-input').forEach(function (inp, idx) {""",
    "blank 恢复保留 peek")

# ---------- 2. QuizView：撤掉 peek 的锁与记账 ----------
sub("Sources/QuizView.swift",
    """    @State private var peekedThis = false
    @State private var peekedCount = 0
    @State private var finished = false""",
    """    @State private var finished = false""",
    "去掉 peeked 状态")

sub("Sources/QuizView.swift",
    """                    .id(index)

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
                    }""",
    """                    .id(index)""",
    "去掉下一题按钮")

sub("Sources/QuizView.swift",
    """                    Text("\\(rightCount) / \\(answeredTotal)")""",
    """                    Text("\\(rightCount) / \\(session.items.count)")""",
    "结果页分母还原")

sub("Sources/QuizView.swift",
    """                    index = 0; rightCount = 0; answeredThis = false
                    peekedThis = false; peekedCount = 0
                    wrongList = []; finished = false""",
    """                    index = 0; rightCount = 0; answeredThis = false
                    wrongList = []; finished = false""",
    "再来一轮还原")

sub("Sources/QuizView.swift",
    """    /// peeked=true 表示「提交前看了解析」：不算答对，记入待复习，停在这一题等用户点下一题
    private func handle(_ ok: Bool, _ peeked: Bool) {
        guard !answeredThis else { return }
        answeredThis = true
        peekedThis = peeked

        let it = session.items[index]
        if peeked {
            peekedCount += 1
            if !wrongList.contains(where: { $0.id == it.id }) { wrongList.append(it) }
        } else if ok {
            rightCount += 1
        } else {
            wrongList.append(it)
        }

        // 记进度 + 错题本 + 每日统计 + 复习排期
        store.record(lessonId: it.lessonId, lessonTitle: it.lessonTitle,
                     cardId: it.card.id, correct: ok, preview: previewText(it),
                     peeked: peeked)

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
    }""",
    """    private func handle(_ ok: Bool, _ peeked: Bool) {
        guard !answeredThis else { return }
        answeredThis = true

        let it = session.items[index]
        if ok { rightCount += 1 } else { wrongList.append(it) }

        // 记进度 + 错题本 + 每日统计 + 复习排期
        store.record(lessonId: it.lessonId, lessonTitle: it.lessonTitle,
                     cardId: it.card.id, correct: ok, preview: previewText(it))

        DispatchQueue.main.asyncAfter(deadline: .now() + 1.4) {
            self.advance()
        }
    }

    private func advance() {
        let nextIndex = index + 1
        if nextIndex < session.items.count {
            index = nextIndex
            answeredThis = false
        } else {
            finished = true
        }
    }""",
    "handle 还原")

sub("Sources/QuizView.swift",
    """    /// 真正作答的题数：看过解析的不算分母
    private var answeredTotal: Int {
        let n = session.items.count - peekedCount
        return n > 0 ? n : 1
    }

    private var rateText: String {
        guard session.items.count > peekedCount else { return "全部看过解析" }
        return "正确率 \\(rightCount * 100 / answeredTotal)%"
    }""",
    """    private var rateText: String {
        let n = session.items.count
        guard n > 0 else { return "" }
        return "正确率 \\(rightCount * 100 / n)%"
    }""",
    "rateText 还原")

# ---------- 3. 设置页去掉那个开关 ----------
sub("Sources/SettingsView.swift",
    """                Section {
                    Toggle("答题前可以看解析", isOn: $allowPeek)
                    Text("打开后每题都有「先看解析」按钮。看了解析的题不算答对，直接记入待复习与错题本，正确率不受影响。")
                        .font(.footnote)
                        .foregroundColor(.secondary)
                } header: {
                    Text("答题")
                }

""",
    "",
    "删设置开关")

sub("Sources/SettingsView.swift",
    """    @AppStorage("hub.allowPeek") private var allowPeek = true
""",
    "",
    "删设置项声明")

print("done")
