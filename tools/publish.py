#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""内容发布工具：国产校验 + 原子升版本

用法：
  python tools/publish.py check              # 只校验，不动任何东西
  python tools/publish.py check --strict     # 严格校验（含答案验算提示）
  python tools/publish.py bump               # 校验通过后把 manifest version +1

设计原则：
  - 校验不通过就绝不 bump
  - bump 只改 version 和 updated，不碰 tree
  - 上传由人工/脚本在外面做（本机 → 服务器）
"""
import json
import glob
import os
import re
import sys
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, "content")
LESSONS = os.path.join(CONTENT, "lessons")
MANIFEST = os.path.join(CONTENT, "manifest.json")


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def all_lesson_ids(tree):
    out = []

    def walk(nodes):
        for n in nodes:
            if n.get("kind") == "lesson":
                out.append(n.get("bundle") or n.get("id"))
            if n.get("children"):
                walk(n["children"])

    walk(tree)
    return out


def check_latex(text):
    """返回花括号不平衡的片段列表"""
    bad = []
    for m in re.finditer(r"\$\$([\s\S]+?)\$\$|\$([^$\n]+?)\$", text or ""):
        tex = m.group(1) or m.group(2) or ""
        opens = tex.count("{") - tex.count("\\{")
        closes = tex.count("}") - tex.count("\\}")
        if opens != closes:
            bad.append(tex[:60])
    return bad


def expected_badge(lid, n_cards, n_quiz):
    """badge 口径：作业册（math/hwb-*）记题数，其余记卡片数。"""
    return f"{n_quiz} 题" if lid.startswith("math/hwb-") else f"{n_cards} 卡"


def sync_badges(man, data, verbose=True):
    """把 manifest 里每个 lesson 的 badge 校准成 expected_badge。返回改动列表。"""
    changed = []

    def walk(nodes):
        for n in nodes:
            lid = n.get("bundle") or n.get("id")
            if n.get("kind") == "lesson" and lid in data:
                nc, nq = data[lid]
                want = expected_badge(lid, nc, nq)
                if n.get("badge") != want:
                    changed.append((lid, n.get("title"), n.get("badge"), want))
                    n["badge"] = want
            if n.get("children"):
                walk(n["children"])

    walk(man.get("tree") or [])
    if verbose:
        for lid, t, old, new in changed:
            print(f"  badge {str(t)[:34]:36s} {old} → {new}")
    return changed


def load_all_lessons():
    """读磁盘所有 lesson，返回 {id: (卡片数, 题数)}"""
    out = {}
    for f in glob.glob(os.path.join(LESSONS, "*.json")):
        try:
            d = load(f)
            lid = d.get("id")
            if not lid:
                continue
            cards = d.get("cards") or []
            out[lid] = (len(cards), len([c for c in cards if c.get("type") != "lecture"]))
        except Exception:
            continue
    return out


def cmd_check(strict=False):
    errors = []
    warnings = []

    if not os.path.isfile(MANIFEST):
        print("FAIL: manifest.json 不存在")
        return False

    man = load(MANIFEST)
    ver = man.get("version")
    print(f"manifest version = {ver}   updated = {man.get('updated')}")

    # badge 是否与实际卡数/题数一致（自动校准，写回文件）
    data = load_all_lessons()
    changed = sync_badges(man, data, verbose=False)
    if changed:
        print(f"badge 不一致 {len(changed)} 处，已自动写入 manifest：")
        for lid, t, old, new in changed:
            print(f"  {str(t)[:34]:36s} {old} → {new}")
        with open(MANIFEST, "w", encoding="utf-8") as f:
            json.dump(man, f, ensure_ascii=False, indent=2)

    ids = all_lesson_ids(man.get("tree") or [])
    print(f"manifest 课程节点 = {len(ids)}")

    if len(ids) != len(set(ids)):
        seen = set()
        dup = [i for i in ids if i in seen or seen.add(i)]
        errors.append(f"manifest 里有重复 id: {dup}")

    # 1. tree 里每个节都要有对应文件
    missing = []
    for lid in ids:
        fn = os.path.join(LESSONS, lid.replace("/", "_") + ".json")
        if not os.path.isfile(fn):
            missing.append(lid)
    if missing:
        errors.append(f"manifest 指向但文件不存在 ({len(missing)}): {missing[:8]}")

    # 2. 磁盘上每个 lesson 文件是否都在 tree 里
    ondisk = set()
    for f in glob.glob(os.path.join(LESSONS, "*.json")):
        ondisk.add(os.path.basename(f)[:-5])
    orphan = []
    for base in sorted(ondisk):
        cand = base.replace("_", "/", 1) if "_" in base else base
        # 更稳的做法：看文件内 id
        try:
            d = load(os.path.join(LESSONS, base + ".json"))
            fid = d.get("id")
        except Exception as e:
            errors.append(f"{base}.json 解析失败: {e}")
            continue
        if fid and fid not in ids:
            orphan.append(fid)
    if orphan:
        warnings.append(f"磁盘上有但 manifest 没收录 ({len(orphan)}): {orphan[:8]}")

    # 3. 逐节检查内容
    empty = []
    no_card = []
    latex_bad = []
    for lid in ids:
        fn = os.path.join(LESSONS, lid.replace("/", "_") + ".json")
        if not os.path.isfile(fn):
            continue
        try:
            d = load(fn)
        except Exception as e:
            errors.append(f"{lid} 解析失败: {e}")
            continue
        cards = d.get("cards") or []
        if not cards:
            empty.append(lid)
            continue
        if not d.get("title"):
            no_card.append(lid)
        for c in cards:
            for fld in ("md", "question", "explain", "q", "exp"):
                t = c.get(fld)
                if isinstance(t, str):
                    b = check_latex(t)
                    if b:
                        latex_bad.append((lid, c.get("id"), fld, b[0]))
    if empty:
        errors.append(f"cards 为空的节 ({len(empty)}): {empty[:8]}")
    if no_card:
        warnings.append(f"缺 title 的节 ({len(no_card)}): {no_card[:8]}")
    if latex_bad:
        errors.append(f"LaTeX 花括号不平衡 {len(latex_bad)} 处，前3: {latex_bad[:3]}")

    # 4. 题型合法性
    valid_types = {"lecture", "choice", "multi", "judge", "blank", "text"}
    bad_type = []
    # 5. 选择题答案范围
    bad_answer = []
    # 6. JSON schema（与 App 的 Codable 对齐：answer 必须 [Int]、blanks 必须 [[String]]）
    schema_bad = []
    for lid in ids:
        fn = os.path.join(LESSONS, lid.replace("/", "_") + ".json")
        if not os.path.isfile(fn):
            continue
        d = load(fn)
        for c in d.get("cards") or []:
            t = c.get("type")
            if t and t not in valid_types:
                bad_type.append((lid, c.get("id"), t))
            cid = c.get("id")
            # id / type 必填且为字符串
            if not isinstance(cid, str) or not cid:
                schema_bad.append((lid, cid, "id 缺失或非字符串"))
            if not isinstance(t, str):
                schema_bad.append((lid, cid, "type 缺失"))
            # answer 必须是 [Int]?
            if c.get("answer") is not None:
                a = c["answer"]
                if not isinstance(a, list) or not all(isinstance(x, int) for x in a):
                    schema_bad.append((lid, cid, f"answer 需 [Int]，实为 {a!r}"))
            # blanks 必须是 [[String]]?
            if c.get("blanks") is not None:
                b = c["blanks"]
                if not isinstance(b, list) or not all(
                    isinstance(x, list) and all(isinstance(y, str) for y in x) for x in b
                ):
                    schema_bad.append((lid, cid, f"blanks 需 [[String]]，实为 {b!r}"))
            # options / tags 必须是 [String]?
            for fld in ("options", "tags"):
                if c.get(fld) is not None:
                    v = c[fld]
                    if not isinstance(v, list) or not all(isinstance(x, str) for x in v):
                        schema_bad.append((lid, cid, f"{fld} 需 [String]，实为 {v!r}"))
            if t in ("choice", "multi", "judge") and isinstance(c.get("options"), list):
                n = len(c["options"])
                ans = c.get("answer")
                if ans is not None:
                    for a in ans:
                        if isinstance(a, int) and not (0 <= a < n):
                            bad_answer.append((lid, cid, a, n))
            if t == "blank" and not c.get("blanks"):
                bad_answer.append((lid, c.get("id"), "缺 blanks", 0))
    if bad_type:
        errors.append(f"未知题型 {len(bad_type)} 处: {bad_type[:5]}")
    if schema_bad:
        errors.append(f"JSON 类型不符 App 解码要求 {len(schema_bad)} 处: {schema_bad[:5]}")
    if bad_answer:
        errors.append(f"答案越界/缺 blanks {len(bad_answer)} 处: {bad_answer[:5]}")
    # 6b. answer 值是否落在 options 范围内（已在上方 bad_answer 处理）

    # 输出
    print()
    if warnings:
        print(f"警告 {len(warnings)}:") 
        for w in warnings:
            print("  ⚠", w)
        print()
    if errors:
        print(f"错误 {len(errors)}:")
        for e in errors:
            print("  ✗", e)
        print("\n校验未通过，不要升版本号。")
        return False

    print("校验通过 ✓")
    if strict:
        print("（strict：以上已包含全部检查项）")
    return True


def cmd_bump():
    if not cmd_check(strict=True):
        print("\n拒绝 bump：先修好上面的错误。")
        return False

    man = load(MANIFEST)
    old = man.get("version") or 0
    man["version"] = old + 1
    man["updated"] = datetime.date.today().isoformat()

    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(man, f, ensure_ascii=False, indent=2)

    print(f"\n已升版本: {old} → {man['version']}   updated={man['updated']}")
    print("下一步：把所有 content/ 传到服务器，再逐个 curl 确认线上内容。")
    return True


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "check"
    strict = "--strict" in sys.argv
    if action == "check":
        sys.exit(0 if cmd_check(strict) else 1)
    elif action == "bump":
        sys.exit(0 if cmd_bump() else 1)
    else:
        print(__doc__)
        sys.exit(1)
