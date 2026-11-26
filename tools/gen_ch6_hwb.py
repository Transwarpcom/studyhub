# -*- coding: utf-8 -*-
"""第六章 作业册（按老师分节）：6.1+面积 / 体积 / 弧长 / 物理应用"""
import json, os

OUT = r"C:/Users/chong/Documents/studyhub/content/lessons"


def save(d):
    p = os.path.join(OUT, d["id"].replace("/", "_") + ".json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    print("written", os.path.basename(p), len(d["cards"]) - 1, "题")


def mk(lid, title, subtitle, intro, items):
    cards = [{"id": "intro", "type": "lecture", "title": "本节考点", "md": intro}]
    for it in items:
        c = {"id": it[0], "type": it[1], "question": it[2], "explain": it[3]}
        if len(it) > 4 and it[4]:
            c.update(it[4])
        cards.append(c)
    return {"id": lid, "title": title, "subtitle": subtitle, "cards": cards}


# ============================================================
# 6.1 元素法 + 6.2 面积
# ============================================================
H61 = mk(
    "math/hwb-6-1",
    "作业册 · 6.1 元素法 + 6.2 面积",
    "摆线 · 星形线 · 极坐标公共部分 · 6 题",
    r"""## 本节考什么

1. **摆线一拱面积** $3\pi a^2$ —— 按参数方程做，$dx=a(1-\cos t)dt$
2. **已知面积反求参数** —— 先列面积式，再解方程
3. **星形线面积** $\dfrac{3\pi a^2}{8}$ —— 用四倍第一象限
4. **$x$ 是 $y$ 的函数时对 $y$ 积分** —— 右减左
5. **圆与直线围成的弓形** —— 可以纯几何算（扇形减三角形）验证
6. **极坐标两曲线公共部分** —— 求交角、分段取里层 $\rho$

**通用检查**：算完看一眼是否小于"包含它的那个大图形"的面积。""",
    [
        ("q1", "blank",
         r"""**一、填空题 第 1 题**

摆线 $x=a(t-\sin t),\ y=a(1-\cos t)$ 的一拱（$0\le t\le 2\pi$）与横轴所围图形的面积为 ____。""",
         r"""**答案**：$3\pi a^2$。

$$A=\int y\,dx=\int_0^{2\pi}a(1-\cos t)\cdot a(1-\cos t)\,dt=a^2\int_0^{2\pi}(1-\cos t)^2dt$$

展开 $(1-\cos t)^2=1-2\cos t+\cos^2t$，逐项积分：

$$\int_0^{2\pi}1\,dt=2\pi,\quad\int_0^{2\pi}\cos t\,dt=0,\quad\int_0^{2\pi}\cos^2t\,dt=\pi$$

$$A=a^2(2\pi-0+\pi)=3\pi a^2$$

摆线还有一个常用结果：一拱的**弧长** $8a$，一起记。""",
         {"blanks": [["3\\pi a^2", "3\\pi a^{2}"]]}),

        ("q2", "blank",
         r"""**一、填空题 第 2 题**

已知曲线 $y=ax^2\ (a>0)$ 与 $y=x^3$ 所围图形的面积为 $8$，则 $a=$ ____。""",
         r"""**答案**：$a=2\sqrt[4]{6}$（即 $a=\sqrt[4]{96}$）。

**求交点**：$ax^2=x^3\Rightarrow x^2(a-x)=0\Rightarrow x=0$ 或 $x=a$。

**谁在上**：在 $(0,a)$ 内 $ax^2-x^3=x^2(a-x)>0$，所以 $y=ax^2$ 在上。

**列面积**

$$A=\int_0^a(ax^2-x^3)dx=\frac{a\cdot a^3}{3}-\frac{a^4}{4}=\frac{a^4}{3}-\frac{a^4}{4}=\frac{a^4}{12}$$

**解方程**

$$\frac{a^4}{12}=8\Rightarrow a^4=96\Rightarrow a=\sqrt[4]{96}=2\sqrt[4]{6}\approx3.13$$

**验证**：$a^4/12=96/12=8$ ✓""",
         {"blanks": [["\\sqrt[4]{96}", "2\\sqrt[4]{6}", "2\\cdot\\sqrt[4]{6}"]]}),

        ("q3", "text",
         r"""**二、计算题 第 1 题**

求星形线 $x=a\cos^3t,\ y=a\sin^3t$ 所围成的图形的面积。""",
         r"""**做法：四倍第一象限**

第一象限对应 $t\in\left[0,\dfrac{\pi}{2}\right]$，$x$ 从 $a$ 降到 $0$。取四分之一面积的 $4$ 倍：

$$A=4\int_{x=0}^{a}y\,dx=4\int_{\pi/2}^{0}a\sin^3t\cdot(-3a\cos^2t\sin t)\,dt$$

两个负号抵消（$dx<0$，上下限调换）：

$$A=12a^2\int_0^{\pi/2}\sin^4t\cos^2t\,dt$$

**算这个积分**：用 Beta 函数或降幂。降幂最稳：

$$\sin^4t\cos^2t=\sin^4t(1-\sin^2t)=\sin^4t-\sin^6t$$

$$\int_0^{\pi/2}\sin^4t\,dt=\frac{3}{4}\cdot\frac{1}{2}\cdot\frac{\pi}{2}=\frac{3\pi}{16},\qquad
\int_0^{\pi/2}\sin^6t\,dt=\frac{5}{6}\cdot\frac{3}{4}\cdot\frac{1}{2}\cdot\frac{\pi}{2}=\frac{5\pi}{32}$$

$$\int_0^{\pi/2}\sin^4t\cos^2t\,dt=\frac{3\pi}{16}-\frac{5\pi}{32}=\frac{6\pi-5\pi}{32}=\frac{\pi}{32}$$

$$A=12a^2\cdot\frac{\pi}{32}=\frac{3\pi a^2}{8}$$

**答案**：$A=\dfrac{3\pi a^2}{8}$。

**自检**：星形线在正方形 $[-a,a]^2$ 内，面积小于 $4a^2$；$\dfrac{3\pi a^2}{8}\approx1.18a^2$，合理。"""),

        ("q4", "text",
         r"""**二、计算题 第 2 题**

求曲线 $y=\ln x$，$y$ 轴与直线 $y=\ln a,\ y=\ln b\ (b>a>0)$ 所围成的图形的面积。""",
         r"""**做法：对 $y$ 积分（右减左）**

曲线写成 $x=e^y$，$y$ 轴是 $x=0$：

$$A=\int_{\ln a}^{\ln b}(e^y-0)\,dy=\big[e^y\big]_{\ln a}^{\ln b}=b-a$$

**答案**：$A=b-a$。

**另一种理解**：这条曲线与 $y$ 轴围成的区域，旋转坐标系后就是 $y=e^x$ 在 $[\ln a,\ln b]$ 下方的面积，结果一样。

**注意**：如果对 $x$ 积分就要分段（$x$ 从 $0$ 到 $a$ 时上边界是 $y=\ln a$，从 $a$ 到 $b$ 才是 $\ln x$），对 $y$ 积分一句话解决。选对积分变量很重要。"""),

        ("q5", "text",
         r"""**二、计算题 第 3 题**

求曲线 $y=\sqrt{2x-x^2}$ 与直线 $y=\dfrac{1}{\sqrt3}x$ 所围成的平面图形的面积。""",
         r"""**第一步：认图形**

$y=\sqrt{2x-x^2}$ 两边平方：$(x-1)^2+y^2=1$，$y\ge0$ —— **上半圆**，圆心 $(1,0)$，半径 $1$。

直线 $y=\dfrac{x}{\sqrt3}$ 过原点，斜率 $\dfrac{1}{\sqrt3}$，倾角 $30^\circ$。

**第二步：求交点**

$$2x-x^2=\frac{x^2}{3}\Rightarrow 6x-3x^2=x^2\Rightarrow 4x^2-6x=0\Rightarrow x=0\ \text{或}\ x=\frac32$$

交点：$(0,0)$ 与 $\left(\dfrac32,\dfrac{\sqrt3}{2}\right)$。

**第三步：积分（上减下）**

$$A=\int_0^{3/2}\left[\sqrt{2x-x^2}-\frac{x}{\sqrt3}\right]dx$$

**第一部分**：令 $x-1=\sin\theta$，$x:0\to\dfrac32$ 对应 $\theta:-\dfrac{\pi}{2}\to\dfrac{\pi}{6}$。

$$\int_0^{3/2}\sqrt{2x-x^2}\,dx=\int_{-\pi/2}^{\pi/6}\cos^2\theta\,d\theta=\left[\frac{\theta}{2}+\frac{\sin2\theta}{4}\right]_{-\pi/2}^{\pi/6}$$

$$=\left(\frac{\pi}{12}+\frac{\sqrt3}{8}\right)-\left(-\frac{\pi}{4}+0\right)=\frac{\pi}{3}+\frac{\sqrt3}{8}$$

**第二部分**：

$$\int_0^{3/2}\frac{x}{\sqrt3}dx=\frac{1}{\sqrt3}\cdot\frac{(3/2)^2}{2}=\frac{9}{8\sqrt3}=\frac{3\sqrt3}{8}$$

**相减**

$$A=\frac{\pi}{3}+\frac{\sqrt3}{8}-\frac{3\sqrt3}{8}=\frac{\pi}{3}-\frac{\sqrt3}{4}$$

**几何验算**（推荐）：圆心 $O(1,0)$，$A_1(0,0)$，$B\left(\dfrac32,\dfrac{\sqrt3}{2}\right)$。

- $\overrightarrow{OA_1}=(-1,0)$，$\overrightarrow{OB}=\left(\dfrac12,\dfrac{\sqrt3}{2}\right)$，夹角 $120^\circ$
- 扇形面积 $=\dfrac12\cdot1^2\cdot\dfrac{2\pi}{3}=\dfrac{\pi}{3}$
- 三角形 $O A_1 B$ 面积 $=\dfrac12\left|(-1)\cdot\dfrac{\sqrt3}{2}-0\right|=\dfrac{\sqrt3}{4}$
- 弓形面积 $=\dfrac{\pi}{3}-\dfrac{\sqrt3}{4}$ ✓

**答案**：$A=\dfrac{\pi}{3}-\dfrac{\sqrt3}{4}$。"""),

        ("q6", "text",
         r"""**二、计算题 第 4 题**

求曲线 $\rho=3\cos\theta$ 及 $\rho=1+\cos\theta$ 所围成平面图形的公共部分的面积。""",
         r"""**第一步：认图形**

- $\rho=3\cos\theta$：圆，圆心 $\left(\dfrac32,0\right)$，半径 $\dfrac32$
- $\rho=1+\cos\theta$：心形线，$\theta=0$ 时 $\rho=2$（最右），$\theta=\pi$ 时 $\rho=0$

**第二步：求交角**

$$3\cos\theta=1+\cos\theta\Rightarrow\cos\theta=\frac12\Rightarrow\theta=\pm\frac{\pi}{3}$$

**第三步：分区间确定"里层"**

公共部分要求同时满足两个不等式。比较两半径：

$$1+\cos\theta\le3\cos\theta\iff\cos\theta\ge\frac12\iff|\theta|\le\frac{\pi}{3}$$

所以

- $|\theta|\le\dfrac{\pi}{3}$：里层是心形线 $\rho=1+\cos\theta$
- $\dfrac{\pi}{3}<|\theta|<\dfrac{\pi}{2}$：里层是圆 $\rho=3\cos\theta$

**第四步：积分（上下对称，乘 2）**

$$A=2\left[\frac12\int_0^{\pi/3}(1+\cos\theta)^2d\theta+\frac12\int_{\pi/3}^{\pi/2}9\cos^2\theta\,d\theta\right]$$

**第一项**

$$(1+\cos\theta)^2=1+2\cos\theta+\cos^2\theta$$

$$\int(1+\cos\theta)^2d\theta=\frac{3\theta}{2}+2\sin\theta+\frac{\sin2\theta}{4}$$

$$\int_0^{\pi/3}=\frac{\pi}{2}+\sqrt3+\frac{\sqrt3}{8}=\frac{\pi}{2}+\frac{9\sqrt3}{8}$$

**第二项**

$$9\int_{\pi/3}^{\pi/2}\cos^2\theta\,d\theta=9\left[\frac{\theta}{2}+\frac{\sin2\theta}{4}\right]_{\pi/3}^{\pi/2}=9\left(\frac{\pi}{4}-\frac{\pi}{6}-\frac{\sqrt3}{8}\right)=\frac{3\pi}{4}-\frac{9\sqrt3}{8}$$

**相加**

$$A=\left(\frac{\pi}{2}+\frac{9\sqrt3}{8}\right)+\left(\frac{3\pi}{4}-\frac{9\sqrt3}{8}\right)=\frac{5\pi}{4}$$

**答案**：$A=\dfrac{5\pi}{4}$。

**自检**：心形线全部面积 $\dfrac{3\pi a^2}{2}$（$a=1$ 时 $\dfrac{3\pi}{2}\approx4.71$），公共部分 $\dfrac{5\pi}{4}\approx3.93$ 小于它 ✓。""")
    ]
)


# ============================================================
# 6.2 体积
# ============================================================
H62A = mk(
    "math/hwb-6-2a",
    "作业册 · 6.2 几何应用（二）体积",
    "圆盘法 · 柱壳法 · 平行截面 · 8 题",
    r"""## 本节三条公式

| 情形 | 公式 |
|---|---|
| 绕 $x$ 轴，单曲线 | $V_x=\pi\displaystyle\int_a^b f^2(x)dx$ |
| 绕 $x$ 轴，两曲线之间 | $V_x=\pi\displaystyle\int_a^b\big[f^2(x)-g^2(x)\big]dx$ |
| 绕 $y$ 轴，已知 $y=f(x)$ | $V_y=2\pi\displaystyle\int_a^b x\,f(x)dx$（柱壳） |
| 平行截面面积已知 | $V=\displaystyle\int_a^b A(x)dx$ |

**最容易错的两点**

1. 环形截面积是 $\pi(R^2-r^2)$，**不是** $\pi(R-r)^2$。
2. 绕 $y$ 轴时，用柱壳法要确认 $x$ 是"半径"、$f(x)$ 是"高"；区域跨过 $y$ 轴时要分段。""",
    [
        ("q1", "blank",
         r"""**一、填空题 第 1 题**

由曲线 $y=\sin x\ (0\le x\le\pi)$ 和 $x$ 轴所围平面图形绕 $x$ 轴旋转所得旋转体的体积为 ____。""",
         r"""**答案**：$\dfrac{\pi^2}{2}$。

$$V=\pi\int_0^\pi\sin^2x\,dx=\pi\cdot\frac{\pi}{2}=\frac{\pi^2}{2}$$

用到 $\int_0^\pi\sin^2x\,dx=\dfrac{\pi}{2}$（半区间上的 $\sin^2$、$\cos^2$ 积分都是 $\dfrac{\pi}{2}$）。""",
         {"blanks": [["\\frac{\\pi^2}{2}", "\\pi^2/2"]]}),

        ("q2", "blank",
         r"""**一、填空题 第 2 题**

由曲线 $y=x^3$，$x=2$ 和 $x$ 轴所围平面图形绕 $x$ 轴旋转所得旋转体的体积为 ____，绕 $y$ 轴旋转所得旋转体的体积为 ____。""",
         r"""**绕 $x$ 轴（圆盘法）**

$$V_x=\pi\int_0^2(x^3)^2dx=\pi\int_0^2x^6dx=\pi\cdot\frac{128}{7}=\frac{128\pi}{7}$$

**绕 $y$ 轴（柱壳法，最省事）**

$$V_y=2\pi\int_0^2x\cdot x^3\,dx=2\pi\int_0^2x^4dx=2\pi\cdot\frac{32}{5}=\frac{64\pi}{5}$$

**用垫片法验算**：$y$ 从 $0$ 到 $8$，$x=y^{1/3}$，外半径 $2$、内半径 $y^{1/3}$：

$$V_y=\pi\int_0^8\left(4-y^{2/3}\right)dy=\pi\left[4y-\frac35y^{5/3}\right]_0^8=\pi\left(32-\frac35\cdot32\right)=\frac{64\pi}{5}\ ✓$$

**答案**：$\dfrac{128\pi}{7}$，$\dfrac{64\pi}{5}$。""",
         {"blanks": [["\\frac{128\\pi}{7}", "128\\pi/7"], ["\\frac{64\\pi}{5}", "64\\pi/5"]]}),

        ("q3", "choice",
         r"""**二、选择题 第 1 题**

由抛物线 $y=x^2,\ x=y^2$ 所围的平面图形绕 $x$ 轴旋转所得的旋转体体积 $V_x=$（　）""",
         r"""**答案：B**

交点为 $(0,0)$、$(1,1)$。在 $0<x<1$ 上 $y=\sqrt x$ 在上，$y=x^2$ 在下。环形截面：

$$V_x=\pi\int_0^1\left[(\sqrt x)^2-(x^2)^2\right]dx=\pi\int_0^1(x-x^4)dx$$

即选项 B（$\pi\int_0^1(x-x^4)dx$）。

**A 错**：$(\sqrt x-x^2)^2$ 是"半径差"的平方，环形面积必须用平方差。
**C 错**：内外颠倒，结果会是负的（$\int_0^1(x^2-\sqrt x)dx<0$）。
**D 错**：同样量纲和符号都不对。

数值：$\pi\left(\dfrac12-\dfrac15\right)=\dfrac{3\pi}{10}$。""",
         {"options": [
             r"""$\pi\displaystyle\int_0^1(\sqrt{x}-x^2)^2dx$""",
             r"""$\pi\displaystyle\int_0^1(x-x^4)dx$""",
             r"""$\pi\displaystyle\int_0^1(x^2-\sqrt{x})^2dx$""",
             r"""$\pi\displaystyle\int_0^1(x^4-x)dx$"""
         ], "answer": [1]}),

        ("q4", "choice",
         r"""**二、选择题 第 2 题**

由曲线 $y=e^x$，$y=e^{-x}$ 及直线 $x=1$ 所围成的平面图形绕 $x$ 轴旋转所得的旋转体体积为（　）""",
         r"""**答案：A**

两曲线交于 $x=0$（$e^0=e^0=1$）。在 $0<x<1$ 上 $e^x>e^{-x}$。

$$V=\pi\int_0^1\left(e^{2x}-e^{-2x}\right)dx=\pi\left[\frac{e^{2x}}{2}+\frac{e^{-2x}}{2}\right]_0^1$$

$$=\pi\left[\left(\frac{e^2}{2}+\frac{1}{2e^2}\right)-1\right]=\frac{\pi}{2}\left(e^2+e^{-2}-2\right)$$

选 A。

**注意**：$\int e^{-2x}dx=-\dfrac{e^{-2x}}{2}$，所以 $-e^{-2x}$ 的原函数是 $+\dfrac{e^{-2x}}{2}$，符号别写反。""",
         {"options": [
             r"""$\dfrac{\pi}{2}(e^2+e^{-2}-2)$""",
             r"""$\dfrac{\pi}{2}(e^2+e^{-2})$""",
             r"""$\pi(e^2+e^{-2}-2)$""",
             r"""$\dfrac{\pi}{2}(e^2+e^{-2}-4)$"""
         ], "answer": [0]}),

        ("q5", "text",
         r"""**三、计算题 第 1 题**

有一立体以抛物线 $y^2=2x$ 与直线 $x=2$ 所围的图形为底，而垂直于抛物线轴的截面都是等边三角形，求该立体的体积。""",
         r"""**理解题意**

"抛物线轴"就是 $x$ 轴。垂直于 $x$ 轴的截面是等边三角形，三角形的**底边**是底面上那条弦。

**底面在 $x$ 处的弦长**

$y^2=2x\Rightarrow y=\pm\sqrt{2x}$，弦长

$$l(x)=2\sqrt{2x}$$

**等边三角形面积**

$$A(x)=\frac{\sqrt3}{4}l^2(x)=\frac{\sqrt3}{4}\cdot4\cdot2x=2\sqrt3\,x$$

**积分**

$$V=\int_0^2 2\sqrt3\,x\,dx=\sqrt3\left[x^2\right]_0^2=4\sqrt3$$

**答案**：$V=4\sqrt3$。

**要点**：这题用的就是"已知平行截面面积 $V=\int A(x)dx$"，不需要旋转。等边三角形面积别记错：$\dfrac{\sqrt3}{4}a^2$。"""),

        ("q6", "text",
         r"""**三、计算题 第 2 题**

求由曲线 $y=\dfrac1x$ 和直线 $y=4x,\ x=2,\ y=0$ 所围平面图形绕 $x$ 轴旋转所成旋转体的体积。""",
         r"""**第一步：画清区域**

- $y=4x$ 与 $y=\dfrac1x$ 交于 $4x=\dfrac1x\Rightarrow x=\dfrac12$，交点 $\left(\dfrac12,2\right)$
- 下边界是 $y=0$，右边界是 $x=2$

所以上边界分两段：

$$y=\begin{cases}4x, & 0\le x\le\dfrac12\\[4pt]\dfrac1x, & \dfrac12\le x\le2\end{cases}$$

**第二步：分段积分**

$$V=\pi\int_0^{1/2}(4x)^2dx+\pi\int_{1/2}^{2}\left(\frac1x\right)^2dx$$

**第一段**

$$\pi\int_0^{1/2}16x^2dx=16\pi\cdot\frac{(1/2)^3}{3}=\frac{16\pi}{24}=\frac{2\pi}{3}$$

**第二段**

$$\pi\int_{1/2}^{2}\frac{dx}{x^2}=\pi\left[-\frac1x\right]_{1/2}^{2}=\pi\left(-\frac12+2\right)=\frac{3\pi}{2}$$

**相加**

$$V=\frac{2\pi}{3}+\frac{3\pi}{2}=\frac{4\pi}{6}+\frac{9\pi}{6}=\frac{13\pi}{6}$$

**答案**：$V=\dfrac{13\pi}{6}$。

**易错点**：漏分段，把整个区间都用 $\dfrac1x$ 或都用 $4x$。"""),

        ("q7", "text",
         r"""**三、计算题 第 3 题**

求由曲线 $y=\dfrac3x$ 和直线 $x+y=4$ 所围平面图形绕 $x$ 轴旋转所成旋转体的体积。""",
         r"""**第一步：求交点**

$$\frac3x=4-x\Rightarrow3=4x-x^2\Rightarrow x^2-4x+3=0\Rightarrow x=1\ \text{或}\ x=3$$

交点 $(1,3)$、$(3,1)$。

**第二步：谁在上**

取 $x=2$：直线 $y=2$，双曲线 $y=1.5$。直线在上。

**第三步：环形截面（外半径 $4-x$，内半径 $\dfrac3x$）**

$$V=\pi\int_1^3\left[(4-x)^2-\left(\frac3x\right)^2\right]dx=\pi\int_1^3\left(16-8x+x^2-\frac{9}{x^2}\right)dx$$

**第四步：逐项积**

$$=\pi\left[16x-4x^2+\frac{x^3}{3}+\frac{9}{x}\right]_1^3$$

上端（$x=3$）：$48-36+9+3=24$

下端（$x=1$）：$16-4+\dfrac13+9=21+\dfrac13=\dfrac{64}{3}$

$$V=\pi\left(24-\frac{64}{3}\right)=\pi\cdot\frac{72-64}{3}=\frac{8\pi}{3}$$

**答案**：$V=\dfrac{8\pi}{3}$。

**检查符号**：$\left[+\dfrac9x\right]$ 的导数确实是 $-\dfrac{9}{x^2}$，符号对上了。"""),

        ("q8", "text",
         r"""**三、计算题 第 4 题**

证明：由平面图形 $0\le a\le x\le b$，$0\le y\le f(x)$ 绕 $y$ 轴旋转所成的旋转体的体积为

$$V=2\pi\int_a^b xf(x)\,dx$$

并求由曲线 $y=\sin x\ (0\le x\le\pi)$ 和 $x$ 轴所围平面图形绕 $y$ 轴旋转所得旋转体的体积。""",
         r"""**证明（柱壳法）**

在 $[x,x+dx]$ 上取一个竖窄条（宽 $dx$、高 $f(x)$）。绕 $y$ 轴旋转时，它扫出一层**薄圆柱壳**：

- 半径 $\approx x$（窄条内每点的旋转半径在 $x$ 与 $x+dx$ 之间）
- 周长 $2\pi x$
- 高 $f(x)$
- 厚 $dx$

所以体积元素

$$dV=2\pi x\,f(x)\,dx$$

误差来自"半径取 $x$ 而非 $x+\theta dx$"，差为 $2\pi f(x)\,dx^2=o(dx)$，合法。于是

$$V=2\pi\int_a^b x f(x)\,dx$$

**应用：$y=\sin x$，$[0,\pi]$**

$$V=2\pi\int_0^\pi x\sin x\,dx$$

分部积分：$\int x\sin x\,dx=-x\cos x+\sin x$。

$$V=2\pi\left[-x\cos x+\sin x\right]_0^\pi=2\pi\left[(-\pi)(-1)+0-0\right]=2\pi^2$$

**答案**：$V=2\pi^2$。""")
    ]
)


# ============================================================
# 6.2 弧长
# ============================================================
H62B = mk(
    "math/hwb-6-2b",
    "作业册 · 6.2 几何应用（三）弧长",
    "心形线 · 渐伸线 · 星形线 · 4 题",
    r"""## 本节三条弧长公式

| 形式 | 公式 |
|---|---|
| $y=f(x)$ | $s=\displaystyle\int_a^b\sqrt{1+y'^2}dx$ |
| 参数方程 | $s=\displaystyle\int_\alpha^\beta\sqrt{x'^2+y'^2}dt$ |
| 极坐标 $\rho(\theta)$ | $s=\displaystyle\int_\alpha^\beta\sqrt{\rho^2+\rho'^2}d\theta$ |

**唯一的技术难点**：开方以后的绝对值怎么去 —— 靠对称性切区间。""",
    [
        ("q1", "choice",
         r"""**一、选择题 第 1 题**

心形线 $\rho=a(1+\cos\theta)\ (a>0)$ 的全长 $S=$（　）""",
         r"""**答案：A**

**先算 $\rho^2+\rho'^2$**

$$\rho=a(1+\cos\theta),\qquad\rho'=-a\sin\theta$$

$$\rho^2+\rho'^2=a^2(1+\cos\theta)^2+a^2\sin^2\theta=a^2\left(1+2\cos\theta+\cos^2\theta+\sin^2\theta\right)$$

$$=a^2(2+2\cos\theta)=4a^2\cos^2\frac{\theta}{2}$$

$$\sqrt{\rho^2+\rho'^2}=2a\left|\cos\frac{\theta}{2}\right|$$

**用对称性**

心形线关于极轴对称，取 $\theta\in[0,\pi]$ 再乘 $2$。此区间内 $\cos\dfrac{\theta}{2}\ge0$，绝对值可去：

$$S=2\int_0^\pi2a\cos\frac{\theta}{2}d\theta=4a\left[2\sin\frac{\theta}{2}\right]_0^\pi=8a$$

选项 A 是 $4a\displaystyle\int_0^\pi\cos\frac{\theta}{2}d\theta=4a\cdot2=8a$ ✓。

**B、D 错**：被积式少了根号，不是弧长公式。
**C 错**：$\int_0^{2\pi}\cos\frac{\theta}{2}d\theta$ 从 $0$ 到 $2\pi$ 跨过 $\theta=\pi$ 变号，直接积得 $0$，必须先用对称性。

**记住**：心形线全长 $8a$。""",
         {"options": [
             r"""$4a\displaystyle\int_0^{\pi}\cos\frac{\theta}{2}d\theta$""",
             r"""$a^2\displaystyle\int_0^{\pi}(1+\cos\theta)^2d\theta$""",
             r"""$2a\displaystyle\int_0^{2\pi}\cos\frac{\theta}{2}d\theta$""",
             r"""$a\displaystyle\int_0^{2\pi}(1+\cos\theta)d\theta$"""
         ], "answer": [0]}),

        ("q2", "choice",
         r"""**一、选择题 第 2 题**

圆的渐伸线 $x=a(\cos t+t\sin t),\ y=a(\sin t-t\cos t)$ 从 $t=0$ 到 $t=\pi$ 的一段弧的长度为（　）""",
         r"""**答案：B**

**求导**

$$x'=a(-\sin t+\sin t+t\cos t)=at\cos t$$

$$y'=a(\cos t-\cos t+t\sin t)=at\sin t$$

**弧微分**

$$ds=\sqrt{x'^2+y'^2}\,dt=\sqrt{a^2t^2\cos^2t+a^2t^2\sin^2t}\,dt=at\,dt\quad(t\ge0)$$

**积分**

$$s=\int_0^\pi at\,dt=\frac{a\pi^2}{2}$$

选 B（$\displaystyle\int_0^\pi at\,dt$）。

**看清结构**：渐伸线的弧长元素是 $at\,dt$，与三角函数无关 —— 这是它的定义性质（弧长等于切线长的增量）。""",
         {"options": [
             r"""$\displaystyle\int_0^{\pi}3at^2dt$""",
             r"""$\displaystyle\int_0^{\pi}at\,dt$""",
             r"""$\displaystyle\int_0^{\pi}a\sin t\cos t\,dt$""",
             r"""$\displaystyle\int_0^{\pi}a\sqrt{1+t^2}\,dt$"""
         ], "answer": [1]}),

        ("q3", "text",
         r"""**二、计算题 第 1 题**

求星形线 $x=a\cos^3t,\ y=a\sin^3t\ (a>0)$ 的全长。""",
         r"""**求导**

$$x'=-3a\cos^2t\sin t,\qquad y'=3a\sin^2t\cos t$$

**弧微分**

$$x'^2+y'^2=9a^2\cos^4t\sin^2t+9a^2\sin^4t\cos^2t=9a^2\sin^2t\cos^2t\left(\cos^2t+\sin^2t\right)$$

$$ds=3a|\sin t\cos t|\,dt$$

**用对称性**

四条弧全等，取第一象限再乘 $4$。$t\in\left[0,\dfrac{\pi}{2}\right]$ 时 $\sin t\cos t\ge0$：

$$s=4\int_0^{\pi/2}3a\sin t\cos t\,dt=12a\left[\frac{\sin^2t}{2}\right]_0^{\pi/2}=12a\cdot\frac12=6a$$

**答案**：$s=6a$。

**另一种积法**：$\sin t\cos t=\dfrac12\sin2t$，$s=4\cdot3a\cdot\dfrac12\displaystyle\int_0^{\pi/2}\sin2t\,dt=6a\cdot1=6a$，一样。

**检查**：星形线在 $[-a,a]^2$ 内接的菱形周长是 $4\sqrt2a\approx5.66a$，星形线 $6a$ 略大，合理。"""),

        ("q4", "text",
         r"""**二、计算题 第 2 题**

求曲线 $x=\dfrac14y^2-\dfrac12\ln y$ 上相应于 $1\le y\le e$ 的一段弧的长度。""",
         r"""**这题是关于 $y$ 的曲线，用 $\dfrac{dx}{dy}$**

$$\frac{dx}{dy}=\frac{y}{2}-\frac{1}{2y}$$

**弧微分**

$$1+\left(\frac{dx}{dy}\right)^2=1+\frac{y^2}{4}-\frac12+\frac{1}{4y^2}=\frac{y^2}{4}+\frac12+\frac{1}{4y^2}$$

**认出来这是完全平方**

$$\frac{y^2}{4}+\frac12+\frac{1}{4y^2}=\left(\frac{y}{2}+\frac{1}{2y}\right)^2$$

所以

$$ds=\left(\frac{y}{2}+\frac{1}{2y}\right)dy\quad(y>0,\ \text{括号恒正，无需绝对值})$$

**积分**

$$s=\int_1^e\left(\frac{y}{2}+\frac{1}{2y}\right)dy=\left[\frac{y^2}{4}+\frac12\ln y\right]_1^e$$

$$=\left(\frac{e^2}{4}+\frac12\right)-\frac14=\frac{e^2+1}{4}$$

**答案**：$s=\dfrac{e^2+1}{4}$。

**要点**：这类"凑完全平方"是弧长题的固定套路 —— 出题人专门配的系数，让 $1+y'^2$ 正好是一个平方。看到 $\dfrac{y}{2}-\dfrac{1}{2y}$ 就该想到它的平方加 $1$ 是 $\left(\dfrac y2+\dfrac1{2y}\right)^2$。""")
    ]
)


# ============================================================
# 6.3 物理应用
# ============================================================
H63 = mk(
    "math/hwb-6-3",
    "作业册 · 6.3 定积分在物理学上的应用",
    "变力做功 · 抽水 · 水压力 · 3 题",
    r"""## 本节做题固定顺序

1. **定坐标**：原点放水面或池底，$y$ 轴方向说清楚（向下还是向上）
2. **写几何量**：半径 $r(y)$、宽度 $w(y)$、提升高度 $h(y)$，全部用相似三角形推
3. **写微元**
 - 做功：$dW=\rho g\,dV\cdot h(y)$
 - 水压力：$dP=\rho g\,y\,w(y)\,dy$
4. **积分并检查量级**

**单位**：用 m 时 $\rho g=9800$；用 cm 时 $\rho g=9.8\times10^{-3}$（或直接用 g 制得 dyn）。**别混用。**""",
    [
        ("q1", "text",
         r"""**第 1 题**

由实验知道，弹簧在拉伸过程中需要的力 $F$（单位 N）与伸长量 $s$（单位 cm）成正比，即 $F=ks$（$k$ 为比例常数）。现有一弹簧，用 $5$ 牛顿的力可以把它拉长 $0.01$ 米。要把弹簧拉长 $0.1$ 米（仍在弹性限度内），计算所作的功。""",
         r"""**第一步：统一单位**

题目给的 $s$ 定义在 cm，但数据是 m。统一用 m：$F=Ks$（$s$ 单位 m）。

$$5=K\cdot0.01\Rightarrow K=500\ \mathrm{N/m}$$

**第二步：变力做功要积分**

$$W=\int_0^{0.1}Ks\,ds=500\left[\frac{s^2}{2}\right]_0^{0.1}=250\cdot0.01=2.5\ \mathrm{J}$$

**答案**：$W=2.5\ \mathrm{J}$。

**易错**：直接算 $5\times0.1=0.5\ \mathrm{J}$。那个 $5\ \mathrm{N}$ 只是拉到 $0.01\ \mathrm{m}$ 时的力；拉到 $0.1\ \mathrm{m}$ 时力已达 $50\ \mathrm{N}$。变力必须积分，且 $W=\dfrac12Ks^2$ 是抛物线增长。"""),

        ("q2", "text",
         r"""**第 2 题**

设一锥形贮水池，深 $15$ 米，口径 $20$ 米，盛满水，今将水全部抽去，问要作多少功？""",
         r"""**第一步：建坐标**

原点取池底，$y$ 轴向上，池口在 $y=15$。

**第二步：写半径**

池口半径 $10\ \mathrm{m}$，池底半径 $0$，线性变化：

$$r(y)=\frac{10}{15}y=\frac{2y}{3}$$

**第三步：取水层**

高 $y$ 处，厚 $dy$ 的一层水：

$$dV=\pi r^2(y)\,dy=\frac{4\pi y^2}{9}dy$$

**第四步：提升高度**

这一层要提到池口（$y=15$），所以提升距离 $15-y$：

$$dW=\rho g\,dV\,(15-y)=9800\cdot\frac{4\pi y^2}{9}(15-y)\,dy$$

**第五步：积分**

$$W=9800\cdot\frac{4\pi}{9}\int_0^{15}(15y^2-y^3)\,dy$$

$$\int_0^{15}(15y^2-y^3)dy=\frac{15^4}{3}-\frac{15^4}{4}=\frac{15^4}{12}=\frac{50625}{12}=4218.75$$

$$W=9800\cdot\frac{4\pi}{9}\cdot4218.75=9800\pi\cdot1875$$

**答案**：$W=1.8375\times10^7\pi\ \mathrm{J}\approx5.77\times10^7\ \mathrm{J}$。

**量级检查**：水量 $V=\dfrac13\pi\cdot10^2\cdot15=500\pi\approx1570\ \mathrm{m^3}$，重 $1.54\times10^7\ \mathrm{N}$，平均提升高度约 $\dfrac{15}{4}\ \mathrm{m}$，功约 $5.8\times10^7\ \mathrm{J}$ ✓。"""),

        ("q3", "text",
         r"""**第 3 题**

一底为 $8$ 厘米、高为 $6$ 厘米的等腰三角形片，铅直地沉没在水中，顶在上，底在下，且与水面平行，而顶离水面 $3$ 厘米。试求它每面所受的侧压力。""",
         r"""**第一步：建坐标**

$y$ 轴向下，水面 $y=0$。

顶点在 $y=3$，底边在 $y=9$（$3+6$）。

**第二步：写宽度（相似三角形）**

深度 $y$ 处的宽度 $w(y)$：从 $y=3$ 到 $y=9$，宽度从 $0$ 线性增到 $8$。

$$\frac{w(y)}{8}=\frac{y-3}{6}\Rightarrow w(y)=\frac{4}{3}(y-3)$$

**第三步：压强与微元**

深度 $y$ 处压强 $\rho g y$，窄条面积 $w(y)dy$：

$$dP=\rho g\,y\cdot\frac43(y-3)\,dy$$

**第四步：积分（用 cm·g·s 制，$\rho=1$，$g=980$）**

$$P=980\cdot\frac43\int_3^9 y(y-3)\,dy$$

$$\int_3^9(y^2-3y)\,dy=\left[\frac{y^3}{3}-\frac{3y^2}{2}\right]_3^9$$

$$=(243-121.5)-(9-13.5)=121.5+4.5=126$$

$$P=980\cdot\frac43\cdot126=980\cdot168=164640\ \mathrm{dyn}$$

**换算 SI**：$1\ \mathrm{N}=10^5\ \mathrm{dyn}$，所以

$$P\approx1.646\ \mathrm{N}$$

**答案**：每面侧压力约 $1.646\times10^5\ \mathrm{dyn}=1.646\ \mathrm{N}$。

**SI 解法验算**：底 $0.08\ \mathrm{m}$，高 $0.06\ \mathrm{m}$，顶深 $0.03\ \mathrm{m}$，$w(y)=\dfrac{4}{3}(y-0.03)$：

$$P=9800\cdot\frac43\int_{0.03}^{0.09}y(y-0.03)dy=9800\cdot\frac43\cdot0.000126=1.6464\ \mathrm{N}\ ✓$$

**注意**：这题"顶离水面 3 cm"是**顶点**在水下 3 cm，别理解成重心深度。""")
    ]
)


for d in (H61, H62A, H62B, H63):
    save(d)
print("ok")
