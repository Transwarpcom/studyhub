# -*- coding: utf-8 -*-
"""填空题：没有 {{n}} 时，把连续下划线按顺序变成输入框（App + 网页版）"""
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


# ---------------- App 内嵌 reader.js ----------------
sub("Resources/web/reader.js",
    """    var q = mdToHtml(card.question || '');
    var n = 0;
    q = q.replace(/\\{\\{(\\d+)\\}\\}/g, function (m, idx) {
      n = Math.max(n, parseInt(idx, 10));
      return '<input class="blank-input" data-blank="' + (parseInt(idx, 10) - 1) + '" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false">';
    });""",
    """    var q = mdToHtml(card.question || '');
    var blankCount = (card.blanks || []).length;

    // 两种占位都支持：{{1}} 显式编号，或 ____ 按出现顺序
    var hasCurly = /\\{\\{\\d+\\}\\}/.test(q);
    if (hasCurly) {
      q = q.replace(/\\{\\{(\\d+)\\}\\}/g, function (m, idx) {
        return '<input class="blank-input" data-blank="' + (parseInt(idx, 10) - 1) +
               '" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false">';
      });
    } else {
      var seq = 0;
      q = q.replace(/_{2,}/g, function () {
        var i = seq < blankCount ? seq : seq;
        seq++;
        return '<input class="blank-input" data-blank="' + i +
               '" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false">';
      });
      // 题干没写 ____ 却有空：在末尾补
      if (seq === 0 && blankCount > 0) {
        var extra = '';
        for (var k = 0; k < blankCount; k++) {
          extra += ' <input class="blank-input" data-blank="' + k +
                   '" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false">';
        }
        q += '<div class="blank-fill">答案：' + extra + '</div>';
      }
    }""", "reader.js 下划线占位")

# ---------------- 网页版 app.js ----------------
sub("web/app.js",
    """  var q = mdEl(card.question || card.q || '');""",
    """  var q = mdEl(card.question || card.q || '');""", "占位（网页版结构不同，单独处理）")

print("\n成功 %d，失败 %d" % (len(OK), len(FAIL)))
for f in FAIL:
    print("  ", f)
