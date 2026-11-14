/* 学习台渲染引擎
 * 入口：window.renderStudyHub(payload)
 * payload = { lessonId, title, subtitle, cards:[Card], progress:{cardId:bool} }
 *
 * Card.type:
 *   lecture  正文（md）
 *   choice   单选
 *   multi    多选
 *   judge    判断
 *   blank    填空（题干里 {{1}} {{2}} 为答案位）
 *   text     简答/解答题
 */
(function () {
  'use strict';

  var S = {
    payload: null,
    lessonId: null,
    answered: {},   // cardId -> {correct, picked, inputs}
    total: 0,
    done: 0
  };

  // 长按复制公式 / 滚动位置上报
  var longPressTimer = null;
  var scrollTimer = null;

  document.addEventListener('touchstart', function (e) {
    var el = e.target && e.target.closest ? e.target.closest('.mtex') : null;
    if (!el) return;
    longPressTimer = setTimeout(function () {
      var tex = el.getAttribute('data-tex') || '';
      if (tex) post({ type: 'copy', tex: tex });
      if (navigator.vibrate) { try { navigator.vibrate(10); } catch (err) {} }
    }, 600);
  }, { passive: true });

  document.addEventListener('touchend', function () { if (longPressTimer) clearTimeout(longPressTimer); });
  document.addEventListener('touchmove', function () { if (longPressTimer) clearTimeout(longPressTimer); });

  window.addEventListener('scroll', function () {
    if (scrollTimer) return;
    scrollTimer = setTimeout(function () {
      scrollTimer = null;
      post({ type: 'scroll', y: window.scrollY || document.documentElement.scrollTop || 0 });
    }, 700);
  });

  // ---------- 与原生通信 ----------
  function post(obj) {
    try {
      if (window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.hub) {
        window.webkit.messageHandlers.hub.postMessage(obj);
      }
    } catch (e) {}
  }

  // ---------- 工具 ----------
  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  function toHalf(s) {
    return String(s == null ? '' : s)
      .replace(/[\uFF01-\uFF5E]/g, function (ch) {
        return String.fromCharCode(ch.charCodeAt(0) - 0xFEE0);
      })
      .replace(/\u3000/g, ' ');
  }

  function norm(s) {
    return toHalf(s)
      .replace(/\s+/g, '')
      .replace(/[，,。.、；;：:]/g, '')
      .replace(/[（(]/g, '(')
      .replace(/[）)]/g, ')')
      .replace(/[−–—]/g, '-')
      .toLowerCase();
  }

  // ---------- Markdown ----------
  function protectMath(src) {
    var store = [];
    var s = src;
    s = s.replace(/\$\$([\s\S]+?)\$\$/g, function (m, body) {
      store.push({ d: true, b: body });
      return '@@MATH' + (store.length - 1) + '@@';
    });
    s = s.replace(/\$([^\$\n]+?)\$/g, function (m, body) {
      store.push({ d: false, b: body });
      return '@@MATH' + (store.length - 1) + '@@';
    });
    return { text: s, store: store };
  }

  function restoreMath(html, store) {
    return html.replace(/@@MATH(\d+)@@/g, function (m, n) {
      var it = store[+n];
      if (!it) return '';
      // 公式里的 < > & 必须先转义，否则 innerHTML 会把 <\varepsilon 当成标签吞掉
      var body = String(it.b)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
      var delim = it.d ? '$$' : '$';
      // 包一层带 data-tex 的 span，长按可以复制 LaTeX 源码
      var raw = String(it.b).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
      return '<span class="mtex" data-tex="' + raw + '">' + delim + body + delim + '</span>';
    });
  }

  function inlineMd(s) {
    s = esc(s);
    s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    s = s.replace(/~~([^~]+)~~/g, '<del>$1</del>');
    s = s.replace(/(^|[^*])\*([^*\n]+)\*(?!\*)/g, '$1<em>$2</em>');
    s = s.replace(/`([^`]+)`/g, '<code>$1</code>');
    s = s.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, '<a href="$2">$1</a>');
    return s;
  }

  function splitRow(line) {
    var t = line.trim();
    if (t.charAt(0) === '|') t = t.slice(1);
    if (t.charAt(t.length - 1) === '|') t = t.slice(0, -1);
    return t.split('|').map(function (c) { return c.trim(); });
  }

  function mdToHtml(raw) {
    if (!raw) return '';
    var math = protectMath(raw);
    var src = math.text;

    var svgs = [];
    src = src.replace(/```svg[ \t]*\n([\s\S]*?)```/g, function (m, code) {
      svgs.push(code);
      return '\n@@SVG' + (svgs.length - 1) + '@@\n';
    });

    var codes = [];
    src = src.replace(/```[ \t]*[a-zA-Z0-9]*\n([\s\S]*?)```/g, function (m, code) {
      codes.push(esc(code));
      return '\n@@CODE' + (codes.length - 1) + '@@\n';
    });

    var lines = src.split('\n');
    var out = [];
    var i = 0;

    while (i < lines.length) {
      var line = lines[i];
      var t = line.trim();

      if (t === '') { i++; continue; }

      var ph = t.match(/^@@(SVG|CODE)(\d+)@@$/);
      if (ph) {
        if (ph[1] === 'SVG') {
          out.push('<div class="figure">' + svgs[+ph[2]] + '</div>');
        } else {
          out.push('<pre class="code"><code>' + codes[+ph[2]] + '</code></pre>');
        }
        i++; continue;
      }

      var h = t.match(/^(#{1,4})\s+(.*)$/);
      if (h) {
        var lv = h[1].length;
        out.push('<h' + lv + '>' + inlineMd(h[2]) + '</h' + lv + '>');
        i++; continue;
      }

      if (/^(-{3,}|\*{3,})$/.test(t)) { out.push('<hr>'); i++; continue; }

      // 表格：首行 |...| 且次行是分隔线
      if (t.charAt(0) === '|' && i + 1 < lines.length &&
          /^\|?[\s:\-|]+\|?$/.test(lines[i + 1].trim()) && lines[i + 1].indexOf('-') >= 0) {
        var head = splitRow(t);
        i += 2;
        var rows = [];
        while (i < lines.length && lines[i].trim().charAt(0) === '|') {
          rows.push(splitRow(lines[i]));
          i++;
        }
        var html = '<div class="tbl-wrap"><table><thead><tr>';
        head.forEach(function (c) { html += '<th>' + inlineMd(c) + '</th>'; });
        html += '</tr></thead><tbody>';
        rows.forEach(function (r) {
          html += '<tr>';
          for (var k = 0; k < head.length; k++) {
            html += '<td>' + inlineMd(r[k] || '') + '</td>';
          }
          html += '</tr>';
        });
        html += '</tbody></table></div>';
        out.push(html);
        continue;
      }

      if (t.charAt(0) === '>') {
        var buf = [];
        while (i < lines.length && lines[i].trim().charAt(0) === '>') {
          buf.push(lines[i].trim().replace(/^>\s?/, ''));
          i++;
        }
        out.push('<blockquote>' + inlineMd(buf.join(' ')) + '</blockquote>');
        continue;
      }

      if (/^[-*+]\s+/.test(t) || /^\d+[.)]\s+/.test(t)) {
        var ordered = /^\d+[.)]\s+/.test(t);
        var items = [];
        while (i < lines.length) {
          var lt = lines[i].trim();
          var mm = ordered ? lt.match(/^\d+[.)]\s+(.*)$/) : lt.match(/^[-*+]\s+(.*)$/);
          if (!mm) break;
          items.push('<li>' + inlineMd(mm[1]) + '</li>');
          i++;
        }
        out.push('<' + (ordered ? 'ol' : 'ul') + '>' + items.join('') + '</' + (ordered ? 'ol' : 'ul') + '>');
        continue;
      }

      var pbuf = [t];
      i++;
      while (i < lines.length) {
        var nt = lines[i].trim();
        if (nt === '') break;
        if (/^(#{1,4}\s|[-*+]\s|\d+[.)]\s|>|\||@@|```)/.test(nt)) break;
        pbuf.push(nt);
        i++;
      }
      out.push('<p>' + inlineMd(pbuf.join(' ')) + '</p>');
    }

    return restoreMath(out.join('\n'), math.store);
  }

  function renderMath(root) {
    if (typeof renderMathInElement !== 'function') return;
    try {
      renderMathInElement(root, {
        delimiters: [
          { left: '$$', right: '$$', display: true },
          { left: '$', right: '$', display: false }
        ],
        throwOnError: false,
        ignoredTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code', 'option']
      });
    } catch (e) {}
    // 兜底：仍然溢出的行内公式，标成可横向滑动
    try {
      root.querySelectorAll('.katex').forEach(function (k) {
        if (k.closest('.katex-display')) return;
        if (k.scrollWidth > k.clientWidth + 2) k.classList.add('kx-wide');
      });
    } catch (e) {}
  }

  // ---------- 卡片构建 ----------
  /** 卡片顶部的「第 N 题 · 题型」 */
  function kickerText(card) {
    var label = typeLabel(card.type);
    var no = card.__qno;
    if (!no) return label;
    return '第 ' + no + ' 题' + (label ? ' · ' + label : '');
  }

  /** 重做本题：清掉记录，重新开放作答 */
  function redoBar(card, reset) {
    var bar = document.createElement('div');
    bar.className = 'btn-row redo-row';
    var b = document.createElement('button');
    b.className = 'btn ghost small';
    b.textContent = '重做本题';
    b.addEventListener('click', function () {
      delete S.answered[card.id];
      post({ type: 'answer', cardId: card.id, correct: null, preview: '' });
      reset();
      bar.style.display = 'none';
      updateProgress();
    });
    bar.appendChild(b);
    return bar;
  }

  function typeLabel(t) {
    return { choice: '单选题', multi: '多选题', judge: '判断题', blank: '填空题', text: '解答题', lecture: '讲解' }[t] || '';
  }

  function buildLecture(card) {
    var el = document.createElement('article');
    el.className = 'card lecture';
    var h = '';
    if (card.title) {
      h += '<div class="card-title"><span class="dot"></span>' + esc(card.title) + '</div>';
    }
    h += '<div class="md">' + mdToHtml(card.md || '') + '</div>';
    if (card.svg) {
      h += '<div class="figure">' + card.svg + '</div>';
    }
    el.innerHTML = h;
    return el;
  }

  function optionsHtml(card, multi) {
    var h = '<div class="opts">';
    (card.options || []).forEach(function (opt, idx) {
      var lab = String.fromCharCode(65 + idx);
      h += '<button class="opt" data-idx="' + idx + '" data-multi="' + (multi ? '1' : '0') + '">' +
           '<span class="lab">' + (multi ? '' : lab) + '</span>' +
           '<span class="txt">' + mdToHtml(opt) + '</span></button>';
    });
    h += '</div>';
    return h;
  }

  function buildChoice(card) {
    var multi = card.type === 'multi';
    var el = document.createElement('article');
    el.className = 'card';
    el.dataset.cardId = card.id;

    var h = '<div class="kicker">' + kickerText(card) + '</div>';
    h += '<div class="md q">' + mdToHtml(card.question || '') + '</div>';
    if (card.svg) h += '<div class="figure">' + card.svg + '</div>';
    h += optionsHtml(card, multi);
    h += '<div class="btn-row"><button class="btn submit" disabled>提交答案</button></div>';
    h += '<div class="verdict"></div><div class="explain" style="display:none"></div>';
    el.innerHTML = h;

    var picked = [];
    var opts = el.querySelectorAll('.opt');
    var submit = el.querySelector('.submit');

    opts.forEach(function (btn) {
      btn.addEventListener('click', function () {
        if (el.dataset.locked === '1') return;
        var idx = parseInt(btn.dataset.idx, 10);
        if (multi) {
          var pos = picked.indexOf(idx);
          if (pos >= 0) { picked.splice(pos, 1); btn.classList.remove('sel'); }
          else { picked.push(idx); btn.classList.add('sel'); }
        } else {
          picked = [idx];
          opts.forEach(function (b) { b.classList.remove('sel'); });
          btn.classList.add('sel');
        }
        submit.disabled = picked.length === 0;
      });
    });

    submit.addEventListener('click', function () {
      evaluateChoice(el, card, picked);
    });

    // 恢复已答状态
    var prev = S.answered[card.id];
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
    }

    return el;
  }

  function evaluateChoice(el, card, picked) {
    var ans = (card.answer || []).slice().sort(function (a, b) { return a - b; });
    var p = picked.slice().sort(function (a, b) { return a - b; });
    var correct = ans.length === p.length && ans.every(function (v, i) { return v === p[i]; });

    el.dataset.locked = '1';
    el.querySelectorAll('.opt').forEach(function (b) {
      var idx = parseInt(b.dataset.idx, 10);
      b.classList.add('locked');
      b.classList.remove('sel');
      if (ans.indexOf(idx) >= 0) b.classList.add('right');
      else if (picked.indexOf(idx) >= 0) b.classList.add('wrong');
    });
    el.querySelector('.submit').style.display = 'none';

    showResult(el, card, correct, { picked: picked });
    record(card.id, correct, { picked: picked }, previewOf(card));
  }

  function restoreChoice(el, card, prev) {
    el.dataset.locked = '1';
    el.querySelector('.submit').style.display = 'none';
    var ans = card.answer || [];
    el.querySelectorAll('.opt').forEach(function (b) {
      var idx = parseInt(b.dataset.idx, 10);
      b.classList.add('locked');
      if (ans.indexOf(idx) >= 0) b.classList.add('right');
      else if ((prev.picked || []).indexOf(idx) >= 0) b.classList.add('wrong');
    });
    showResult(el, card, prev.correct, prev);
  }

  function buildBlank(card) {
    var el = document.createElement('article');
    el.className = 'card';
    el.dataset.cardId = card.id;

    var q = mdToHtml(card.question || '');
    var n = 0;
    q = q.replace(/\{\{(\d+)\}\}/g, function (m, idx) {
      n = Math.max(n, parseInt(idx, 10));
      return '<input class="blank-input" data-blank="' + (parseInt(idx, 10) - 1) + '" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false">';
    });

    var h = '<div class="kicker">' + kickerText(card) + '</div>';
    h += '<div class="md q">' + q + '</div>';
    if (card.svg) h += '<div class="figure">' + card.svg + '</div>';
    h += '<div class="btn-row"><button class="btn submit">提交答案</button></div>';
    h += '<div class="verdict"></div><div class="explain" style="display:none"></div>';
    el.innerHTML = h;

    el.querySelector('.submit').addEventListener('click', function () {
      var inputs = el.querySelectorAll('.blank-input');
      var blanks = card.blanks || [];
      var okAll = true;
      var picked = [];
      inputs.forEach(function (inp) {
        var k = parseInt(inp.dataset.blank, 10);
        var val = inp.value;
        picked.push(val);
        var accepted = (blanks[k] || []).map(norm);
        var ok = accepted.indexOf(norm(val)) >= 0;
        inp.classList.add(ok ? 'right' : 'wrong');
        inp.readOnly = true;
        if (!ok) okAll = false;
      });
      el.querySelector('.submit').style.display = 'none';
      showResult(el, card, okAll, { picked: picked });
      record(card.id, okAll, { picked: picked }, previewOf(card));
    });

    var prev = S.answered[card.id];
    if (prev) {
      el.querySelectorAll('.blank-input').forEach(function (inp, idx) {
        inp.value = (prev.picked || [])[idx] || '';
        var blanks = card.blanks || [];
        var accepted = (blanks[idx] || []).map(norm);
        var ok = accepted.indexOf(norm(inp.value)) >= 0;
        inp.classList.add(ok ? 'right' : 'wrong');
        inp.readOnly = true;
      });
      el.querySelector('.submit').style.display = 'none';
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
    }

    return el;
  }

  function buildText(card) {
    var el = document.createElement('article');
    el.className = 'card';
    el.dataset.cardId = card.id;

    var h = '<div class="kicker">' + kickerText(card) + '</div>';
    h += '<div class="md q">' + mdToHtml(card.question || '') + '</div>';
    if (card.svg) h += '<div class="figure">' + card.svg + '</div>';
    h += '<textarea class="ans" placeholder="写你的思路（可选），写完对答案自评"></textarea>';
    h += '<div class="btn-row"><button class="btn submit">看解析</button></div>';
    h += '<div class="btn-row self-row" style="display:none">' +
         '<button class="btn small" data-ok="1">会了</button>' +
         '<button class="btn ghost small" data-ok="0">还不会</button></div>';
    h += '<div class="explain" style="display:none"></div>';
    el.innerHTML = h;

    var ta = el.querySelector('textarea');
    var showBtn = el.querySelector('.submit');
    var selfRow = el.querySelector('.self-row');

    showBtn.addEventListener('click', function () {
      showBtn.style.display = 'none';
      ta.readOnly = true;
      var box = el.querySelector('.explain');
      box.style.display = 'block';
      box.innerHTML = '<div class="tag">参考解答</div><div class="md">' + mdToHtml(card.explain || '（暂无解析）') + '</div>';
      renderMath(box);
      selfRow.style.display = 'flex';
    });

    selfRow.querySelectorAll('[data-ok]').forEach(function (b) {
      b.addEventListener('click', function () {
        selfRow.style.display = 'none';
        var ok = b.dataset.ok === '1';
        record(card.id, ok, { picked: [ta.value] }, previewOf(card));
        updateProgress();
      });
    });

    // 恢复已答状态
    var prev = S.answered[card.id];
    if (prev) {
      ta.value = (prev.picked || [])[0] || '';
      ta.readOnly = true;
      showBtn.style.display = 'none';
      selfRow.style.display = 'none';
      var box = el.querySelector('.explain');
      box.style.display = 'block';
      box.innerHTML = '<div class="tag">参考解答</div><div class="md">' + mdToHtml(card.explain || '（暂无解析）') + '</div>';
      renderMath(box);
      el.appendChild(redoBar(card, function () {
        ta.value = '';
        ta.readOnly = false;
        showBtn.style.display = '';
        selfRow.style.display = 'none';
        var ex = el.querySelector('.explain');
        if (ex) { ex.style.display = 'none'; ex.innerHTML = ''; }
      }));
    }

    return el;
  }

  function showResult(el, card, correct, info) {
    var v = el.querySelector('.verdict');
    if (v) {
      v.textContent = correct ? '✓ 答对了' : '✗ 再想想';
      v.className = 'verdict ' + (correct ? 'ok' : 'bad');
    }
    var box = el.querySelector('.explain');
    if (box && card.explain) {
      box.style.display = 'block';
      box.innerHTML = '<div class="tag">解析</div><div class="md">' + mdToHtml(card.explain) + '</div>';
      renderMath(box);
    }
    if (correct) post({ type: 'haptic' });
  }

  function previewOf(card) {
    var t = (card.question || card.md || '')
      .replace(/\$\$[\s\S]*?\$\$/g, ' ')
      .replace(/\$[^$\n]*\$/g, ' ')
      .replace(/[#*`>|_]/g, ' ')
      .replace(/\s+/g, ' ')
      .trim();
    return t.slice(0, 60);
  }

  function record(cardId, correct, info, preview) {
    S.answered[cardId] = { correct: correct, picked: info.picked || [] };
    post({ type: 'answer', cardId: cardId, correct: !!correct, preview: preview || '' });
    updateProgress();
  }

  // ---------- 进度 ----------
  function updateProgress() {
    var total = S.total;
    var done = Object.keys(S.answered).length;
    if (done > total) done = total;
    var pct = total > 0 ? Math.round(done * 100 / total) : 100;
    var fill = document.getElementById('hfill');
    if (fill) fill.style.width = pct + '%';

    var right = 0;
    Object.keys(S.answered).forEach(function (k) { if (S.answered[k].correct) right++; });
    var meta = document.getElementById('hmeta');
    if (meta) {
      if (total === 0) {
        meta.textContent = '阅读材料 · ' + S.payload.cards.length + ' 张卡片';
      } else {
        meta.textContent = '已答 ' + done + '/' + total + ' · 正确 ' + right +
          (done > 0 ? '（' + Math.round(right * 100 / done) + '%）' : '');
      }
    }
    var foot = document.getElementById('foot');
    if (foot) {
      foot.textContent = total > 0 && done >= total
        ? '本节完成 ' + right + '/' + total + '（' + Math.round(right * 100 / total) + '%）'
        : '共 ' + S.payload.cards.length + ' 张卡片';
    }
  }

  // ---------- 主入口 ----------
  function applyFontSize(v) {
    var size = (typeof v === 'number' && v >= 13 && v <= 24) ? v : 17;
    document.body.style.fontSize = size + 'px';
  }

  function applyTheme(t) {
    document.body.classList.remove('theme-light', 'theme-dark');
    if (t === 'light') document.body.classList.add('theme-light');
    else if (t === 'dark') document.body.classList.add('theme-dark');
  }

  function build(payload) {
    S.payload = payload;
    S.lessonId = payload.lessonId;
    applyFontSize(payload.fontSize);
    applyTheme(payload.theme);
    S.answered = {};
    S.total = 0;
    S.done = 0;

    var prog = payload.progress || {};
    Object.keys(prog).forEach(function (k) { S.answered[k] = { correct: !!prog[k], picked: [] }; });

    (payload.cards || []).forEach(function (c) {
      if (c.type !== 'lecture') S.total++;
    });

    document.getElementById('htitle').textContent = payload.title || '学习台';
    var stage = document.getElementById('stage');
    stage.innerHTML = '';

    var qNo = 0;
    (payload.cards || []).forEach(function (card) {
      var isQ = card.type !== 'lecture';
      if (isQ) { qNo++; card.__qno = qNo; }
      var el;
      switch (card.type) {
        case 'lecture': el = buildLecture(card); break;
        case 'choice':
        case 'judge':
        case 'multi': el = buildChoice(card); break;
        case 'blank': el = buildBlank(card); break;
        case 'text': el = buildText(card); break;
        default: el = buildLecture(card); break;
      }
      if (isQ) el.dataset.qno = String(qNo);
      stage.appendChild(el);
    });

    renderMath(stage);

    var hint = document.createElement('div');
    hint.className = 'hintbox';
    hint.textContent = '答完一题会立刻判分并给出解析。想让我讲更深、加题，直接在「答疑」里发消息或拍照。';
    stage.appendChild(hint);

    updateProgress();
    post({ type: 'ready' });

    // 恢复上次阅读位置
    if (payload.scrollY && payload.scrollY > 10) {
      var target = payload.scrollY;
      setTimeout(function () {
        try { window.scrollTo(0, target); } catch (e) {}
      }, 260);
    }
  }

  window.renderStudyHub = function (payload) {
    if (!payload) return;
    if (S.lessonId === payload.lessonId && document.getElementById('stage').children.length > 0) {
      // 同一节只更新进度，避免打断阅读位置
      var prog = payload.progress || {};
      var changed = false;
      Object.keys(prog).forEach(function (k) {
        if (!S.answered[k]) { S.answered[k] = { correct: !!prog[k], picked: [] }; changed = true; }
      });
      if (changed) updateProgress();
      return;
    }
    build(payload);
  };

  window.addEventListener('error', function () {
    // 静默：避免 flaky 报错弹窗
  });
})();
