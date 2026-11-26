# -*- coding: utf-8 -*-
"""修 inject_figs_ch6.py 里拼错的字符串"""
import io

P = r"C:/Users/chong/Documents/studyhub/tools/inject_figs_ch6.py"
s = io.open(P, encoding="utf-8").read()


def sub(old, new, tag):
    global s
    n = s.count(old)
    assert n == 1, "%s 命中 %d" % (tag, n)
    s = s.replace(old, new)
    print("  ok", tag)


# 加一个拼 path 的帮助函数
sub("""LESSONS = r"C:/Users/chong/Documents/studyhub/content/lessons"
""",
    """LESSONS = r"C:/Users/chong/Documents/studyhub/content/lessons"


def poly_d(pts, close=False):
    d = "M" + " L".join("%s %s" % (_fmt(p[0]), _fmt(p[1])) for p in pts)
    return d + (" Z" if close else "")
""", "poly_d")

# 极坐标：两条弧
sub("""    f.add('<path d="M" + " L".join("%s %s" % (_fmt(p[0]), _fmt(p[1])) for p in arc) + '
          'fill="none" stroke="%s" stroke-width="2"/>' % BLUE)""",
    """    f.add('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (poly_d(arc), BLUE))""",
    "polar arc")

sub("""    f.add('<path d="M" + " L".join("%s %s" % (_fmt(p[0]), _fmt(p[1])) for p in arc2) + '
          'fill="none" stroke="%s" stroke-width="1.4" stroke-dasharray="4 4"/>' % GREEN)""",
    """    f.add('<path d="%s" fill="none" stroke="%s" stroke-width="1.4" stroke-dasharray="4 4"/>'
          % (poly_d(arc2), GREEN))""",
    "polar arc2")

# 旋转体：两条母线
sub("""    f.add('<path d="M" + " L".join("%s %s" % (_fmt(p[0]), _fmt(p[1])) for p in pts_t) +
          ' fill="none" stroke="%s" stroke-width="2.2"/>' % BLUE)""",
    """    f.add('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (poly_d(pts_t), BLUE))""",
    "revolve 上母线")

sub("""    f.add('<path d="M" + " L".join("%s %s" % (_fmt(p[0]), _fmt(p[1])) for p in pts_b) +
          ' fill="none" stroke="%s" stroke-width="1.5"%s/>' % (BLUE, dashes))""",
    """    f.add('<path d="%s" fill="none" stroke="%s" stroke-width="1.5"%s/>'
          % (poly_d(pts_b), BLUE, dashes))""",
    "revolve 下母线")

# 摆线
sub("""    f.add('<path d="M" + " L".join("%s %s" % (_fmt(p[0]), _fmt(p[1])) for p in pts) +
          ' fill="none" stroke="%s" stroke-width="2.4"/>' % BLUE)""",
    """    f.add('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (poly_d(pts), BLUE))""",
    "cycloid")

# 星形线
sub("""    f.add('<path d="M" + " L".join("%s %s" % (_fmt(p[0]), _fmt(p[1])) for p in pts) +
          ' fill="%s" fill-opacity="0.08" stroke="%s" stroke-width="2.2"/>' % (BLUE, BLUE))""",
    """    f.add('<path d="%s" fill="%s" fill-opacity="0.08" stroke="%s" stroke-width="2.2"/>'
          % (poly_d(pts, True), BLUE, BLUE))""",
    "astroid 外形")

sub("""        f.add('<path d="M" + " L".join("%s %s" % (_fmt(p[0]), _fmt(p[1])) for p in q) +
              ' fill="none" stroke="%s" stroke-width="3.4"/>' % ORANGE)""",
    """        f.add('<path d="%s" fill="none" stroke="%s" stroke-width="3.4"/>' % (poly_d(q), ORANGE))""",
    "astroid 第一象限")

# 两圆公共部分
sub("""    f.add('<path d="M" + " L".join("%s %s" % (_fmt(p[0]), _fmt(p[1])) for p in poly) +
          ' Z" fill="%s" fill-opacity="0.22" stroke="none"/>' % ORANGE)""",
    """    f.add('<path d="%s" fill="%s" fill-opacity="0.22" stroke="none"/>'
          % (poly_d(poly, True), ORANGE))""",
    "two circles")

io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("written")
