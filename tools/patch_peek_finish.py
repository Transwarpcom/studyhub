# -*- coding: utf-8 -*-
"""收尾：peek 之后的「重做本题」、恢复态隐藏 peek、状态细化"""
import io

P = r"C:/Users/chong/Documents/studyhub/Resources/web/reader.js"
s = io.open(P, encoding="utf-8").read()


def sub(old, new, tag):
    global s
    n = s.count(old)
    assert n == 1, "%s 命中 %d 次" % (tag, n)
    s = s.replace(old, new)
    print("  ok", tag)


# 1) 单选：resetUI 抽出来，peek 也能「重做本题」
sub("""    if (peekBtn) {
      peekBtn.addEventListener('click', function () {
        if (el.dataset.locked === '1') return;
        peekAnswer(el, card, { picked: picked });
      });
    }""",
    """    function resetUI() {
      picked = [];
      el.dataset.locked = '0';
      opts.forEach(function (b) { b.classList.remove('sel', 'right', 'wrong', 'locked'); });
      submit.disabled = true;
      submit.style.display = '';
      if (peekBtn) peekBtn.style.display = '';
      el.querySelector('.verdict').textContent = '';
      el.querySelector('.verdict').className = 'verdict';
      var ex = el.querySelector('.explain');
      if (ex) { ex.style.display = 'none'; ex.innerHTML = ''; }
    }

    if (peekBtn) {
      peekBtn.addEventListener('click', function () {
        if (el.dataset.locked === '1') return;
        peekAnswer(el, card, { picked: picked }, resetUI);
      });
    }""", "choice resetUI")

sub("""    var prev = S.answered[card.id];
    if (prev) {
      restoreChoice(el, card, prev);
      el.appendChild(redoBar(card, function () {
        picked = [];
        el.dataset.locked = '0';
        opts.forEach(function (b) { b.classList.remove('sel', 'right', 'wrong'); });
        submit.disabled = true;
        submit.style.display = '';
        el.querySelector('.verdict').textContent = '';
        el.querySelector('.verdict').className = 'verdict';
        var ex = el.querySelector('.explain');
        if (ex) { ex.style.display = 'none'; ex.innerHTML = ''; }
      }));
    }""",
    """    var prev = S.answered[card.id];
    if (prev) {
      restoreChoice(el, card, prev);
      el.appendChild(redoBar(card, resetUI));
    }""", "choice redoBar 复用")

# 2) restoreChoice 隐藏 peek
sub("""  function restoreChoice(el, card, prev) {
    el.dataset.locked = '1';
    el.querySelector('.submit').style.display = 'none';""",
    """  function restoreChoice(el, card, prev) {
    el.dataset.locked = '1';
    el.querySelector('.submit').style.display = 'none';
    var pk = el.querySelector('.peek');
    if (pk) pk.style.display = 'none';""", "restoreChoice 隐藏 peek")

# 3) 填空：peek 传 resetUI
sub("""    var peekBtn = el.querySelector('.peek');
    if (peekBtn) {
      peekBtn.addEventListener('click', function () {
        if (el.dataset.locked === '1') return;
        var picked = [];
        el.querySelectorAll('.blank-input').forEach(function (inp) { picked.push(inp.value); });
        peekAnswer(el, card, { picked: picked });
      });
    }""",
    """    var peekBtn = el.querySelector('.peek');

    function resetUI() {
      el.dataset.locked = '0';
      el.querySelectorAll('.blank-input').forEach(function (inp) {
        inp.value = '';
        inp.readOnly = false;
        inp.classList.remove('right', 'wrong');
      });
      var sub = el.querySelector('.submit');
      if (sub) sub.style.display = '';
      if (peekBtn) peekBtn.style.display = '';
      el.querySelector('.verdict').textContent = '';
      el.querySelector('.verdict').className = 'verdict';
      var ex = el.querySelector('.explain');
      if (ex) { ex.style.display = 'none'; ex.innerHTML = ''; }
    }

    if (peekBtn) {
      peekBtn.addEventListener('click', function () {
        if (el.dataset.locked === '1') return;
        var picked = [];
        el.querySelectorAll('.blank-input').forEach(function (inp) { picked.push(inp.value); });
        peekAnswer(el, card, { picked: picked }, resetUI);
      });
    }""", "blank resetUI")

# 4) 填空恢复态：隐藏 peek + 复用 resetUI
sub("""    var prev = S.answered[card.id];
    if (prev) {
      el.querySelectorAll('.blank-input').forEach(function (inp, idx) {""",
    """    var prev = S.answered[card.id];
    if (prev) {
      if (peekBtn) peekBtn.style.display = 'none';
      el.querySelectorAll('.blank-input').forEach(function (inp, idx) {""", "blank 恢复隐藏 peek")

sub("""      el.querySelector('.submit').style.display = 'none';
      showResult(el, card, prev.correct, prev);
      el.appendChild(redoBar(card, function () {
        el.querySelectorAll('.blank-input').forEach(function (inp) {
          inp.value = '';
          inp.readOnly = false;
          inp.classList.remove('right', 'wrong');
        });
        el.querySelector('.submit').style.display = '';
        el.querySelector('.verdict').textContent = '';
        el.querySelector('.verdict').className = 'verdict';
        var ex = el.querySelector('.explain');
        if (ex) { ex.style.display = 'none'; ex.innerHTML = ''; }
      }));
    }""",
    """      var subBtn = el.querySelector('.submit');
      if (subBtn) subBtn.style.display = 'none';
      showResult(el, card, prev.correct, prev);
      el.appendChild(redoBar(card, resetUI));
    }""", "blank redoBar 复用")

# 5) peekAnswer 支持 reset
sub("""  function peekAnswer(el, card, info) {
    el.dataset.locked = '1';""",
    """  function peekAnswer(el, card, info, reset) {
    el.dataset.locked = '1';""", "peekAnswer 签名")

sub("""    showResult(el, card, false, { picked: picked, peeked: true });
    record(card.id, false, { picked: picked, peeked: true }, previewOf(card));
  }""",
    """    showResult(el, card, false, { picked: picked, peeked: true });
    record(card.id, false, { picked: picked, peeked: true }, previewOf(card));
    if (reset) el.appendChild(redoBar(card, reset));
  }""", "peekAnswer 重做条")

io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("written", P)
