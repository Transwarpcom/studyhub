# -*- coding: utf-8 -*-
"""考试模式（限时交卷）+ payload.exam + Store 扩展"""
import io

ROOT = r"C:/Users/chong/Documents/studyhub/"


def sub(path, old, new, tag):
    p = ROOT + path
    s = io.open(p, encoding="utf-8").read()
    n = s.count(old)
    assert n == 1, "%s: %s 命中 %d" % (path, tag, n)
    io.open(p, "w", encoding="utf-8", newline="\n").write(s.replace(old, new))
    print("  ok", path, "|", tag)


# ---------- 1. RenderPayload 加 exam ----------
sub("Sources/ReaderWebView.swift",
    """    var allowPeek: Bool?
}""",
    """    var allowPeek: Bool?
    var exam: Bool?
}""", "payload exam")

# ---------- 2. reader.js：考试模式不判分，只上报选择 ----------
sub("Resources/web/reader.js",
    """    answered: {},   // cardId -> {correct, picked, peeked}
    allowPeek: true,""",
    """    answered: {},   // cardId -> {correct, picked, peeked}
    allowPeek: true,
    exam: false,     // 考试模式：只记录选择，交卷后由 App 统一判分""", "S.exam")

sub("Resources/web/reader.js",
    """    S.allowPeek = payload.allowPeek !== false;""",
    """    S.allowPeek = payload.allowPeek !== false;
    S.exam = payload.exam === true;""", "读 exam")

# 单选/多选：exam 只上报
sub("Resources/web/reader.js",
    """        submit.disabled = picked.length === 0;
      });
    });""",
    """        submit.disabled = picked.length === 0;
        if (S.exam) {
          post({ type: 'pick', cardId: card.id, picked: picked.map(String) });
        }
      });
    });""", "choice exam")

# 多选提交：exam 模式下不判分
sub("Resources/web/reader.js",
    """    submit.addEventListener('click', function () {
      evaluateChoice(el, card, picked);
    });""",
    """    submit.addEventListener('click', function () {
      if (S.exam) {
        post({ type: 'pick', cardId: card.id, picked: picked.map(String) });
        return;
      }
      evaluateChoice(el, card, picked);
    });""", "multi exam")

# 填空：exam 模式隐藏提交、输入即上报
sub("Resources/web/reader.js",
    """    var peekBtn = el.querySelector('.peek');

    function resetUI() {""",
    """    var peekBtn = el.querySelector('.peek');

    if (S.exam) {
      var sb = el.querySelector('.submit');
      if (sb) sb.style.display = 'none';
      el.querySelectorAll('.blank-input').forEach(function (inp) {
        inp.addEventListener('input', function () {
          var vals = [];
          el.querySelectorAll('.blank-input').forEach(function (x) { vals.push(x.value); });
          post({ type: 'pick', cardId: card.id, picked: vals });
        });
      });
    }

    function resetUI() {""", "blank exam")

print("done")
