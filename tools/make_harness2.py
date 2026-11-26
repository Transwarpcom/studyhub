# -*- coding: utf-8 -*-
"""交互测试：注入每张卡后模拟点击/填写，检查判分与解析是否真的出现"""
import glob
import io
import json
import os
import shutil

ROOT = r"C:/Users/chong/Documents/studyhub"
TMP = os.path.join(ROOT, "out-harness2")

if os.path.isdir(TMP):
    shutil.rmtree(TMP)
os.makedirs(TMP)
for f in ("reader.html", "reader.js"):
    shutil.copy(os.path.join(ROOT, "Resources", "web", f), os.path.join(TMP, f))
shutil.copytree(os.path.join(ROOT, "Resources", "web", "katex"), os.path.join(TMP, "katex"))

cards = []
for p in sorted(glob.glob(os.path.join(ROOT, "content", "lessons", "*.json"))):
    d = json.load(io.open(p, encoding="utf-8"))
    for c in d.get("cards") or []:
        if c.get("type") == "lecture":
            continue
        cards.append({"lesson": d["id"], "card": c})

io.open(os.path.join(TMP, "cards.js"), "w", encoding="utf-8").write(
    "window.CASES = " + json.dumps(cards, ensure_ascii=False) + ";\n")

html = io.open(os.path.join(TMP, "reader.html"), encoding="utf-8").read()

test = """
<div id="harness-out" style="display:none;white-space:pre"></div>
<script src="cards.js"></script>
<script>
(function () {
  var results = [];
  var cases = window.CASES || [];
  var i = 0;

  function run(c) {
    var stage = document.getElementById('stage');
    var card = c.card;
    window.renderStudyHub({
      lessonId: 'h' + i, title: 't', subtitle: '', cards: [card],
      progress: {}, fontSize: 16, scrollY: 0, theme: 'light', allowPeek: true
    });
    var r = { lesson: c.lesson, id: card.id, type: card.type };

    if (card.type === 'choice' || card.type === 'multi' || card.type === 'judge') {
      var opt = stage.querySelector('.opt');
      if (!opt) { r.fail = '没有选项元素'; return r; }
      opt.click();
      var sub = stage.querySelector('.submit');
      if (sub && !sub.disabled) sub.click();
      var v = stage.querySelector('.verdict');
      r.verdict = v ? v.textContent.trim() : '';
      var ex = stage.querySelector('.explain');
      r.exExplain = !!(ex && ex.style.display === 'block');
    } else if (card.type === 'blank') {
      var inputs = stage.querySelectorAll('.blank-input');
      if (!inputs.length) { r.fail = '没有输入框'; return r; }
      var blanks = card.blanks || [];
      inputs.forEach(function (inp, k) {
        var acc = blanks[k] || [];
        inp.value = acc.length ? String(acc[0]) : 'x';
      });
      var sub2 = stage.querySelector('.submit');
      if (!sub2) { r.fail = '没有提交按钮'; return r; }
      sub2.click();
      var v2 = stage.querySelector('.verdict');
      r.verdict = v2 ? v2.textContent.trim() : '';
      var ex2 = stage.querySelector('.explain');
      r.exExplain = !!(ex2 && ex2.style.display === 'block');
    } else if (card.type === 'text') {
      var show = stage.querySelector('.submit');
      if (!show) { r.fail = '没有看解析按钮'; return r; }
      show.click();
      var ex3 = stage.querySelector('.explain');
      r.exExplain = !!(ex3 && ex3.style.display === 'block');
      r.exLen = ex3 ? ex3.textContent.trim().length : 0;
    }
    return r;
  }

  function step() {
    if (i >= cases.length) {
      var out = document.getElementById('harness-out');
      out.textContent = JSON.stringify(results);
      out.style.display = 'block';
      document.title = 'DONE';
      return;
    }
    try {
      var r = run(cases[i]);
      if (r) results.push(r);
    } catch (e) {
      results.push({ lesson: cases[i].lesson, id: cases[i].card.id, type: cases[i].card.type,
                     fail: String(e) });
    }
    i++;
    setTimeout(step, 0);
  }
  setTimeout(step, 30);
})();
</script>
"""

marker = '<script src="reader.js"></script>'
html = html.replace(marker, marker + "\n" + test)
io.open(os.path.join(TMP, "harness2.html"), "w", encoding="utf-8").write(html)
print("harness2 ready, cases:", len(cards))
