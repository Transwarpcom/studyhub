# -*- coding: utf-8 -*-
"""极简 SVG 绘图库：真坐标映射 + 区域填充 + 标注 + 等轴测 3D"""

import math

BLUE = "#2563eb"
RED = "#dc2626"
GREEN = "#16a34a"
ORANGE = "#ea8a1f"
PURPLE = "#7c3aed"
LINE = "var(--line)"
SUB = "var(--sub)"


def _fmt(v):
    return ("%.2f" % v).rstrip("0").rstrip(".")


class Fig:
    """数学坐标 → 像素坐标的绘图器（SVG y 向下）"""

    def __init__(self, w=320, h=240, xr=(0.0, 1.0), yr=(0.0, 1.0),
                 pl=38, pr=16, pt=16, pb=26):
        self.w, self.h = w, h
        self.x0, self.x1 = xr
        self.y0, self.y1 = yr
        self.pl, self.pr, self.pt, self.pb = pl, pr, pt, pb
        self.iw = w - pl - pr
        self.ih = h - pt - pb
        self.parts = []

    # ---------- 坐标 ----------
    def X(self, x):
        return self.pl + (x - self.x0) / (self.x1 - self.x0) * self.iw

    def Y(self, y):
        return self.pt + (self.y1 - y) / (self.y1 - self.y0) * self.ih

    # ---------- 基础图形 ----------
    def add(self, s):
        self.parts.append(s)

    def axes(self, xticks=None, yticks=None, xtitle="x", ytitle="y", origin=True):
        x0, y0 = self.X(self.x0), self.Y(0)
        y0c = self.Y(0) if self.y0 <= 0 <= self.y1 else self.pt + self.ih
        # x 轴
        self.add('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="1.1"/>'
                 % (_fmt(self.pl - 6), _fmt(y0c), _fmt(self.pl + self.iw + 4), _fmt(y0c), LINE))
        self.add(self._tri(self.pl + self.iw + 8, y0c, 0, LINE))
        # y 轴
        x0c = self.X(0) if self.x0 <= 0 <= self.x1 else self.pl
        self.add('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="1.1"/>'
                 % (_fmt(x0c), _fmt(self.pt + self.ih + 6), _fmt(x0c), _fmt(self.pt - 2), LINE))
        self.add(self._tri(x0c, self.pt - 6, 270, LINE))
        if origin and self.x0 <= 0 and self.y0 <= 0:
            self.add('<text x="%s" y="%s" font-size="11" fill="%s">O</text>'
                     % (_fmt(x0c - 11), _fmt(y0c + 13), SUB))
        if xtitle:
            self.add('<text x="%s" y="%s" font-size="11.5" font-style="italic" fill="%s">%s</text>'
                     % (_fmt(self.pl + self.iw - 2), _fmt(y0c + 15), SUB, xtitle))
        if ytitle:
            self.add('<text x="%s" y="%s" font-size="11.5" font-style="italic" fill="%s">%s</text>'
                     % (_fmt(x0c + 6), _fmt(self.pt + 2), SUB, ytitle))

    def _tri(self, x, y, deg, color):
        a = math.radians(deg)
        s = 5.0
        p1 = (x + s * math.cos(a), y + s * math.sin(a))
        p2 = (x + s * math.cos(a + 2.6), y + s * math.sin(a + 2.6))
        p3 = (x + s * math.cos(a - 2.6), y + s * math.sin(a - 2.6))
        return '<path d="M%s %s L%s %s L%s %s Z" fill="%s"/>' % (
            _fmt(p1[0]), _fmt(p1[1]), _fmt(p2[0]), _fmt(p2[1]),
            _fmt(p3[0]), _fmt(p3[1]), color)

    def curve(self, f, a, b, color=BLUE, width=2.2, n=180, dash=None, closed=False):
        pts = []
        for i in range(n + 1):
            x = a + (b - a) * i / n
            try:
                y = f(x)
            except Exception:
                continue
            if y is None or not (self.y0 - 3 <= y <= self.y1 + 3):
                continue
            pts.append((self.X(x), self.Y(y)))
        if not pts:
            return
        d = "M" + " L".join("%s %s" % (_fmt(p[0]), _fmt(p[1])) for p in pts)
        dash_attr = ' stroke-dasharray="%s"' % dash if dash else ""
        self.add('<path d="%s" fill="none" stroke="%s" stroke-width="%s"%s stroke-linejoin="round"/>'
                 % (d, color, width, dash_attr))

    def region(self, f_up, f_dn, a, b, color=BLUE, opacity="0.14", n=160):
        up, dn = [], []
        for i in range(n + 1):
            x = a + (b - a) * i / n
            up.append((self.X(x), self.Y(f_up(x))))
            dn.append((self.X(x), self.Y(f_dn(x))))
        pts = up + dn[::-1]
        d = "M" + " L".join("%s %s" % (_fmt(p[0]), _fmt(p[1])) for p in pts) + " Z"
        self.add('<path d="%s" fill="%s" fill-opacity="%s" stroke="none"/>' % (d, color, opacity))

    def band(self, x1, x2, ytop, ybot, color=BLUE, opacity="0.3"):
        xa, xb = self.X(x1), self.X(x2)
        ya, yb = self.Y(ytop), self.Y(ybot)
        self.add('<rect x="%s" y="%s" width="%s" height="%s" fill="%s" fill-opacity="%s" stroke="none"/>'
                 % (_fmt(xa), _fmt(min(ya, yb)), _fmt(abs(xb - xa)), _fmt(abs(yb - ya)), color, opacity))

    def vline(self, x, y1, y2, color=SUB, width=1.1, dash="4 4"):
        dash_attr = ' stroke-dasharray="%s"' % dash if dash else ""
        self.add('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s"%s/>'
                 % (_fmt(self.X(x)), _fmt(self.Y(y1)), _fmt(self.X(x)), _fmt(self.Y(y2)),
                    color, width, dash_attr))

    def hline(self, y, x1, x2, color=SUB, width=1.1, dash="4 4"):
        dash_attr = ' stroke-dasharray="%s"' % dash if dash else ""
        self.add('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s"%s/>'
                 % (_fmt(self.X(x1)), _fmt(self.Y(y)), _fmt(self.X(x2)), _fmt(self.Y(y)),
                    color, width, dash_attr))

    def seg(self, x1, y1, x2, y2, color=LINE, width=1.2, dash=None):
        dash_attr = ' stroke-dasharray="%s"' % dash if dash else ""
        self.add('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s"%s/>'
                 % (_fmt(self.X(x1)), _fmt(self.Y(y1)), _fmt(self.X(x2)), _fmt(self.Y(y2)),
                    color, width, dash_attr))

    def dot(self, x, y, color=BLUE, r=3.2):
        self.add('<circle cx="%s" cy="%s" r="%s" fill="%s"/>'
                 % (_fmt(self.X(x)), _fmt(self.Y(y)), r, color))

    def label(self, x, y, text, dx=0, dy=-8, color=SUB, size=11, anchor="middle", style=""):
        self.add('<text x="%s" y="%s" font-size="%s" fill="%s" text-anchor="%s" style="%s">%s</text>'
                 % (_fmt(self.X(x) + dx), _fmt(self.Y(y) + dy), size, color, anchor, style, text))

    def tex(self, px, py, text, color=SUB, size=11, anchor="middle", italic=False):
        st = "font-style:italic;" if italic else ""
        self.add('<text x="%s" y="%s" font-size="%s" fill="%s" text-anchor="%s" style="%s">%s</text>'
                 % (_fmt(px), _fmt(py), size, color, anchor, st, text))

    def arrow(self, x1, y1, x2, y2, color=ORANGE, width=1.6, curve=0.0):
        """曲线箭头：curve 为控制点偏移（px），用来画旋转方向"""
        cxp = (x1 + x2) / 2 + curve
        cyp = (y1 + y2) / 2 - abs(curve) * 0.15
        self.add('<path d="M%s %s Q%s %s %s %s" fill="none" stroke="%s" stroke-width="%s"/>'
                 % (_fmt(x1), _fmt(y1), _fmt(cxp), _fmt(cyp), _fmt(x2), _fmt(y2), color, width))
        ang = math.degrees(math.atan2(y2 - cyp, x2 - cxp))
        self.add(self._tri(x2, y2, ang, color))

    def ellipse(self, cx, cy, rx, ry, color=BLUE, width=1.6, dash=None, fill=None, opacity="0.1"):
        dash_attr = ' stroke-dasharray="%s"' % dash if dash else ""
        f = ' fill="%s" fill-opacity="%s"' % (color, opacity) if fill else ' fill="none"'
        self.add('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" stroke="%s" stroke-width="%s"%s%s/>'
                 % (_fmt(cx), _fmt(cy), _fmt(rx), _fmt(ry), color, width, dash_attr, f))

    def render(self):
        return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" '
                'font-family="-apple-system, Helvetica, serif">%s</svg>'
                % (self.w, self.h, self.w, "".join(self.parts)))
