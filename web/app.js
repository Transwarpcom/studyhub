(function () {
'use strict';

/* ============================================================
 * 0. 常量
 * ============================================================ */
var API = location.origin;
var LS = {
  token: 'sh.token', user: 'sh.user',
  progress: 'sh.progress', wrongs: 'sh.wrongs',
  manifest: 'sh.manifest', lesson: 'sh.lesson.'
};

/* ============================================================
 * 1. 状态
 * ============================================================ */
var S = {
  token: '', user: '', registerOpen: false,
  manifest: null, lessons: {},
  progress: {}, wrongs: [],
  route: { name: 'home', id: '' },
  pushTimer: null
};

/* ============================================================
 * 2. 小工具
 * ============================================================ */
function $(sel, root) { return (root || document).querySelector(sel); }
function $$(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }
function esc(s) {
  return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
    return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
  });
}
function el(html) {
  var d = document.createElement('div');
  d.innerHTML = html.trim();
  return d.firstElementChild;
}
function store(k, v) {
  try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {}
}
function read(k, d) {
  try {
    var v = JSON.parse(localStorage.getItem(k));
    return v == null ? d : v;
  } catch (e) { return d; }
}
var toastTimer;
function toast(msg) {
  var t = $('#toast');
  t.textContent = msg;
  t.classList.add('on');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(function () { t.classList.remove('on'); }, 1700);
}

/* ============================================================
 * 3. 渲染：Markdown + KaTeX
 * ============================================================ */
marked.setOptions({ gfm: true, breaks: true, headerIds: false, mangle: false });

/**
 * Markdown → HTML，数学片段先抽出来占位，跑完 marked 再填回。
 * 否则 `\{` `\}` `\_` 这类 LaTeX 转义会被 Markdown 吃掉（花括号消失）。
 */
function md(src) {
  if (!src) return '';
  var s = String(src);
  // 题库填空占位符
  s = s.replace(/\{\{\s*\d+\s*\}\}/g, '＿＿＿＿');

  var maths = [];
  // 块级 $$...$$（可跨行）
  s = s.replace(/\$\$([\s\S]+?)\$\$/g, function (_, tex) {
    maths.push({ tex: tex, display: true });
    return '\u0000M' + (maths.length - 1) + '\u0000';
  });
  // 同时支持 \[...\]
  s = s.replace(/\\\[([\s\S]+?)\\\]/g, function (_, tex) {
    maths.push({ tex: tex, display: true });
    return '\u0000M' + (maths.length - 1) + '\u0000';
  });
  // 行内 $...$（不跨行，避开已转义的 \$）
  s = s.replace(/(^|[^\\])\$([^$\n]+?)\$/g, function (m, pre, tex) {
    maths.push({ tex: tex, display: false });
    return pre + '\u0000M' + (maths.length - 1) + '\u0000';
  });
  // 行内 \(...\)
  s = s.replace(/\\\(([\s\S]+?)\\\)/g, function (_, tex) {
    maths.push({ tex: tex, display: false });
    return '\u0000M' + (maths.length - 1) + '\u0000';
  });

  var html = marked.parse(s);

  return html.replace(/\u0000M(\d+)\u0000/g, function (_, i) {
    var m = maths[+i];
    if (!m) return '';
    return '<span class="math-src" data-tex="' + esc(m.tex) + '" data-block="' + (m.display ? '1' : '0') + '"></span>';
  });
}

/** 渲染数学占位 + 兜底处理漏网的 $...$ */
function fillMath(node) {
  // 1) 我们自己占位的
  $$('.math-src[data-tex]', node).forEach(function (n) {
    var tex = n.getAttribute('data-tex');
    try {
      katex.render(tex, n, {
        throwOnError: false,
        displayMode: n.getAttribute('data-block') === '1',
        strict: false,
        trust: false
      });
      n.removeAttribute('data-tex');
    } catch (e) {
      n.textContent = tex;
    }
  });
  // 2) 兜底：正文里如果还有没被抽到的 $...$
  if (window.renderMathInElement) {
    try {
      renderMathInElement(node, {
        delimiters: [
          { left: '$$', right: '$$', display: true },
          { left: '$', right: '$', display: false }
        ],
        throwOnError: false,
        strict: false,
        ignoredTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code', 'option']
      });
    } catch (e) {}
  }
}

/** Markdown 字符串 → 已渲染公式的 DOM 片段 */
function mdNode(src) {
  var d = document.createElement('div');
  d.className = 'md';
  d.innerHTML = md(src);
  fillMath(d);
  return d;
}

/* ============================================================
 * 4. API
 * ============================================================ */
function api(path, opt) {
  opt = opt || {};
  var headers = { 'Content-Type': 'application/json' };
  if (S.token) headers['Authorization'] = 'Bearer ' + S.token;
  var init = {
    method: opt.method || 'GET',
    headers: headers,
    body: opt.body
  };
  return fetch(API + path, init).then(function (r) {
    return r.text().then(function (txt) {
      var data = null;
      try { data = JSON.parse(txt); } catch (e) {}
      if (!r.ok) {
        var m = (data && (data.message || data.error)) || ('HTTP ' + r.status);
        throw new Error(m);
      }
      return data;
    });
  });
}

/* ============================================================
 * 5. 路由
 * ============================================================ */
function parseHash() {
  var raw = (location.hash || '#/home').replace(/^#/, '');
  var qi = raw.indexOf('?');
  var path = qi < 0 ? raw : raw.slice(0, qi);
  var qs = qi < 0 ? '' : raw.slice(qi + 1);
  var params = {};
  qs.split('&').forEach(function (kv) {
    if (!kv) return;
    var p = kv.split('=');
    params[decodeURIComponent(p[0])] = decodeURIComponent(p[1] || '');
  });
  var parts = path.split('/').filter(Boolean).map(function (x) { return decodeURIComponent(x); });
  return { name: parts[0] || 'home', id: parts[1] || '', params: params };
}

function go(path) { location.hash = '#' + path; }

function setHeader(title, showBack) {
  $('#title').textContent = title;
  var b = $('#back');
  if (showBack) b.removeAttribute('hidden'); else b.setAttribute('hidden', '');
  $('#authBtn').textContent = S.user || '登录';
}

function markTab(name) {
  $$('#tab a').forEach(function (a) {
    a.classList.toggle('on', a.dataset.tab === name);
  });
}

/* ============================================================
 * 6. 数据加载
 * ============================================================ */
function loadManifest() {
  var cached = read(LS.manifest, null);
  if (cached) S.manifest = cached;
  return fetch(API + '/manifest')
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(function (m) { if (m) { S.manifest = m; store(LS.manifest, m); } })
    .catch(function () {});
}

function allLessons() {
  var out = [];
  (function walk(list) {
    (list || []).forEach(function (n) {
      if ((n.kind || '') === 'lesson') out.push(n);
      if (n.children) walk(n.children);
    });
  })(S.manifest && S.manifest.tree);
  return out;
}

function findNode(id) {
  var hit = null;
  (function walk(list, trail) {
    (list || []).forEach(function (n) {
      if (hit) return;
      if (n.id === id) { hit = { node: n, trail: trail }; return; }
      if (n.children) walk(n.children, trail.concat([n]));
    });
  })(S.manifest && S.manifest.tree, []);
  return hit;
}

function loadLesson(id) {
  if (S.lessons[id]) return Promise.resolve(S.lessons[id]);
  var cached = read(LS.lesson + id, null);
  if (cached) S.lessons[id] = cached;
  return api('/lesson?id=' + encodeURIComponent(id))
    .then(function (d) {
      S.lessons[id] = d;
      store(LS.lesson + id, d);
      return d;
    })
    .catch(function () { return S.lessons[id] || null; });
}

/* ============================================================
 * 7. 页面：今日
 * ============================================================ */
function pageHome(app) {
  setHeader('今日', false);
  markTab('home');
  var total = allLessons().length;
  var done = Object.keys(S.progress).filter(function (k) { return S.progress[k] === true; }).length;
  var wrongN = S.wrongs.length;

  app.innerHTML =
    '<div class="card">' +
      '<div class="muted">' + (S.user ? '👤 ' + esc(S.user) + ' · 进度已同步' : '未登录 · 进度只存本机') + '</div>' +
      '<div class="stats">' +
        '<div><b>' + done + '</b><span>答对</span></div>' +
        '<div><b>' + wrongN + '</b><span>错题</span></div>' +
        '<div><b>' + total + '</b><span>总节数</span></div>' +
      '</div>' +
    '</div>' +
    '<div class="card tight">' +
      '<button class="row" data-go="/lib">' +
        '<div class="t"><b>全部课程</b><small>高等数学 A1 · 大学英语</small></div>' +
        '<span class="tag">' + total + ' 节</span>' +
      '</button>' +
      '<button class="row" data-go="/wrong">' +
        '<div class="t"><b>错题本</b><small>答错自动收录，重做答对移除</small></div>' +
        '<span class="tag">' + wrongN + '</span>' +
      '</button>' +
      '<button class="row" data-go="/me">' +
        '<div class="t"><b>账号</b><small>' + (S.user ? '已登录 ' + esc(S.user) : '登录后跨设备同步进度') + '</small></div>' +
        '<span class="tag">' + (S.user ? '已登录' : '未登录') + '</span>' +
      '</button>' +
    '</div>';

  $$('[data-go]', app).forEach(function (b) {
    b.onclick = function () { go(b.dataset.go); };
  });
}

/* ============================================================
 * 8. 页面：课程树
 * ============================================================ */
function pageLib(app, id) {
  markTab('lib');
  var found = id ? findNode(id) : null;
  var nodes = found ? (found.node.children || []) : ((S.manifest && S.manifest.tree) || []);

  var crumb = '';
  if (found) {
    var chain = found.trail.concat([found.node]);
    crumb = '<div class="crumb"><a href="#/lib">课程</a>' +
      chain.map(function (n, i) {
        var last = i === chain.length - 1;
        return ' › ' + (last ? '<b>' + esc(n.title) + '</b>'
          : '<a href="#/lib/' + encodeURIComponent(n.id) + '">' + esc(n.title) + '</a>');
      }).join('') + '</div>';
  }

  setHeader(found ? found.node.title : '课程', !!id);

  if (!nodes.length) {
    app.innerHTML = crumb + '<div class="card"><div class="muted">这一层还没有内容</div></div>';
    return;
  }

  var html = crumb + '<div class="card tight">';
  nodes.forEach(function (n) {
    var isLesson = (n.kind || '') === 'lesson';
    var kids = (n.children || []).length;
    var pct = isLesson ? lessonPct(n.id) : 0;
    html += '<button class="row" data-id="' + esc(n.id) + '" data-lesson="' + (isLesson ? '1' : '0') + '">' +
      '<div class="t"><b>' + esc(n.title) + '</b>' +
      (n.summary ? '<small>' + esc(n.summary) + '</small>' : '') + '</div>' +
      (pct > 0 ? '<span class="pill ok">' + pct + '%</span>' : '') +
      (n.badge ? '<span class="tag">' + esc(n.badge) + '</span>'
               : (kids ? '<span class="tag">' + kids + ' 节</span>' : '')) +
    '</button>';
  });
  html += '</div>';
  app.innerHTML = html;

  $$('[data-id]', app).forEach(function (b) {
    b.onclick = function () {
      var id2 = b.dataset.id;
      go(b.dataset.lesson === '1' ? '/lesson/' + encodeURIComponent(id2)
                                  : '/lib/' + encodeURIComponent(id2));
    };
  });
}

function lessonPct(lid) {
  var l = S.lessons[lid];
  if (!l || !l.cards) return 0;
  var qs = l.cards.filter(function (c) { return c.type !== 'lecture'; });
  if (!qs.length) return 0;
  var done = qs.filter(function (c) { return S.progress[lid + '|' + c.id] !== undefined; }).length;
  return Math.round(done / qs.length * 100);
}

/* ============================================================
 * 9. 页面：单节课
 * ============================================================ */
function pageLesson(app, id) {
  var found = findNode(id);
  setHeader(found ? found.node.title : '', true);
  app.innerHTML = '<div class="card"><div class="skel"></div><div class="skel"></div><div class="skel"></div></div>';

  loadLesson(id).then(function (l) {
    if (!l) {
      app.innerHTML = '<div class="card"><div class="muted">加载失败，检查网络后重试</div></div>';
      return;
    }
    renderLesson(app, id, l);
  });
}

function renderLesson(app, lid, lesson) {
  var cards = lesson.cards || [];
  app.innerHTML = '';

  if (lesson.subtitle) {
    var sub = el('<div class="muted" style="margin:0 2px 11px"></div>');
    sub.textContent = lesson.subtitle;
    app.appendChild(sub);
  }

  cards.forEach(function (card, idx) {
    app.appendChild(buildCard(lid, card, idx, cards.length));
  });

  if (!cards.length) {
    app.innerHTML = '<div class="card"><div class="muted">这一节还没有内容</div></div>';
  }
}

/** 单张卡片 */
function buildCard(lid, card, idx, total) {
  // 讲义
  if (card.type === 'lecture') {
    var lec = el('<div class="card"></div>');
    lec.appendChild(mdNode(card.md || ''));
    return lec;
  }

  var wrap = el('<div class="card"></div>');
  wrap.dataset.card = card.id;

  // 头部：第 N 张 + 状态
  var key = lid + '|' + card.id;
  var st = S.progress[key];
  var head = el(
    '<div class="qhead">' +
      '<span class="tag">第 ' + (idx + 1) + ' 张</span>' +
      (st === true ? '<span class="pill ok">已答对</span>'
        : st === false ? '<span class="pill bad">答错过</span>' : '') +
    '</div>'
  );
  wrap.appendChild(head);

  // 题干
  var body = el('<div class="qbody"></div>');
  body.appendChild(mdNode(card.question || card.q || ''));
  wrap.appendChild(body);

  // 作答区
  var area = el('<div class="answers"></div>');
  wrap.appendChild(area);

  // 解析区
  var exp = el('<div class="exp" style="display:none"></div>');
  wrap.appendChild(exp);

  renderAnswers(area, exp, lid, card, wrap);

  return wrap;
}

/* ============================================================
 * 10. 题型
 * ============================================================ */
function answerIndexes(card) {
  var a = card.answer;
  if (a == null) return [];
  if (Array.isArray(a)) return a.map(String);
  return [String(a)];
}

function renderAnswers(area, exp, lid, card, wrap) {
  var key = lid + '|' + card.id;
  var settled = S.progress[key] !== undefined;
  var type = card.type || '';

  if ((type === 'choice' || type === 'judge') && Array.isArray(card.options)) {
    renderSingle(area, exp, lid, card, wrap, settled);
  } else if (type === 'multi' && Array.isArray(card.options)) {
    renderMulti(area, exp, lid, card, wrap, settled);
  } else if (type === 'blank') {
    renderBlank(area, exp, lid, card, wrap, settled);
  } else if (type === 'text') {
    renderText(area, exp, lid, card, wrap, settled);
  } else if (Array.isArray(card.options)) {
    // 兜底：有选项就按单选
    renderSingle(area, exp, lid, card, wrap, settled);
  } else {
    var d = el('<div class="muted">（未支持的题型：' + esc(type || '空') + '）</div>');
    area.appendChild(d);
  }
}

/* ---- 单选 / 判断 ---- */
function renderSingle(area, exp, lid, card, wrap, settled) {
  var correct = answerIndexes(card);
  var picked = card._picked;

  card.options.forEach(function (opt, i) {
    var b = el('<button class="opt" type="button"></button>');
    b.dataset.i = String(i);
    b.appendChild(mdNode(opt));
    b.onclick = function () {
      if (b.disabled) return;
      var ok = correct.indexOf(String(i)) >= 0;
      card._picked = i;
      $$('.opt', area).forEach(function (x) {
        x.disabled = true;
        var xi = x.dataset.i;
        if (correct.indexOf(xi) >= 0) x.classList.add('ok');
        else if (xi === String(i)) x.classList.add('bad');
      });
      settle(exp, lid, card, wrap, ok);
    };
    if (settled) {
      b.disabled = true;
      if (correct.indexOf(String(i)) >= 0) b.classList.add('ok');
      else if (i === picked) b.classList.add('bad');
    }
    area.appendChild(b);
  });

  if (settled) showExplain(exp, card);
}

/* ---- 多选 ---- */
function renderMulti(area, exp, lid, card, wrap, settled) {
  var correct = answerIndexes(card);
  var picked = {};

  card.options.forEach(function (opt, i) {
    var b = el('<button class="opt" type="button"></button>');
    b.dataset.i = String(i);
    b.appendChild(mdNode(opt));
    b.onclick = function () {
      if (b.disabled) return;
      var k = String(i);
      if (picked[k]) { delete picked[k]; b.classList.remove('sel'); }
      else { picked[k] = 1; b.classList.add('sel'); }
    };
    if (settled) b.disabled = true;
    area.appendChild(b);
  });

  var submit = el('<button class="btn sm" type="button" style="margin-top:9px">提交答案</button>');
  submit.onclick = function () {
    var got = Object.keys(picked).sort().join(',');
    var want = correct.slice().sort().join(',');
    var ok = got === want;
    $$('.opt', area).forEach(function (x) {
      x.disabled = true;
      var xi = x.dataset.i;
      if (correct.indexOf(xi) >= 0) x.classList.add('ok');
      else if (picked[xi]) x.classList.add('bad');
    });
    submit.disabled = true;
    settle(exp, lid, card, wrap, ok);
  };
  if (settled) submit.disabled = true;
  area.appendChild(submit);

  if (settled) showExplain(exp, card);
}

/* ---- 填空 ---- */
function renderBlank(area, exp, lid, card, wrap, settled) {
  var input = el('<input class="input" type="text" placeholder="输入答案" autocomplete="off" autocapitalize="off" spellcheck="false">');
  var submit = el('<button class="btn sm" type="button">提交</button>');

  function judge() {
    if (input.disabled) return;
    var got = input.value.trim();
    var want = String(Array.isArray(card.answer) ? card.answer[0] : (card.answer || '')).trim();
    var ok = got.length > 0 && (
      got === want ||
      got.replace(/\s+/g, '').toLowerCase() === want.replace(/\s+/g, '').toLowerCase()
    );
    input.disabled = true;
    submit.disabled = true;
    input.style.borderColor = ok ? 'var(--ok)' : 'var(--bad)';
    settle(exp, lid, card, wrap, ok);
  }

  submit.onclick = judge;
  input.onkeydown = function (e) { if (e.key === 'Enter') judge(); };

  if (settled) { input.disabled = true; submit.disabled = true; }
  area.appendChild(input);
  area.appendChild(submit);

  if (settled) showExplain(exp, card);
}

/* ---- 开放题 ---- */
function renderText(area, exp, lid, card, wrap, settled) {
  var ta = el('<textarea class="input" placeholder="写下你的思路（可选）"></textarea>');
  var look = el('<button class="btn ghost sm" type="button">看解析</button>');
  var judgeRow = el(
    '<div style="display:none;gap:9px;margin-top:9px">' +
      '<button class="btn sm" style="flex:1" data-ok="1">会了</button>' +
      '<button class="btn ghost sm" style="flex:1" data-ok="0">还不会</button>' +
    '</div>'
  );

  look.onclick = function () {
    showExplain(exp, card);
    look.style.display = 'none';
    judgeRow.style.display = 'flex';
  };
  $$('[data-ok]', judgeRow).forEach(function (b) {
    b.onclick = function () {
      judgeRow.style.display = 'none';
      settle(exp, lid, card, wrap, b.dataset.ok === '1');
    };
  });

  if (settled) { ta.disabled = true; look.style.display = 'none'; }
  area.appendChild(ta);
  area.appendChild(look);
  area.appendChild(judgeRow);

  if (settled) showExplain(exp, card);
}

/* ---- 结算 ---- */
function showExplain(exp, card) {
  var text = card.explain || card.exp;
  if (!text) return;
  exp.style.display = 'block';
  exp.innerHTML = '';
  var lab = el('<div class="lab">解析</div>');
  exp.appendChild(lab);
  exp.appendChild(mdNode(text));
}

function settle(exp, lid, card, wrap, ok) {
  var key = lid + '|' + card.id;
  S.progress[key] = ok;

  var wi = -1;
  S.wrongs.forEach(function (w, i) { if (w.id === key) wi = i; });
  if (ok) {
    if (wi >= 0) S.wrongs.splice(wi, 1);
  } else if (wi < 0) {
    var found = findNode(lid);
    var preview = String(card.question || card.q || '')
      .replace(/[$*#`>|{}]/g, '').replace(/\s+/g, ' ').trim().slice(0, 46);
    S.wrongs.unshift({
      id: key, lessonId: lid,
      lessonTitle: found ? found.node.title : lid,
      cardId: card.id, preview: preview, ts: Date.now()
    });
  }

  store(LS.progress, S.progress);
  store(LS.wrongs, S.wrongs);

  // 头部状态
  var head = $('.qhead', wrap);
  if (head) {
    $$('.pill', head).forEach(function (p) { p.remove(); });
    var pill = el('<span class="pill ' + (ok ? 'ok' : 'bad') + '">' + (ok ? '已答对' : '答错过') + '</span>');
    head.appendChild(pill);
  }

  showExplain(exp, card);
  toast(ok ? '✓ 答对了' : '✗ 答错了，已进错题本');
  if (S.token) queuePush();
}

/* ============================================================
 * 11. 页面：错题本
 * ============================================================ */
function pageWrong(app) {
  setHeader('错题本', false);
  markTab('wrong');

  if (!S.wrongs.length) {
    app.innerHTML = '<div class="card"><div class="muted">还没有错题。答错的选择、填空会自动进这里，重做答对就移除。</div></div>';
    return;
  }

  var html = '<div class="card tight">';
  S.wrongs.forEach(function (w, i) {
    html += '<button class="row" data-i="' + i + '">' +
      '<div class="t"><b>' + esc(w.preview || w.cardId) + '</b>' +
      '<small>' + esc(w.lessonTitle || '') + '</small></div>' +
      '<span class="tag">重做</span>' +
    '</button>';
  });
  html += '</div>';
  app.innerHTML = html;

  $$('[data-i]', app).forEach(function (b) {
    b.onclick = function () {
      var w = S.wrongs[+b.dataset.i];
      if (!w) return;
      go('/lesson/' + encodeURIComponent(w.lessonId));
      setTimeout(function () { scrollToCard(w.cardId); }, 900);
    };
  });
}

function scrollToCard(cardId) {
  var n = document.querySelector('[data-card="' + cardId + '"]');
  if (n) n.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

/* ============================================================
 * 12. 页面：我的
 * ============================================================ */
function pageMe(app) {
  setHeader('我的', false);
  markTab('me');

  if (S.user) {
    app.innerHTML =
      '<div class="card">' +
        '<div style="font-size:15.5px;font-weight:600">👤 ' + esc(S.user) + '</div>' +
        '<div class="muted" style="margin-top:5px">进度、错题绑定此账号，换设备登录自动同步</div>' +
        '<div class="muted" style="margin-top:2px;word-break:break-all">服务器 ' + esc(location.host) + '</div>' +
      '</div>' +
      '<div class="card">' +
        '<button class="btn" id="syncBtn">立即同步</button>' +
        '<div style="height:9px"></div>' +
        '<button class="btn ghost" id="outBtn">退出登录</button>' +
      '</div>' +
      '<div class="card"><div class="muted">课程与题目对所有人开放，不登录也能看。登录只用于同步你自己的答题进度和错题，账号之间互相看不到。</div></div>';

    $('#syncBtn').onclick = function () {
      var b = $('#syncBtn');
      b.disabled = true; b.textContent = '同步中…';
      pushProgress()
        .then(function () { toast('已同步'); })
        .catch(function (e) { toast('同步失败：' + e.message); })
        .then(function () { b.disabled = false; b.textContent = '立即同步'; });
    };
    $('#outBtn').onclick = function () {
      api('/auth/logout', { method: 'POST', body: '{}' }).catch(function () {});
      S.token = ''; S.user = '';
      localStorage.removeItem(LS.token);
      localStorage.removeItem(LS.user);
      toast('已退出');
      go('/home');
    };
    return;
  }

  app.innerHTML =
    '<div class="card">' +
      '<div style="font-weight:600;margin-bottom:12px">登录</div>' +
      '<div class="field"><label>用户名</label>' +
        '<input class="input" id="u" type="text" autocomplete="username" autocapitalize="off" spellcheck="false"></div>' +
      '<div class="field"><label>密码</label>' +
        '<input class="input" id="p" type="password" autocomplete="current-password"></div>' +
      '<div class="msg" id="msg"></div>' +
      '<button class="btn" id="loginBtn">登录</button>' +
      '<div style="height:9px"></div>' +
      '<button class="btn ghost" id="regBtn"' + (S.registerOpen ? '' : ' disabled') + '>' +
        (S.registerOpen ? '注册新账号' : '注册暂未开放') + '</button>' +
    '</div>' +
    '<div class="card"><div class="muted">课程和题目不用登录也能看。登录后进度、错题才会存进账号，换设备自动同步。</div></div>';

  $('#loginBtn').onclick = doLogin;
  $('#p').onkeydown = function (e) { if (e.key === 'Enter') doLogin(); };
  $('#regBtn').onclick = doRegister;
}

function setMsg(text, isErr) {
  var m = $('#msg');
  if (!m) return;
  m.textContent = text || '';
  m.className = 'msg' + (text ? (isErr ? ' err' : ' ok') : '');
}

function doLogin() {
  var u = ($('#u').value || '').trim();
  var p = $('#p').value || '';
  setMsg('');
  if (!u || !p) { setMsg('用户名和密码都要填', true); return; }

  var b = $('#loginBtn');
  b.disabled = true; b.textContent = '登录中…';
  api('/auth/login', { method: 'POST', body: JSON.stringify({ username: u, password: p }) })
    .then(function (d) {
      S.token = d.token; S.user = d.username;
      localStorage.setItem(LS.token, d.token);
      localStorage.setItem(LS.user, d.username);
      return pullProgress();
    })
    .then(function () {
      toast('登录成功');
      go('/home');
    })
    .catch(function (e) {
      setMsg(e.message, true);
      b.disabled = false; b.textContent = '登录';
    });
}

function doRegister() {
  var u = ($('#u').value || '').trim();
  var p = $('#p').value || '';
  setMsg('');
  if (p.length < 6) { setMsg('密码至少 6 位', true); return; }

  api('/auth/register', { method: 'POST', body: JSON.stringify({ username: u, password: p }) })
    .then(function (d) {
      S.token = d.token; S.user = d.username;
      localStorage.setItem(LS.token, d.token);
      localStorage.setItem(LS.user, d.username);
      toast('注册成功');
      go('/home');
    })
    .catch(function (e) { setMsg(e.message, true); });
}

/* ============================================================
 * 13. 同步
 * ============================================================ */
function queuePush() {
  clearTimeout(S.pushTimer);
  S.pushTimer = setTimeout(function () { pushProgress().catch(function () {}); }, 2200);
}

function pushProgress() {
  if (!S.token) return Promise.resolve();
  return api('/progress', {
    method: 'POST',
    body: JSON.stringify({
      progress: S.progress,
      wrongs: S.wrongs.map(function (w) {
        return {
          id: w.id, lessonId: w.lessonId, lessonTitle: w.lessonTitle,
          cardId: w.cardId, preview: w.preview
        };
      }),
      notes: {}
    })
  });
}

var lastPullAt = 0;

function pullProgress(force) {
  if (!S.token) return Promise.resolve();
  var now = Date.now();
  if (!force && now - lastPullAt < 30000) return Promise.resolve();
  lastPullAt = now;
  return api('/progress')
    .then(function (d) {
      var p = (d && d.data) || {};
      if (p.progress) {
        Object.keys(p.progress).forEach(function (k) {
          var remote = p.progress[k];
          var local = S.progress[k];
          // 任一端答对就算对；本地没有才用云端的 false
          if (remote === true || local === undefined) S.progress[k] = remote;
        });
      }
      if (Array.isArray(p.wrongs)) {
        var have = {};
        S.wrongs.forEach(function (w) { have[w.id] = 1; });
        p.wrongs.forEach(function (w) { if (!have[w.id]) S.wrongs.push(w); });
      }
      store(LS.progress, S.progress);
      store(LS.wrongs, S.wrongs);
    })
    .catch(function () {});
}

function restoreAuth() {
  S.token = localStorage.getItem(LS.token) || '';
  S.user = localStorage.getItem(LS.user) || '';
  S.progress = read(LS.progress, {});
  S.wrongs = read(LS.wrongs, []);

  return fetch(API + '/auth/config')
    .then(function (r) { return r.json(); })
    .then(function (d) { S.registerOpen = !!d.registerOpen; })
    .catch(function () {})
    .then(function () {
      if (!S.token) return;
      return api('/auth/me')
        .then(function (d) {
          S.user = d.username;
          localStorage.setItem(LS.user, d.username);
          return pullProgress();
        })
        .catch(function () {
          S.token = ''; S.user = '';
          localStorage.removeItem(LS.token);
          localStorage.removeItem(LS.user);
        });
    });
}

/* ============================================================
 * 14. 启动
 * ============================================================ */
function render() {
  var r = parseHash();
  S.route = r;
  var app = $('#app');
  app.innerHTML = '';

  switch (r.name) {
    case 'home':   pageHome(app); break;
    case 'lib':    pageLib(app, r.id); break;
    case 'lesson': pageLesson(app, r.id); break;
    case 'wrong':  pageWrong(app); break;
    case 'me':     pageMe(app); break;
    default:       go('/home');
  }
  window.scrollTo(0, 0);
}

// ---------- 自动同步 ----------
// 页面重新可见时拉一次（别的设备刚改过）
document.addEventListener('visibilitychange', function () {
  if (document.visibilityState === 'visible' && S.token) {
    pullProgress(true).then(function () {
      // 如果正停在课程页，重绘一次让状态更新
      if (S.route && S.route.name === 'lesson') render();
    });
  }
});

// 每分钟静默拉一次
setInterval(function () {
  if (S.token && document.visibilityState === 'visible') {
    pullProgress(true).then(function () {
      if (S.route && S.route.name === 'lesson') render();
    });
  }
}, 60000);

$('#back').onclick = function () {
  if (history.length > 1) history.back();
  else go('/lib');
};
$('#authBtn').onclick = function () { go('/me'); };
window.addEventListener('hashchange', render);

loadManifest()
  .then(restoreAuth)
  .then(render)
  .catch(render);


// 调试出口
window.__md = md;
window.__fill = fillMath;
window.__S = S;

})();
