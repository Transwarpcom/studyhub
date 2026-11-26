# -*- coding: utf-8 -*-
"""给第六章的题注入矢量示意图：区域阴影、辅助线、标注、等轴测 3D"""
import io, json, math, os, sys

sys.path.insert(0, r"C:/Users/chong/Documents/studyhub/tools")
from svgkit import (Fig, BLUE, RED, GREEN, ORANGE, PURPLE, LINE, SUB, _fmt)

LESSONS = r"C:/Users/chong/Documents/studyhub/content/lessons"


def poly_d(pts, close=False):
    d = "M" + " L".join("%s %s" % (_fmt(p[0]), _fmt(p[1])) for p in pts)
    return d + (" Z" if close else "")


# ============================================================
# 通用片段
# ============================================================
def tag_dx(fig, x, y, text="dx", color=ORANGE):
    fig.label(x, y, text, dy=16, color=color, size=10.5, style="font-style:italic")


def tick(fig, x, text="", y=0, below=True):
    fig.dot(x, y, LINE, 2.2)
    if text:
        fig.label(x, y, text, dy=(15 if below else -7), size=10)


def area_between_two_curves():
    """元素法：窄条 + 上下曲线"""
    f = Fig(320, 220, (0, 2.3), (-0.3, 2.6))
    up = lambda x: 1.15 + 1.05 * x - 0.28 * x * x
    dn = lambda x: 0.15 + 0.28 * x * x
    f.axes(xtitle="x", ytitle="y")
    f.region(up, dn, 0, 2.1)
    f.curve(up, 0, 2.1, BLUE)
    f.curve(dn, 0, 2.1, GREEN)
    # 窄条
    x, d = 1.35, 0.14
    f.band(x, x + d, up(x), dn(x), ORANGE, "0.34")
    f.seg(x, dn(x), x, up(x), ORANGE, 1.3)
    f.seg(x + d, dn(x + d), x + d, up(x + d), ORANGE, 1.3)
    f.hline(dn(x), 0, x, SUB, 1, "3 3")
    f.label(x + d / 2, dn(x), "dx", dy=17, color=ORANGE, size=10.5)
    f.tex(f.X(x) + 26, (f.Y(up(x)) + f.Y(dn(x))) / 2 + 4,
          "y₂−y₁", ORANGE, 10.5, "start", True)
    f.tex(f.X(2.1) - 6, f.Y(up(2.1)) - 8, "y=y₂(x)", BLUE, 10.5, "end", True)
    f.tex(f.X(1.9) + 6, f.Y(dn(1.9)) + 14, "y=y₁(x)", GREEN, 10.5, "start", True)
    f.label(1.05, 0, "x", dy=16, size=10)
    f.label(1.05 + d, 0, "", dy=16)
    f.tex(f.X(0.35), f.Y(0) + 30, "a", SUB, 10)
    f.tex(f.X(2.05), f.Y(0) + 30, "b", SUB, 10)
    return f.render()


def area_x_x2():
    """y=x² 与 y=x 围成的面积"""
    f = Fig(300, 220, (-0.12, 1.45), (-0.12, 1.5))
    f.axes(xtitle="x", ytitle="y")
    f.region(lambda x: x, lambda x: x * x, 0, 1)
    f.curve(lambda x: x, 0, 1.3, BLUE)
    f.curve(lambda x: x * x, 0, 1.2, GREEN)
    f.band(0.56, 0.7, 0.7, 0.56 * 0.56, ORANGE, "0.3")
    f.label(0.63, 0.6, "dx", dy=15, color=ORANGE, size=10)
    f.dot(0, 0, BLUE, 2.6)
    f.dot(1, 1, BLUE, 3.2)
    f.label(1, 1, "(1,1)", dx=4, dy=-8, size=10, anchor="start")
    f.tex(f.X(0.35), f.Y(0.2), "y=x²", GREEN, 10.5, "start", True)
    f.tex(f.X(0.72), f.Y(0.78), "y=x", BLUE, 10.5, "start", True)
    return f.render()


def polar_sector():
    """极坐标扇形 dθ 与 ρ"""
    f = Fig(260, 230, (-1.5, 1.5), (-0.4, 1.5))
    cx, cy = f.X(0), f.Y(0)
    f.seg(-1.2, 0, 1.2, 0, LINE, 1)
    f.seg(0, -0.2, 0, 1.35, LINE, 1)
    # 两条射线
    for ang, lab in ((0.55, "θ"), (0.85, "θ+dθ")):
        f.seg(0, 0, 1.2 * math.cos(ang), 1.2 * math.sin(ang), SUB, 1.1, "4 4")
    # 弧
    f.curve(lambda a: None, 0, 0, BLUE, 0)
    arc = []
    for i in range(60):
        a = 0.55 + (0.85 - 0.55) * i / 59
        arc.append((f.X(1.2 * math.cos(a)), f.Y(1.2 * math.sin(a))))
    f.add('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (poly_d(arc), BLUE))
    arc2 = []
    for i in range(60):
        a = 0.55 + (0.85 - 0.55) * i / 59
        arc2.append((f.X(0.95 * math.cos(a)), f.Y(0.95 * math.sin(a))))
    f.add('<path d="%s" fill="none" stroke="%s" stroke-width="1.4" stroke-dasharray="4 4"/>'
          % (poly_d(arc2), GREEN))
    f.tex(f.X(0.62 * 1.02), f.Y(0.62 * 0.72), "dθ", ORANGE, 10.5, "middle")
    f.tex(f.X(0.62), f.Y(0.62 * 0.35), "ρ", BLUE, 11, "middle", True)
    f.tex(cx - 10, cy + 14, "O", SUB, 11)
    return f.render()


def revolve_x_axis():
    """3D：曲线绕 x 轴旋转成的旋转体"""
    f = Fig(330, 220, (0, 1), (0, 1), 10, 10, 10, 14)
    cy = 128
    ax0, ax1 = 30, 300
    f.add('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1.1"/>'
           % (ax0 - 6, cy, ax1 + 10, cy, LINE))
    f.arrow(ax1 + 2, cy, ax1 + 12, cy, LINE, 1.1)
    f.tex(ax1 - 4, cy + 16, "x", SUB, 11, "end", True)

    # 母线：y = f(x)
    def top(u, k=1.0):
        return cy - k * (20 + 46 * math.sin((u - 0.08) * 2.4))

    pts_t, pts_b = [], []
    for i in range(61):
        u = 0.12 + 0.72 * i / 60
        px = ax0 + (ax1 - ax0) * u
        yt = top(u)
        pts_t.append((px, yt))
        pts_b.append((px, cy + (cy - yt)))
    # 曲面（渐变感：填充整块）
    d = "M" + " L".join("%s %s" % (_fmt(p[0]), _fmt(p[1])) for p in pts_t)
    d += " L" + " L".join("%s %s" % (_fmt(p[0]), _fmt(p[1])) for p in pts_b[::-1]) + " Z"
    f.add('<path d="%s" fill="%s" fill-opacity="0.10" stroke="none"/>' % (d, BLUE))
    dashes = ' stroke-dasharray="5 4"'
    f.add('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (poly_d(pts_t), BLUE))
    f.add('<path d="%s" fill="none" stroke="%s" stroke-width="1.5"%s/>'
          % (poly_d(pts_b), BLUE, dashes))

    # 两端椭圆（截口）
    f.ellipse(pts_t[0][0], cy, 9, 4.2, BLUE, 1.5)
    f.ellipse(pts_t[-1][0], cy, 9, 4.2, BLUE, 1.5)
    # 一道中间截口 + 半径标注
    mx = 178
    u = (mx - ax0) / (ax1 - ax0)
    ry = cy - top(u)
    f.ellipse(mx, cy, 9, 4.2, ORANGE, 1.4)
    f.add('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1.3" stroke-dasharray="3 3"/>'
           % (mx + 9, cy, mx + 9, cy - ry + 3, ORANGE))
    f.tex(mx + 14, cy - ry / 2, "f(x)", ORANGE, 10.5, "start", True)
    # dx 与旋转箭头
    f.tex(pts_t[-1][0] - 4, cy + 30, "dx", ORANGE, 10.5, "end", True)
    f.arrow(mx + 26, cy - ry - 12, mx + 66, cy - ry + 10, ORANGE, 1.5, 14)
    f.tex(mx + 62, cy - ry - 12, "绕 x 轴", ORANGE, 10.5, "start")
    return f.render()


def shell_method():
    """柱壳法示意（俯视 + 侧视合在一张）"""
    f = Fig(300, 210, (0, 1), (0, 1), 12, 12, 12, 14)
    # 俯视：环
    cx, cy = 96, 104
    f.ellipse(cx, cy, 66, 30, SUB, 1.1, "4 4")
    f.ellipse(cx, cy, 40, 18, BLUE, 1.5)
    f.ellipse(cx, cy, 46, 21, ORANGE, 1.6)
    f.add('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1"/>'
           % (cx, cy, cx + 46, cy, ORANGE))
    f.tex(cx + 30, cy - 6, "x", ORANGE, 10.5, "middle", True)
    f.tex(cx + 12, cy + 34, "薄壳", ORANGE, 10.5, "start")
    # 侧视：圆柱壳
    f.add('<rect x="196" y="58" width="26" height="86" fill="%s" fill-opacity="0.14" stroke="%s" stroke-width="1.5"/>'
           % (BLUE, BLUE))
    f.ellipse(209, 58, 13, 5, BLUE, 1.4)
    f.ellipse(209, 144, 13, 5, BLUE, 1.4)
    f.tex(214, 168, "高 f(x)", SUB, 10, "middle")
    f.tex(214, 46, "厚 dx", ORANGE, 10, "middle")
    return f.render()


def arc_triangle():
    """弧微分三角形 dx / dy / ds"""
    f = Fig(280, 200, (0, 1), (0, 1), 16, 16, 14, 18)
    f.add('<path d="M30 150 Q90 40 250 96" fill="none" stroke="%s" stroke-width="2.4"/>' % BLUE)
    # 割线三角形
    f.add('<line x1="90" y1="112" x2="200" y2="150" stroke="%s" stroke-width="0"/>' % LINE)
    f.add('<line x1="90" y1="112" x2="200" y2="112" stroke="%s" stroke-width="1.2" stroke-dasharray="4 4"/>' % GREEN)
    f.add('<line x1="200" y1="112" x2="200" y2="150" stroke="%s" stroke-width="1.2" stroke-dasharray="4 4"/>' % ORANGE)
    f.add('<circle cx="90" cy="112" r="3" fill="%s"/>' % BLUE)
    f.add('<circle cx="200" cy="150" r="3" fill="%s"/>' % BLUE)
    f.tex(145, 128, "dx", GREEN, 11, "middle", True)
    f.tex(206, 132, "dy", ORANGE, 11, "start", True)
    f.tex(150, 148, "ds=√(dx²+dy²)", BLUE, 10.5, "middle", True)
    return f.render()


def cyclone_arch():
    """摆线一拱 + 面积"""
    a = 0.5
    f = Fig(320, 190, (-0.4, 2 * math.pi + 0.4), (-0.4, 1.9), 26, 12, 14, 26)
    f.axes(xtitle="x", ytitle="y")
    X = lambda t: a * (t - math.sin(t))
    Y = lambda t: a * (1 - math.cos(t))
    f.region(lambda u: Y(u), lambda u: 0, 0, 2 * math.pi)
    pts = [(f.X(X(t)), f.Y(Y(t))) for t in [2 * math.pi * i / 200 for i in range(201)]]
    f.add('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (poly_d(pts), BLUE))
    # 滚动圆
    import math as m
    cx, cy = f.X(a * math.pi), f.Y(a)
    f.ellipse(cx, cy, 46, 40, ORANGE, 1.3, "4 4")
    f.dot(a * math.pi, a, ORANGE, 2.6)
    f.tex(f.X(a * math.pi) + 8, f.Y(a) - 40, "2a", ORANGE, 10.5, "start", True)
    f.tex(f.X(0.2), f.Y(0) + 26, "O", SUB, 10.5)
    f.tex(f.X(2 * math.pi) - 8, f.Y(0) + 26, "2πa", SUB, 10.5, "end")
    return f.render()


def astroid(k=1.0, quarter=False, label_all=False):
    f = Fig(280, 250, (-1.25, 1.25), (-1.25, 1.25))
    f.axes(xtitle="x", ytitle="y")
    pts = []
    for i in range(241):
        t = 2 * math.pi * i / 240
        pts.append((f.X(math.cos(t) ** 3), f.Y(math.sin(t) ** 3)))
    f.add('<path d="%s" fill="%s" fill-opacity="0.08" stroke="%s" stroke-width="2.2"/>'
          % (poly_d(pts, True), BLUE, BLUE))
    if quarter:
        q = []
        for i in range(61):
            t = (math.pi / 2) * i / 60
            q.append((f.X(math.cos(t) ** 3), f.Y(math.sin(t) ** 3)))
        f.add('<path d="%s" fill="none" stroke="%s" stroke-width="3.4"/>' % (poly_d(q), ORANGE))
    if label_all:
        for t, txt, dx, dy, anch in (
                (0, "(a,0)", 6, -8, "start"),
                (math.pi / 2, "(0,a)", 6, -6, "start"),
                (math.pi, "(−a,0)", -6, -8, "end"),
                (3 * math.pi / 2, "(0,−a)", 6, 14, "start")):
            x, y = math.cos(t) ** 3, math.sin(t) ** 3
            f.dot(x, y, BLUE, 2.8)
            f.label(x, y, txt, dx=dx, dy=dy, size=9.5, anchor=anch)
    f.tex(f.X(0.55), f.Y(0.62), "x^(2/3)+y^(2/3)=a^(2/3)", SUB, 9.5, "start")
    return f.render()


def half_disc_line():
    """上半圆与直线：弓形面积"""
    f = Fig(280, 210, (-0.3, 2.4), (-0.3, 1.5))
    f.axes(xtitle="x", ytitle="y")
    up = lambda x: math.sqrt(max(0.0, 1 - (x - 1) ** 2))
    f.region(up, lambda x: x / math.sqrt(3), 0, 1.5)
    f.curve(up, 0, 2, BLUE)
    f.curve(lambda x: x / math.sqrt(3), 0, 2.2, GREEN)
    f.dot(0, 0, BLUE, 2.8)
    f.dot(1.5, 1.5 / math.sqrt(3), BLUE, 2.8)
    f.label(1.5, 1.5 / math.sqrt(3), "(3/2, √3/2)", dx=-4, dy=-8, size=9.5, anchor="end")
    f.dot(1, 0, SUB, 2.2)
    f.label(1, 0, "O₁", dy=15, size=9.5)
    f.tex(f.X(0.45), f.Y(0.95), "y=√(2x−x²)", BLUE, 9.5, "start", True)
    f.tex(f.X(1.75), f.Y(1.05), "y=x/√3", GREEN, 9.5, "start", True)
    return f.render()


def cardioid_and_circle():
    """ρ=3cosθ（圆）与 ρ=1+cosθ（心形线）的公共部分"""
    f = Fig(300, 250, (-2.1, 3.5), (-2.4, 2.4))
    f.axes(xtitle="x", ytitle="y")

    def polar_path(fn, t0, t1, n=160):
        pts = []
        for i in range(n + 1):
            th = t0 + (t1 - t0) * i / n
            r = fn(th)
            if r < 0:
                continue
            pts.append((f.X(r * math.cos(th)), f.Y(r * math.sin(th))))
        return pts

    # 圆 ρ=3cosθ：θ ∈ [-π/2, π/2]
    f.add('<path d="%s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="5 4"/>'
          % (poly_d(polar_path(lambda th: 3 * math.cos(th), -math.pi / 2, math.pi / 2)), SUB))
    # 心形线 ρ=1+cosθ
    f.add('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>'
          % (poly_d(polar_path(lambda th: 1 + math.cos(th), -math.pi, math.pi)), BLUE))
    # 公共部分填充：按角度切楔形逐块填（里层曲线：|θ|≤π/3 心形线，其余圆）
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
              % (poly_d(pts, True), ORANGE))
    # 交点
    for th in (math.pi / 3, -math.pi / 3):
        r = 3 * math.cos(th)
        f.dot(r * math.cos(th), r * math.sin(th), ORANGE, 3)
    f.label(1.5 * math.cos(math.pi / 3), 1.5 * math.sin(math.pi / 3), "θ=π/3",
            dx=4, dy=-8, size=9.5, anchor="start")
    f.tex(f.X(2.35), f.Y(1.15), "ρ=3cosθ", SUB, 9.5, "middle", True)
    f.tex(f.X(0.9), f.Y(-1.75), "ρ=1+cosθ", BLUE, 9.5, "middle", True)
    return f.render()


def two_circles_polar():
    """两圆公共部分：ρ=√3a 与 ρ=2a cosθ"""
    f = Fig(300, 240, (-2.0, 3.4), (-1.9, 1.9))
    f.axes(xtitle="x", ytitle="y")
    # 大圆（中心原点）
    f.curve(lambda x: math.sqrt(max(0.0, 3 - x * x)), -1.74, 1.74, SUB, 1.3, 200, "4 4")
    f.curve(lambda x: -math.sqrt(max(0.0, 3 - x * x)), -1.74, 1.74, SUB, 1.3, 200, "4 4")
    # 小圆（心 (a,0)，半径 a）
    up2 = lambda x: math.sqrt(max(0.0, 1 - (x - 1) ** 2))
    dn2 = lambda x: -math.sqrt(max(0.0, 1 - (x - 1) ** 2))
    f.curve(up2, 0, 2, BLUE, 2.2)
    f.curve(dn2, 0, 2, BLUE, 2.2)
    # 公共区域：用多边形近似填充
    import math as m
    poly = []
    for i in range(0, 121):
        th = -m.pi / 6 + (m.pi / 3) * i / 120
        poly.append((f.X((1 + math.cos(th)) * math.cos(th)), f.Y((1 + math.cos(th)) * math.sin(th))))
    for i in range(0, 121):
        th = m.pi / 6 + (m.pi / 3) * i / 120
        r = 3 ** 0.5
        poly.append((f.X(r * math.cos(th)), f.Y(r * math.sin(th))))
    f.add('<path d="%s" fill="%s" fill-opacity="0.22" stroke="none"/>'
          % (poly_d(poly, True), ORANGE))
    f.dot(math.sqrt(3) / 2, 0.5, ORANGE, 2.8)
    f.label(math.sqrt(3) / 2, 0.5, "θ=π/6", dx=2, dy=-8, size=9.5, anchor="start")
    f.tex(f.X(1.0), f.Y(-1.35), "ρ=2a cosθ", BLUE, 9.5, "middle", True)
    f.tex(f.X(-1.55), f.Y(1.55), "ρ=√3a", SUB, 9.5, "middle", True)
    return f.render()


def spring_work():
    """弹簧 F-s 图：功=三角形面积"""
    f = Fig(290, 200, (-0.006, 0.135), (-2, 58))
    f.axes(xtitle="s(m)", ytitle="F(N)")
    f.region(lambda s: 500 * s, lambda s: 0, 0, 0.1, ORANGE, "0.2")
    f.curve(lambda s: 500 * s, 0, 0.112, BLUE, 2.2)
    f.vline(0.1, 0, 50, ORANGE, 1.2, "4 3")
    f.hline(50, 0, 0.1, ORANGE, 1.2, "4 3")
    f.dot(0.1, 50, ORANGE, 3)
    f.label(0.1, 50, "(0.1, 50)", dx=4, dy=-9, size=10, anchor="end")
    f.tex(f.X(0.052), f.Y(14), "W=∫F ds", ORANGE, 10.5, "middle")
    return f.render()


def pool_work():
    """锥形水池：水层 dy 与提升距离"""
    f = Fig(300, 230, (0, 1), (0, 1), 24, 24, 14, 16)
    # 锥形剖面（顶宽 20，深 15）
    f.add('<path d="M60 40 L220 40 L140 196 Z" fill="%s" fill-opacity="0.08" stroke="%s" stroke-width="1.8"/>'
           % (BLUE, BLUE))
    # 水面
    f.add('<line x1="52" y1="40" x2="228" y2="40" stroke="%s" stroke-width="1.6"/>' % GREEN)
    f.tex(230, 44, "水面 (y=15)", GREEN, 10, "start")
    # 水层
    y1, y2 = 132, 142
    # 该高度处半宽：顶半宽 80，底 0，深度 0→156
    def halfw(py):
        return 80 * (1 - (py - 40) / 156.0)

    f.add('<path d="M%s %s L%s %s L%s %s L%s %s Z" fill="%s" fill-opacity="0.35" stroke="%s" stroke-width="1.1"/>'
           % (_fmt(140 - halfw(y1)), y1, _fmt(140 + halfw(y1)), y1,
              _fmt(140 + halfw(y2)), y2, _fmt(140 - halfw(y2)), y2, ORANGE, ORANGE))
    f.tex(140 + halfw(y1) + 8, y1 + 4, "dy", ORANGE, 10.5, "start", True)
    f.tex(140 + halfw(y1) // 2, y1 - 10, "πr²(y)dy", ORANGE, 9.5, "middle")
    # 提升箭头
    f.arrow(96, 132, 96, 54, RED, 1.6, 0)
    f.tex(88, 96, "15−y", RED, 10.5, "end")
    f.tex(140, 214, "深 15 m，口半径 10 m", SUB, 10, "middle")
    return f.render()


def triangle_pressure(apex_down=False, top_depth=None, depth_all=None):
    """等腰三角薄板压力图。
    apex_down=True：顶在下、底与水面相齐（test-6 第四题）
    apex_down=False：顶在上、底在下、顶离水面 top_depth（作业册 6.3 第 3 题）
    """
    f = Fig(290, 215, (0, 1), (0, 1), 34, 26, 14, 18)
    f.add('<line x1="18" y1="42" x2="266" y2="42" stroke="%s" stroke-width="1.6"/>' % GREEN)
    f.tex(250, 36, "水面", GREEN, 10, "end")
    top = 42
    if apex_down:
        # 底边在水面，顶点在下方 h=120
        bx1, bx2, apex_y = 62, 208, 168
        f.add('<path d="M%d %d L%d %d L%d %d Z" fill="%s" fill-opacity="0.12" stroke="%s" stroke-width="1.8"/>'
              % (bx1, top, bx2, top, 135, apex_y, BLUE, BLUE))
        f.tex(135, top - 8, "底 b（与水面相齐）", SUB, 9.5, "middle")
        f.tex(135, apex_y + 22, "顶在下", SUB, 9.5, "middle")
        yy = 108
        hw = (bx2 - bx1) / 2.0 * (yy - top) / (apex_y - top)
        f.add('<line x1="%s" y1="%d" x2="%s" y2="%d" stroke="%s" stroke-width="3"/>'
              % (_fmt(135 - hw), yy, _fmt(135 + hw), yy, ORANGE))
        f.tex(135 + hw + 6, yy + 4, "w(y)", ORANGE, 10, "start")
        f.add('<line x1="30" y1="%d" x2="30" y2="%d" stroke="%s" stroke-width="1" stroke-dasharray="4 3"/>'
              % (top, apex_y, SUB))
        f.tex(24, (top + apex_y) / 2, "a", SUB, 10, "end")
    else:
        # 顶在水下 3，底在下（宽 8）
        apex_y = top + 34
        bot_y = 178
        f.add('<path d="M135 %d L62 %d L208 %d Z" fill="%s" fill-opacity="0.12" stroke="%s" stroke-width="1.8"/>'
              % (apex_y, bot_y, bot_y, BLUE, BLUE))
        f.tex(135, bot_y + 20, "底 8 cm（在下）", SUB, 9.5, "middle")
        f.tex(142, apex_y - 8, "顶（在上）", SUB, 9.5, "start")
        f.add('<line x1="30" y1="%d" x2="30" y2="%d" stroke="%s" stroke-width="1" stroke-dasharray="4 3"/>'
              % (top, apex_y, SUB))
        f.tex(24, (top + apex_y) / 2 + 4, "3", SUB, 10, "end")
        f.add('<line x1="30" y1="%d" x2="30" y2="%d" stroke="%s" stroke-width="1" stroke-dasharray="4 3"/>'
              % (apex_y, bot_y, SUB))
        f.tex(24, (apex_y + bot_y) / 2, "6 cm", SUB, 10, "end")
        yy = 148
        hw = (208 - 62) / 2.0 * (yy - apex_y) / (bot_y - apex_y)
        f.add('<line x1="%s" y1="%d" x2="%s" y2="%d" stroke="%s" stroke-width="3"/>'
              % (_fmt(135 - hw), yy, _fmt(135 + hw), yy, ORANGE))
        f.tex(135 + hw + 6, yy + 4, "w(y)", ORANGE, 10, "start")
    return f.render()


def triangle_old():
    """三角形薄板：顶在上，底与水面相齐"""
    f = Fig(280, 210, (0, 1), (0, 1), 30, 24, 14, 18)
    f.add('<line x1="20" y1="40" x2="258" y2="40" stroke="%s" stroke-width="1.6"/>' % GREEN)
    f.tex(250, 34, "水面", GREEN, 10, "end")
    # 三角形：底 y=3 宽 8，底边 y=9 顶点
    f.add('<path d="M60 70 L200 70 L130 190 Z" fill="%s" fill-opacity="0.10" stroke="%s" stroke-width="1.8"/>'
           % (BLUE, BLUE))
    # 深度标注
    f.add('<line x1="36" y1="70" x2="36" y2="190" stroke="%s" stroke-width="1" stroke-dasharray="4 3"/>' % SUB)
    f.tex(30, 132, "6 cm", SUB, 10, "end")
    f.add('<line x1="30" y1="40" x2="30" y2="70" stroke="%s" stroke-width="1" stroke-dasharray="3 3"/>' % SUB)
    f.tex(24, 58, "3", SUB, 10, "end")
    # 窄条
    yy = 120
    hw = 70 * (yy - 70) / 120.0
    f.add('<line x1="%s" y1="%d" x2="%s" y2="%d" stroke="%s" stroke-width="3"/>'
           % (_fmt(130 - hw), yy, _fmt(130 + hw), yy, ORANGE))
    f.tex(130 + hw + 6, yy + 4, "w(y)", ORANGE, 10, "start")
    f.tex(130, 66, "8 cm", SUB, 10, "middle")
    return f.render()


def section_solid():
    """以 y²=2x 与 x=2 为底、垂直于 x 轴的截面为等边三角形"""
    f = Fig(300, 230, (0, 1), (0, 1), 34, 20, 16, 26)
    # 底：抛物线 y²=2x 与 x=2 围成的区域（俯视）
    f.add('<line x1="52" y1="112" x2="266" y2="112" stroke="%s" stroke-width="1.1"/>' % LINE)
    f.tex(270, 116, "x", SUB, 10.5, "start", True)
    f.add('<path d="M52 112 Q120 60 166 74 Q212 88 246 112 Z" fill="%s" fill-opacity="0.10" stroke="%s" stroke-width="1.5"/>'
          % (BLUE, BLUE))
    f.add('<line x1="246" y1="74" x2="246" y2="150" stroke="%s" stroke-width="1.1" stroke-dasharray="4 3"/>' % SUB)
    f.tex(250, 164, "x=2", SUB, 9.5, "start")
    # 一个竖起的截面（等边三角形），底边在 x 处
    bx = 152
    half = 30
    f.add('<path d="M%d 96 L%d 96 L%d 40 Z" fill="%s" fill-opacity="0.35" stroke="%s" stroke-width="1.5"/>'
          % (bx - half, bx + half, bx, ORANGE, ORANGE))
    f.add('<line x1="%d" y1="96" x2="%d" y2="96" stroke="%s" stroke-width="2.4"/>' % (bx - half, bx + half, ORANGE))
    f.tex(bx, 30, "截面：等边三角形", ORANGE, 10, "middle")
    f.tex(bx + half + 4, 70, "边长 = 2√(2x)", ORANGE, 9.5, "start")
    f.tex(96, 132, "底：y²=2x 与 x=2", BLUE, 10, "start", True)
    f.tex(bx, 112 + 16, "x", SUB, 9.5, "middle")
    # 底面抛物线（俯视感）
    f.add('<path d="M60 120 Q150 40 240 120 Q150 200 60 120 Z" fill="%s" fill-opacity="0.10" stroke="%s" stroke-width="1.6"/>'
           % (BLUE, BLUE))
    f.add('<line x1="60" y1="120" x2="252" y2="120" stroke="%s" stroke-width="1.1"/>' % LINE)
    f.tex(258, 124, "x", SUB, 10.5, "start", True)
    # 一个截面三角形
    f.add('<path d="M150 96 L182 140 L118 140 Z" fill="%s" fill-opacity="0.3" stroke="%s" stroke-width="1.4"/>'
           % (ORANGE, ORANGE))
    f.tex(150, 88, "等边三角形截面", ORANGE, 9.5, "middle")
    f.tex(150, 156, "底：y²=2x", BLUE, 10, "middle", True)
    f.tex(236, 132, "x=2", SUB, 9.5, "start")
    return f.render()


def piecewise_region():
    """y=1/x 与 y=4x 分段区域"""
    f = Fig(300, 220, (-0.1, 2.3), (-0.2, 2.6))
    f.axes(xtitle="x", ytitle="y")
    f.region(lambda x: 4 * x, lambda x: 0, 0, 0.5, BLUE, "0.16")
    f.region(lambda x: 1 / x, lambda x: 0, 0.5, 2, GREEN, "0.16")
    f.curve(lambda x: 4 * x, 0, 0.72, BLUE)
    f.curve(lambda x: 1 / x, 0.42, 2.2, GREEN)
    f.vline(0.5, 0, 2, ORANGE, 1.3, "4 3")
    f.vline(2.0, 0, 0.5, ORANGE, 1.3, "4 3")
    f.dot(0.5, 2, BLUE, 3)
    f.label(0.5, 2, "", dy=-6)
    f.tex(f.X(0.62), f.Y(2.1), "(1/2, 2)", BLUE, 9.5, "start")
    f.tex(f.X(0.2), f.Y(1.3), "y=4x", BLUE, 10, "middle", True)
    f.tex(f.X(1.45), f.Y(0.72), "y=1/x", GREEN, 10, "middle", True)
    f.tex(f.X(1.0), f.Y(0) + 22, "1/2", SUB, 9.5)
    f.tex(f.X(2.0), f.Y(0) + 22, "2", SUB, 9.5)
    return f.render()


def curve_arclen():
    """x = y²/4 − (1/2)ln y 的弧"""
    f = Fig(280, 220, (-0.3, 2.4), (-0.2, 2.2))
    f.axes(xtitle="y", ytitle="x")
    def g(y):
        return y * y / 4 - 0.5 * math.log(y)
    # 这里以 y 为横轴画：x=f(y)
    f.region(g, lambda y: 0, 1, math.e, ORANGE, "0.10")
    f.curve(g, 0.42, 2.6, BLUE, 2.3)
    f.vline(1, 0, g(1), SUB, 1.2, "4 3")
    f.vline(math.e, 0, g(math.e), SUB, 1.2, "4 3")
    f.label(1, 0, "1", dy=16, size=10)
    f.label(math.e, 0, "e", dy=16, size=10)
    f.tex(f.X(1.5), f.Y(g(1.5)) - 12, "x=y²/4−(1/2)ln y", BLUE, 9.5, "middle", True)
    return f.render()


def ellipse_revolve_talk():
    """椭圆两向旋转体对比"""
    f = Fig(320, 180, (0, 1), (0, 1), 14, 14, 16, 18)
    # 左：绕 x
    f.ellipse(84, 84, 52, 28, BLUE, 1.6, None, False)
    f.add('<line x1="18" y1="84" x2="152" y2="84" stroke="%s" stroke-width="1"/>' % LINE)
    f.tex(150, 100, "V₁ 绕 x", BLUE, 10.5, "end")
    # 右：绕 y
    f.ellipse(236, 84, 28, 52, GREEN, 1.6, None, False)
    f.add('<line x1="236" y1="18" x2="236" y2="150" stroke="%s" stroke-width="1"/>' % LINE)
    f.tex(268, 96, "V₂ 绕 y", GREEN, 10.5, "start")
    f.tex(160, 156, "a>b ⇒ V₂>V₁", SUB, 10.5, "middle")
    return f.render()


FIGS = {
    "math/6-1": {"c3": area_between_two_curves},
    "math/6-2": {"c1": area_x_x2, "c2": revolve_x_axis, "c5": lambda: astroid(label_all=True), "c6": cyclone_arch},
    "math/6-3": {"c2": spring_work, "c3": pool_work},
    "math/hwb-6-1": {"q1": cyclone_arch, "q3": lambda: astroid(quarter=True), "q5": half_disc_line,
                       "q6": cardioid_and_circle},
    "math/hwb-6-2a": {"q1": revolve_x_axis, "q5": section_solid, "q6": piecewise_region},
    "math/hwb-6-2b": {"q3": lambda: astroid(quarter=True), "q4": curve_arclen},
    "math/hwb-6-3": {"q1": spring_work, "q2": pool_work,
                      "q3": lambda: triangle_pressure(apex_down=False)},
    "math/test-6": {"q2": revolve_x_axis, "q7": shell_method, "q8": piecewise_region,
                     "q9": lambda: triangle_pressure(apex_down=True),
                     "q10": two_circles_polar, "q6": ellipse_revolve_talk},
}


def main():
    total = 0
    for lid, cards in FIGS.items():
        p = os.path.join(LESSONS, lid.replace("/", "_") + ".json")
        d = json.load(io.open(p, encoding="utf-8"))
        by_id = {c["id"]: c for c in d["cards"]}
        for cid, maker in cards.items():
            c = by_id.get(cid)
            if not c:
                print("!! 缺卡片", lid, cid)
                continue
            svg = maker()
            c["svg"] = svg
            total += 1
        json.dump(d, io.open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print("注入", lid, len(cards), "张")
    print("共", total, "张")


if __name__ == "__main__":
    main()
