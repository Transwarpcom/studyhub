# -*- coding: utf-8 -*-
"""网页版：渲染 card.svg + 每题「看解析」开关（只查看，不锁不判分）"""
import io

ROOT = r"C:/Users/chong/Documents/studyhub/"


def sub(path, old, new, tag):
    p = ROOT + path
    s = io.open(p, encoding="utf-8").read()
    n = s.count(old)
    assert n == 1, "%s: %s 命中 %d" % (path, tag, n)
    io.open(p, "w", encoding="utf-8", newline="\n").write(s.replace(old, new))
    print("  ok", path, "|", tag)


# 1) qcard：题干后面插示意图
sub("web/app.js",
    """  var body = el('<div class="qbody"></div>');
  body.appendChild(mdEl(card.question || card.q || ''));
  c.appendChild(body);""",
    """  var body = el('<div class="qbody"></div>');
  body.appendChild(mdEl(card.question || card.q || ''));
  if (card.svg) {
    var fig = el('<div class="figure">' + card.svg + '</div>');
    body.appendChild(fig);
  }
  c.appendChild(body);""", "qcard svg")

# 2) renderAnswer：非解答题加「看解析」（纯查看）
sub("web/app.js",
    """function renderAnswer(area, exp, head, lid, card, c, settled) {
  var t = card.type || '';
""",
    """function renderAnswer(area, exp, head, lid, card, c, settled) {
  var t = card.type || '';

  // 上课用：随时看一眼解析，不锁选项、不判分、不记录
  if (t !== 'text' && (card.explain || card.exp)) {
    var peek = el('<button class="btn sm ghost peekbtn" type="button">看解析</button>');
    peek.onclick = function () {
      var willOpen = !!exp.hidden;
      if (willOpen) {
        if (!exp.dataset.filled) {
          exp.innerHTML = '';
          exp.appendChild(mdEl(card.explain || card.exp));
          exp.dataset.filled = '1';
        }
        exp.hidden = false;
        peek.textContent = '收起解析';
      } else {
        exp.hidden = true;
        peek.textContent = '看解析';
      }
    };
    area.appendChild(peek);
  }
""", "renderAnswer peek")

# 3) 样式
sub("web/app.css",
    """/* ===== 题目 ===== */""",
    """/* ===== 示意图 ===== */
.figure{margin:10px 0 4px;text-align:center}
.figure svg{max-width:100%;height:auto}
.peekbtn{margin:2px 0 8px}

/* ===== 题目 ===== */""", "figure 样式")

print("done")
