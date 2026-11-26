# -*- coding: utf-8 -*-
"""心形线公共部分：用密集楔形填充，避免路径自交"""
import io

P = r"C:/Users/chong/Documents/studyhub/tools/inject_figs_ch6.py"
s = io.open(P, encoding="utf-8").read()

old = """    # 公共部分填充：|θ|≤π/3 取 1+cosθ；π/3<|θ|<π/2 取 3cosθ
    poly = polar_path(lambda th: 1 + math.cos(th), -math.pi / 3, math.pi / 3, 90)
    poly += polar_path(lambda th: 3 * math.cos(th), math.pi / 3, math.pi / 2, 45)
    poly += polar_path(lambda th: 3 * math.cos(th), -math.pi / 2, -math.pi / 3, 45)
    f.add('<path d="%s" fill="%s" fill-opacity="0.2" stroke="none"/>' % (poly_d(poly, True), ORANGE))"""

new = """    # 公共部分填充：按角度切楔形逐块填（里层曲线：|θ|≤π/3 心形线，其余圆）
    def inner(th):
        c = math.cos(th)
        return (1 + c) if abs(th) <= math.pi / 3 else 3 * c

    n = 160
    for i in range(n):
        th0 = -math.pi / 2 + math.pi * i / n
        th1 = -math.pi / 2 + math.pi * (i + 1) / n
        r0 = inner(th0)
        r1 = inner(th1)
        if r0 <= 0 or r1 <= 0:
            continue
        pts = [(f.X(0), f.Y(0)),
               (f.X(r0 * math.cos(th0)), f.Y(r0 * math.sin(th0))),
               (f.X(r1 * math.cos(th1)), f.Y(r1 * math.sin(th1)))]
        f.add('<path d="%s" fill="%s" fill-opacity="0.22" stroke="none"/>'
              % (poly_d(pts, True), ORANGE))"""

assert s.count(old) == 1
io.open(P, "w", encoding="utf-8", newline="\n").write(s.replace(old, new))
print("patched")
