# -*- coding: utf-8 -*-
"""把第六章三节、作业册四节、六份章检测题挂进 manifest（不动版本号）"""
import json, io, os

P = r"C:/Users/chong/Documents/studyhub/content/manifest.json"
m = json.load(io.open(P, encoding="utf-8"))


def find(nodes, nid):
    for n in nodes:
        if n.get("id") == nid:
            return n
        r = find(n.get("children") or [], nid)
        if r:
            return r
    return None


math = find(m["tree"], "math")
assert math, "找不到 math 根节点"

# ---------- 1. 第六章（课本） ----------
ch6 = {
    "id": "math/6",
    "title": "第六章 定积分的应用",
    "kind": "folder",
    "summary": "元素法 · 面积体积弧长 · 物理应用",
    "children": [
        {"id": "math/6-1", "title": "6.1 定积分的元素法", "kind": "lesson"},
        {"id": "math/6-2", "title": "6.2 定积分在几何学上的应用", "kind": "lesson"},
        {"id": "math/6-3", "title": "6.3 定积分在物理学上的应用", "kind": "lesson"},
    ],
}

kids = math["children"]
ids = [c.get("id") for c in kids]
if "math/6" not in ids:
    pos = ids.index("math/5") + 1 if "math/5" in ids else len(kids)
    kids.insert(pos, ch6)
    print("插入 第六章 于位置", pos)

# ---------- 2. 作业册追加四节 ----------
hwb = find(m["tree"], "math/hwb")
assert hwb, "找不到 math/hwb"
new_hwb = [
    {"id": "math/hwb-6-1", "title": "作业册 · 6.1 元素法 + 6.2 面积", "kind": "lesson"},
    {"id": "math/hwb-6-2a", "title": "作业册 · 6.2 几何应用（二）体积", "kind": "lesson"},
    {"id": "math/hwb-6-2b", "title": "作业册 · 6.2 几何应用（三）弧长", "kind": "lesson"},
    {"id": "math/hwb-6-3", "title": "作业册 · 6.3 物理应用", "kind": "lesson"},
]
exist = {c.get("id") for c in hwb["children"]}
for n in new_hwb:
    if n["id"] not in exist:
        hwb["children"].append(n)
        print("追加作业册", n["id"])

# ---------- 3. 章检测题 ----------
tests = {
    "id": "math/test",
    "title": "章检测题（作业册）",
    "kind": "folder",
    "summary": "第一 ~ 六章整卷 · 全部带解答",
    "children": [
        {"id": "math/test-1", "title": "第一章检测题 · 函数与极限", "kind": "lesson"},
        {"id": "math/test-2", "title": "第二章检测题 · 导数与微分", "kind": "lesson"},
        {"id": "math/test-3", "title": "第三章检测题 · 中值定理与导数应用", "kind": "lesson"},
        {"id": "math/test-4", "title": "第四章检测题 · 不定积分", "kind": "lesson"},
        {"id": "math/test-5", "title": "第五章检测题 · 定积分", "kind": "lesson"},
        {"id": "math/test-6", "title": "第六章检测题 · 定积分的应用", "kind": "lesson"},
    ],
}
if "math/test" not in {c.get("id") for c in kids}:
    kids.append(tests)
    print("追加 章检测题")

# 更新根 summary
math["summary"] = "同济第 8 版上册 · 1.1 至 6.3 全 32 节 + 作业真题 + 章检测题"

json.dump(m, io.open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("manifest written, version =", m["version"], "tree top =", [c["title"] for c in m["tree"]])
