# -*- coding: utf-8 -*-
"""作业册 · 章检测题 第一 ~ 第三章"""
import json, os

OUT = r"C:/Users/chong/Documents/studyhub/content/lessons"


def save(d):
    p = os.path.join(OUT, d["id"].replace("/", "_") + ".json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    print("written", os.path.basename(p), len(d["cards"]) - 1, "题")


def mk(lid, title, subtitle, intro, items):
    cards = [{"id": "intro", "type": "lecture", "title": "本章要考什么", "md": intro}]
    for it in items:
        c = {"id": it[0], "type": it[1], "question": it[2], "explain": it[3]}
        if len(it) > 4 and it[4]:
            c.update(it[4])
        cards.append(c)
    return {"id": lid, "title": title, "subtitle": subtitle, "cards": cards}


# ============================================================
# 第一章检测题
# ============================================================
T1 = mk(
    "math/test-1",
    "第一章检测题 · 函数与极限",
    "有界与收敛 · 重要极限 · 间断点分类 · 极限计算 · 13 题",
    r"""## 本章命题重点

1. **必要条件 vs 充分条件**：有界⇐收敛，单调有界⇒收敛
2. **两个重要极限**：$\lim\limits_{x\to0}\dfrac{\sin x}{x}=1$，$\lim\limits_{x\to\infty}\left(1+\dfrac1x\right)^x=e$
3. **等价无穷小替换**：$\sin x\sim x$，$e^x-1\sim x$，$\ln(1+x)\sim x$，$1-\cos x\sim\dfrac{x^2}{2}$
4. **间断点四分类**：可去、跳跃、无穷、振荡 —— 关键看**左右极限是否存在、是否相等**
5. **夹逼准则**：$n$ 项和的极限常用

**本章最容易丢分的两处**

- 分段函数在分界点求极限：必须左右分别算
- 极限含有界函数：$\cos\dfrac1x$ 这类因子直接判 0""",
    [
        ("q1", "blank",
         r"""**一、填空题 1**

数列 $\{x_n\}$ 有界是 $\lim\limits_{n\to\infty}x_n$ 存在的 ____ 条件；数列 $\{x_n\}$ 单调有界是 $\lim\limits_{n\to\infty}x_n$ 存在的 ____ 条件。""",
         r"""**答案**：必要条件；充分条件。

**推理**

- **收敛 ⇒ 有界**（收敛数列必有界），反之不成立（$x_n=(-1)^n$ 有界但发散）。所以"有界"是"收敛"的**必要**条件。
- **单调有界 ⇒ 收敛**（单调有界准则），这个方向成立，所以"单调有界"是"收敛"的**充分**条件。

**易混**：只说"有界"不能推出收敛；加上"单调"才行。题目第二空强调"单调有界"，就填"充分"。""",
         {"blanks": [["必要", "必要条件"], ["充分", "充分条件"]]}),

        ("q2", "blank",
         r"""**一、填空题 2**

设 $f(x)$ 处处连续，且 $f(2)=5$，则 $\lim\limits_{x\to0}\dfrac{\sin3x}{x}f\!\left(\dfrac{e^{2x}-1}{x}\right)=$ ____。""",
         r"""**答案**：$15$。

**拆开看**

第一部分（重要极限）：

$$\lim_{x\to0}\frac{\sin3x}{x}=\lim_{x\to0}\frac{\sin3x}{3x}\cdot3=3$$

第二部分（等价无穷小）：$e^{2x}-1\sim2x$，所以

$$\frac{e^{2x}-1}{x}\to2$$

**用连续性**

$f$ 处处连续，$f(2)=5$，所以 $f\!\left(\dfrac{e^{2x}-1}{x}\right)\to f(2)=5$。

**相乘**

$$\lim=3\times5=15$$

**陷阱**：这题的"坑"在于 $f$ 的解析式没给 —— 不需要它，连续性就够了。""",
         {"blanks": [["15"]]}),

        ("q3", "blank",
         r"""**一、填空题 3**

若 $f(x-2)=x^2+2x+3$，则 $f(x)=$ ____。""",
         r"""**答案**：$f(x)=x^2+6x+11$。

**换元**

令 $t=x-2$，则 $x=t+2$，代入：

$$f(t)=(t+2)^2+2(t+2)+3=t^2+4t+4+2t+4+3=t^2+6t+11$$

所以 $f(x)=x^2+6x+11$。

**验算**

原式 $x=0$ 时 $f(-2)=0+0+3=3$；新式 $f(-2)=4-12+11=3$ ✓""",
         {"blanks": [["x^2+6x+11", "x^{2}+6x+11"]]}),

        ("q4", "blank",
         r"""**一、填空题 4**

若 $f(x)=\begin{cases}e^x(\sin x+\cos x), & x>0\\ 2x+a, & x\le0\end{cases}$ 在 $(-\infty,+\infty)$ 连续，则 $a=$ ____。""",
         r"""**答案**：$a=1$。

**在分界点 $x=0$ 处左右取极限**

左极限：

$$\lim_{x\to0^-}(2x+a)=a$$

右极限：

$$\lim_{x\to0^+}e^x(\sin x+\cos x)=1\cdot(0+1)=1$$

**连续要求左右相等**

$$a=1$$

**注意**：$f(0)=2\cdot0+a=a$，所以函数值也自动匹配。""",
         {"blanks": [["1"]]}),

        ("q5", "choice",
         r"""**二、选择题 1**

$\lim\limits_{x\to0}\left(\tan x\cos\dfrac1x-\dfrac{1}{x^2}\sin ax^2\right)=$（　）""",
         r"""**答案**：C，$-a$。

**第一项**

$\tan x\to0$，而 $\cos\dfrac1x$ 有界（$|\cos|\le1$），无穷小乘有界量仍是无穷小：

$$\lim_{x\to0}\tan x\cos\frac1x=0$$

**第二项**

$\sin ax^2\sim ax^2$，所以

$$\frac{1}{x^2}\sin ax^2\to\frac{1}{x^2}\cdot ax^2=a$$

**相减**

$$\lim=0-a=-a$$

选 C。""",
         {"options": ["$0$", "$-1$", "$-a$", "$a$"], "answer": [2]}),

        ("q6", "choice",
         r"""**二、选择题 2**

$\lim\limits_{x\to0}\dfrac{x^2\sin\dfrac2x}{\tan x}=$（　）""",
         r"""**答案**：C，$0$。

**化简**

$\tan x\sim x$：

$$\frac{x^2\sin\frac2x}{\tan x}\sim\frac{x^2\sin\frac2x}{x}=x\sin\frac2x$$

**夹逼**

$$\left|x\sin\frac2x\right|\le|x|\to0$$

所以极限为 $0$。

选 C。

**要点**：$\sin\dfrac2x$ 当 $x\to0$ 时**没有极限**（振荡），但它有界，乘上趋于 $0$ 的 $x$ 就压成 $0$。""",
         {"options": ["$1$", "$2$", "$0$", "不存在"], "answer": [2]}),

        ("q7", "choice",
         r"""**二、选择题 3**

$\lim\limits_{n\to\infty}n\left[\ln(n-1)-\ln(n+1)\right]=$（　）""",
         r"""**答案**：B，$-2$。

**合并对数**

$$n\ln\frac{n-1}{n+1}=n\ln\left(1-\frac{2}{n+1}\right)$$

**用 $\ln(1+u)\sim u$**，这里 $u=-\dfrac{2}{n+1}\to0$：

$$n\ln\left(1-\frac{2}{n+1}\right)\sim n\cdot\left(-\frac{2}{n+1}\right)=-\frac{2n}{n+1}\to-2$$

选 B。

**别踩的坑**：直接把 $\ln(n-1)-\ln(n+1)$ 当 $0$ 处理（两个都 $\to\infty$，差是 $-\infty+\infty$ 型），会丢答案。必须先合并成一个对数。""",
         {"options": ["$2$", "$-2$", "$\infty$", "不存在但非无穷大"], "answer": [1]}),

        ("q8", "choice",
         r"""**二、选择题 4**

设 $f(x)=\dfrac{1+e^{1/x}}{2+e^{1/x}}\arctan\dfrac1x$，则 $x=0$ 是 $f(x)$ 的（　）""",
         r"""**答案**：B，跳跃间断点。

**分左右算**

$x\to0^+$：$e^{1/x}\to+\infty$，分子分母同除 $e^{1/x}$：

$$\frac{1+e^{1/x}}{2+e^{1/x}}=\frac{e^{-1/x}+1}{2e^{-1/x}+1}\to\frac{1}{1}=1$$

$\arctan\dfrac1x\to\dfrac{\pi}{2}$，所以右极限 $=\dfrac{\pi}{2}$。

$x\to0^-$：$e^{1/x}\to0$：

$$\frac{1+0}{2+0}=\frac12,\qquad \arctan\frac1x\to-\frac{\pi}{2}$$

左极限 $=\dfrac12\cdot\left(-\dfrac{\pi}{2}\right)=-\dfrac{\pi}{4}$。

**判断**

左右极限都存在，但 $-\dfrac{\pi}{4}\ne\dfrac{\pi}{2}$ → **跳跃间断点**（第一类）。

选 B。""",
         {"options": ["可去间断点", "跳跃间断点", "无穷间断点", "振荡间断点"], "answer": [1]}),

        ("q9", "text",
         r"""**三、计算题 1**

求 $\lim\limits_{n\to\infty}\left(\dfrac{1}{1\cdot3}+\dfrac{1}{3\cdot5}+\dfrac{1}{5\cdot7}+\cdots+\dfrac{1}{(2n-1)(2n+1)}\right)$。""",
         r"""**裂项**

$$\frac{1}{(2k-1)(2k+1)}=\frac12\left(\frac{1}{2k-1}-\frac{1}{2k+1}\right)$$

**求和（望远镜）**

$$S_n=\frac12\left[\left(1-\frac13\right)+\left(\frac13-\frac15\right)+\cdots+\left(\frac{1}{2n-1}-\frac{1}{2n+1}\right)\right]$$

中间项全消：

$$S_n=\frac12\left(1-\frac{1}{2n+1}\right)$$

**取极限**

$$\lim_{n\to\infty}S_n=\frac12(1-0)=\frac12$$

**答案**：$\dfrac12$。

**一句话**：$\dfrac{1}{(2k-1)(2k+1)}$ 型求和永远先裂项，$n$ 项和就变成首尾两项。"""),

        ("q10", "text",
         r"""**三、计算题 2**

求 $\lim\limits_{n\to\infty}\left(\dfrac{1}{\sqrt{n^2+\pi}}+\dfrac{1}{\sqrt{n^2+2\pi}}+\cdots+\dfrac{1}{\sqrt{n^2+n\pi}}\right)$。""",
         r"""**这是 $n$ 项和，分母都带 $n^2$，用夹逼**

记

$$S_n=\sum_{k=1}^{n}\frac{1}{\sqrt{n^2+k\pi}}$$

**找上下界**：$1\le k\le n$ 时

$$\sqrt{n^2+\pi}\le\sqrt{n^2+k\pi}\le\sqrt{n^2+n\pi}$$

所以

$$\frac{n}{\sqrt{n^2+n\pi}}\le S_n\le\frac{n}{\sqrt{n^2+\pi}}$$

**两边取极限**

$$\frac{n}{\sqrt{n^2+n\pi}}=\frac{1}{\sqrt{1+\frac{\pi}{n}}}\to1$$

$$\frac{n}{\sqrt{n^2+\pi}}=\frac{1}{\sqrt{1+\frac{\pi}{n^2}}}\to1$$

**夹逼**

$$\lim_{n\to\infty}S_n=1$$

**答案**：$1$。

**注意**：不能把它写成定积分（分母不是齐次的 $n$ 倍结构），这题的正解是夹逼。"""),

        ("q11", "text",
         r"""**三、计算题 3**

求 $\lim\limits_{x\to0}(\cos x)^{\cot x}$。""",
         r"""**幂指函数 → 取对数**

$$L=\lim_{x\to0}(\cos x)^{\cot x},\qquad \ln L=\lim_{x\to0}\cot x\ln\cos x$$

**用等价无穷小**：$\ln\cos x=\ln(1+(\cos x-1))\sim\cos x-1\sim-\dfrac{x^2}{2}$

**乘起来**

$$\cot x\ln\cos x\sim\frac{1}{\tan x}\cdot\left(-\frac{x^2}{2}\right)\sim\frac{1}{x}\cdot\left(-\frac{x^2}{2}\right)=-\frac{x}{2}\to0$$

**所以**

$$\ln L=0\ \Longrightarrow\ L=e^0=1$$

**答案**：$1$。

**要点**

1. 幂指函数一律先取对数
2. 取对数后是 $0\cdot\infty$ 型 → 化成 $\dfrac{\ln\cos x}{\tan x}$ 或用等价无穷小
3. 三个等价式子连用：$\cot x\sim\dfrac1x$，$\ln(1+u)\sim u$，$\cos x-1\sim-\dfrac{x^2}{2}$"""),

        ("q12", "text",
         r"""**四、**

设 $f(x)=\begin{cases}e^{\frac{1}{x-1}}, & x>0\\[4pt]\ln(1+x), & -1<x\le0\end{cases}$，求 $f(x)$ 的间断点，并说明间断点所属类型。""",
         r"""**分段点 $x=0$**

左极限（用 $x\le0$ 分支）：

$$\lim_{x\to0^-}\ln(1+x)=\ln1=0$$

右极限（用 $x>0$ 分支）：

$$\lim_{x\to0^+}e^{\frac{1}{x-1}}=e^{\frac{1}{-1}}=e^{-1}=\frac1e$$

$0\ne\dfrac1e$ → **$x=0$ 是跳跃间断点**（第一类）。

**$x=1$（在 $x>0$ 分支内）**

$$\lim_{x\to1^-}e^{\frac{1}{x-1}}=e^{-\infty}=0,\qquad \lim_{x\to1^+}e^{\frac{1}{x-1}}=e^{+\infty}=+\infty$$

右侧极限为无穷 → **$x=1$ 是无穷间断点**（第二类）。

**结论**

| 间断点 | 类型 | 依据 |
|---|---|---|
| $x=0$ | 跳跃 | 左右极限存在但不等 |
| $x=1$ | 无穷 | 单侧极限为 $\infty$ |

**注意**：$x=1$ 不在定义域的"空洞"上 —— 定义域是 $x>0$ 与 $-1<x\le0$，$x=1$ 属于 $x>0$ 分支，只是函数在该点无定义（$e^{1/0}$）。"""),

        ("q13", "text",
         r"""**五、**

已知 $f(x)=\dfrac{ax^3+bx^2+cx+d}{x^2+x-2}$，试确定 $a,b,c,d$，使 $\lim\limits_{x\to\infty}f(x)=1$，且 $\lim\limits_{x\to1}f(x)=0$。""",
         r"""**第一步：$x\to\infty$ 定 $a$**

分子三次、分母二次。要极限有限，必须**三次项系数为 $0$**：

$$a=0$$

此时 $f(x)\sim\dfrac{bx^2}{x^2}=b$，所以

$$b=1$$

**第二步：$x\to1$ 定 $c,d$**

分母 $x^2+x-2=(x-1)(x+2)$，在 $x=1$ 为 $0$。要极限存在，分子在 $x=1$ 也必须为 $0$：

$$1+c+d=0\quad\cdots(1)$$

**第三步：极限值为 $0$，需要更高阶的零点**

分母是**一阶**零点，要商趋于 $0$，分子必须是**二阶**零点：

$$f'(x)\big|_{x=1}=2x+c\big|_{x=1}=2+c=0\Rightarrow c=-2$$

代回 $(1)$：

$$1-2+d=0\Rightarrow d=1$$

**验算**

$$f(x)=\frac{x^2-2x+1}{(x-1)(x+2)}=\frac{(x-1)^2}{(x-1)(x+2)}=\frac{x-1}{x+2}$$

$x\to1$：$0$ ✓；$x\to\infty$：$1$ ✓。

**答案**：$a=0,\ b=1,\ c=-2,\ d=1$。""")
    ]
)


# ============================================================
# 第二章检测题
# ============================================================
T2 = mk(
    "math/test-2",
    "第二章检测题 · 导数与微分",
    "求导法则 · 隐函数 · 高阶导数 · 绝对值可导性 · 13 题",
    r"""## 本章命题重点

1. **先化简再求导**：$\dfrac{\cos2x}{\sin x-\cos x}$ 这种一定要先拆成 $-\cos x-\sin x$
2. **微分形式不变性**：$d(\cdot)=f'(\cdot)d(\cdot)$，注意 $d\dfrac1x=-\dfrac{dx}{x^2}$
3. **隐函数求导**：$y^x=x^y$ 先取对数
4. **参数方程二阶导**：$y''=\dfrac{d}{dt}\left(\dfrac{dy}{dx}\right)\Big/\dfrac{dx}{dt}$，**别忘除 $\dfrac{dx}{dt}$**
5. **$|x|$ 在 $0$ 处**：连续但不可导，左右导数互为相反数
6. **切线与坐标轴平行**：$y'=0$ 或 $y'\to\infty$（竖直）

**最高频错点**：参数方程二阶导漏掉除以 $\dfrac{dx}{dt}$。""",
    [
        ("q1", "blank",
         r"""**一、填空题 1**

$y=\dfrac{\cos2x}{\sin x-\cos x}$，则 $y'=$ ____。""",
         r"""**先化简（关键）**

$$\cos2x=\cos^2x-\sin^2x=(\cos x-\sin x)(\cos x+\sin x)$$

$$\frac{\cos2x}{\sin x-\cos x}=-(\cos x+\sin x)$$

**再求导**

$$y'=-(-\sin x+\cos x)=\sin x-\cos x$$

**答案**：$\sin x-\cos x$。

**教训**：直接上商法则会得到一大坨，化简后一步出结果。看到 $\cos2x$ 与 $\sin x\pm\cos x$ 同时出现，先想二倍角公式。""",
         {"blanks": [["\\sin x-\\cos x", "-\\cos x+\\sin x"]]}),

        ("q2", "blank",
         r"""**一、填空题 2**

$d\!\left(\dfrac{\sin x}{x^2}\right)=$ ____ $d\!\left(\dfrac1x\right)$。""",
         r"""**答案**：$\dfrac{2\sin x-x\cos x}{x}$。

**思路：两个微分之比**

$$\frac{d\!\left(\dfrac{\sin x}{x^2}\right)}{d\!\left(\dfrac1x\right)}=\frac{\left(\dfrac{\sin x}{x^2}\right)'}{\left(\dfrac1x\right)'}$$

**分母**

$$\left(\frac1x\right)'=-\frac{1}{x^2}$$

**分子**

$$\left(\frac{\sin x}{x^2}\right)'=\frac{x^2\cos x-2x\sin x}{x^4}=\frac{x\cos x-2\sin x}{x^3}$$

**相除**

$$\frac{\dfrac{x\cos x-2\sin x}{x^3}}{-\dfrac{1}{x^2}}=-\frac{x\cos x-2\sin x}{x}=\frac{2\sin x-x\cos x}{x}$$

所以

$$d\!\left(\frac{\sin x}{x^2}\right)=\frac{2\sin x-x\cos x}{x}\,d\!\left(\frac1x\right)$$

**技巧**：这题不要真的去凑微分，直接算比值最快。""",
         {"blanks": [["\\frac{2\\sin x-x\\cos x}{x}", "(2\\sin x-x\\cos x)/x"]]}),

        ("q3", "blank",
         r"""**一、填空题 3**

过点 $(1,2)$ 作曲线 $y=2+3\sqrt{x-1}$ 的切线，此切线方程为 ____。""",
         r"""**答案**：$x=1$。

**先看点是否在曲线上**

$x=1$：$y=2+3\sqrt0=2$ ✓ 点在曲线上，是曲线左端点。

**求导看斜率**

$$y'=\frac{3}{2\sqrt{x-1}}$$

$x\to1^+$ 时 $y'\to+\infty$。

**结论**

切线斜率不存在 → 切线是**竖直线**：

$$x=1$$

**要点**：这题考"切线不一定有斜率"。曲线端点处导数为无穷，切线垂直于 $x$ 轴。""",
         {"blanks": [["x=1", "x = 1"]]}),

        ("q4", "choice",
         r"""**二、选择题 1**

曲线 $y=x-e^x$ 上点（　）处的切线与 $x$ 轴平行。""",
         r"""**答案**：B，$(0,-1)$。

**切线与 $x$ 轴平行 ⇔ $y'=0$**

$$y'=1-e^x=0\Rightarrow e^x=1\Rightarrow x=0$$

**代入求点**

$$y(0)=0-e^0=-1$$

点是 $(0,-1)$。

选 B。

**注意**：$(0,1)$ 是 $y=e^x$ 上的点，不是这条曲线上的点。""",
         {"options": ["$(0,1)$", "$(0,-1)$", "$(-1,1)$", "不存在这样的点"], "answer": [1]}),

        ("q5", "choice",
         r"""**二、选择题 2**

函数 $f(x)=|\sin x|$ 在 $x=0$ 处（　）""",
         r"""**答案**：C，连续不可导。

**连续**

$$|\sin x|\to0=f(0)$$ ✓

**可导性：算左右导数**

$x\to0^+$ 时 $\sin x>0$，$f=\sin x$：

$$f'_+(0)=\cos0=1$$

$x\to0^-$ 时 $\sin x<0$，$f=-\sin x$：

$$f'_-(0)=-\cos0=-1$$

左右导数不等（$1\ne-1$）→ **不可导**，是尖点。

选 C。

**结论**：$|u(x)|$ 在 $u=0$ 处，若 $u'(0)\ne0$ 则不可导（左右导数互为相反数），切线呈"尖"。""",
         {"options": ["连续可导", "不连续可导", "连续不可导", "不连续不可导"], "answer": [2]}),

        ("q6", "choice",
         r"""**二、选择题 3**

设 $\begin{cases}x=a(t-\sin t)\\ y=a(1-\cos t)\end{cases}$，则 $y''=$（　）""",
         r"""**答案**：B，$-\dfrac{1}{4a\sin^4\dfrac t2}$。

**一阶导**

$$\frac{dy}{dx}=\frac{a\sin t}{a(1-\cos t)}=\frac{\sin t}{1-\cos t}=\cot\frac t2$$

**二阶导：必须再除以 $\dfrac{dx}{dt}$**

$$y''=\frac{d}{dt}\left(\cot\frac t2\right)\Big/\frac{dx}{dt}$$

$$\frac{d}{dt}\cot\frac t2=-\frac12\csc^2\frac t2=-\frac{1}{2\sin^2\frac t2}$$

$$\frac{dx}{dt}=a(1-\cos t)=2a\sin^2\frac t2$$

$$y''=-\frac{1}{2\sin^2\dfrac t2}\cdot\frac{1}{2a\sin^2\dfrac t2}=-\frac{1}{4a\sin^4\dfrac t2}$$

选 B。

**最高频错误**：只算 $\dfrac{d}{dt}\left(\dfrac{dy}{dx}\right)$ 就交卷，忘了除以 $\dfrac{dx}{dt}$，会得到 $-\dfrac{1}{2\sin^2\frac t2}$（选项 C）。""",
         {"options": [
             r"""$\dfrac{1}{4a\sin^4\dfrac t2}$""",
             r"""$-\dfrac{1}{4a\sin^4\dfrac t2}$""",
             r"""$-\dfrac{1}{2\sin^2\dfrac t2}$""",
             r"""$\dfrac{1}{\sin^4\dfrac t2}$"""
         ], "answer": [1]}),

        ("q7", "choice",
         r"""**二、选择题 4**

设 $y=\tan x+\ln2$，则 $y'=$（　）""",
         r"""**答案**：C，$\sec^2x$。

$\ln2$ 是**常数**，导数为 $0$。所以

$$y'=\sec^2x$$

选 C。

**干扰项**：B 的 $\sec^2x+2$ 是把 $\ln2$ 当函数处理了；A 把 $\sec^2x$ 记成了 $\sec x$。""",
         {"options": [r"""$\sec x+\dfrac12$""", r"""$\sec^2x+2$""", r"""$\sec^2x$""", r"""$\cot x$"""],
         "answer": [2]}),

        ("q8", "text",
         r"""**三、计算题 1**

设 $y=\arcsin(\sin x)+\ln\cos(e^x)$，求 $y'$。""",
         r"""**第一部分**

$$\left(\arcsin(\sin x)\right)'=\frac{1}{\sqrt{1-\sin^2x}}\cdot\cos x=\frac{\cos x}{|\cos x|}$$

在 $\cos x>0$ 的区间上它等于 $1$，$\cos x<0$ 时等于 $-1$。一般写成

$$\frac{\cos x}{\sqrt{1-\sin^2x}}$$

**第二部分**

$$\left(\ln\cos(e^x)\right)'=\frac{1}{\cos(e^x)}\cdot\left(-\sin(e^x)\right)\cdot e^x=-e^x\tan(e^x)$$

**合并**

$$y'=\frac{\cos x}{\sqrt{1-\sin^2x}}-e^x\tan(e^x)$$

**要点**：$\arcsin(\sin x)$ 不是恒等于 $x$（只在 $|x|<\dfrac{\pi}{2}$ 成立），必须老老实实按复合函数求导。"""),

        ("q9", "text",
         r"""**三、计算题 2**

设 $y^x=x^y$，求 $\dfrac{dy}{dx}$。""",
         r"""**两边取对数（幂指函数的标准做法）**

$$x\ln y=y\ln x$$

**两边对 $x$ 求导**（$y$ 是 $x$ 的函数）

$$\ln y+x\cdot\frac{y'}{y}=y'\ln x+y\cdot\frac1x$$

**整理**

$$y'\left(\frac{x}{y}-\ln x\right)=\frac{y}{x}-\ln y$$

$$y'=\frac{\dfrac yx-\ln y}{\dfrac xy-\ln x}$$

**化简成整数形式**（上下同乘 $xy$）

$$y'=\frac{y^2-xy\ln y}{x^2-xy\ln x}$$

**注意**：$y^x$ 和 $x^y$ 都不能直接求导（底和指数都含 $x$），必须取对数。"""),

        ("q10", "text",
         r"""**三、计算题 3**

设 $f(x)=(x-a)^2\varphi(x)$，其中 $\varphi(x)$ 的一阶导数有界，求 $f''(a)$。""",
         r"""**一阶导**

$$f'(x)=2(x-a)\varphi(x)+(x-a)^2\varphi'(x)$$

**二阶导**

$$f''(x)=2\varphi(x)+2(x-a)\varphi'(x)+2(x-a)\varphi'(x)+(x-a)^2\varphi''(x)$$

即

$$f''(x)=2\varphi(x)+4(x-a)\varphi'(x)+(x-a)^2\varphi''(x)$$

**取 $x=a$**

后两项含 $(x-a)$ 因子：

- $4(x-a)\varphi'(x)\to0$（$\varphi'$ 有界，$(x-a)\to0$）
- $(x-a)^2\varphi''(x)$：$\varphi''$ 甚至可能不存在，但乘了 $(x-a)^2$ 仍是 $o((x-a))$，不影响

所以

$$f''(a)=2\varphi(a)$$

**答案**：$f''(a)=2\varphi(a)$。

**这题在考什么**：$\varphi'$ 有界这个条件就是为了说明"含 $(x-a)$ 的项能取到 $0$"，同时避免要求 $\varphi$ 二阶可导。"""),

        ("q11", "text",
         r"""**三、计算题 4**

已知 $y=\sqrt{\dfrac{x(x-1)^3}{(x^2+1)^3}}$，求 $\dfrac{dy}{dx}$。""",
         r"""**先取对数（对数求导法）**

$$\ln y=\frac12\left[\ln x+3\ln(x-1)-3\ln(x^2+1)\right]$$

**两边求导**

$$\frac{y'}{y}=\frac12\left[\frac1x+\frac{3}{x-1}-\frac{6x}{x^2+1}\right]$$

**乘回 $y$**

$$y'=\sqrt{\frac{x(x-1)^3}{(x^2+1)^3}}\cdot\frac12\left[\frac1x+\frac{3}{x-1}-\frac{6x}{x^2+1}\right]$$

**要点**：根号、乘除、幂次同时出现时，对数求导法比直接链式法则快十倍。"""),

        ("q12", "text",
         r"""**四、**

讨论函数 $f(x)=x|x|$ 在 $(-\infty,+\infty)$ 内的可导性，求 $f'(x)$。""",
         r"""**分段写开**

$$f(x)=\begin{cases}x^2, & x\ge0\\ -x^2, & x<0\end{cases}$$

**两侧分别求导**

- $x>0$：$f'(x)=2x$
- $x<0$：$f'(x)=-2x$

**关键看 $x=0$**

左导数：

$$f'_-(0)=\lim_{h\to0^-}\frac{-h^2-0}{h}=\lim_{h\to0^-}(-h)=0$$

右导数：

$$f'_+(0)=\lim_{h\to0^+}\frac{h^2-0}{h}=\lim_{h\to0^+}h=0$$

左右相等 → **$f'(0)=0$ 存在**。

**结论**

$f(x)$ 在 $(-\infty,+\infty)$ 上处处可导，且

$$f'(x)=2|x|$$

**对比**：$|x|$ 在 $0$ 处不可导（左右导数为 $\pm1$），但 $x|x|$ 可导 —— 因为乘了 $x$ 之后两边的斜率都"扁"到 $0$。"""),

        ("q13", "text",
         r"""**五、**

设 $f(x)$ 在 $(-\infty,+\infty)$ 可导，且为以 $T$ 为周期的周期函数，证明其导数 $f'(x)$ 也是以 $T$ 为周期的周期函数。""",
         r"""**用导数定义**

$$f'(x+T)=\lim_{h\to0}\frac{f(x+T+h)-f(x+T)}{h}$$

**用周期性** $f(u+T)=f(u)$：

- $f(x+T+h)=f(x+h)$
- $f(x+T)=f(x)$

代入：

$$f'(x+T)=\lim_{h\to0}\frac{f(x+h)-f(x)}{h}=f'(x)$$

**结论**

$$f'(x+T)=f'(x)$$

所以 $f'(x)$ 也以 $T$ 为周期。

**补充**：不能对 $f(x+T)=f(x)$ 两边直接求导了事（那是循环论证的常见写法），用定义展开才是严谨写法。当然，两边对 $x$ 求导在链式法则下也成立 —— 左式 $\dfrac{d}{dx}f(x+T)=f'(x+T)\cdot1$，右式 $f'(x)$，同样得到结论。两种写法都可以，考试写定义版更保险。""")
    ]
)


# ============================================================
# 第三章检测题
# ============================================================
T3 = mk(
    "math/test-3",
    "第三章检测题 · 微分中值定理与导数的应用",
    "单调性 · 极值 · 凹凸 · 洛必达 · 泰勒 · 13 题",
    r"""## 本章命题重点

1. **单调区间**：解 $f'(x)=0$ 与不可导点，列表判号
2. **凹凸区间**：解 $f''(x)=0$，$f''>0$ 凹（开口向上），$f''<0$ 凸
3. **极值判据**：一阶变号 / 二阶导符号
4. **洛必达**：只能用 $\dfrac00$、$\dfrac{\infty}{\infty}$；每步检查条件
5. **泰勒**：求极限时用带皮亚诺余项的展开
6. **不等式证明**：构造 $g(x)$，用单调性

**本章最容易栽的地方**：洛必达用在非未定式上；不等式证明构造不出辅助函数。""",
    [
        ("q1", "blank",
         r"""**一、填空题 1**

函数 $f(x)=2\arctan x-\ln(1+x^2)$ 的单调减区间是 ____。""",
         r"""**求导**

$$f'(x)=\frac{2}{1+x^2}-\frac{2x}{1+x^2}=\frac{2(1-x)}{1+x^2}$$

**判号**

分母 $1+x^2>0$ 恒成立，符号只由 $1-x$ 决定：

- $x<1$：$f'>0$，递增
- $x>1$：$f'<0$，递减

**答案**：单调减区间 $(1,+\infty)$（写成 $[1,+\infty)$ 也算对）。""",
         {"blanks": [["(1,+\\infty)", "[1,+\\infty)", "(1,+\\infty)"]]}),

        ("q2", "blank",
         r"""**一、填空题 2**

函数 $f(x)=3-x-x^3$ 在 $[1,3]$ 上的最大值是 ____。""",
         r"""**先看单调性**

$$f'(x)=-1-3x^2<0$$

在 $[1,3]$ 上恒负 → $f$ **严格递减**。

**最大值在左端点**

$$f(1)=3-1-1=1$$

**答案**：$1$。

**要点**：闭区间上的最值 = 比较端点值与内部极值。这里没有内部极值（$f'\ne0$），只比端点：$f(1)=1$，$f(3)=3-3-27=-27$。最大 $1$，最小 $-27$。""",
         {"blanks": [["1"]]}),

        ("q3", "blank",
         r"""**一、填空题 3**

曲线 $y=x^4+x^2-\sin x$ 在区间 ____ 是凹的。""",
         r"""**求二阶导**

$$y''=12x^2+2+\sin x$$

**判断符号**

$$12x^2+2\ge2,\qquad \sin x\ge-1$$

所以

$$y''\ge2-1=1>0$$

对**一切** $x$ 成立。

**答案**：$(-\infty,+\infty)$（整条曲线都是凹向上，没有拐点）。

**要点**：这题的技巧是"放缩"—— 不需要解 $y''=0$（根本解不出来），只要证 $y''$ 恒正。$12x^2$ 项足够大，$\sin x$ 的 $-1$ 撼动不了。""",
         {"blanks": [["(-\\infty,+\\infty)", "(-\\infty,+\\infty)", "R"]]}),

        ("q4", "blank",
         r"""**一、填空题 4**

设 $\lim\limits_{x\to\infty}f'(x)=k$，则 $\lim\limits_{x\to\infty}[f(x+a)-f(x)]=$ ____。""",
         r"""**答案**：$ka$。

**用拉格朗日中值定理**

对区间 $[x,x+a]$（或 $[x+a,x]$，看 $a$ 的符号）：

$$f(x+a)-f(x)=f'(\xi)\cdot a,\qquad \xi\ \text{介于}\ x\ \text{与}\ x+a\ \text{之间}$$

**取极限**

当 $x\to\infty$ 时 $\xi\to\infty$，所以

$$f'(\xi)\to k$$

$$\lim_{x\to\infty}[f(x+a)-f(x)]=ka$$

**要点**：这题是"用导数极限推函数增量极限"的模板，本质是拉格朗日中值定理 + 夹逼（$\xi$ 被夹在 $x$ 与 $x+a$ 之间）。""",
         {"blanks": [["ka", "a k", "ak"]]}),

        ("q5", "choice",
         r"""**二、选择题 1**

设 $f(x),g(x)$ 在 $[a,b]$ 可导，且 $f'(x)g(x)+f(x)g'(x)<0$，则当 $x\in(a,b)$ 时有不等式（　）""",
         r"""**答案**：D，$f(x)g(x)>f(b)g(b)$。

**认出左边是乘积的导数**

$$f'(x)g(x)+f(x)g'(x)=\left[f(x)g(x)\right]'<0$$

所以 $F(x)=f(x)g(x)$ 在 $[a,b]$ 上**严格递减**。

**递减的推论**

对 $x\in(a,b)$：

$$F(a)>F(x)>F(b)$$

即

$$f(x)g(x)>f(b)g(b)$$

选 D。

**逐项分析**

- A、B 把结论错写成"商"的比较，题目给的是乘积的导数，与商无关
- C 方向反了（递减应该是 $F(x)<F(a)$）
- D 正确""",
         {"options": [
             r"""$\dfrac{f(x)}{f(a)}>\dfrac{g(x)}{g(a)}$""",
             r"""$\dfrac{f(x)}{f(b)}>\dfrac{g(x)}{g(b)}$""",
             r"""$f(x)g(x)>f(a)g(a)$""",
             r"""$f(x)g(x)>f(b)g(b)$"""
         ], "answer": [3]}),

        ("q6", "choice",
         r"""**二、选择题 2**

设 $f(x)=x^3+ax^2+bx$ 在 $x=1$ 处有极小值 $-2$，则（　）""",
         r"""**答案**：C，$a=0,\ b=-3$。

**两个条件列两个方程**

① 极值点处导数为零：

$$f'(1)=3+2a+b=0$$

② 极值为 $-2$：

$$f(1)=1+a+b=-2$$

**相减**

$$(3+2a+b)-(1+a+b)=0-(-2)\Rightarrow2+a=2\Rightarrow a=0$$

代入 ②：

$$1+0+b=-2\Rightarrow b=-3$$

**验证确是极小值**

$f=x^3-3x$，$f'=3x^2-3=3(x-1)(x+1)$。在 $x=1$ 左右：$f'$ 由负变正 → 极小 ✓，且 $f(1)=1-3=-2$ ✓。

选 C。""",
         {"options": ["$a=b=1$", "$a=-4,\\ b=1$", "$a=0,\\ b=-3$", "$a=4,\\ b=-7$"],
         "answer": [2]}),

        ("q7", "choice",
         r"""**二、选择题 3**

使不等式 $\arctan x+\dfrac{x^3}{3}<x$ 成立的最大范围是（　）""",
         r"""**答案**：B，$0<x<+\infty$。

**构造辅助函数**

$$g(x)=x-\arctan x-\frac{x^3}{3}$$

不等式 $\arctan x+\dfrac{x^3}{3}<x$ 等价于 $g(x)>0$。

**求导判单调**

$$g'(x)=1-\frac{1}{1+x^2}-x^2=\frac{x^2}{1+x^2}-x^2=x^2\left(\frac{1}{1+x^2}-1\right)=-\frac{x^4}{1+x^2}$$

**符号与单调性**

$g'(x)\le0$（仅在 $x=0$ 处为 $0$）→ $g$ 在 $\mathbb R$ 上**严格递减**，且 $g(0)=0$。

**由单调性判号**

- $x<0$ 时 $g(x)>g(0)=0$，即 $\arctan x+\dfrac{x^3}{3}<x$ ✓ 成立
- $x>0$ 时 $g(x)<g(0)=0$，即 $\arctan x+\dfrac{x^3}{3}>x$ ✗ 不成立

所以范围是 $-\infty<x<0$，选 D。

**再核对**：取 $x=1$：$\arctan1+\dfrac13=0.785+0.333=1.118>1$，不成立 ✓。取 $x=-1$：$\arctan(-1)+\dfrac{(-1)^3}{3}=-0.785-0.333=-1.118<-1$ ✓ 成立。

**答案**：D，$-\infty<x<0$。

（这题是经典"方向陷阱"，一定要代一个数验证。）""",
         {"options": ["$0<|x|<+\\infty$", "$0<x<+\\infty$", "$-1<x<0$", "$-\\infty<x<0$"],
         "answer": [3]}),

        ("q8", "choice",
         r"""**二、选择题 4**

设 $f(x)=a-\sqrt[5]{(x-b)^4}$，则（　）""",
         r"""**答案**：D，$f(b)$ 是 $f(x)$ 在 $(-\infty,+\infty)$ 上的最大值。

**先看形状**

$$\sqrt[5]{(x-b)^4}\ge0,\qquad f(x)\le a$$

当且仅当 $x=b$ 时取等号 → $f(b)=a$ 是**最大值**。

**看导数**

$$f'(x)=-\frac45(x-b)^{-1/5}$$

- $x<b$：$(x-b)^{-1/5}<0$ → $f'>0$，递增
- $x>b$：$f'>0$？注意 $(x-b)<0$ 时 $(x-b)^{-1/5}=1/\sqrt[5]{x-b}<0$，所以 $f'>0$；$(x-b)>0$ 时 $f'<0$。

所以 $x<b$ 递增、$x>b$ 递减 → $x=b$ 是**极大值**（也是最大值）。

**是不是拐点？**

$$f''(x)=\frac{4}{25}(x-b)^{-6/5}>0\quad(x\ne b)$$

两侧都凹向上，凹凸性没变 → **不是拐点**。

**逐项看**

- A 错：不是拐点
- B 错：是极大值，但"不是最大值"错了 —— 它确实是最大值
- C 错：是极大值不是极小值
- D 对

选 D。""",
         {"options": [
             "点 $(b,a)$ 是曲线 $y=f(x)$ 的拐点",
             "$f(b)$ 是 $f(x)$ 的极大值，但不是最大值",
             "$f(b)$ 是 $f(x)$ 的极小值",
             "$f(b)$ 是 $f(x)$ 在 $(-\\infty,+\\infty)$ 上的最大值"
         ], "answer": [3]}),

        ("q9", "text",
         r"""**三、计算题 1**

求 $\lim\limits_{x\to0}\dfrac{e^{-\frac{1}{x^2}}}{x^{1000}}$。""",
         r"""**答案**：$0$。

**换元**

令 $t=\dfrac{1}{x^2}\to+\infty$，则

$$\frac{1}{x^{1000}}=\left(\frac{1}{x^2}\right)^{500}=t^{500}$$

原式变成

$$\lim_{t\to+\infty}\frac{t^{500}}{e^t}$$

**指数增长快于任何多项式**

$$e^t=\sum_{k=0}^{\infty}\frac{t^k}{k!}\ge\frac{t^{501}}{501!}$$

所以

$$\frac{t^{500}}{e^t}\le\frac{501!}{t}\to0$$

**结论**：极限为 $0$。

**要点**：$e^{-1/x^2}$ 在 $x=0$ 处"平到不能更平"，任何 $1/x^{n}$ 都压不过它。这是"无穷次可导但泰勒级数不收敛"的经典例子。"""),

        ("q10", "text",
         r"""**三、计算题 2**

求 $\lim\limits_{x\to0}\dfrac{x\cot x-1}{x^2}$。""",
         r"""**方法一：泰勒展开**

$$\sin x=x-\frac{x^3}{6}+\frac{x^5}{120}+o(x^5),\qquad \cos x=1-\frac{x^2}{2}+\frac{x^4}{24}+o(x^4)$$

$$\cot x=\frac{\cos x}{\sin x}=\frac{1-\frac{x^2}{2}+\frac{x^4}{24}}{x\left(1-\frac{x^2}{6}+\frac{x^4}{120}\right)}$$

先算倒数部分，用 $\dfrac{1}{1-u}\approx1+u$：

$$\frac{1}{1-\frac{x^2}{6}+\frac{x^4}{120}}\approx1+\left(\frac{x^2}{6}-\frac{x^4}{120}\right)+\frac{x^4}{36}=1+\frac{x^2}{6}+\frac{x^4}{36}-\frac{x^4}{120}$$

**乘开**

$$\cot x=\frac1x\left(1-\frac{x^2}{2}+\frac{x^4}{24}\right)\left(1+\frac{x^2}{6}+\frac{x^4}{36}-\frac{x^4}{120}\right)$$

常数项：$1$
$x^2$ 项：$-\dfrac12+\dfrac16=-\dfrac13$
$x^4$ 项：忽略

所以

$$x\cot x=1-\frac{x^2}{3}+o(x^2)$$

**代入**

$$\frac{x\cot x-1}{x^2}=\frac{-\frac{x^2}{3}+o(x^2)}{x^2}\to-\frac13$$

**答案**：$-\dfrac13$。

**方法二（更快）：直接洛必达两次**

$$x\cot x-1=\frac{x\cos x-\sin x}{\sin x}\sim\frac{x\cos x-\sin x}{x}$$

$$\frac{x\cos x-\sin x}{x^3}=\frac{(-x\sin x)+(\cos x)-(\cos x)}{3x^2}=\frac{-x\sin x}{3x^2}=\frac{-\sin x}{3x}\to-\frac13$$

（分子求导：$(x\cos x)'=\cos x-x\sin x$，$(\sin x)'=\cos x$，相减得 $-x\sin x$。）

**结果**：$-\dfrac13$。"""),

        ("q11", "text",
         r"""**三、计算题 3**

求 $\lim\limits_{x\to0}(2-\cos3x)^{\frac{1}{\ln(1+x^2)}}$。""",
         r"""**取对数（$1^\infty$ 型）**

$$L=\exp\left[\lim_{x\to0}\frac{\ln(2-\cos3x)}{\ln(1+x^2)}\right]$$

**上下都用等价无穷小**

因为 $2-\cos3x\to1$，记 $u=1-\cos3x\to0$：

$$\ln(1+u)\sim u\ \Rightarrow\ \ln(2-\cos3x)\sim1-\cos3x\sim\frac{(3x)^2}{2}=\frac{9x^2}{2}$$

分母：

$$\ln(1+x^2)\sim x^2$$

**相除**

$$\frac{\frac{9x^2}{2}}{x^2}=\frac92$$

**结论**

$$L=e^{9/2}$$

**答案**：$e^{9/2}$。

**要点**：$1^\infty$ 型三步曲 —— 取对数、两端各替换成等价无穷小、再回去取 $e$。"""),

        ("q12", "text",
         r"""**三、计算题 4**

求 $\lim\limits_{x\to1}\left(\dfrac{2x}{x+1}\right)^{\frac{2x}{x-1}}$。""",
         r"""**取对数（$1^\infty$ 型）**

$$\ln L=\lim_{x\to1}\frac{2x}{x-1}\ln\frac{2x}{x+1}$$

**令 $u=x-1\to0$，$x=1+u$**

$$\frac{2x}{x+1}=\frac{2+2u}{2+u}=\frac{1+u}{1+\frac u2}$$

$$\ln\frac{1+u}{1+\frac u2}=\ln\left(1+\frac{u-\frac u2}{1+\frac u2}\right)\approx\ln\left(1+\frac u2\right)\approx\frac u2$$

**指数部分**

$$\frac{2x}{x-1}=\frac{2+2u}{u}\approx\frac2u$$

**相乘**

$$\ln L=\frac2u\cdot\frac u2=1$$

**结论**

$$L=e$$

**答案**：$e$。

**验算（数值）**：$x=1.01$：底 $=\dfrac{2.02}{2.01}=1.00498$，指数 $=\dfrac{2.02}{0.01}=202$。$1.00498^{202}=\exp(202\times0.004966)=\exp(1.003)\approx2.73$ ✓ 接近 $e$。"""),

        ("q13", "text",
         r"""**四、**

求曲线 $y=x^2\ln x$ 的凹凸区间及拐点坐标。""",
         r"""**定义域**：$x>0$。

**一阶导**

$$y'=2x\ln x+x\cdot\frac1x=2x\ln x+x$$

**二阶导**

$$y''=2\ln x+2x\cdot\frac1x+1=2\ln x+3$$

**解 $y''=0$**

$$2\ln x+3=0\Rightarrow\ln x=-\frac32\Rightarrow x=e^{-3/2}$$

**判凹**（凹向上即 $y''>0$）

- $0<x<e^{-3/2}$：$y''<0$ → 凸（向下）
- $x>e^{-3/2}$：$y''>0$ → 凹（向上）

**拐点纵坐标**

$$y(e^{-3/2})=e^{-3}\cdot\left(-\frac32\right)=-\frac{3}{2e^3}$$

**结论**

- 凹向下（凸）区间：$\left(0,e^{-3/2}\right)$
- 凹向上区间：$\left(e^{-3/2},+\infty\right)$
- 拐点：$\left(e^{-3/2},-\dfrac{3}{2e^3}\right)$

**注意**：$x=e^{-3/2}\approx0.223$，$y\approx-0.0746$，无法化得更简，保留这个形式。""")
    ]
)


for d in (T1, T2, T3):
    save(d)
print("ok")
