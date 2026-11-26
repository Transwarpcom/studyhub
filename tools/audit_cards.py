# -*- coding: utf-8 -*-
"""静态体检：逐卡检查输入控件、答案、选项、公式占位"""
import glob
import io
import json
import os
import re
import sys

LESSONS = r"C:/Users/chong/Documents/studyhub/content/lessons"

problems = []


def add(lid, cid, kind, detail):
    problems.append((lid, cid, kind, detail))


files = sorted(glob.glob(os.path.join(LESSONS, "*.json")))
print("扫描 %d 个 lesson" % len(files))

stat = {"lesson": 0, "card": 0, "blank": 0, "choice": 0, "text": 0}

for f in files:
    try:
        d = json.load(io.open(f, encoding="utf-8"))
    except Exception as e:
        add(os.path.basename(f), "-", "解析失败", str(e))
        continue
    lid = d.get("id", "?")
    stat["lesson"] += 1
    if not d.get("title"):
        add(lid, "-", "缺 title", "")
    for c in d.get("cards") or []:
        stat["card"] += 1
        cid = c.get("id", "?")
        t = c.get("type")
        q = c.get("question") or ""
        md = c.get("md") or ""
        opts = c.get("options")
        ans = c.get("answer")
        blanks = c.get("blanks")

        if t not in ("lecture", "choice", "multi", "judge", "blank", "text"):
            add(lid, cid, "未知题型", str(t))

        # answer 类型
        if ans is not None and not (isinstance(ans, list) and all(isinstance(x, int) for x in ans)):
            add(lid, cid, "answer 不是 [Int]", repr(ans)[:60])

        # 选择题要有 2 个以上选项、答案在范围内
        if t in ("choice", "multi", "judge"):
            stat["choice"] += 1
            if not isinstance(opts, list) or len(opts) < 2:
                add(lid, cid, "选项不足", repr(opts)[:50])
            else:
                n = len(opts)
                if not ans:
                    add(lid, cid, "选择题无答案", "")
                else:
                    for a in ans:
                        if not (0 <= a < n):
                            add(lid, cid, "答案越界", "%s / %d 项" % (ans, n))
            if not c.get("explain"):
                add(lid, cid, "选择题缺解析", "")

        # 填空题：占位符与 blanks 必须配套
        if t == "blank":
            stat["blank"] += 1
            if not isinstance(blanks, list) or not blanks:
                add(lid, cid, "填空题缺 blanks", "")
                continue
            nblank = len(blanks)
            ncurly = len(re.findall(r"\{\{(\d+)\}\}", q))
            # 连续下划线（两种：ASCII 与全角）
            nline = len(re.findall(r"_{2,}", q))
            if ncurly == 0 and nline == 0:
                add(lid, cid, "没有填空位", "题干里既没有 {{n}} 也没有 ____")
            elif ncurly == 0 and nline != nblank:
                add(lid, cid, "下划线与空数不符", "____×%d vs blanks×%d" % (nline, nblank))
            elif ncurly and ncurly != nblank:
                add(lid, cid, "占位与空数不符", "{{n}}×%d vs blanks×%d" % (ncurly, nblank))
            # 每个空至少一个答案
            for i, acc in enumerate(blanks):
                if not isinstance(acc, list) or not acc:
                    add(lid, cid, "第 %d 空没有答案" % (i + 1), repr(acc)[:40])
            if not c.get("explain"):
                add(lid, cid, "填空题缺解析", "")

        if t == "text":
            stat["text"] += 1
            if not c.get("explain"):
                add(lid, cid, "解答题缺解析", "")

        # 题干为空
        if t != "lecture" and not q.strip():
            add(lid, cid, "题干为空", "")

        # 公式花括号平衡（与 publish.py 一致）
        for fld, s in (("question", q), ("explain", c.get("explain")), ("md", md)):
            if not isinstance(s, str):
                continue
            for m in re.finditer(r"\$\$([\s\S]+?)\$\$|\$([^$\n]+?)\$", s):
                tex = m.group(1) or m.group(2) or ""
                o = tex.count("{") - tex.count("\\{")
                cl = tex.count("}") - tex.count("\\}")
                if o != cl:
                    add(lid, cid, "LaTeX 花括号不平衡", fld + ": " + tex[:50])

        # SVG 是否合法（粗检）
        svg = c.get("svg")
        if svg:
            if not svg.strip().startswith("<svg") or "</svg>" not in svg:
                add(lid, cid, "SVG 结构异常", svg[:40])
            for tag in ("viewBox",):
                if tag not in svg:
                    add(lid, cid, "SVG 缺 viewBox", "")

print("统计:", stat)
print()
print("问题 %d 条" % len(problems))
by_kind = {}
for lid, cid, kind, detail in problems:
    by_kind.setdefault(kind, []).append((lid, cid, detail))
for kind, items in sorted(by_kind.items(), key=lambda kv: -len(kv[1])):
    print("\n## %s（%d）" % (kind, len(items)))
    for lid, cid, detail in items[:12]:
        print("   %-22s %-6s %s" % (lid, cid, detail))
    if len(items) > 12:
        print("   …还有 %d 条" % (len(items) - 12))
