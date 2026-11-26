# -*- coding: utf-8 -*-
"""生成渲染测试台（直接用 reader.html 的骨架，末尾插测试脚本）"""
import glob
import io
import json
import os
import shutil

ROOT = r"C:/Users/chong/Documents/studyhub"
TMP = os.path.join(ROOT, "out-harness")

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

with io.open(os.path.join(TMP, "cards.js"), "w", encoding="utf-8") as f:
    f.write("window.CASES = ")
    json.dump(cards, f, ensure_ascii=False)
    f.write(";\n")

# 用 reader.html 的骨架，插脚本
html = io.open(os.path.join(TMP, "reader.html"), encoding="utf-8").read()

base = os.path.basename("reader.html")
test = """
<div id="harness-out" style="white-space:pre;font-size:11px;padding:10px;display:none"></div>
<script src="cards.js"></script>
<script>
(function () {
  var results = [];
  var cases = window.CASES || [];
  var i = 0;

  function stat(c) {
    var stage = document.getElementById('stage');
    var html = stage.innerHTML;
    return {
      lesson: c.lesson,
      id: c.card.id,
      type: c.card.type,
      opts: stage.querySelectorAll('.opt').length,
      optWant: (c.card.options || []).length,
      inputs: stage.querySelectorAll('.blank-input').length,
      inputWant: (c.card.blanks || []).length,
      svg: stage.querySelectorAll('svg').length,
      svgWant: c.card.svg ? 1 : 0,
      katex: stage.querySelectorAll('.katex').length,
      mathWant: (String(c.card.question || '').indexOf('$') >= 0) ? 1 : 0,
      submit: stage.querySelector('.submit') ? 1 : 0,
      verdict: stage.querySelector('.verdict') ? 1 : 0,
      explain: stage.querySelector('.explain') ? 1 : 0,
      peek: stage.querySelector('.peek') ? 1 : 0,
      leftover: (html.indexOf('{{') >= 0 || html.indexOf('____') >= 0) ? 1 : 0,
      text: html.replace(/<[^>]+>/g, ' ').slice(0, 0)
    };
  }

  function step() {
    if (i >= cases.length) {
      var out = document.getElementById('harness-out');
      out.textContent = JSON.stringify(results);
      out.style.display = 'block';
      document.title = 'DONE';
      return;
    }
    var c = cases[i];
    try {
      window.renderStudyHub({
        lessonId: 'h' + i,
        title: 't',
        subtitle: '',
        cards: [c.card],
        progress: {},
        fontSize: 16,
        scrollY: 0,
        theme: 'light',
        allowPeek: true
      });
      results.push(stat(c));
    } catch (e) {
      results.push({ lesson: c.lesson, id: c.card.id, type: c.card.type, error: String(e) });
    }
    i++;
    setTimeout(step, 0);
  }
  setTimeout(step, 30);
})();
</script>
"""

# 在 reader.js 之后插入
marker = '<script src="reader.js"></script>'
assert marker in html, "reader.html 里没找到 reader.js 引用"
html = html.replace(marker, marker + "\n" + test)

io.open(os.path.join(TMP, "harness.html"), "w", encoding="utf-8").write(html)
print("harness ready:", TMP, "| cases:", len(cards))
