(function () {
'use strict';

/* ============================================================
   常量与状态
   ============================================================ */
var API = location.origin;
var K = {
  token: 'sh.token', user: 'sh.user',
  progress: 'sh.progress', wrongs: 'sh.wrongs',
  manifest: 'sh.manifest', lesson: 'sh.lesson.', openGroups: 'sh.openGroups'
};

var S = {
  token: '', user: '', registerOpen: false,
  manifest: null, lessons: {},
  progress: {}, wrongs: {},
  openGroups: {},
  route: { name: 'home', id: '' },
  pushTimer: null, pollCtl: null, lastUpdated: 0, lastPullAt: 0
};

/* ============================================================
   工具
   ============================================================ */
function $(s, r) { return (r || document).querySelector(s); }
function $$(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }
function esc(s) {
  return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
    return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
  });
}
function el(h) { var d = document.createElement('div'); d.innerHTML = h.trim(); return d.firstElementChild; }
function save(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
function load(k, d) {
  try { var v = JSON.parse(localStorage.getItem(k)); return v == null ? d : v; }
  catch (e) { return d; }
}
var toastTimer;
function toast(msg, kind) {
  var t = $('#toast');
  $('.ti', t).textContent = kind === 'bad' ? '✕' : '✓';
  $('.tm', t).textContent = msg;
  t.classList.add('on');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(function () { t.classList.remove('on'); }, 1800);
}

var ICON = {
  chev: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M9 6l6 6-6 6"/></svg>',
  chevR: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18l6-6-6-6"/></svg>'
};

/* ============================================================
   Markdown + KaTeX
   ============================================================ */
marked.setOptions({ gfm: true, breaks: true, headerIds: false, mangle: false });

function md(src) {
  if (!src) return '';
  var s = String(src).replace(/\{\{\s*\d+\s*\}\}/g, '＿＿＿＿');
  var maths = [];

  function stash(tex, display) {
    maths.push({ tex: tex, display: display });
    return '\u0000M' + (maths.length - 1) + '\u0000';
  }

  s = s.replace(/\$\$([\s\S]+?)\$\$/g, function (_, t) { return stash(t, true); });
  s = s.replace(/\\\[([\s\S]+?)\\\]/g, function (_, t) { return stash(t, true); });
  s = s.replace(/(^|[^\\])\$([^$\n]+?)\$/g, function (m, pre, t) { return pre + stash(t, false); });
  s = s.replace(/\\\(([\s\S]+?)\\\)/g, function (_, t) { return stash(t, false); });

  var html = marked.parse(s);
  return html.replace(/\u0000M(\d+)\u0000/g, function (_, i) {
    var m = maths[+i];
    if (!m) return '';
    return '<span class="mth" data-tex="' + esc(m.tex) + '" data-block="' + (m.display ? '1' : '0') + '"></span>';
  });
}

function typeset(node) {
  $$('.mth[data-tex]', node).forEach(function (n) {
    var tex = n.getAttribute('data-tex');
    try {
      katex.render(tex, n, {
        throwOnError: false,
        displayMode: n.getAttribute('data-block') === '1',
        strict: false, trust: false
      });
      n.removeAttribute('data-tex');
    } catch (e) { n.textContent = tex; }
  });
  if (typeof renderMathInElement === 'function') {
    try {
      renderMathInElement(node, {
        delimiters: [{ left: '$$', right: '$$', display: true }, { left: '$', right: '$', display: false }],
        throwOnError: false, strict: false,
        ignoredTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code', 'option']
      });
    } catch (e) {}
  }
}

function mdEl(src, cls) {
  var d = document.createElement('div');
  if (cls) d.className = cls;
  d.innerHTML = md(src);
  typeset(d);
  return d;
}

/** 把 svg 图标串放进节点前 */
function withIcon(node, icon, cls) {
  var w = document.createElement('span');
  w.className = cls || '';
  w.innerHTML = icon;
  return w;
}

/* ============================================================
   API
   ============================================================ */
function api(path, opt) {
  opt = opt || {};
  var h = { 'Content-Type': 'application/json' };
  if (S.token) h['Authorization'] = 'Bearer ' + S.token;
  return fetch(API + path, { method: opt.method || 'GET', headers: h, body: opt.body })
    .then(function (r) {
      return r.text().then(function (txt) {
        var d = null;
        try { d = JSON.parse(txt); } catch (e) {}
        if (!r.ok) throw new Error((d && (d.message || d.error)) || ('HTTP ' + r.status));
        return d;
      });
    });
}

/* ============================================================
   数据
   ============================================================ */
function loadManifest() {
  var c = load(K.manifest, null);
  if (c) S.manifest = c;
  return fetch(API + '/manifest')
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(function (m) { if (m) { S.manifest = m; save(K.manifest, m); } })
    .catch(function () {});
}

function tree() { return (S.manifest && S.manifest.tree) || []; }

function walk(nodes, fn, parents) {
  parents = parents || [];
  (nodes || []).forEach(function (n) {
    fn(n, parents);
    if (n.children) walk(n.children, fn, parents.concat([n]));
  });
}

function findNode(id) {
  var hit = null;
  walk(tree(), function (n, parents) {
    if (n.id === id) hit = { node: n, parents: parents };
  });
  return hit;
}

function leaves() {
  var out = [];
  walk(tree(), function (n) { if ((n.kind || '') === 'lesson') out.push(n); });
  return out;
}

function loadLesson(id) {
  if (S.lessons[id]) return Promise.resolve(S.lessons[id]);
  var c = load(K.lesson + id, null);
  if (c) S.lessons[id] = c;
  return api('/lesson?id=' + encodeURIComponent(id))
    .then(function (d) { S.lessons[id] = d; save(K.lesson + id, d); return d; })
    .catch(function () { return S.lessons[id] || null; });
}

/* ============================================================
   路由
   ============================================================ */
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
  var seg = path.split('/').filter(Boolean).map(decodeURIComponent);
  return { name: seg[0] || 'home', id: seg[1] || '', params: params };
}

function go(p) { location.hash = '#' + p; }

/* ============================================================
   侧栏：课程树
   ============================================================ */
function renderTree() {
  var box = $('#tree');
  var cur = S.route.name === 'lesson' ? S.route.id : '';
  box.innerHTML = '';

  var filtered = null;
  var q = ($('#search').value || '').trim().toLowerCase();
  if (q) {
    filtered = leaves().filter(function (n) {
      return (n.title || '').toLowerCase().indexOf(q) >= 0 ||
             (n.summary || '').toLowerCase().indexOf(q) >= 0;
    });
  }

  if (filtered) {
    if (!filtered.length) {
      box.appendChild(el('<div class="empty" style="padding:32px 12px"><p>没有匹配的章节</p></div>'));
      return;
    }
    var wrap = el('<div class="tree"></div>');
    filtered.forEach(function (n) {
      wrap.appendChild(leafNode(n, cur, true));
    });
    box.appendChild(wrap);
    return;
  }

  // 展开到当前节所在的路径
  if (cur) {
    var f = findNode(cur);
    if (f) {
      f.parents.forEach(function (p) { S.openGroups[p.id] = true; });
      save(K.openGroups, S.openGroups);
    }
  }

  var root = el('<div class="tree"></div>');
  tree().forEach(function (n) { root.appendChild(nodeEl(n, cur, 0)); });
  box.appendChild(root);

  // 滚动到当前节
  var act = $('.tree-leaf.active', box);
  if (act) {
    var sb = $('.sb-scroll');
    var top = act.offsetTop - sb.clientHeight / 2;
    if (top > 0) sb.scrollTop = top;
  }
}

function nodeEl(n, cur, depth) {
  if ((n.kind || '') === 'lesson') return leafNode(n, cur, false);

  var open = S.openGroups[n.id];
  if (open === undefined) open = depth < 1;   // 默认展开第一层

  var g = el('<div class="tree-group"></div>');
  var btn = el('<button class="tree-node group" data-open="' + (open ? '1' : '0') + '">' +
    '<span class="tw">' + ICON.chev + '</span>' +
    '<span class="lbl">' + esc(n.title) + '</span>' +
  '</button>');

  var kids = el('<div class="tree-children"' + (open ? '' : ' hidden') + '></div>');
  (n.children || []).forEach(function (c) { kids.appendChild(nodeEl(c, cur, depth + 1)); });

  btn.onclick = function () {
    var now = kids.hasAttribute('hidden');
    if (now) kids.removeAttribute('hidden'); else kids.setAttribute('hidden', '');
    btn.dataset.open = now ? '1' : '0';
    S.openGroups[n.id] = now;
    save(K.openGroups, S.openGroups);
  };

  g.appendChild(btn);
  g.appendChild(kids);
  return g;
}

function leafNode(n, cur, flat) {
  var a = el('<a class="tree-leaf' + (n.id === cur ? ' active' : '') + '" href="#/lesson/' +
    encodeURIComponent(n.id) + '"><span class="txt">' + esc(n.title) + '</span></a>');
  var pct = lessonPct(n.id);
  var dot = el('<span class="dot' + (pct >= 100 ? ' done' : pct > 0 ? ' part' : '') + '"></span>');
  a.appendChild(dot);
  if (flat) a.title = n.summary || '';
  a.onclick = function () { closeDrawer(); };
  return a;
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
   侧栏底部：账号
   ============================================================ */
function renderFoot() {
  var f = $('#sbFoot');
  f.innerHTML = '';
  var b = el('<button class="user-chip"></button>');

  var av = el('<span class="avatar' + (S.user ? '' : ' anon') + '">' +
    (S.user ? esc(S.user.slice(0, 1)) : '?') + '</span>');
  b.appendChild(av);

  var meta = el('<span class="user-meta"><b>' + (S.user ? esc(S.user) : '未登录') + '</b>' +
    '<small>' + (S.user ? '进度已同步' : '点此登录') + '</small></span>');
  b.appendChild(meta);

  b.onclick = function () { go('/me'); closeDrawer(); };
  f.appendChild(b);
}

/* ============================================================
   顶栏 / 面包屑
   ============================================================ */
function setCrumbs(items) {
  var c = $('#crumbs');
  c.innerHTML = '';
  items.forEach(function (it, i) {
    if (i) c.appendChild(el('<span class="sep">/</span>'));
    if (it.href && i < items.length - 1) {
      var a = el('<a href="' + it.href + '">' + esc(it.text) + '</a>');
      c.appendChild(a);
    } else {
      c.appendChild(el('<span class="' + (i === items.length - 1 ? 'current' : '') + '">' + esc(it.text) + '</span>'));
    }
  });
}

function setAuthBtn() {
  var b = $('#authBtn');
  b.textContent = S.user || '登录';
  b.onclick = function () { go('/me'); };
  // 桌面端侧栏底部已有账号入口，顶栏这个只在窄屏显示
  b.style.display = window.matchMedia('(max-width: 900px)').matches ? '' : 'none';
}

function setActiveTab(name) {
  $$('#tabbar a').forEach(function (a) { a.classList.toggle('on', a.dataset.tab === name); });
}

/* ============================================================
   移动端抽屉
   ============================================================ */
function openDrawer() {
  $('#sidebar').classList.add('open');
  $('#scrim').classList.add('on');
  document.body.style.overflow = 'hidden';
}
function closeDrawer() {
  $('#sidebar').classList.remove('open');
  $('#scrim').classList.remove('on');
  document.body.style.overflow = '';
}
function isMobile() { return window.matchMedia('(max-width: 900px)').matches; }

/* ============================================================
   视图：今日
   ============================================================ */
function viewHome(v) {
  setCrumbs([{ text: '今日' }]);
  setActiveTab('home');

  var total = leaves().length;
  var done = 0, seen = 0;
  Object.keys(S.progress).forEach(function (k) {
    if (S.progress[k] === true) done++;
    if (S.progress[k] !== undefined) seen++;
  });
  var wrongN = Object.keys(S.wrongs).length;

  // 最近学的一节
  var recent = load('sh.recent', null);

  v.innerHTML = '';

  var hero = el('<div class="hero">' +
    '<h1>' + (S.user ? '继续，' + esc(S.user) : '开始学习') + '</h1>' +
    '<p>同济第八版上册 1.1–5.1 全节，配大学英语四级题型。</p>' +
    '<div style="display:flex;gap:10px;margin-top:20px">' +
      '<button class="btn" id="ctaGo">' + (recent ? '继续上次的章节' : '从第一节开始') + '</button>' +
    '</div>' +
  '</div>');
  v.appendChild(hero);

  var stats = el('<div class="stat-row">' +
    '<div class="stat"><b>' + done + '</b><span>答对题数</span></div>' +
    '<div class="stat"><b>' + wrongN + '</b><span>待攻克错题</span></div>' +
    '<div class="stat"><b>' + total + '</b><span>课程总节数</span></div>' +
  '</div>');
  v.appendChild(stats);

  if (recent) {
    var rn = findNode(recent);
    if (rn) {
      v.appendChild(el('<h2 class="section-title">继续学习<small>上次看到这里</small></h2>'));
      var lst0 = el('<div class="list"></div>');
      var row0 = el('<button class="list-row">' +
        '<div class="lr-main"><span class="lr-title">' + esc(rn.node.title) + '</span>' +
        '<span class="lr-sub">' + esc(rn.node.summary || '') + '</span></div>' +
        '<span class="chevron">' + ICON.chevR + '</span>' +
      '</button>');
      row0.onclick = function () { go('/lesson/' + encodeURIComponent(recent)); };
      lst0.appendChild(row0);
      v.appendChild(lst0);
    }
  }

  v.appendChild(el('<h2 class="section-title">全部课程<small>' + total + ' 节</small></h2>'));

  var grid = el('<div class="grid"></div>');
  tree().forEach(function (n) {
    var leavesN = 0, doneN = 0;
    walk([n], function (x) {
      if ((x.kind || '') === 'lesson') {
        leavesN++;
        if (lessonPct(x.id) >= 100) doneN++;
      }
    });
    var pct = leavesN ? Math.round(doneN / leavesN * 100) : 0;

    var t = el('<a class="tile" href="#/lib/' + encodeURIComponent(n.id) + '">' +
      '<div class="t-top">' +
        '<span class="t-icon">' + (n.icon === 'function' ? '∫' : 'A') + '</span>' +
        '<span class="t-name">' + esc(n.title) + '</span>' +
      '</div>' +
      '<div class="t-desc">' + esc(n.summary || '') + '</div>' +
      '<div class="t-bar"><i style="width:' + pct + '%"></i></div>' +
      '<div class="t-desc" style="margin-top:2px">' + doneN + ' / ' + leavesN + ' 节完成</div>' +
    '</a>');
    grid.appendChild(t);
  });
  v.appendChild(grid);

  // 最近错题（最多 4 条）
  var wrongList = Object.keys(S.wrongs).map(function (k) { return S.wrongs[k]; })
    .sort(function (a, b) { return (b.ts || 0) - (a.ts || 0); });

  if (wrongN) {
    v.appendChild(el('<h2 class="section-title">最近错题<small>' + wrongN + ' 道待攻克</small></h2>'));
    var lb = el('<div class="list"></div>');
    wrongList.slice(0, 4).forEach(function (w) {
      var lr = el('<button class="list-row">' +
        '<div class="lr-main"><span class="lr-title">' + esc(w.preview || w.cardId) + '</span>' +
        '<span class="lr-sub">' + esc(w.lessonTitle || '') + '</span></div>' +
        '<span class="chevron">' + ICON.chevR + '</span></button>');
      lr.onclick = function () {
        go('/lesson/' + encodeURIComponent(w.lessonId));
        setTimeout(function () {
          var n = document.querySelector('[data-card="' + w.cardId + '"]');
          if (n) n.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 700);
      };
      lb.appendChild(lr);
    });
    if (wrongN > 4) {
      var more = el('<button class="list-row">' +
        '<div class="lr-main"><span class="lr-title">查看全部 ' + wrongN + ' 道</span></div>' +
        '<span class="chevron">' + ICON.chevR + '</span></button>');
      more.onclick = function () { go('/wrong'); };
      lb.appendChild(more);
    }
    v.appendChild(lb);
  }

  // 快捷入口（固定 2x2）
  v.appendChild(el('<h2 class="section-title">快捷入口</h2>'));
  var quick = el('<div class="grid cols-2"></div>');
  [
    { t: '错题本', d: wrongN ? wrongN + ' 道待复习' : '还没有错题', go: '/wrong', ic: '✕' },
    { t: '我的账号', d: S.user ? '已登录 ' + S.user : '登录后同步进度', go: '/me', ic: '人' },
    { t: '高等数学', d: '同济八版上册 1.1–5.1', go: '/lib/math', ic: '∫' },
    { t: '大学英语', d: '四级题型训练', go: '/lib/english', ic: 'A' }
  ].forEach(function (q) {
    var exists = q.go.indexOf('/lib/') === 0 ? findNode(q.go.replace('/lib/', '')) : true;
    if (!exists) return;
    var t = el('<a class="tile" href="#' + q.go + '">' +
      '<div class="t-top"><span class="t-icon">' + q.ic + '</span>' +
      '<span class="t-name">' + esc(q.t) + '</span></div>' +
      '<div class="t-desc">' + esc(q.d) + '</div></a>');
    quick.appendChild(t);
  });
  v.appendChild(quick);
}

/* ============================================================
   视图：课程树页面
   ============================================================ */
function viewLib(v, id) {
  var found = id ? findNode(id) : null;

  if (!found) {
    setCrumbs([{ text: '课程' }]);
    setActiveTab('lib');
    // 展示顶层目录
    v.innerHTML = '';
    v.appendChild(el('<div class="page-head">' +
      '<div class="page-eyebrow">课程</div>' +
      '<h1 class="page-title">全部课程</h1>' +
      '<p class="page-desc">共 ' + leaves().length + ' 节，左侧目录可直接跳转。</p>' +
    '</div>'));

    var grid = el('<div class="grid" style="margin-top:24px"></div>');
    tree().forEach(function (n) {
      var cnt = 0, dn = 0;
      walk([n], function (x) {
        if ((x.kind || '') === 'lesson') { cnt++; if (lessonPct(x.id) >= 100) dn++; }
      });
      var pct = cnt ? Math.round(dn / cnt * 100) : 0;
      var t = el('<a class="tile" href="#/lib/' + encodeURIComponent(n.id) + '">' +
        '<div class="t-top"><span class="t-icon">' + (n.icon === 'function' ? '∫' : 'A') + '</span>' +
        '<span class="t-name">' + esc(n.title) + '</span></div>' +
        '<div class="t-desc">' + esc(n.summary || '') + '</div>' +
        '<div class="t-bar"><i style="width:' + pct + '%"></i></div>' +
        '<div class="t-desc" style="margin-top:2px">' + dn + ' / ' + cnt + ' 节完成</div></a>');
      grid.appendChild(t);
    });
    v.appendChild(grid);
    return;
  }

  var chain = found.parents.concat([found.node]);
  setCrumbs([{ text: '课程', href: '#/lib' }].concat(chain.map(function (n, i) {
    return i === chain.length - 1
      ? { text: n.title }
      : { text: n.title, href: '#/lib/' + encodeURIComponent(n.id) };
  })));
  setActiveTab('lib');

  v.innerHTML = '';
  v.appendChild(el('<div class="page-head">' +
    (chain.length > 1 ? '<div class="page-eyebrow">' + esc(chain[chain.length - 2].title) + '</div>' : '') +
    '<h1 class="page-title">' + esc(found.node.title) + '</h1>' +
    (found.node.summary ? '<p class="page-desc">' + esc(found.node.summary) + '</p>' : '') +
  '</div>'));

  var kids = found.node.children || [];
  if (!kids.length) {
    v.appendChild(el('<div class="empty"><p>这一层还没有内容</p></div>'));
    return;
  }

  var list = el('<div class="list"></div>');
  kids.forEach(function (n) {
    var isL = (n.kind || '') === 'lesson';
    var pct = isL ? lessonPct(n.id) : 0;
    var sub = n.summary || (n.children ? n.children.length + ' 节' : '');
    var row = el('<button class="list-row">' +
      '<div class="lr-main"><span class="lr-title">' + esc(n.title) + '</span>' +
      '<span class="lr-sub">' + esc(sub) + '</span></div>' +
      (isL && pct > 0
        ? '<span class="pill ' + (pct >= 100 ? 'ok' : 'soft') + '">' + pct + '%</span>'
        : (n.badge ? '<span class="pill soft">' + esc(n.badge) + '</span>' : '')) +
      '<span class="chevron">' + ICON.chevR + '</span>' +
    '</button>');
    row.onclick = function () {
      go(isL ? '/lesson/' + encodeURIComponent(n.id) : '/lib/' + encodeURIComponent(n.id));
    };
    list.appendChild(row);
  });
  v.appendChild(list);
}

/* ============================================================
   视图：讲义 + 题目
   ============================================================ */
function viewLesson(v, id) {
  var found = findNode(id);
  if (!found) { go('/lib'); return; }

  var chain = found.parents.concat([found.node]);
  setCrumbs([{ text: '课程', href: '#/lib' }].concat(chain.map(function (n, i) {
    return i === chain.length - 1
      ? { text: n.title }
      : { text: n.title, href: '#/lib/' + encodeURIComponent(n.id) };
  })));
  setActiveTab('lib');
  save('sh.recent', id);

  v.innerHTML = '<div class="skel skel-line w60" style="height:22px;margin-bottom:16px"></div>' +
                '<div class="skel skel-block"></div><div class="skel skel-block"></div>';

  loadLesson(id).then(function (l) {
    if (!l) {
      v.innerHTML = '';
      v.appendChild(el('<div class="empty"><h3>加载失败</h3><p>检查网络后刷新页面</p></div>'));
      return;
    }
    renderLesson(v, id, l, found.node);
  });
}

function renderLesson(v, lid, l, node) {
  v.innerHTML = '';

  var cards = l.cards || [];
  var quiz = cards.filter(function (c) { return c.type !== 'lecture'; });

  // 页头
  v.appendChild(el('<div class="page-head">' +
    '<div class="page-eyebrow">' + esc((findNode(lid) || {}).parents ? (findNode(lid).parents.map(function(p){return p.title;}).pop() || '课程') : '课程') + '</div>' +
    '<h1 class="page-title">' + esc(node.title || l.title || '') + '</h1>' +
    (l.subtitle ? '<p class="page-desc">' + esc(l.subtitle) + '</p>' : '') +
    '<div class="page-meta">' +
      '<span>' + cards.length + ' 张卡片</span>' +
      (quiz.length ? '<span>' + quiz.length + ' 道题</span>' : '') +
      '<span class="js-pct"></span>' +
    '</div>' +
  '</div>'));

  // 宽屏且本节有题：拆成「讲义」「题目」两栏
  var wide = window.matchMedia('(min-width: 1400px)').matches;
  var split = wide && quiz.length > 0;
  v.classList.toggle('split', split);

  var colLecture, colQuiz;
  if (split) {
    colLecture = el('<div class="col col-lecture"></div>');
    v.appendChild(colLecture);

    colQuiz = el('<div class="col col-quiz"></div>');
    var qDone = quiz.filter(function (c) { return S.progress[lid + '|' + c.id] !== undefined; }).length;
    var qRight = quiz.filter(function (c) { return S.progress[lid + '|' + c.id] === true; }).length;
    colQuiz.appendChild(el('<h2 class="section-title js-quizhead">练习' +
      '<small>' + qRight + '/' + quiz.length + ' 答对' +
      (qDone > qRight ? ' · ' + (qDone - qRight) + ' 错' : '') + '</small></h2>'));
    colQuiz.appendChild(el('<div class="quiz"></div>'));
    v.appendChild(colQuiz);
  } else {
    colLecture = v;
  }

  var qNo = 0;
  cards.forEach(function (c) {
    if (c.type === 'lecture') {
      var art = document.createElement('article');
      art.className = 'prose';
      art.style.marginBottom = split ? '28px' : '32px';
      art.appendChild(mdEl(c.md || ''));
      colLecture.appendChild(art);
      return;
    }

    qNo++;

    if (split) {
      $('.quiz', colQuiz).appendChild(qcard(lid, c, qNo, quiz.length));
      return;
    }

    // 单栏：题目集中到末尾
    if (!v.querySelector('.quiz')) {
      colLecture.appendChild(el('<h2 class="section-title" style="margin-top:36px">练习<small>' +
        quiz.length + ' 题</small></h2>'));
      colLecture.appendChild(el('<div class="quiz"></div>'));
    }
    v.querySelector('.quiz').appendChild(qcard(lid, c, qNo, quiz.length));
  });

  // 只有讲义没题目：显示提示
  if (!quiz.length) {
    colLecture.appendChild(el('<div class="empty" style="padding:40px 0">' +
      '<p>这一节是纯讲义，没有练习</p></div>'));
  }

  updatePct(lid, v);
  observeProgress();
  v.appendChild(lessonNav(lid));
}

/** 上一节 / 下一节 */
function lessonNav(lid) {
  var all = leaves();
  var i = -1;
  all.forEach(function (n, k) { if (n.id === lid) i = k; });
  var wrap = el('<nav class="lesson-nav"></nav>');
  if (i > 0) {
    var prev = all[i - 1];
    var a = el('<a class="nav-card" href="#/lesson/' + encodeURIComponent(prev.id) + '">' +
      '<span class="nav-dir">上一节</span>' +
      '<span class="nav-title">' + esc(prev.title) + '</span></a>');
    wrap.appendChild(a);
  } else {
    wrap.appendChild(el('<span></span>'));
  }
  if (i >= 0 && i < all.length - 1) {
    var next = all[i + 1];
    var b = el('<a class="nav-card next" href="#/lesson/' + encodeURIComponent(next.id) + '">' +
      '<span class="nav-dir">下一节</span>' +
      '<span class="nav-title">' + esc(next.title) + '</span></a>');
    wrap.appendChild(b);
  }
  return wrap;
}

var TYPE_NAME = { choice: '单选', multi: '多选', judge: '判断', blank: '填空', text: '解答' };

function qcard(lid, card, qNo, total) {
  var key = lid + '|' + card.id;
  var st = S.progress[key];

  var c = el('<section class="qcard" data-card="' + esc(card.id) + '"></section>');

  var head = el('<div class="qhead">' +
    '<span class="qnum">' + qNo + '</span>' +
    '<span class="qtype">' + (TYPE_NAME[card.type] || '题目') + '</span>' +
  '</div>');
  c.appendChild(head);

  var body = el('<div class="qbody"></div>');
  body.appendChild(mdEl(card.question || card.q || ''));
  c.appendChild(body);

  var area = el('<div class="qans"></div>');
  c.appendChild(area);

  var exp = el('<div class="exp" hidden></div>');
  c.appendChild(exp);

  renderAnswer(area, exp, head, lid, card, c, st !== undefined);
  return c;
}

function answerIdxs(card) {
  var a = card.answer;
  if (a == null) return [];
  if (Array.isArray(a)) return a.map(String);
  return [String(a)];
}

function renderAnswer(area, exp, head, lid, card, c, settled) {
  var t = card.type || '';

  if ((t === 'choice' || t === 'judge' || (t === '' && card.options)) && Array.isArray(card.options)) {
    renderChoice(area, exp, head, lid, card, c, settled, false);
  } else if (t === 'multi' && Array.isArray(card.options)) {
    renderChoice(area, exp, head, lid, card, c, settled, true);
  } else if (t === 'blank') {
    renderBlankAns(area, exp, head, lid, card, c, settled);
  } else if (t === 'text') {
    renderTextAns(area, exp, head, lid, card, c, settled);
  } else if (Array.isArray(card.options)) {
    renderChoice(area, exp, head, lid, card, c, settled, false);
  } else {
    area.appendChild(el('<div class="page-desc">（未支持的题型：' + esc(t || '空') + '）</div>'));
  }
}

var LETTER = 'ABCDEFGHIJ';

function renderChoice(area, exp, head, lid, card, c, settled, multi) {
  var correct = answerIdxs(card);
  var picked = {};

  var box = el('<div class="opts"></div>');
  card.options.forEach(function (opt, i) {
    var b = el('<button class="opt" type="button">' +
      '<span class="key">' + (LETTER[i] || i + 1) + '</span>' +
      '<span class="body"></span></button>');
    b.dataset.i = String(i);
    $('.body', b).appendChild(mdEl(opt));

    b.onclick = function () {
      if (b.disabled) return;
      if (!multi) {
        var ok = correct.indexOf(String(i)) >= 0;
        $$('.opt', box).forEach(function (x) {
          x.disabled = true;
          if (correct.indexOf(x.dataset.i) >= 0) x.classList.add('ok');
          else if (x.dataset.i === String(i)) x.classList.add('bad');
        });
        settle(exp, head, lid, card, c, ok);
        return;
      }
      // 多选：切换
      var k = String(i);
      if (picked[k]) { delete picked[k]; b.classList.remove('sel'); }
      else { picked[k] = 1; b.classList.add('sel'); }
    };

    if (settled) {
      b.disabled = true;
      if (correct.indexOf(String(i)) >= 0) b.classList.add('ok');
    }
    box.appendChild(b);
  });
  area.appendChild(box);

  if (multi && !settled) {
    var act = el('<div class="qactions"><button class="btn sm" type="button">提交答案</button></div>');
    $('button', act).onclick = function () {
      var got = Object.keys(picked).sort().join(',');
      var want = correct.slice().sort().join(',');
      $$('.opt', box).forEach(function (x) {
        x.disabled = true;
        if (correct.indexOf(x.dataset.i) >= 0) x.classList.add('ok');
        else if (picked[x.dataset.i]) x.classList.add('bad');
      });
      $('button', act).disabled = true;
      settle(exp, head, lid, card, c, got === want);
    };
    area.appendChild(act);
  }

  if (settled) showExp(exp, card);
}

/** 归一化答案：去空格、转小写、全角括号转半角 */
function normAns(v) {
  return String(v == null ? '' : v)
    .trim()
    .replace(/\s+/g, '')
    .replace(/[（）]/g, function (ch) { return ch === '（' ? '(' : ')'; })
    .replace(/[，]/g, ',')
    .toLowerCase();
}

/** 取某道填空的所有可接受答案：优先 blanks[i]，其次 answer */
function blankAccepts(card, i) {
  var bl = card.blanks;
  if (Array.isArray(bl) && Array.isArray(bl[i])) {
    return bl[i].map(String);
  }
  // 兼容：answer 是数组
  if (card.answer != null) {
    var a = card.answer;
    if (Array.isArray(a)) {
      // answer: ["a","b"] 两空 或 answer: [0] 索引式 → 作单空多答案
      return a.map(String);
    }
    return [String(a)];
  }
  return [];
}

function renderBlankAns(area, exp, head, lid, card, c, settled) {
  var nBlank = 1;
  if (Array.isArray(card.blanks) && card.blanks.length) nBlank = card.blanks.length;

  var inputs = [];
  var wrap = el('<div class="blank-list"></div>');

  for (var i = 0; i < nBlank; i++) {
    var row = el('<div class="blank-row"></div>');
    var tag = el('<span class="blank-tag">' + (nBlank > 1 ? '第 ' + (i + 1) + ' 空' : '答案') + '</span>');
    var inp = el('<input class="blank-input" type="text" placeholder="输入答案" ' +
      'autocomplete="off" autocapitalize="off" spellcheck="false" data-i="' + i + '">');
    row.appendChild(tag);
    row.appendChild(inp);
    wrap.appendChild(row);
    inputs.push(inp);
  }
  area.appendChild(wrap);

  var act = el('<div class="qactions"><button class="btn sm" type="button">提交</button>' +
    '<span class="hint"><kbd>Enter</kbd></span></div>');

  function judge() {
    if (act.dataset.done === '1') return;
    var allOk = true;
    inputs.forEach(function (inp, i) {
      var got = normAns(inp.value);
      var accepts = blankAccepts(card, i).map(normAns).filter(function (x) { return x; });
      var ok = got.length > 0 && accepts.indexOf(got) >= 0;
      if (!ok) allOk = false;
      inp.disabled = true;
      inp.classList.add(ok ? 'ok' : 'bad');
      if (!ok && accepts.length) {
        // 错了就提示正确答案
        var tip = el('<span class="blank-correct">正确：' + esc(blankAccepts(card, i)[0]) + '</span>');
        inp.parentNode.appendChild(tip);
      }
    });
    act.dataset.done = '1';
    $('button', act).disabled = true;
    settle(exp, head, lid, card, c, allOk);
  }

  $('button', act).onclick = judge;
  inputs.forEach(function (inp) {
    inp.onkeydown = function (e) { if (e.key === 'Enter') judge(); };
  });

  if (settled) {
    inputs.forEach(function (inp) { inp.disabled = true; });
    $('button', act).disabled = true;
    act.dataset.done = '1';
  }
  area.appendChild(act);
  if (settled) showExp(exp, card);
}

function renderTextAns(area, exp, head, lid, card, c, settled) {
  var ta = el('<textarea class="input" placeholder="写下你的思路（可选）" rows="3"></textarea>');
  var act = el('<div class="qactions">' +
    '<button class="btn ghost sm" type="button" data-act="show">看解析</button>' +
    '<span style="flex:1"></span>' +
    '<button class="btn sm" type="button" data-ok="1" hidden>会了</button>' +
    '<button class="btn ghost sm" type="button" data-ok="0" hidden>还不会</button>' +
  '</div>');

  $('[data-act="show"]', act).onclick = function () {
    showExp(exp, card);
    this.hidden = true;
    $$('[data-ok]', act).forEach(function (b) { b.hidden = false; });
  };
  $$('[data-ok]', act).forEach(function (b) {
    b.onclick = function () {
      $$('[data-ok]', act).forEach(function (x) { x.hidden = true; });
      settle(exp, head, lid, card, c, b.dataset.ok === '1');
    };
  });

  if (settled) {
    ta.disabled = true;
    $$('button', act).forEach(function (b) { b.disabled = true; b.hidden = true; });
  }
  area.appendChild(ta);
  area.appendChild(act);
  if (settled) showExp(exp, card);
}

function showExp(exp, card) {
  var text = card.explain || card.exp;
  if (!text) return;
  exp.hidden = false;
  exp.innerHTML = '';
  exp.appendChild(el('<div class="exp-label">解析</div>'));
  exp.appendChild(mdEl(text));
}

function settle(exp, head, lid, card, c, ok) {
  var key = lid + '|' + card.id;
  S.progress[key] = ok;

  if (ok) {
    delete S.wrongs[key];
  } else if (!S.wrongs[key]) {
    var f = findNode(lid);
    var prev = String(card.question || card.q || '')
      .replace(/[$*#`>|{}]/g, '').replace(/\s+/g, ' ').trim().slice(0, 50);
    S.wrongs[key] = {
      id: key, lessonId: lid,
      lessonTitle: f ? f.node.title : lid,
      cardId: card.id, preview: prev, ts: Date.now()
    };
  }
  save(K.progress, S.progress);
  save(K.wrongs, S.wrongs);

  $$('.pill', head).forEach(function (p) { p.remove(); });
  head.appendChild(el('<span class="pill ' + (ok ? 'ok' : 'bad') + '">' +
    (ok ? '✓ 答对' : '✕ 答错') + '</span>'));

  showExp(exp, card);
  toast(ok ? '答对了' : '已记入错题本', ok ? '' : 'bad');
  updatePct(lid, $('#view'));
  updateQuizHead(lid);
  renderTree();
  if (S.token) queuePush();
}

function updateQuizHead(lid) {
  var head = document.querySelector('.js-quizhead');
  if (!head) return;
  var l = S.lessons[lid];
  if (!l || !l.cards) return;
  var quiz = l.cards.filter(function (c) { return c.type !== 'lecture'; });
  var done = quiz.filter(function (c) { return S.progress[lid + '|' + c.id] !== undefined; }).length;
  var right = quiz.filter(function (c) { return S.progress[lid + '|' + c.id] === true; }).length;
  head.innerHTML = '练习<small>' + right + '/' + quiz.length + ' 答对' +
    (done > right ? ' · ' + (done - right) + ' 错' : '') + '</small>';
}

function updatePct(lid, v) {
  if (!v) return;
  var p = v.querySelector('.js-pct');
  if (!p) return;
  var pct = lessonPct(lid);
  p.textContent = pct > 0 ? '完成 ' + pct + '%' : '未开始';
}

/* 阅读进度条 */
var scrollHandler = null;
function observeProgress() {
  var bar = $('#readProgress');
  if (!bar) return;
  if (scrollHandler) window.removeEventListener('scroll', scrollHandler);
  scrollHandler = function () {
    var h = document.documentElement.scrollHeight - window.innerHeight;
    var p = h > 0 ? Math.min(100, Math.max(0, window.scrollY / h * 100)) : 0;
    bar.style.width = p + '%';
  };
  window.addEventListener('scroll', scrollHandler, { passive: true });
  scrollHandler();
}

/* ============================================================
   视图：错题本
   ============================================================ */
function viewWrong(v) {
  setCrumbs([{ text: '错题本' }]);
  setActiveTab('wrong');

  var list = Object.keys(S.wrongs).map(function (k) { return S.wrongs[k]; })
    .sort(function (a, b) { return (b.ts || 0) - (a.ts || 0); });

  v.innerHTML = '';
  v.appendChild(el('<div class="page-head">' +
    '<div class="page-eyebrow">复习</div>' +
    '<h1 class="page-title">错题本</h1>' +
    '<p class="page-desc">' + (list.length ? '共 ' + list.length + ' 道，答对自动移出。' : '答错的选择题和填空题会自动收进这里。') + '</p>' +
  '</div>'));

  if (!list.length) {
    v.appendChild(el('<div class="empty">' +
      '<div class="ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg></div>' +
      '<h3>没有错题</h3><p>继续保持</p></div>'));
    return;
  }

  var box = el('<div class="list"></div>');
  list.forEach(function (w) {
    var row = el('<button class="list-row">' +
      '<div class="lr-main"><span class="lr-title">' + esc(w.preview || w.cardId) + '</span>' +
      '<span class="lr-sub">' + esc(w.lessonTitle || '') + '</span></div>' +
      '<span class="chevron">' + ICON.chevR + '</span></button>');
    row.onclick = function () {
      go('/lesson/' + encodeURIComponent(w.lessonId));
      setTimeout(function () {
        var n = document.querySelector('[data-card="' + w.cardId + '"]');
        if (n) n.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }, 700);
    };
    box.appendChild(row);
  });
  v.appendChild(box);
}

/* ============================================================
   视图：账号
   ============================================================ */
function viewMe(v) {
  setCrumbs([{ text: '我的' }]);
  setActiveTab('me');
  v.innerHTML = '';

  if (S.user) {
    v.appendChild(el('<div class="page-head">' +
      '<div class="page-eyebrow">账号</div>' +
      '<h1 class="page-title">我的</h1></div>'));

    var pc = el('<div class="profile-card">' +
      '<span class="avatar">' + esc(S.user.slice(0, 1)) + '</span>' +
      '<div><div class="pc-name">' + esc(S.user) + '</div>' +
      '<div class="pc-sub">进度已绑定此账号</div></div></div>');
    v.appendChild(pc);

    v.appendChild(el('<div style="height:16px"></div>'));

    var info = el('<div class="list" style="padding:18px 20px">' +
      '<dl class="kv">' +
        '<dt>服务器</dt><dd>' + esc(location.host) + '</dd>' +
        '<dt>答对</dt><dd>' + Object.keys(S.progress).filter(function (k) { return S.progress[k] === true; }).length + ' 题</dd>' +
        '<dt>错题</dt><dd>' + Object.keys(S.wrongs).length + ' 道</dd>' +
      '</dl></div>');
    v.appendChild(info);

    v.appendChild(el('<div style="height:16px"></div>'));

    var acts = el('<div style="display:flex;gap:10px;flex-wrap:wrap">' +
      '<button class="btn" id="syncBtn">立即同步</button>' +
      '<button class="btn ghost" id="outBtn">退出登录</button></div>');
    v.appendChild(acts);

    $('#syncBtn').onclick = function () {
      var b = this; b.disabled = true; b.textContent = '同步中…';
      pushProgress().then(function () { toast('已同步'); })
        .catch(function (e) { toast('失败：' + e.message, 'bad'); })
        .then(function () { b.disabled = false; b.textContent = '立即同步'; });
    };
    $('#outBtn').onclick = function () {
      api('/auth/logout', { method: 'POST', body: '{}' }).catch(function () {});
      stopPolling();
      S.token = ''; S.user = '';
      localStorage.removeItem(K.token); localStorage.removeItem(K.user);
      toast('已退出');
      go('/home');
    };

    v.appendChild(el('<p class="page-desc" style="margin-top:24px;font-size:13px">' +
      '课程与题目对所有人开放。登录只用于同步答题进度与错题，不同账号之间互相看不到。</p>'));
    return;
  }

  v.appendChild(el('<div class="page-head"><div class="page-eyebrow">账号</div>' +
    '<h1 class="page-title">登录</h1></div>'));

  var panel = el('<div class="auth-panel">' +
    '<h2>登录学习台</h2>' +
    '<p class="sub">登录后答题进度和错题会同步到账号，换设备自动接上。</p>' +
    '<div class="field"><label for="u">用户名</label>' +
      '<input class="input" id="u" type="text" autocomplete="username" autocapitalize="off" spellcheck="false"></div>' +
    '<div class="field"><label for="p">密码</label>' +
      '<input class="input" id="p" type="password" autocomplete="current-password"></div>' +
    '<div class="msg" id="msg"></div>' +
    '<button class="btn block" id="loginBtn">登录</button>' +
    '<div class="divider-or">或</div>' +
    '<button class="btn ghost block" id="regBtn"' + (S.registerOpen ? '' : ' disabled') + '>' +
      (S.registerOpen ? '注册新账号' : '注册暂未开放') + '</button>' +
  '</div>');
  v.appendChild(panel);

  $('#loginBtn').onclick = doLogin;
  $('#p').onkeydown = function (e) { if (e.key === 'Enter') doLogin(); };
  $('#regBtn').onclick = doRegister;
}

function setMsg(t, err) {
  var m = $('#msg');
  if (!m) return;
  m.textContent = t || '';
  m.className = 'msg' + (t ? (err ? ' err' : ' ok') : '');
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
      localStorage.setItem(K.token, d.token);
      localStorage.setItem(K.user, d.username);
      return pullProgress(true);
    })
    .then(function () { startPolling(); toast('登录成功'); go('/home'); })
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
      localStorage.setItem(K.token, d.token);
      localStorage.setItem(K.user, d.username);
      startPolling();
      toast('注册成功');
      go('/home');
    })
    .catch(function (e) { setMsg(e.message, true); });
}

/* ============================================================
   同步
   ============================================================ */
function queuePush() {
  clearTimeout(S.pushTimer);
  S.pushTimer = setTimeout(function () { pushProgress().catch(function () {}); }, 900);
}

function pushProgress() {
  if (!S.token) return Promise.resolve();
  return api('/progress', {
    method: 'POST',
    body: JSON.stringify({
      progress: S.progress,
      wrongs: Object.keys(S.wrongs).map(function (k) { return S.wrongs[k]; }),
      notes: {}
    })
  });
}

function mergeRemote(p) {
  if (!p) return false;
  var changed = false;
  if (p.progress) {
    Object.keys(p.progress).forEach(function (k) {
      var r = p.progress[k], l = S.progress[k];
      if (r === true || l === undefined) {
        if (S.progress[k] !== r) changed = true;
        S.progress[k] = r;
      }
    });
  }
  if (Array.isArray(p.wrongs)) {
    p.wrongs.forEach(function (w) {
      if (w && w.id && !S.wrongs[w.id]) { S.wrongs[w.id] = w; changed = true; }
    });
  }
  if (changed) { save(K.progress, S.progress); save(K.wrongs, S.wrongs); }
  return changed;
}

function pullProgress(force) {
  if (!S.token) return Promise.resolve(false);
  var now = Date.now();
  if (!force && now - S.lastPullAt < 20000) return Promise.resolve(false);
  S.lastPullAt = now;
  return api('/progress')
    .then(function (d) { return mergeRemote((d && d.data) || {}); })
    .catch(function () { return false; });
}

function startPolling() {
  if (!S.token) return;
  stopPolling();
  var ctl = { dead: false, ac: (typeof AbortController !== 'undefined') ? new AbortController() : null };
  S.pollCtl = ctl;
  var since = S.lastUpdated || 0;

  function tick() {
    if (ctl.dead || !S.token) return;
    if (document.visibilityState !== 'visible') { ctl.dead = true; return; }
    fetch(API + '/progress/poll?since=' + encodeURIComponent(since), {
      headers: { 'Authorization': 'Bearer ' + S.token },
      signal: ctl.ac ? ctl.ac.signal : undefined
    })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (ctl.dead) return;
        if (d && d.updated) since = d.updated;
        if (d && d.data) {
          var ch = mergeRemote(d.data);
          if (ch) rerenderCurrent();
        }
        tick();
      })
      .catch(function () { if (!ctl.dead) setTimeout(tick, 2500); });
  }
  tick();
}

function stopPolling() {
  if (S.pollCtl) {
    S.pollCtl.dead = true;
    try { if (S.pollCtl.ac) S.pollCtl.ac.abort(); } catch (e) {}
    S.pollCtl = null;
  }
}

/** 云端有变化时刷新当前页（不打断输入） */
function rerenderCurrent() {
  var active = document.activeElement;
  if (active && (active.tagName === 'INPUT' || active.tagName === 'TEXTAREA')) return;
  renderTree();
  var r = S.route;
  if (r.name === 'lesson') {
    var v = $('#view');
    var cards = $$('.qcard[data-card]', v);
    if (!cards.length) return;
    // 只更新状态，不重建 DOM
    cards.forEach(function (c) {
      var lid = r.id, cid = c.dataset.card;
      var st = S.progress[lid + '|' + cid];
      var head = $('.qhead', c);
      if (!head) return;
      var pill = $('.pill', head);
      if (st !== undefined && !pill) {
        head.appendChild(el('<span class="pill ' + (st ? 'ok' : 'bad') + '">' +
          (st ? '✓ 答对' : '✕ 答错') + '</span>'));
      }
    });
    updatePct(r.id, v);
  } else if (r.name === 'wrong' || r.name === 'home') {
    render();
  }
}

/* ============================================================
   启动
   ============================================================ */
function render() {
  var r = parseHash();
  S.route = r;
  var v = $('#view');
  if (r.name !== 'lesson') {
    if (scrollHandler) window.removeEventListener('scroll', scrollHandler);
    $('#readProgress').style.width = '0';
  }

  v.classList.toggle('wide', r.name === 'home' || r.name === 'lib' || r.name === 'wrong');

  switch (r.name) {
    case 'home':   viewHome(v); break;
    case 'lib':    viewLib(v, r.id); break;
    case 'lesson': viewLesson(v, r.id); break;
    case 'wrong':  viewWrong(v); break;
    case 'me':     viewMe(v); break;
    default:       go('/home'); return;
  }
  renderTree();
  renderFoot();
  setAuthBtn();
  window.scrollTo(0, 0);
}

function restoreAuth() {
  S.token = localStorage.getItem(K.token) || '';
  S.user = localStorage.getItem(K.user) || '';
  S.progress = load(K.progress, {});
  S.wrongs = load(K.wrongs, {});
  S.openGroups = load(K.openGroups, {});

  // 兼容旧版数组格式的错题
  if (Array.isArray(S.wrongs)) {
    var m = {};
    S.wrongs.forEach(function (w) { if (w && w.id) m[w.id] = w; });
    S.wrongs = m;
    save(K.wrongs, S.wrongs);
  }

  return fetch(API + '/auth/config')
    .then(function (r) { return r.json(); })
    .then(function (d) { S.registerOpen = !!d.registerOpen; })
    .catch(function () {})
    .then(function () {
      if (!S.token) return;
      return api('/auth/me')
        .then(function (d) {
          S.user = d.username;
          localStorage.setItem(K.user, d.username);
          return pullProgress(true);
        })
        .catch(function () {
          S.token = ''; S.user = '';
          localStorage.removeItem(K.token); localStorage.removeItem(K.user);
        });
    });
}

/* ---------- 事件绑定 ---------- */
$('#menuBtn').onclick = function () {
  if ($('#sidebar').classList.contains('open')) closeDrawer(); else openDrawer();
};
$('#scrim').onclick = closeDrawer;
$('#authBtn').onclick = function () { go('/me'); };

var searchTimer;
$('#search').oninput = function () {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(renderTree, 140);
};

// "/" 聚焦搜索
document.addEventListener('keydown', function (e) {
  if (e.key === '/' && !/INPUT|TEXTAREA/.test(document.activeElement.tagName)) {
    e.preventDefault();
    $('#search').focus();
  }
  if (e.key === 'Escape') {
    if ($('#search') === document.activeElement) $('#search').blur();
    closeDrawer();
  }
});

window.addEventListener('hashchange', function () { closeDrawer(); render(); });

document.addEventListener('visibilitychange', function () {
  if (document.visibilityState === 'visible' && S.token) {
    pullProgress(true);
    startPolling();
  } else {
    stopPolling();
  }
});

var lastWide = window.matchMedia('(min-width: 1400px)').matches;
window.addEventListener('resize', function () {
  if (!isMobile()) closeDrawer();
  var nowWide = window.matchMedia('(min-width: 1400px)').matches;
  // 只在跨越断点时重排，避免拖动窗口时反复重建
  if (nowWide !== lastWide) {
    lastWide = nowWide;
    if (S.route.name === 'lesson') render();
  }
});

/* ---------- 起 ---------- */
loadManifest()
  .then(restoreAuth)
  .then(function () {
    render();
    if (S.token) startPolling();
  })
  .catch(function () { render(); });

})();
