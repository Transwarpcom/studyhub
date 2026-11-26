# -*- coding: utf-8 -*-
"""按预览逐张修正：星形线标签 / 心形线版本 / 三角板两向 / 弹簧留边 / 截面正视"""
import io

P = r"C:/Users/chong/Documents/studyhub/tools/inject_figs_ch6.py"
s = io.open(P, encoding="utf-8").read()


def sub(old, new, tag):
    global s
    n = s.count(old)
    assert n == 1, "%s 命中 %d" % (tag, n)
    s = s.replace(old, new)
    print("  ok", tag)


# ---------- 1. 弹簧：加宽横轴，标注右对齐 ----------
sub("""    f = Fig(280, 200, (-0.05, 0.12), (-1, 55))""",
    """    f = Fig(290, 200, (-0.006, 0.135), (-2, 58))""", "弹簧坐标")
sub("""    f.label(0.1, 50, "  (0.1, 50)", dx=6, dy=-8, size=10, anchor="start")""",
    """    f.label(0.1, 50, "(0.1, 50)", dx=4, dy=-9, size=10, anchor="end")""", "弹簧标注")

# ---------- 2. 星形线：四个顶点写成坐标 ----------
sub("""    if label_all:
        for t, tx, ty in ((0, "a", 0), (math.pi / 2, "0", "a"), (math.pi, "-a", 0), (3 * math.pi / 2, "0", "-a")):
            f.dot(math.cos(t) ** 3, math.sin(t) ** 3, BLUE, 2.8)
            f.label(math.cos(t) ** 3, math.sin(t) ** 3, tx if tx else "", dx=10, dy=-8, size=10)""",
    """    if label_all:
        for t, txt, dx, dy, anch in (
                (0, "(a,0)", 6, -8, "start"),
                (math.pi / 2, "(0,a)", 6, -6, "start"),
                (math.pi, "(−a,0)", -6, -8, "end"),
                (3 * math.pi / 2, "(0,−a)", 6, 14, "start")):
            x, y = math.cos(t) ** 3, math.sin(t) ** 3
            f.dot(x, y, BLUE, 2.8)
            f.label(x, y, txt, dx=dx, dy=dy, size=9.5, anchor=anch)""", "星形线顶点")

# ---------- 3. 心形线与圆（ρ=3cosθ / ρ=1+cosθ） ----------
sub("""def two_circles_polar():""",
    """def cardioid_and_circle():
    \"\"\"ρ=3cosθ（圆）与 ρ=1+cosθ（心形线）的公共部分\"\"\"
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
    # 公共部分填充：|θ|≤π/3 取 1+cosθ；π/3<|θ|<π/2 取 3cosθ
    poly = polar_path(lambda th: 1 + math.cos(th), -math.pi / 3, math.pi / 3, 90)
    poly += polar_path(lambda th: 3 * math.cos(th), math.pi / 3, math.pi / 2, 45)
    poly += polar_path(lambda th: 3 * math.cos(th), -math.pi / 2, -math.pi / 3, 45)
    f.add('<path d="%s" fill="%s" fill-opacity="0.2" stroke="none"/>' % (poly_d(poly, True), ORANGE))
    # 交点
    for th in (math.pi / 3, -math.pi / 3):
        r = 3 * math.cos(th)
        f.dot(r * math.cos(th), r * math.sin(th), ORANGE, 3)
    f.label(1.5 * math.cos(math.pi / 3), 1.5 * math.sin(math.pi / 3), "θ=π/3",
            dx=4, dy=-8, size=9.5, anchor="start")
    f.tex(f.X(2.35), f.Y(1.15), "ρ=3cosθ", SUB, 9.5, "middle", True)
    f.tex(f.X(0.9), f.Y(-1.75), "ρ=1+cosθ", BLUE, 9.5, "middle", True)
    return f.render()


def two_circles_polar():""", "心形线函数")

# ---------- 4. 三角板：两个方向 ----------
sub("""def triangle_pressure():""",
    """def triangle_pressure(apex_down=False, top_depth=None, depth_all=None):
    \"\"\"等腰三角薄板压力图。
    apex_down=True：顶在下、底与水面相齐（test-6 第四题）
    apex_down=False：顶在上、底在下、顶离水面 top_depth（作业册 6.3 第 3 题）
    \"\"\"
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


def triangle_old():""", "三角板两向")

# ---------- 5. 等边三角形截面：改成侧视更清楚 ----------
sub("""def section_solid():
    \"\"\"3D：以 y²=2x 与 x=2 为底、等边三角形截面\"\"\"
    f = Fig(300, 220, (0, 1), (0, 1), 30, 24, 16, 18)""",
    """def section_solid():
    \"\"\"以 y²=2x 与 x=2 为底、垂直于 x 轴的截面为等边三角形\"\"\"
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
    f.tex(bx, 112 + 16, "x", SUB, 9.5, "middle")""", "截面侧视")

# ---------- 6. 映射表更新 ----------
sub("""    "math/hwb-6-1": {"q1": cyclone_arch, "q3": lambda: astroid(quarter=True), "q5": half_disc_line,
                       "q6": two_circles_polar},""",
    """    "math/hwb-6-1": {"q1": cyclone_arch, "q3": lambda: astroid(quarter=True), "q5": half_disc_line,
                       "q6": cardioid_and_circle},""", "hwb-6-1 映射")

sub("""    "math/hwb-6-3": {"q1": spring_work, "q2": pool_work, "q3": triangle_pressure},""",
    """    "math/hwb-6-3": {"q1": spring_work, "q2": pool_work,
                      "q3": lambda: triangle_pressure(apex_down=False)},""", "hwb-6-3 映射")

sub("""    "math/test-6": {"q2": revolve_x_axis, "q7": shell_method, "q8": piecewise_region,
                     "q9": triangle_pressure, "q10": two_circles_polar, "q6": ellipse_revolve_talk},""",
    """    "math/test-6": {"q2": revolve_x_axis, "q7": shell_method, "q8": piecewise_region,
                     "q9": lambda: triangle_pressure(apex_down=True),
                     "q10": two_circles_polar, "q6": ellipse_revolve_talk},""", "test-6 映射")

io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("written")
