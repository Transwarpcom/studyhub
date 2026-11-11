const fs = require('fs');
const path = require('path');
const katex = require(path.resolve('C:/Users/chong/Documents/studyhub/Resources/web/katex/katex.min.js'));

const rows = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
let bad = [];
let ok = 0;
for (const r of rows) {
  try {
    katex.renderToString(r.tex, { throwOnError: true, displayMode: !!r.display, strict: 'ignore' });
    ok++;
  } catch (e) {
    bad.push({ file: r.f, card: r.c, field: r.fld, tex: r.tex.slice(0, 120), err: String(e.message).slice(0, 160) });
  }
}
console.log(JSON.stringify({ total: rows.length, ok, bad: bad.length, errors: bad }, null, 1));
