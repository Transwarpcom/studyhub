# -*- coding: utf-8 -*-
"""作业册 · 章检测题 第四 ~ 第六章"""
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
# 第四章检测题
# ============================================================
T4 = mk(
    "math/test-4",
    "第四章检测题 · 不定积分",
    "原函数与积分 · 换元 · 分部 · 有理函数 · 16 题",
    r"""## 本章命题重点

1. **原函数与积分的关系**：$\int f\,dx=F+C$，$F'=f$
2. **凑微分**：$f'(x)dx=d f(x)$，看到 $\dfrac{f'}{\sqrt{1-f^2}}$ 就想 $\arcsin f$
3. **三角有理式**：分母 $1+x^4$ 型，分子分母同除 $x^2$ 是标准套路
4. **根式换元**：$\sqrt{a^2-x^2}$ 用 $x=a\sin t$；$\sqrt{x^2+a^2}$ 用 $x=a\tan t$
5. **分部积分**：$\int xf'(x)dx=xf(x)-\int f(x)dx$，这个恒等式反复用

**本章的核心能力**：认出该用哪一类换元，见到什么想什么。""",
    [
        ("q1", "choice",
         r"""**一、选择题 1**

若函数 $f(x)$ 和 $g(x)$ 对于 $(a,b)$ 内每一点都有 $f'(x)=g'(x)$，则在 $(a,b)$ 内必有（　）""",
         r"""**答案**：C，$f(x)-g(x)=C$。

**推理**

令 $h(x)=f(x)-g(x)$，则 $h'(x)=0$ 在 $(a,b)$ 内恒成立。由拉格朗日中值定理（或"导数为零则函数为常数"），$h$ 在 $(a,b)$ 内是常数：

$$f(x)-g(x)=C$$

选 C。

**为什么不是 A**：只有 $C=0$（即 $f(0)=g(0)$ 这类额外条件）时才是 $f-g=0$。题目没给初值。""",
         {"options": [
             "$f(x)-g(x)=0$",
             "$f(x)+g(x)=0$",
             "$f(x)-g(x)=C$",
             "$f(x)+g(x)=C$"
         ], "answer": [2]}),

        ("q2", "choice",
         r"""**一、选择题 2**

设 $F(x)$ 在 $(-\infty,+\infty)$ 内连续，且 $F'(x)=f(x)$，则 $\displaystyle\int f(\sqrt x+1)\frac{dx}{\sqrt x}=$（　）""",
         r"""**答案**：C，$2F(\sqrt x+1)+C$。

**凑微分**

$$u=\sqrt x+1,\qquad du=\frac{1}{2\sqrt x}dx\ \Longrightarrow\ \frac{dx}{\sqrt x}=2du$$

**代入**

$$\int f(u)\cdot2du=2\int f(u)du=2F(u)+C=2F(\sqrt x+1)+C$$

选 C。

**要点**：$\dfrac{dx}{\sqrt x}$ 这一坨就是为 $u=\sqrt x$ 准备的 —— 出题人已经把换元写在你脸上了。""",
         {"options": [
             "$F(\\sqrt x+1)$",
             "$F(\\sqrt x+1)+C$",
             "$2F(\\sqrt x+1)+C$",
             "$\\dfrac12F(\\sqrt x+1)+C$"
         ], "answer": [2]}),

        ("q3", "choice",
         r"""**一、选择题 3**

$d\displaystyle\int f'(x)dx=$（　）""",
         r"""**答案**：C，$f'(x)dx$。

**先积分再微分**

$$\int f'(x)dx=f(x)+C$$

再取微分：

$$d\left[f(x)+C\right]=f'(x)dx+0=f'(x)dx$$

选 C。

**逐项看**

- A 少了 $dx$：微分的结果必须是"某量 $\times dx$"的形式
- B 多加了 $C$：微分消掉常数
- D 同样多加了 $C$

**同类结论**（要背）：
$$d\int f(x)dx=f(x)dx,\qquad \left(\int f(x)dx\right)'=f(x),\qquad \int df(x)=f(x)+C$$""",
         {"options": ["$f'(x)$", "$f'(x)+C$", "$f'(x)dx$", "$f'(x)dx+C$"], "answer": [2]}),

        ("q4", "choice",
         r"""**一、选择题 4**

在函数 $f(x)$ 的积分曲线族中，每一条曲线对应于同一横坐标的点处的切线（　）""",
         r"""**答案**：D，相互平行。

**理由**

积分曲线族：$y=F(x)+C$（$F$ 是 $f$ 的某个原函数），各条曲线只差一个常数，形状完全相同。

同一横坐标 $x_0$ 处的切线斜率：

$$y'(x_0)=F'(x_0)=f(x_0)$$

与 $C$ 无关 → 所有曲线的切线斜率相同 → **互相平行**。

选 D。

**直观**：$y=F(x)+C$ 就是把一条曲线上下平移，平移不改变切线方向。""",
         {"options": ["平行于 $x$ 轴", "平行于 $y$ 轴", "相互垂直", "相互平行"], "answer": [3]}),

        ("q5", "blank",
         r"""**二、填空题 1**

$\displaystyle\int x^3(1+x^4)^{\frac12}dx=$ ____。""",
         r"""**答案**：$\dfrac16(1+x^4)^{3/2}+C$。

**凑微分**

$$u=1+x^4,\qquad du=4x^3dx\Rightarrow x^3dx=\frac{du}{4}$$

$$\int x^3\sqrt{1+x^4}\,dx=\frac14\int u^{1/2}du=\frac14\cdot\frac23u^{3/2}+C=\frac16(1+x^4)^{3/2}+C$$

**验算（求导回去）**

$$\frac16\cdot\frac32(1+x^4)^{1/2}\cdot4x^3=x^3\sqrt{1+x^4}\ ✓$$""",
         {"blanks": [["\\frac16(1+x^4)^{3/2}+C", "\\frac{1}{6}(1+x^4)^{3/2}+C", "(1/6)(1+x^4)^{3/2}+C"]]}),

        ("q6", "blank",
         r"""**二、填空题 2**

$\displaystyle\int\frac{\sin x\,dx}{1+\cos^2x}=$ ____。""",
         r"""**答案**：$-\arctan(\cos x)+C$。

**凑微分**

$$u=\cos x,\qquad du=-\sin x\,dx\Rightarrow \sin x\,dx=-du$$

$$\int\frac{\sin x}{1+\cos^2x}dx=-\int\frac{du}{1+u^2}=-\arctan u+C=-\arctan(\cos x)+C$$

**验算**

$$\left[-\arctan(\cos x)\right]'=-\frac{1}{1+\cos^2x}\cdot(-\sin x)=\frac{\sin x}{1+\cos^2x}\ ✓$$""",
         {"blanks": [["-\\arctan(\\cos x)+C", "-\\arctan\\cos x+C"]]}),

        ("q7", "text",
         r"""**三、计算题 1**

$\displaystyle\int\frac{\cos2x}{1+\sin x\cos x}dx$。""",
         r"""**关键：$\sin x\cos x=\dfrac12\sin2x$**

分母 $=1+\dfrac12\sin2x$。令

$$u=1+\frac12\sin2x,\qquad du=\frac12\cos2x\cdot2\,dx=\cos2x\,dx$$

**代入**

$$\int\frac{du}{u}=\ln|u|+C$$

分子里的 $\cos2x\,dx$ 正好被 $du$ 吸收，非常干净。

**答案**

$$\ln\left|1+\sin x\cos x\right|+C$$

因为 $1+\sin x\cos x=1+\dfrac12\sin2x\ge\dfrac12>0$，绝对值可去掉：

$$\ln\left(1+\sin x\cos x\right)+C$$

**验算**：$\left[\ln(1+\sin x\cos x)\right]'=\dfrac{\cos^2x-\sin^2x}{1+\sin x\cos x}=\dfrac{\cos2x}{1+\sin x\cos x}$ ✓"""),

        ("q8", "text",
         r"""**三、计算题 2**

$\displaystyle\int x^3(1+x^2)^{\frac12}dx$。""",
         r"""**换元消根号**

令 $u=1+x^2$，则 $x^2=u-1$，$x\,dx=\dfrac{du}{2}$。

$$x^3dx=x^2\cdot x\,dx=(u-1)\frac{du}{2}$$

**代入**

$$\int(u-1)u^{1/2}\cdot\frac{du}{2}=\frac12\int\left(u^{3/2}-u^{1/2}\right)du$$

$$=\frac12\left(\frac25u^{5/2}-\frac23u^{3/2}\right)+C$$

**答案**

$$\frac15(1+x^2)^{5/2}-\frac13(1+x^2)^{3/2}+C$$

也可写成 $\dfrac{(1+x^2)^{3/2}}{15}\left(3x^2-2\right)+C$（提公因式），两种都对。

**要点**：$x^3=x^2\cdot x$，把 $x^2$ 用 $u-1$ 替换、$x\,dx$ 用 $\dfrac{du}{2}$ 替换 —— 奇次幂配平方换元的标准拆法。"""),

        ("q9", "text",
         r"""**三、计算题 3**

$\displaystyle\int\frac{1+x^2}{1+x^4}dx$。""",
         r"""**标准套路：分子分母同除 $x^2$**

$$\frac{1+x^2}{1+x^4}=\frac{1+\dfrac{1}{x^2}}{x^2+\dfrac{1}{x^2}}$$

**凑微分**：注意

$$d\left(x-\frac1x\right)=\left(1+\frac{1}{x^2}\right)dx$$

这正是分子。

**分母配方**

$$x^2+\frac{1}{x^2}=\left(x-\frac1x\right)^2+2$$

**代入**：令 $u=x-\dfrac1x$，$du=\left(1+\dfrac1{x^2}\right)dx$

$$\int\frac{du}{u^2+2}=\frac{1}{\sqrt2}\arctan\frac{u}{\sqrt2}+C$$

**答案**

$$\frac{1}{\sqrt2}\arctan\frac{x-\dfrac1x}{\sqrt2}+C$$

**要点**：$\displaystyle\int\frac{dx}{1+x^4}$、$\displaystyle\int\frac{x^2\,dx}{1+x^4}$、$\displaystyle\int\frac{(1+x^2)dx}{1+x^4}$ 这三个是同一家族的题，全都靠"除 $x^2$ + 配方"。"""),

        ("q10", "text",
         r"""**三、计算题 4**

$\displaystyle\int\frac{dx}{\sqrt{2e^{2x}+2e^{x}+1}}$。""",
         r"""**先换元**：$u=e^x$，$dx=\dfrac{du}{u}$

$$\int\frac{du}{u\sqrt{2u^2+2u+1}}$$

**再倒代换**：$t=\dfrac1u$，$du=-\dfrac{dt}{t^2}$，$u=\dfrac1t$

$$\int\frac{-\dfrac{dt}{t^2}}{\dfrac1t\sqrt{\dfrac{2}{t^2}+\dfrac2t+1}}=-\int\frac{dt}{\sqrt{2+2t+t^2}}$$

**配方**

$$2+2t+t^2=(t+1)^2+1$$

**积分**

$$-\int\frac{dt}{\sqrt{(t+1)^2+1}}=-\ln\left|t+1+\sqrt{(t+1)^2+1}\right|+C$$

**代回**：$t=e^{-x}$

$$-\ln\left|e^{-x}+1+\sqrt{(e^{-x}+1)^2+1}\right|+C$$

**化简**（把 $e^{-x}$ 从根号提出来）

$$\sqrt{e^{-2x}+2e^{-x}+2}=e^{-x}\sqrt{1+2e^x+2e^{2x}}$$

$$-\ln\left[e^{-x}\left(1+e^x+\sqrt{1+2e^x+2e^{2x}}\right)\right]+C$$

**答案**

$$x-\ln\left(1+e^x+\sqrt{2e^{2x}+2e^x+1}\right)+C$$

**要点**：被积函数含 $e^x$ 又有根号时，先 $u=e^x$ 再倒代换 $t=1/u$，能把根号化成 $\sqrt{(\cdot)^2+1}$ 这种"$\ln$ 型"。"""),

        ("q11", "text",
         r"""**三、计算题 5**

$\displaystyle\int\frac{1}{1-x^2}\ln\!\left(\frac{1+x}{1-x}\right)dx$。""",
         r"""**认出 $\ln$ 的导数**

令

$$t=\ln\frac{1+x}{1-x}$$

**求 $dt$**

$$\frac{d}{dx}\ln\frac{1+x}{1-x}=\frac{1}{1+x}+\frac{1}{1-x}=\frac{(1-x)+(1+x)}{1-x^2}=\frac{2}{1-x^2}$$

所以

$$\frac{dx}{1-x^2}=\frac{dt}{2}$$

**代入**

$$\int t\cdot\frac{dt}{2}=\frac{t^2}{4}+C$$

**答案**

$$\frac14\ln^2\!\left(\frac{1+x}{1-x}\right)+C$$

**验算**：$\dfrac14\cdot2\ln(\cdot)\cdot\dfrac{2}{1-x^2}=\dfrac{\ln(\cdot)}{1-x^2}$ ✓

**要点**：整道题的分母 $\dfrac{1}{1-x^2}$ 恰好是那个对数的导数的一半 —— 出题人就是这么设计的。"""),

        ("q12", "text",
         r"""**三、计算题 6**

$\displaystyle\int\frac{\arccos x}{(1-x^2)^{\frac32}}dx$。""",
         r"""**三角换元**：$x=\cos t$，$dx=-\sin t\,dt$，$(1-x^2)^{3/2}=\sin^3t$，$t=\arccos x$

**代入**

$$\int\frac{t}{\sin^3t}\cdot(-\sin t\,dt)=-\int\frac{t}{\sin^2t}dt=-\int t\csc^2t\,dt$$

**分部积分**

$$\int t\csc^2t\,dt=-t\cot t+\int\cot t\,dt=-t\cot t+\ln|\sin t|$$

所以

$$-\int t\csc^2t\,dt=t\cot t-\ln|\sin t|+C$$

**代回**

- $t=\arccos x$，$\cot t=\dfrac{\cos t}{\sin t}=\dfrac{x}{\sqrt{1-x^2}}$
- $\sin t=\sqrt{1-x^2}$，$\ln\sqrt{1-x^2}=\dfrac12\ln(1-x^2)$

**答案**

$$\frac{x\arccos x}{\sqrt{1-x^2}}+\frac12\ln(1-x^2)+C$$

**注意**：$-\ln|\sin t|=-\dfrac12\ln(1-x^2)$，符号别丢。"""),

        ("q13", "text",
         r"""**三、计算题 7**

$\displaystyle\int\sqrt{1-x^2}\arcsin x\,dx$。""",
         r"""**换元**：$x=\sin t$，$dx=\cos t\,dt$，$\sqrt{1-x^2}=\cos t$，$t=\arcsin x$

$$\int\cos t\cdot t\cdot\cos t\,dt=\int t\cos^2t\,dt$$

**降幂**

$$\cos^2t=\frac{1+\cos2t}{2}$$

$$\int t\cos^2t\,dt=\frac12\int t\,dt+\frac12\int t\cos2t\,dt$$

$$\int t\cos2t\,dt=\frac{t\sin2t}{2}+\frac{\cos2t}{4}$$

**合起来**

$$=\frac{t^2}{4}+\frac{t\sin2t}{4}+\frac{\cos2t}{8}+C$$

**代回**

- $t=\arcsin x$
- $\sin2t=2\sin t\cos t=2x\sqrt{1-x^2}$
- $\cos2t=1-2\sin^2t=1-2x^2$

**答案**

$$\frac{(\arcsin x)^2}{4}+\frac{x\sqrt{1-x^2}\arcsin x}{2}+\frac{1-2x^2}{8}+C$$

**要点**：$\sin2t$、$\cos2t$ 都要用 $x$ 表示回去，不能留着 $t$ 交卷。"""),

        ("q14", "text",
         r"""**四、**

若 $f(x)$ 的一个原函数是 $(1+\sin x)\ln x$，求 $\displaystyle\int xf'(x)dx$。""",
         r"""**用分部积分恒等式**

$$\int xf'(x)dx=xf(x)-\int f(x)dx$$

**已知**：$F(x)=(1+\sin x)\ln x$ 是 $f$ 的原函数，即

$$f(x)=F'(x),\qquad \int f(x)dx=F(x)+C$$

**先求 $f$**

$$f(x)=\cos x\ln x+\frac{1+\sin x}{x}$$

**代入**

$$\int xf'(x)dx=x\left(\cos x\ln x+\frac{1+\sin x}{x}\right)-(1+\sin x)\ln x+C$$

**答案**

$$x\cos x\ln x+1+\sin x-(1+\sin x)\ln x+C$$

**要点**：这题不需要真的算 $f'$ 再积分 —— 用 $xf(x)-\int f\,dx$ 一步到位。"""),

        ("q15", "text",
         r"""**五、**

设 $f'(\sin^2x)=\cos2x$，且 $f(0)=0$，求 $f(x)$。""",
         r"""**把 $\cos2x$ 写成 $\sin^2x$ 的函数**

$$\cos2x=1-2\sin^2x$$

**令 $u=\sin^2x$**

$$f'(u)=1-2u$$

**积分**

$$f(u)=u-u^2+C$$

**用 $f(0)=0$**

$$0-0+C=0\Rightarrow C=0$$

**答案**

$$f(x)=x-x^2$$

**要点**：$f'(\sin^2x)=\cos2x$ 这种写法，第一步永远是"把右边也用 $\sin^2x$ 表示"，然后用 $u$ 替换。"""),

        ("q16", "text",
         r"""**六、**

设 $\displaystyle\int f(x)dx=\sin x+c$，求 $\displaystyle\int f^{(n)}(x)dx$。""",
         r"""**先求 $f$**

$$f(x)=(\sin x)'=\cos x$$

**求 $n$ 阶导**

$$\cos x\ \text{的}\ n\ \text{阶导为}\ \cos\left(x+\frac{n\pi}{2}\right)$$

即

$$f^{(n)}(x)=\cos\left(x+\frac{n\pi}{2}\right)$$

**再积分**

$$\int f^{(n)}(x)dx=f^{(n-1)}(x)+C=\cos\left(x+\frac{(n-1)\pi}{2}\right)+C$$

**答案**

$$\cos\left(x+\frac{(n-1)\pi}{2}\right)+C$$

**另一种写法**：因为 $\cos\left(x+\dfrac{(n-1)\pi}{2}\right)$ 随 $n$ 周期变化，可写成

$$n=1,2,3,4\ \text{时依次为}\ \sin x,\ -\cos x,\ -\sin x,\ \cos x\ (\text{加}\ C)$$

**要点**：$\int f^{(n)}dx=f^{(n-1)}+C$ 这条恒等式是本题的全部。""")
    ]
)


# ============================================================
# 第五章检测题
# ============================================================
T5 = mk(
    "math/test-5",
    "第五章检测题 · 定积分",
    "奇偶性 · 变上限求导 · 换元 · 反常积分 · 12 题",
    r"""## 本章命题重点

1. **对称区间奇偶性**：奇函数积分为 $0$，偶函数两倍 —— 每年必考
2. **变上限积分求导**：上下限都是函数时，两项相减各乘导数
3. **定积分换元**：换元必换限
4. **分段函数积分**：在分界点拆开
5. **反常积分判敛**：$p$ 积分，$\displaystyle\int_1^{\infty}\frac{dx}{x^p}$ 当 $p>1$ 收敛
6. **积分中值定理**：$\displaystyle\int_a^b f=f(\xi)(b-a)$

**最容易丢分**：变上限求导时上下限都是复合函数，只算了一项。""",
    [
        ("q1", "blank",
         r"""**一、填空题 1**

$\displaystyle\int_{-\pi}^{\pi}x^4\sin x\,dx=$ ____。""",
         r"""**答案**：$0$。

**用奇偶性**

被积函数 $x^4\sin x$：$x^4$ 是偶函数，$\sin x$ 是奇函数，乘积是**奇函数**。

对称区间上奇函数的积分为 $0$：

$$\int_{-\pi}^{\pi}x^4\sin x\,dx=0$$

**要点**：看到 $[-\pi,\pi]$、$[-a,a]$、$[-1,1]$ 这种对称区间，第一反应就是"能不能凑奇偶"。这题一眼 $0$，不用算。""",
         {"blanks": [["0"]]}),

        ("q2", "blank",
         r"""**一、填空题 2**

$\displaystyle\int_{1}^{+\infty}\frac{dx}{x^4}=$ ____。""",
         r"""**答案**：$\dfrac13$。

**按定义算**

$$\int_1^{+\infty}\frac{dx}{x^4}=\lim_{b\to+\infty}\int_1^b x^{-4}dx=\lim_{b\to+\infty}\left[-\frac{1}{3x^3}\right]_1^b$$

$$=\lim_{b\to+\infty}\left(-\frac{1}{3b^3}+\frac13\right)=0+\frac13=\frac13$$

**结论**：$p$ 积分 $\displaystyle\int_1^{+\infty}\frac{dx}{x^p}$，$p>1$ 收敛且等于 $\dfrac{1}{p-1}$。这里 $p=4$，值 $\dfrac{1}{3}$ ✓""",
         {"blanks": [["\\frac13", "1/3"]]}),

        ("q3", "blank",
         r"""**一、填空题 3**

函数 $f(x)=\displaystyle\int_0^x\frac{1-2t}{\sqrt{t^2+1}}dt$ 在区间 ____ 内单调增加，曲线 $y=f(x)$ 在区间 ____ 内向上凹。""",
         r"""**第一空：单调增加 ⇔ $f'(x)>0$**

$$f'(x)=\frac{1-2x}{\sqrt{x^2+1}}$$

分母恒正，所以 $f'(x)>0\iff1-2x>0\iff x<\dfrac12$。

**增区间**：$\left(-\infty,\dfrac12\right)$。

**第二空：向上凹 ⇔ $f''(x)>0$**

$$f'(x)=(1-2x)(x^2+1)^{-1/2}$$

$$f''(x)=-2(x^2+1)^{-1/2}+(1-2x)\cdot\left(-\frac12\right)(x^2+1)^{-3/2}\cdot2x$$

$$=\frac{-2(x^2+1)-x(1-2x)}{(x^2+1)^{3/2}}=\frac{-2x^2-2-x+2x^2}{(x^2+1)^{3/2}}=\frac{-(x+2)}{(x^2+1)^{3/2}}$$

$$f''(x)>0\iff x+2<0\iff x<-2$$

**凹向上区间**：$(-\infty,-2)$。

**答案**：$\left(-\infty,\dfrac12\right)$；$(-\infty,-2)$。

**要点**：$f(x)$ 是变上限积分，$f'$ 就是被积函数，完全不用积出来。""",
         {"blanks": [["(-\\infty,\\frac12)", "(-\\infty,1/2)", "x<1/2"],
                     ["(-\\infty,-2)", "x<-2"]]}),

        ("q4", "blank",
         r"""**一、填空题 4**

设 $f(x)$ 在 $(-\infty,+\infty)$ 上连续，则 $\dfrac{d}{dx}\displaystyle\int_{3x^2}^{\cos x^2}f(t)dt=$ ____。""",
         r"""**上下限都是复合函数，两项都要算**

公式：

$$\frac{d}{dx}\int_{a(x)}^{b(x)}f(t)dt=f(b(x))b'(x)-f(a(x))a'(x)$$

**这里**

- 上限 $b(x)=\cos x^2$，$b'(x)=-\sin(x^2)\cdot2x=-2x\sin x^2$
- 下限 $a(x)=3x^2$，$a'(x)=6x$

**答案**

$$-2x\sin x^2\,f(\cos x^2)-6x\,f(3x^2)$$

**最高频错误**：只算上限那一项，忘了下限项（或把下限项写成加号）。""",
         {"blanks": [["-2x\\sin x^2 f(\\cos x^2)-6x f(3x^2)",
                      "-2x\\sin(x^2)f(\\cos x^2)-6xf(3x^2)"]]}),

        ("q5", "choice",
         r"""**二、选择题 1**

$\displaystyle\int_{-2}^{1}\frac{dx}{(11+5x)^3}$ 的值是（　）""",
         r"""**答案**：A，$\dfrac{51}{512}$。

**换元**

$$u=11+5x,\qquad du=5dx\Rightarrow dx=\frac{du}{5}$$

上下限：$x=-2\Rightarrow u=1$；$x=1\Rightarrow u=16$。

**积分**

$$\frac15\int_1^{16}u^{-3}du=\frac15\left[-\frac{1}{2u^2}\right]_1^{16}=\frac15\left(-\frac{1}{512}+\frac12\right)$$

$$=\frac15\cdot\frac{512-1}{1024}\cdot2=\frac15\cdot\frac{255}{512}=\frac{51}{512}$$

**答案**：$\dfrac{51}{512}$，选 A。

**要点**：换元后上下限要跟着换，别用原来的 $-2,1$ 去代 $u$。""",
         {"options": [r"""$\dfrac{51}{512}$""", r"""$\dfrac{5}{11}$""", r"""$-\dfrac{51}{512}$""", r"""$-\dfrac{5}{11}$"""],
         "answer": [0]}),

        ("q6", "choice",
         r"""**二、选择题 2**

下列广义积分中发散的是（　）""",
         r"""**答案**：D，$\displaystyle\int_0^{\frac{\pi}{2}}\frac{dx}{\sin^2x}$。

**逐项判断**

- A：$\displaystyle\int_e^{+\infty}\frac{dx}{x\ln^2x}$。令 $u=\ln x$，得 $\displaystyle\int_1^{+\infty}\frac{du}{u^2}=1$，**收敛**。
- B：$\displaystyle\int_e^{+\infty}\frac{\ln x}{x^2}dx$。$p=2>1$ 且对数因子不改变敛散性，**收敛**（值 $\dfrac{1}{e}(1+1)=\dfrac2e$）。
- C：$\displaystyle\int_2^3\frac{dx}{x^4\sqrt{9-x^2}}$。$x=3$ 处 $\sqrt{9-x^2}\sim\sqrt6\sqrt{3-x}$，是 $1/2$ 阶瑕点，$1/2<1$ → **收敛**。
- D：$\displaystyle\int_0^{\frac{\pi}{2}}\frac{dx}{\sin^2x}$。$x=0$ 处 $\sin x\sim x$，被积函数 $\sim\dfrac{1}{x^2}$，$p=2>1$ → **发散**。

选 D。

**判据记牢**：$\displaystyle\int_0^a\frac{dx}{x^p}$ 当 $p<1$ 收敛，$p\ge1$ 发散 —— 跟无穷限的方向**相反**。""",
         {"options": [
             r"""$\displaystyle\int_e^{+\infty}\frac{dx}{x\ln^2x}$""",
             r"""$\displaystyle\int_e^{+\infty}\frac{\ln x}{x^2}dx$""",
             r"""$\displaystyle\int_2^3\frac{dx}{x^4\sqrt{9-x^2}}$""",
             r"""$\displaystyle\int_0^{\frac{\pi}{2}}\frac{dx}{\sin^2x}$"""
         ], "answer": [3]}),

        ("q7", "choice",
         r"""**二、选择题 3**

设 $f(x)$ 在 $[0,+\infty)$ 上连续，且 $\displaystyle\int_0^x f(t)dt=x(1+\cos x)$，则 $f\!\left(\dfrac{\pi}{2}\right)$ 应为（　）""",
         r"""**答案**：B，$1-\dfrac{\pi}{2}$。

**两边求导得 $f$**

$$f(x)=\left[x(1+\cos x)\right]'=1+\cos x-x\sin x$$

**代入 $x=\dfrac{\pi}{2}$**

$$f\!\left(\frac{\pi}{2}\right)=1+0-\frac{\pi}{2}\cdot1=1-\frac{\pi}{2}$$

选 B。

**要点**：给的是积分等式，求被积函数值 —— 求导就完事，不需要积分。""",
         {"options": [r"""$1+\dfrac{\pi}{2}$""", r"""$1-\dfrac{\pi}{2}$""", "$1$", r"""$\dfrac{\pi}{2}$"""],
         "answer": [1]}),

        ("q8", "text",
         r"""**三、证明与计算 1**

设函数 $f(x)$ 在 $[0,1]$ 上连续，在 $(0,1)$ 内可导，且 $3\displaystyle\int_{\frac23}^{1}f(x)dx=f(0)$，证明：在 $(0,1)$ 内至少存在一点 $C$，使 $f'(C)=0$。""",
         r"""**第一步：积分中值定理**

$f$ 在 $\left[\dfrac23,1\right]$ 上连续，由积分中值定理，存在 $\xi\in\left[\dfrac23,1\right]$，使

$$\int_{2/3}^{1}f(x)dx=f(\xi)\left(1-\frac23\right)=\frac13f(\xi)$$

所以

$$3\int_{2/3}^{1}f(x)dx=f(\xi)$$

**第二步：用已知条件**

题设 $3\displaystyle\int_{2/3}^{1}f=f(0)$，所以

$$f(\xi)=f(0)$$

**第三步：罗尔定理**

$f$ 在 $[0,\xi]$ 上连续、在 $(0,\xi)$ 内可导，且 $f(0)=f(\xi)$。

由罗尔定理，存在 $C\in(0,\xi)\subset(0,1)$，使

$$f'(C)=0$$

**证毕。**

**要点**：这题的两个动作 —— **把积分换成函数值（积分中值）**、**在等值点上用罗尔** —— 是中值定理证明题的固定套路。"""),

        ("q9", "text",
         r"""**三、证明与计算 2**

讨论函数

$$f(x)=\begin{cases}\sin2(e^x-1), & x>0\\ 2, & x=0\\[4pt]\dfrac1x\displaystyle\int_0^x\cos^2t\,dt, & x<0\end{cases}$$

的连续性。""",
         r"""**在 $x\ne0$ 处**

三段各自连续：$\sin2(e^x-1)$ 是复合连续函数；$\dfrac1x\int_0^x\cos^2t\,dt$ 是"连续函数 / $x$"，在 $x<0$ 上连续。所以只需看 $x=0$。

**右极限**

$$\lim_{x\to0^+}\sin2(e^x-1)=\sin2(e^0-1)=\sin0=0$$

**左极限**

$$\lim_{x\to0^-}\frac1x\int_0^x\cos^2t\,dt$$

这是"变上限积分 / $x$"型 $\dfrac00$ 极限，用洛必达（或直接用导数定义）：

$$=\lim_{x\to0^-}\frac{\cos^2x}{1}=\cos^20=1$$

**函数值**

$$f(0)=2$$

**结论**

$$0\ne1\ne2$$

左右极限都存在但不相等，且都不等于函数值 → **$x=0$ 是跳跃间断点**，$f$ 在 $x=0$ 不连续，在其余点连续。

**要点**：$\displaystyle\lim_{x\to0}\frac1x\int_0^xf(t)dt=f(0)$ 这条恒等式（$f$ 连续时）可以直接引用，它就是"积分平均值"的极限。"""),

        ("q10", "text",
         r"""**三、证明与计算 3**

若 $f(x)=\begin{cases}e^{-2x}, & -1\le x<0\\[4pt]\dfrac{x^2}{1+x^2}, & 0<x\le1\end{cases}$，求 $\displaystyle\int_0^2f(t-1)dt$。""",
         r"""**先平移**

令 $u=t-1$，$t=0\to u=-1$，$t=2\to u=1$，$dt=du$：

$$\int_0^2f(t-1)dt=\int_{-1}^{1}f(u)du$$

**分段拆开**

$$\int_{-1}^{0}e^{-2u}du+\int_0^1\frac{u^2}{1+u^2}du$$

**第一段**

$$\int_{-1}^{0}e^{-2u}du=\left[-\frac12e^{-2u}\right]_{-1}^{0}=-\frac12+\frac12e^{2}=\frac{e^2-1}{2}$$

**第二段**（先做多项式除法）

$$\frac{u^2}{1+u^2}=1-\frac{1}{1+u^2}$$

$$\int_0^1\left(1-\frac{1}{1+u^2}\right)du=\left[u-\arctan u\right]_0^1=1-\frac{\pi}{4}$$

**相加**

$$\int_0^2f(t-1)dt=\frac{e^2-1}{2}+1-\frac{\pi}{4}$$

**答案**

$$\frac{e^2-1}{2}+1-\frac{\pi}{4}$$

**要点**：$f(t-1)$ 这种平移，先换元回到 $f(u)$ 再分段；$\dfrac{u^2}{1+u^2}$ 一定要先除成 $1-\dfrac{1}{1+u^2}$。"""),

        ("q11", "text",
         r"""**三、证明与计算 4**

计算 $\lim\limits_{x\to0}\dfrac{\displaystyle\int_0^x(\arcsin t-t)dt}{x(e^x-1)^3}$。""",
         r"""**分母先用等价无穷小**

$$e^x-1\sim x\Rightarrow (e^x-1)^3\sim x^3\Rightarrow x(e^x-1)^3\sim x^4$$

**分子用泰勒**

$$\arcsin t=t+\frac{t^3}{6}+o(t^3)$$

$$\arcsin t-t=\frac{t^3}{6}+o(t^3)$$

$$\int_0^x\left(\frac{t^3}{6}+o(t^3)\right)dt=\frac{x^4}{24}+o(x^4)$$

**相除**

$$\lim_{x\to0}\frac{\frac{x^4}{24}}{x^4}=\frac{1}{24}$$

**答案**：$\dfrac{1}{24}$。

**也可以洛必达**：分子求导得 $\arcsin x-x$，分母四次求导会越来越复杂，**不如泰勒**。看到 $\arcsin t-t$ 就想到它从 $\dfrac{t^3}{6}$ 起跳。"""),

        ("q12", "text",
         r"""**三、证明与计算 5**

证明 $\displaystyle\int_0^{\pi}\sin^nx\,dx=2\int_0^{\frac{\pi}{2}}\sin^nx\,dx$。""",
         r"""**拆区间**

$$\int_0^{\pi}\sin^nx\,dx=\int_0^{\frac{\pi}{2}}\sin^nx\,dx+\int_{\frac{\pi}{2}}^{\pi}\sin^nx\,dx$$

**对第二个积分换元**：令 $u=\pi-x$，$dx=-du$

$x=\dfrac{\pi}{2}\Rightarrow u=\dfrac{\pi}{2}$；$x=\pi\Rightarrow u=0$。

$$\int_{\frac{\pi}{2}}^{\pi}\sin^nx\,dx=\int_{\frac{\pi}{2}}^{0}\sin^n(\pi-u)(-du)=\int_0^{\frac{\pi}{2}}\sin^nu\,du$$

（用了 $\sin(\pi-u)=\sin u$。）

**合起来**

$$\int_0^{\pi}\sin^nx\,dx=\int_0^{\frac{\pi}{2}}\sin^nx\,dx+\int_0^{\frac{\pi}{2}}\sin^nx\,dx=2\int_0^{\frac{\pi}{2}}\sin^nx\,dx$$

**证毕。**

**要点**：$\sin x$ 关于 $x=\dfrac{\pi}{2}$ 对称，这个换元把 $[0,\pi]$ 的上半段翻到第一象限。华里士公式的全区间版本就靠这条。""")
    ]
)


# ============================================================
# 第六章检测题
# ============================================================
T6 = mk(
    "math/test-6",
    "第六章检测题 · 定积分的应用",
    "面积 · 体积 · 水压力 · 极值化 · 13 题",
    r"""## 本章命题重点

1. **面积**：直角坐标上减下，极坐标 $\dfrac12\int\rho^2d\theta$
2. **体积**：垫片 $\pi(R^2-r^2)$、柱壳 $2\pi\int xf(x)dx$
3. **椭圆与圆旋转体的标准值**
4. **水压力**：$P=\rho g\int y\,w(y)dy$，宽度靠相似三角形
5. **"求最值"型应用**：先列面积/体积表达式，再求导定最优参数

**本章综合题比例高**：最后几题（六、七、八）都是"面积 + 求导求极值"，要有耐心列式。""",
    [
        ("q1", "blank",
         r"""**一、填空题 1**

① 由曲线 $y=e^x$，$y=e^{-x}$ 及直线 $x=1$ 所围成图形的面积是 ____。

② 由曲线 $y=e^x$，$y=e^{-2x}$ 及直线 $x=-1$ 所围成图形的面积是 ____。""",
         r"""**①**

交点：$e^x=e^{-x}\Rightarrow x=0$。在 $0<x<1$ 上 $e^x>e^{-x}$。

$$A=\int_0^1\left(e^x-e^{-x}\right)dx=\left[e^x+e^{-x}\right]_0^1=\left(e+\frac1e\right)-2$$

**答案**：$e+\dfrac1e-2$。

**②**

交点：$e^x=e^{-2x}\Rightarrow x=0$。在 $-1<x<0$ 上 $e^{-2x}>e^x$（例如 $x=-1$ 时 $e^2\approx7.4>e^{-1}$）。

$$A=\int_{-1}^{0}\left(e^{-2x}-e^x\right)dx=\left[-\frac12e^{-2x}-e^x\right]_{-1}^{0}$$

$$=\left(-\frac12-1\right)-\left(-\frac{e^2}{2}-e^{-1}\right)=-\frac32+\frac{e^2}{2}+\frac1e$$

**答案**：$\dfrac{e^2-3}{2}+\dfrac1e$。

**检查**：第二个图形跨过 $x=-1$ 到 $0$，$e^2/2\approx3.69$，$+0.368-1.5\approx2.56$，合理。""",
         {"blanks": [["e+\\frac1e-2", "e+1/e-2"],
                     ["\\frac{e^2-3}{2}+\\frac1e", "(e^2-3)/2+1/e"]]}),

        ("q2", "blank",
         r"""**一、填空题 2**

由曲线 $y=f(x)$（$f(x)>0$），直线 $x=a$，$x=b$（$a<b$）及 $x$ 轴所围成的平面图形绕 $Ox$ 轴旋转而成的旋转体体积 $V=$ ____。""",
         r"""**答案**：$\displaystyle V=\pi\int_a^bf^2(x)dx$。

**理由**：在 $[x,x+dx]$ 上截面是半径 $f(x)$ 的圆盘，

$$dV=\pi f^2(x)dx$$

**注意**：不是 $\displaystyle\int_a^b\pi f(x)dx$（少平方），也不是 $2\pi\displaystyle\int_a^b f(x)dx$（那是周长，不是面积）。""",
         {"blanks": [["\\pi\\int_a^b f^2(x)dx", "\\pi\\int_a^b f^{2}(x)\\,dx", "pi*Int"]]}),

        ("q3", "blank",
         r"""**一、填空题 3**

设 $\varphi'(t),\psi'(t)$ 连续且不同时为 $0$，曲线 $x=\varphi(t)$，$y=\psi(t)$ 自 $t=a$ 的点到 $t=b$ 的点（$a\le t\le b$）之间的弧长为 ____。""",
         r"""**答案**：$\displaystyle s=\int_a^b\sqrt{\varphi'^2(t)+\psi'^2(t)}\,dt$。

**理由**：弧微分 $ds=\sqrt{x'^2+y'^2}\,dt$。

**注意**：根号里是"导数平方和"，不是"函数平方和"——别和极坐标的 $\sqrt{\rho^2+\rho'^2}$ 混。""",
         {"blanks": [["\\int_a^b\\sqrt{\\varphi'^2(t)+\\psi'^2(t)}dt",
                      "\\int_a^b \\sqrt{(\\varphi'(t))^2+(\\psi'(t))^2}dt"]]}),

        ("q4", "choice",
         r"""**二、选择题 1**

由曲线 $y=x^2$ 与 $y=\sqrt x$ 围成平面图形绕 $OX$ 轴旋转而成的旋转体体积为（　）""",
         r"""**答案**：C，$\displaystyle\pi\int_0^1(x-x^4)dx$。

交点为 $(0,0)$、$(1,1)$，在 $0<x<1$ 上 $\sqrt x>x^2$。

$$V=\pi\int_0^1\left[(\sqrt x)^2-(x^2)^2\right]dx=\pi\int_0^1(x-x^4)dx$$

**逐项看**

- A：区间 $[-1,1]$ 错（两曲线只在第一象限相交），$x^4-x$ 也错
- B：$(\sqrt x-x^2)^2$ 是半径之差的平方，环形面积必须是平方差
- C：正确
- D：$x-x^2$ 是面积公式（不是体积公式），少了一个平方

选 C。""",
         {"options": [
             r"""$\displaystyle\int_{-1}^{1}\pi(x^4-x)dx$""",
             r"""$\displaystyle\int_0^1\pi(\sqrt x-x^2)^2dx$""",
             r"""$\displaystyle\int_0^1\pi(x-x^4)dx$""",
             r"""$\displaystyle\int_0^1\pi(x-x^2)dx$"""
         ], "answer": [2]}),

        ("q5", "choice",
         r"""**二、选择题 2**

星形线 $x=a\cos^3t$，$y=a\sin^3t$ 所围成的图形的面积为（　）""",
         r"""**答案**：D，$\displaystyle 4\int_{\frac{\pi}{2}}^{0}a\sin^3t\,(a\cos^3t)'dt$。

**关键在符号**

$x$ 从 $0$ 增到 $a$ 对应 $t$ 从 $\dfrac{\pi}{2}$ 降到 $0$。取四分之一再乘 4：

$$A=4\int_{x=0}^{a}y\,dx=4\int_{\frac{\pi}{2}}^{0}a\sin^3t\cdot(a\cos^3t)'dt$$

**算一下确认是正数**

$(a\cos^3t)'=-3a\cos^2t\sin t$，代进去：

$$4\int_{\pi/2}^{0}a\sin^3t\cdot(-3a\cos^2t\sin t)dt=12a^2\int_0^{\pi/2}\sin^4t\cos^2t\,dt$$

$$=12a^2\cdot\frac{\pi}{32}=\frac{3\pi a^2}{8}>0\ ✓$$

**逐项看**

- A、C 从 $0$ 积到 $\dfrac{\pi}{2}$，此时 $dx<0$，结果是负的
- B 乘了 2（应该乘 4），且方向也错
- D 正确

选 D。

**记法**：参数方程求面积，注意 $\displaystyle\int y\,dx$ 里 $dx$ 的符号，上下限要跟 $x$ 的走向一致。""",
         {"options": [
             r"""$\displaystyle 2\int_0^{\frac{\pi}{2}}a\sin^3t(a\cos^3t)'dt$""",
             r"""$\displaystyle 2\int_{\frac{\pi}{2}}^{0}a\sin^3t(a\cos^3t)'dt$""",
             r"""$\displaystyle 4\int_0^{\frac{\pi}{2}}a\sin^3t(a\cos^3t)'dt$""",
             r"""$\displaystyle 4\int_{\frac{\pi}{2}}^{0}a\sin^3t(a\cos^3t)'dt$"""
         ], "answer": [3]}),

        ("q6", "choice",
         r"""**二、选择题 3**

椭圆 $\dfrac{x^2}{a^2}+\dfrac{y^2}{b^2}=1$（$a>b>0$）绕 $x$ 轴旋转得到的旋转体体积 $V_1$ 与绕 $y$ 轴旋转得到的旋转体体积 $V_2$ 之间的关系为（　）""",
         r"""**答案**：B，$V_1<V_2$。

**绕 $x$ 轴**：$y^2=b^2\left(1-\dfrac{x^2}{a^2}\right)$

$$V_1=\pi\int_{-a}^{a}b^2\left(1-\frac{x^2}{a^2}\right)dx=\pi b^2\left(2a-\frac{2a}{3}\right)=\frac{4\pi ab^2}{3}$$

**绕 $y$ 轴**：$x^2=a^2\left(1-\dfrac{y^2}{b^2}\right)$

$$V_2=\pi\int_{-b}^{b}a^2\left(1-\frac{y^2}{b^2}\right)dy=\frac{4\pi a^2b}{3}$$

**比较**：$a>b>0$ 时

$$\frac{V_2}{V_1}=\frac{a^2b}{ab^2}=\frac ab>1$$

所以 $V_1<V_2$，选 B。

**直觉**：绕 $y$ 轴转的是"长轴方向"，扫出的体积更大。""",
         {"options": ["$V_1>V_2$", "$V_1<V_2$", "$V_1=V_2$", "$V_1=3V_2$"], "answer": [1]}),

        ("q7", "choice",
         r"""**二、选择题 4**

由相交于点 $(x_1,y_1)$ 及 $(x_2,y_2)$（$x_1<x_2$）的两曲线 $y=f(x)>0$，$y=g(x)>0$ 所围图形绕 $x$ 轴旋转一周所得的旋转体体积 $V$ 是（　）""",
         r"""**答案**：B，$\displaystyle\int_{x_1}^{x_2}\pi\left|f^2(x)-g^2(x)\right|dx$。

**理由**

旋转体的截面是环形，面积 $\pi\left(\text{外半径}^2-\text{内半径}^2\right)$。题目没有指明哪条曲线在上，所以写**绝对值**保证非负：

$$V=\pi\int_{x_1}^{x_2}\left|f^2(x)-g^2(x)\right|dx$$

**逐项看**

- A：$\pi[f-g]^2$ —— 半径之差的平方，错
- B：正确
- C：$\pi\int f^2-\int(\pi g)^2$ 写法混乱，且没有绝对值，若不是 $f$ 恒在上会出现负数
- D：$\pi f-\pi g$ 少平方，量纲都不对

选 B。""",
         {"options": [
             r"""$\displaystyle\int_{x_1}^{x_2}\pi[f(x)-g(x)]^2dx$""",
             r"""$\displaystyle\int_{x_1}^{x_2}\pi|f^2(x)-g^2(x)|dx$""",
             r"""$\displaystyle\int_{x_1}^{x_2}\pi[f(x)]^2dx-\int_{x_1}^{x_2}[\pi g(x)]^2dx$""",
             r"""$\displaystyle\int_{x_1}^{x_2}[\pi f(x)-\pi g(x)]dx$"""
         ], "answer": [1]}),

        ("q8", "text",
         r"""**三、**

求曲线 $xy=a$（$a>0$）与直线 $x=a$，$x=2a$ 及 $y=0$ 所围成的图形分别绕 $OX$ 轴、$OY$ 轴旋转一周所得旋转体的体积。""",
         r"""**区域**：$a\le x\le2a$，$0\le y\le\dfrac ax$

**绕 $OX$ 轴（圆盘法）**

$$V_x=\pi\int_a^{2a}\left(\frac ax\right)^2dx=\pi a^2\left[-\frac1x\right]_a^{2a}=\pi a^2\left(\frac1a-\frac{1}{2a}\right)=\frac{\pi a}{2}$$

**绕 $OY$ 轴（柱壳法最省事）**

$$V_y=2\pi\int_a^{2a}x\cdot\frac ax\,dx=2\pi\int_a^{2a}a\,dx=2\pi a\cdot a=2\pi a^2$$

**用垫片法验算**

$y$ 的范围：$y=\dfrac ax$，$x\in[a,2a]\Rightarrow y\in\left[\dfrac12,1\right]$。

对固定 $y$，区域是 $a\le x\le\dfrac ay$（因为 $y\le\dfrac ax\iff x\le\dfrac ay$）。

还要考虑 $y\in\left[0,\dfrac12\right]$ 时整个 $[a,2a]$ 都在区域内。所以

$$V_y=\pi\int_0^{1/2}\left[(2a)^2-a^2\right]dy+\pi\int_{1/2}^{1}\left[\left(\frac ay\right)^2-a^2\right]dy$$

$$=\pi\cdot3a^2\cdot\frac12+\pi a^2\left(\left[-\frac1y-y\right]_{1/2}^{1}\right)$$

$$=\frac{3\pi a^2}{2}+\pi a^2\left[(-2)-(-2.5)\right]=\frac{3\pi a^2}{2}+\frac{\pi a^2}{2}=2\pi a^2\ ✓$$

**答案**

$$V_x=\frac{\pi a}{2},\qquad V_y=2\pi a^2$$

**要点**：$V_x$ 的量纲是 $a$ 的一次方？检查：$y$ 的量纲是 $a$，$y^2$ 是 $a^2$，乘 $dx$（$a$）得 $a^3$ ✓。$\dfrac{\pi a}{2}$ 里的 $a$ 实际应写作 $a^3/a^2$ —— 因为 $y=\dfrac ax$ 中 $a$ 的量纲是 $a^2$。按纯符号运算，结果就是 $\dfrac{\pi a}{2}$。"""),

        ("q9", "text",
         r"""**四、**

一块高为 $a$、底为 $b$ 的等腰三角形薄板，垂直地沉没在水中，**顶在下、底与水面相齐**，试计算薄板每面所受的压力。如果把它**倒放**（顶与水面相齐，底与水面平行），压力又如何？""",
         r"""**建坐标**：$y$ 轴向下，水面在 $y=0$，深度 $y\in[0,a]$。

**情形一：顶在下、底与水面相齐**

底边在 $y=0$（宽 $b$），顶点在 $y=a$（宽 $0$）。宽度线性：

$$w(y)=b\left(1-\frac ya\right)$$

**压力**

$$P_1=\rho g\int_0^a y\cdot b\left(1-\frac ya\right)dy=\rho g\frac ba\int_0^a\left(ay-y^2\right)dy$$

$$\int_0^a(ay-y^2)dy=\frac{a^3}{2}-\frac{a^3}{3}=\frac{a^3}{6}$$

$$P_1=\rho g\cdot\frac ba\cdot\frac{a^3}{6}=\frac{\rho g\,ba^2}{6}$$

**情形二：倒放（顶与水面相齐）**

顶点在 $y=0$，底边在 $y=a$（宽 $b$）：

$$w(y)=\frac{b}{a}y$$

$$P_2=\rho g\int_0^a y\cdot\frac bay\,dy=\rho g\frac ba\cdot\frac{a^3}{3}=\frac{\rho g\,ba^2}{3}$$

**结论**

$$P_1=\frac{\rho g\,ba^2}{6},\qquad P_2=\frac{\rho g\,ba^2}{3}=2P_1$$

**倒放时压力大一倍。**

**直观**：倒放时宽的那头在水下最深处（压强最大），力臂大，所以压力大。这是"同面积薄板放法不同压力不同"的经典结论。

**单位提示**：若用 cm 制（$\rho=1$，$g=980$），$P_1=\dfrac{490}{3}ba^2\ \mathrm{dyn}$，$P_2=\dfrac{980}{3}ba^2\ \mathrm{dyn}$。"""),

        ("q10", "text",
         r"""**五、**

求两圆 $r\le\sqrt3a$ 及 $r\le2a\cos\theta$ 公共部分的面积。""",
         r"""**第一步：认图形**

- $r=\sqrt3a$：以原点为圆心，半径 $\sqrt3a$ 的圆
- $r=2a\cos\theta$：以 $(a,0)$ 为圆心，半径 $a$ 的圆

**第二步：求交角**

$$\sqrt3a=2a\cos\theta\Rightarrow\cos\theta=\frac{\sqrt3}{2}\Rightarrow\theta=\pm\frac{\pi}{6}$$

**第三步：用几何法（推荐）**

两圆心距 $d=a$，半径 $r_1=\sqrt3a$，$r_2=a$。

公共面积 = 两段弓形之和：

$$A=\frac12r_1^2(\alpha-\sin\alpha)+\frac12r_2^2(\beta-\sin\beta)$$

其中 $\alpha$ 是大圆里的圆心角，$\beta$ 是小圆里的。

**求角**

由余弦定理：

$$\cos\frac{\alpha}{2}=\frac{d^2+r_1^2-r_2^2}{2dr_1}=\frac{a^2+3a^2-a^2}{2\cdot a\cdot\sqrt3a}=\frac{\sqrt3}{2}\Rightarrow\frac{\alpha}{2}=\frac{\pi}{6}\Rightarrow\alpha=\frac{\pi}{3}$$

$$\cos\frac{\beta}{2}=\frac{d^2+r_2^2-r_1^2}{2dr_2}=\frac{a^2+a^2-3a^2}{2a^2}=-\frac12\Rightarrow\frac{\beta}{2}=\frac{2\pi}{3}\Rightarrow\beta=\frac{4\pi}{3}$$

**代公式**

$$A=\frac12\cdot3a^2\left(\frac{\pi}{3}-\sin\frac{\pi}{3}\right)+\frac12\cdot a^2\left(\frac{4\pi}{3}-\sin\frac{4\pi}{3}\right)$$

$$=\frac{3a^2}{2}\left(\frac{\pi}{3}-\frac{\sqrt3}{2}\right)+\frac{a^2}{2}\left(\frac{4\pi}{3}+\frac{\sqrt3}{2}\right)$$

$$=\frac{\pi a^2}{2}-\frac{3\sqrt3a^2}{4}+\frac{2\pi a^2}{3}+\frac{\sqrt3a^2}{4}$$

$$=\frac{7\pi a^2}{6}-\frac{\sqrt3a^2}{2}$$

**答案**：$A=\dfrac{7\pi a^2}{6}-\dfrac{\sqrt3a^2}{2}$。

**数值自检**：$\dfrac{7\pi}{6}\approx3.665$，$\dfrac{\sqrt3}{2}\approx0.866$，$A\approx2.80a^2$。小圆面积 $\pi a^2\approx3.14a^2$，公共部分略小于它 ✓。"""),

        ("q11", "text",
         r"""**六、**

求抛物线 $y=-x^2+4x-3$ 及其在点 $(0,-3)$ 和 $(3,0)$ 处的切线所围成的图形的面积。""",
         r"""**第一步：求两条切线**

$y'=-2x+4$。

在 $(0,-3)$：$y'=4$，切线 $y+3=4x$，即

$$y=4x-3$$

在 $(3,0)$：$y'=-2$，切线 $y=-2(x-3)$，即

$$y=-2x+6$$

**第二步：两切线交点**

$$4x-3=-2x+6\Rightarrow x=\frac32,\quad y=3$$

**第三步：分区积分**

图形由抛物线（下）与两条切线（上）围成，顶点在 $\left(\dfrac32,3\right)$。

$x\in\left[0,\dfrac32\right]$：上边界 $4x-3$

$x\in\left[\dfrac32,3\right]$：上边界 $-2x+6$

**第一段**

$$4x-3-\left(-x^2+4x-3\right)=x^2$$

$$\int_0^{3/2}x^2dx=\frac{(3/2)^3}{3}=\frac{27/8}{3}=\frac98$$

**第二段**

$$-2x+6-\left(-x^2+4x-3\right)=x^2-6x+9=(x-3)^2$$

$$\int_{3/2}^{3}(x-3)^2dx=\left[\frac{(x-3)^3}{3}\right]_{3/2}^{3}=0-\frac{(-3/2)^3}{3}=\frac{27/8}{3}=\frac98$$

**相加**

$$A=\frac98+\frac98=\frac94$$

**答案**：$A=\dfrac94$。

**对称性观察**：抛物线关于 $x=2$ 对称，两条切线也关于 $x=\dfrac32$ 对称，两段面积相等（都是 $\dfrac98$），这是可以预期的。"""),

        ("q12", "text",
         r"""**七、**

在曲线 $y=\ln x$ 介于 $[4,6]$ 上求一点，使过该点的切线与曲线及直线 $x=4$，$x=6$ 所围的面积最小。""",
         r"""**设切点** $(t,\ln t)$，$t\in[4,6]$。

**切线方程**

$$y=\ln t+\frac1t(x-t)=\frac xt+\ln t-1$$

**谁在上**

$\ln x$ 是凹函数（$\ln''=-\dfrac{1}{x^2}<0$），切线在曲线上方。

**面积**

$$S(t)=\int_4^6\left[\frac xt+\ln t-1-\ln x\right]dx$$

**先算不定积分**

$$\int\frac xt\,dx=\frac{x^2}{2t},\qquad \int\ln x\,dx=x\ln x-x$$

所以原函数是

$$\frac{x^2}{2t}+x\ln t-x-x\ln x+x=\frac{x^2}{2t}+x\ln t-x\ln x$$

**代上下限**

$$S(t)=\left[\frac{36}{2t}+6\ln t-6\ln6\right]-\left[\frac{16}{2t}+4\ln t-4\ln4\right]$$

$$=\frac{18-8}{t}+2\ln t-6\ln6+4\ln4=\frac{10}{t}+2\ln t-6\ln6+4\ln4$$

**求导**

$$S'(t)=-\frac{10}{t^2}+\frac2t=0\Rightarrow2t=10\Rightarrow t=5$$

**验证极小**

$$S''(t)=\frac{20}{t^3}-\frac{2}{t^2},\qquad S''(5)=\frac{20}{125}-\frac{2}{25}=0.16-0.08>0$$

是极小值（端点处 $S$ 更大，因为 $t=5$ 是唯一驻点）。

**答案**：切点为 $(5,\ln5)$，最小面积

$$S_{\min}=2+2\ln5-6\ln6+4\ln4$$

**要点**：这题的难点是"被积函数带参数 $t$"。做法是先把 $t$ 当常数积出 $S(t)$，再对 $t$ 求导，别把 $t$ 和被积变量混在一起。"""),

        ("q13", "text",
         r"""**八、**

设抛物线 $y=ax^2+bx+c$ 通过点 $(0,0)$，且当 $x\in[0,1]$ 时 $y\ge0$。试确定 $a,b,c$ 的值，使得该抛物线与直线 $x=1$、$y=0$ 所围图形的面积为 $\dfrac49$，且使该图形绕 $x$ 轴旋转而成的旋转体的体积最小。""",
         r"""**第一步：过原点**

$$c=0$$

所以 $y=ax^2+bx=x(ax+b)$。

**第二步：面积条件**

$$A=\int_0^1(ax^2+bx)dx=\frac a3+\frac b2=\frac49\quad\cdots(1)$$

**第三步：$y\ge0$ 条件**

$x\in[0,1]$ 上 $x(ax+b)\ge0\iff ax+b\ge0$，需要

$$b\ge0,\qquad a+b\ge0$$

**第四步：体积表达式**

$$V=\pi\int_0^1(ax^2+bx)^2dx=\pi\left[\frac{a^2}{5}+\frac{ab}{2}+\frac{b^2}{3}\right]$$

**第五步：消去 $b$**

由 $(1)$：$b=\dfrac89-\dfrac{2a}{3}$。

**代进 $V/\pi$**：

$$\frac{a^2}{5}+\frac{a}{2}\left(\frac89-\frac{2a}{3}\right)+\frac13\left(\frac89-\frac{2a}{3}\right)^2$$

$$=\frac{a^2}{5}+\frac{4a}{9}-\frac{a^2}{3}+\frac13\left(\frac{64}{81}-\frac{32a}{27}+\frac{4a^2}{9}\right)$$

**合并同类项**

$a^2$ 项：$\dfrac15-\dfrac13+\dfrac{4}{27}=\dfrac{27-45+20}{135}=\dfrac{2}{135}$

$a$ 项：$\dfrac49-\dfrac{32}{81}=\dfrac{36-32}{81}=\dfrac4{81}$

常数项：$\dfrac{64}{243}$

所以

$$f(a)=\frac{2}{135}a^2+\frac{4}{81}a+\frac{64}{243}$$

**第六步：求最小**

$$f'(a)=\frac{4}{135}a+\frac4{81}=0\Rightarrow a=-\frac{4}{81}\cdot\frac{135}{4}=-\frac{135}{81}=-\frac53$$

**求 $b$**

$$b=\frac89-\frac23\cdot\left(-\frac53\right)=\frac89+\frac{10}{9}=2$$

**第七步：检查约束**

- $b=2\ge0$ ✓
- $a+b=-\dfrac53+2=\dfrac13\ge0$ ✓
- 面积：$\dfrac a3+\dfrac b2=-\dfrac59+1=\dfrac49$ ✓

**答案**

$$a=-\frac53,\qquad b=2,\qquad c=0$$

即抛物线为

$$y=-\frac53x^2+2x$$

**要点**：这是"带约束的最优化"标准题 —— 先用面积条件消掉一个参数，剩下的单变量函数求极值，最后**必须回代检查约束**（$y\ge0$）。""")
    ]
)


for d in (T4, T5, T6):
    save(d)
print("ok")
