# -*- coding: utf-8 -*-
"""把 4.2 / 4.3 作业册转成手机友好 PDF 用的 HTML（KaTeX 本地渲染）"""
import json, os, re, html

ROOT = r"C:/Users/chong/Documents/studyhub"
KATEX = ROOT + "/web/katex"
OUT = r"C:/Users/chong/Documents/exports/hwb-pdf"
os.makedirs(OUT, exist_ok=True)

SECTIONS = [("4-2", "4.2 换元积分法"), ("4-3", "4.3 分部积分法")]


def load(k):
    return json.load(open(rf"{ROOT}/content/lessons/math_hwb-{k}.json", encoding="utf-8"))


def esc(s):
    return html.escape(s, quote=False)


# ---- 极简 Markdown → HTML（只处理本内容用到的语法）----
def md2html(md):
    """行内：**粗体**、$公式$、`code`；块级：## 标题、表格、列表、$$公式$$、段落"""
    lines = md.split("\n")
    out = []
    i = 0
    n = len(lines)

    def inline(t):
        # 保护 $...$ 公式
        maths = []

        def keep(m):
            maths.append(m.group(0))
            return f"\x00M{len(maths)-1}\x00"

        t = re.sub(r"\$\$(.+?)\$\$", keep, t, flags=re.S)
        t = re.sub(r"(?<!\$)\$([^$\n]+?)\$(?!\$)", keep, t)
        # 粗体
        t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
        # 行内代码
        t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
        # 还原公式，交给 KaTeX
        for idx, m in enumerate(maths):
            t = t.replace(f"\x00M{idx}\x00", m)
        return t

    while i < n:
        line = lines[i]
        s = line.rstrip()

        if not s.strip():
            i += 1
            continue

        # 独立公式块
        if s.strip().startswith("$$"):
            buf = [s.strip()]
            # 单行 $$...$$
            if s.strip().count("$$") >= 2 and len(s.strip()) > 4:
                out.append(f'<div class="eq">{esc(s.strip())}</div>')
                i += 1
                continue
            i += 1
            while i < n and "$$" not in lines[i]:
                buf.append(lines[i].rstrip())
                i += 1
            if i < n:
                buf.append(lines[i].strip())
                i += 1
            out.append(f'<div class="eq">{esc(chr(10).join(buf))}</div>')
            continue

        # 标题
        m = re.match(r"^(#{1,4})\s+(.*)$", s.strip())
        if m:
            lv = len(m.group(1))
            out.append(f"<h{lv+1}>{inline(m.group(2))}</h{lv+1}>")
            i += 1
            continue

        # 表格
        if s.strip().startswith("|") and i + 1 < n and re.match(r"^\|?[\s:\-|]+\|?$", lines[i + 1].strip()):
            head = [c.strip() for c in s.strip().strip("|").split("|")]
            i += 2
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            t = ['<table><thead><tr>']
            t += [f"<th>{inline(c)}</th>" for c in head]
            t.append("</tr></thead><tbody>")
            for r in rows:
                t.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
            t.append("</tbody></table>")
            out.append("".join(t))
            continue

        # 列表
        if re.match(r"^\s*[-*+]\s+", s):
            items = []
            while i < n and re.match(r"^\s*[-*+]\s+", lines[i]):
                items.append(re.sub(r"^\s*[-*+]\s+", "", lines[i].rstrip()))
                i += 1
            out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ul>")
            continue

        if re.match(r"^\s*\d+\.\s+", s):
            items = []
            while i < n and re.match(r"^\s*\d+\.\s+", lines[i]):
                items.append(re.sub(r"^\s*\d+\.\s+", "", lines[i].rstrip()))
                i += 1
            out.append("<ol>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ol>")
            continue

        # 分隔线
        if re.match(r"^(-{3,}|\*{3,})$", s.strip()):
            out.append("<hr>")
            i += 1
            continue

        # 段落（合并连续非空行）
        buf = [s.strip()]
        i += 1
        while i < n and lines[i].strip() and not re.match(r"^(#{1,4}\s|\||[-*+]\s|\d+\.\s|\$\$|-{3,})", lines[i].strip()):
            buf.append(lines[i].strip())
            i += 1
        out.append("<p>" + inline(" ".join(buf)) + "</p>")

    return "\n".join(out)


CSS = """
:root{--ink:#111;--dim:#666;--line:#d8d8d8;--accent:#0b62d6}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{
  font-family:"Times New Roman","Songti SC",STSong,SimSun,serif;
  font-size:14pt;line-height:1.7;color:var(--ink);
  padding:0 12pt;
  -webkit-text-size-adjust:100%;
}
h1{font-size:19pt;margin:0 0 2pt;font-weight:700;letter-spacing:.3pt}
h2{font-size:16.5pt;margin:0 0 8pt;padding-bottom:6pt;border-bottom:2px solid var(--ink);font-weight:700}
h3{font-size:13.8pt;margin:16pt 0 6pt;font-weight:700}
h4{font-size:13pt;margin:13pt 0 5pt;font-weight:700}
.sub{color:var(--dim);font-size:11.5pt;margin:0 0 16pt}
p{margin:7pt 0}
strong{font-weight:700}
hr{border:none;border-top:1px solid var(--line);margin:14pt 0}
ul,ol{margin:7pt 0;padding-left:20pt}
li{margin:3.5pt 0}
code{font-family:Consolas,Menlo,monospace;font-size:11.5pt;background:#f4f4f4;padding:1pt 4pt;border-radius:3px}
table{border-collapse:collapse;width:100%;margin:9pt 0;font-size:11.8pt;table-layout:fixed}
th,td{border:1px solid var(--line);padding:5pt 6pt;text-align:left;vertical-align:top;word-wrap:break-word}
th{background:#f6f6f6;font-weight:700}
.eq{
  margin:9pt 0;padding:7pt 8pt;background:#fafafa;border-left:3px solid var(--accent);
  overflow-x:visible;text-align:center;
}
.katex{font-size:1.02em}
.katex-display{margin:4pt 0}
.katex-display>.katex{white-space:normal}
/* 卡片 */
.q{margin:0 0 18pt;padding:0 0 12pt;border-bottom:1px dashed var(--line)}
.qh{page-break-after:avoid;break-after:avoid}
.explain{page-break-inside:auto;break-inside:auto}
.qh{font-size:14.5pt;font-weight:700;margin:0 0 9pt}
.qn{display:inline-block;min-width:20pt;color:var(--accent)}
.tag{display:inline-block;font-size:9.5pt;color:#fff;background:#555;border-radius:3pt;
  padding:.5pt 5pt;margin-left:5pt;font-weight:400;vertical-align:2pt}
.explain{margin-top:10pt;padding:10pt 11pt;background:#f8f9fa;border:1px solid #e6e8eb;border-radius:5pt;font-size:13.2pt}
.explain .lbl{font-size:10.5pt;font-weight:700;color:var(--dim);letter-spacing:.5pt;margin:0 0 6pt}
.sec-break{page-break-before:always;break-before:page;margin-top:0}
.lead{page-break-after:avoid;break-after:avoid}
@page{size:A5;margin:11mm 9mm}
"""

TMPL = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<link rel="stylesheet" href="{katex}/katex.min.css">
<style>{css}</style>
</head><body>
{body}
<script src="{katex}/katex.min.js"></script>
<script src="{katex}/contrib/auto-render.min.js"></script>
<script>
renderMathInElement(document.body, {{
  delimiters: [
    {{left:"$$", right:"$$", display:true}},
    {{left:"$", right:"$", display:false}}
  ],
  throwOnError: false,
  strict: false,
  trust: true,
  macros: {{"\\\\R":"\\\\mathbb{{R}}", "\\\\dd":"\\\\mathrm{{d}}", "\\\\dx":"\\\\mathrm{{d}}x"}}
}});
</script>
</body></html>
"""


def render():
    parts = []
    for idx, (k, name) in enumerate(SECTIONS):
        d = load(k)
        qn = 0
        body = []
        brk = ""   # 不强制分页，靠自然流排布，避免半空页
        body.append(f'<div class="sec{brk}">')
        body.append(f'<h2>{esc(name)}</h2>')
        body.append(f'<p class="sub">{esc(d.get("subtitle") or "")}</p>')

        for c in d["cards"]:
            t = c["type"]
            if t == "lecture":
                md = (c.get("md") or "").strip()
                # 讲义首行是「## 4.2 换元积分法」，与上面 h2 重复，去掉
                md = re.sub(r"^#{1,4}\s*[^\n]*\n?", "", md, count=1)
                body.append(md2html(md.strip()))
                continue
            qn += 1
            lbl = {"choice": "单选", "multi": "多选", "judge": "判断",
                   "blank": "填空", "text": "解答"}.get(t, t)
            q = c.get("question") or ""
            # 题干首行常是「**一、填空题 第 1 题**」
            m = re.match(r"^\s*\*\*(.+?)\*\*\s*", q, re.S)
            head = m.group(1) if m else ""
            rest = q[m.end():] if m else q
            body.append('<div class="q">')
            body.append(f'<div class="qh">{esc(head)}<span class="tag">{lbl}</span></div>')
            body.append(md2html(rest))
            opts = c.get("options")
            if opts:
                body.append("<ol type=\"A\">" + "".join(f"<li>{esc(o)}</li>" for o in opts) + "</ol>")
            ex = c.get("explain")
            if ex:
                body.append('<div class="explain"><div class="lbl">解答</div>' + md2html(ex) + "</div>")
            body.append("</div>")
        body.append("</div>")
        parts.append("\n".join(body))

    body_html = "\n".join(parts)
    full = TMPL.format(
        title="数学作业册 4.2 / 4.3 解答",
        katex="file:///" + KATEX.replace("\\", "/"),
        css=CSS,
        body=body_html,
    )
    p = os.path.join(OUT, "hwb-4-2-4-3.html")
    open(p, "w", encoding="utf-8").write(full)
    print("HTML:", p, len(full), "字节")
    return p


if __name__ == "__main__":
    render()
