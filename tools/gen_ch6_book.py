# -*- coding: utf-8 -*-
"""第六章 定积分的应用 —— 课本三节（6.1 元素法 / 6.2 几何应用 / 6.3 物理应用）"""
import json, os

OUT = r"C:/Users/chong/Documents/studyhub/content/lessons"


def save(d):
    p = os.path.join(OUT, d["id"].replace("/", "_") + ".json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    print("written", p, len(d["cards"]), "cards")


# ============================================================
# 6.1 定积分的元素法
# ============================================================
L61 = {
    "id": "math/6-1",
    "title": "6.1 定积分的元素法",
    "subtitle": "从四步到一步 · 微元怎么取 · 误差必须 o(dx)",
    "cards": [
        {
            "id": "c1",
            "type": "lecture",
            "title": "元素法是什么",
            "md": r"""## 一句话

定积分能算的东西都长一个样：**某个量 $U$ 分布在一个区间上，而且能按区间相加**。面积、体积、弧长、变力做功、水压力，全是这一类。

## 记号怎么来的

设 $U$ 对应区间 $[a,x]$（$U$ 随 $x$ 变）。在 $[x,x+dx]$ 上取一小段，若

$$\Delta U \approx f(x)\,dx,\qquad \Delta U-f(x)\,dx=o(dx)$$

则

$$U=\int_a^b f(x)\,dx$$

那个 $f(x)\,dx$ 就叫 **元素**（微元），记作 $dU$。

## 三个前提

1. **可加性**：区间分成若干段，$U$ 等于各段之和
2. **在 $[x,x+dx]$ 上"以常代变"**：能拿 $x$ 处的值当整段的值
3. **误差是 $dx$ 的高阶无穷小**：这一条最容易忘，也是元素法合法的真正条件

## 教材四步 vs 做题三步

教材写的是「分割、近似、求和、取极限」，做题时压成三步：

| 教材 | 做题 |
|---|---|
| 分割 | 选积分变量、定区间（看交点） |
| 近似、求和、取极限 | 直接写微元 $dU=f(x)dx$，再积 $U=\int_a^b dU$ |

**第 2 步才是这章的全部技术含量**：把图形当成矩形、薄片、薄层算，写出 $dU$。
"""
        },
        {
            "id": "c2",
            "type": "choice",
            "question": r"""关于元素法，下列说法**正确**的是（　）""",
            "options": [
                r"""$dU$ 与 $\Delta U$ 可以相差一个与 $dx$ 同阶的量，只要最后取极限就行""",
                r"""$dU=f(x)dx$ 中的 $f(x)$ 必须取在小区间 $[x,x+dx]$ 上的最大值""",
                r"""元素法要求 $\Delta U-f(x)dx$ 是 $dx$ 的高阶无穷小，否则积分出来不是 $U$""",
                r"""元素法只适用于求面积，求体积和弧长要用别的方法"""
            ],
            "answer": [2],
            "explain": r"""**答案：第三项。**

逐条看：

- **第一项错**：如果误差只是 $o(1)$ 或者与 $dx$ 同阶，累加起来不会消失，积分出来的就不是 $U$。必须是 $o(dx)$，累加后才有 $\sum o(dx)\to 0$。
- **第二项错**：取哪一点都行（左端点、右端点、中点），因为连续函数在 $[x,x+dx]$ 上变化量是 $o(1)$，乘 $dx$ 后就是 $o(dx)$。习惯上取左端点 $x$。
- **第三项对**：这就是元素法成立的核心条件。
- **第四项错**：元素法是万能框架，面积、体积、弧长、功、压力、引力全都用它，只是 $dU$ 长得不同。"""
        },
        {
            "id": "c3",
            "type": "blank",
            "question": r"""设平面图形由 $y=y_2(x)$（上）与 $y=y_1(x)$（下）在 $a\le x\le b$ 上围成。

用元素法，面积元素 $dA=$ ____，面积 $A=$ ____。""",
            "blanks": [["(y_2(x)-y_1(x))dx", "[y_2(x)-y_1(x)]dx", "(y_2-y_1)dx"],
                       ["\\int_a^b[y_2(x)-y_1(x)]dx", "\\int_a^b (y_2(x)-y_1(x))dx"]],
            "explain": r"""**第一空**：在 $[x,x+dx]$ 上，图形近似是一个宽 $dx$、高 $y_2(x)-y_1(x)$ 的窄条，所以

$$dA=[y_2(x)-y_1(x)]\,dx$$

**第二空**：把窄条从 $a$ 累加到 $b$：

$$A=\int_a^b[y_2(x)-y_1(x)]\,dx$$

一句话记法：**上减下，右端点减左端点**。

误差检验：真实面积与矩形面积之差是高阶小量（高在 $dx$ 内变化 $\le Mdx$，面积差 $\le M(dx)^2=o(dx)$），所以元素法合法。"""
        },
        {
            "id": "c4",
            "type": "text",
            "question": r"""用元素法写出「由曲线 $y=f(x)$、直线 $x=a$、$x=b$ 及 $x$ 轴围成的图形绕 $x$ 轴旋转所得旋转体的体积元素」，并说明为什么是 $\pi f^2(x)dx$ 而不是 $2\pi f(x)dx$。""",
            "explain": r"""**体积元素**

在 $[x,x+dx]$ 上，旋转体是一个**薄圆盘**：半径 $f(x)$，厚 $dx$。所以

$$dV=\pi f^2(x)\,dx,\qquad V=\pi\int_a^b f^2(x)\,dx$$

**为什么不是 $2\pi f(x)dx$**

- $2\pi f(x)$ 是圆盘的**周长**，不是面积。拿周长乘 $dx$ 得到的是"侧面积"，量纲也不对（长度²而非长度³）。
- 圆盘面积是 $\pi f^2(x)$，厚度 $dx$，才有体积量纲（长度³）。
- $2\pi x f(x)dx$ 那个是**柱壳法**的体积元素（绕 $y$ 轴时用），半径是 $x$ 不是 $f(x)$。

**误差**：薄圆盘与真实薄片的差来自 $f$ 在 $dx$ 内的变化，体积差 $O(dx^2)=o(dx)$，合法。"""
        }
    ]
}


# ============================================================
# 6.2 定积分在几何学上的应用
# ============================================================
L62 = {
    "id": "math/6-2",
    "title": "6.2 定积分在几何学上的应用",
    "subtitle": "面积 · 体积 · 弧长 · 三种坐标系",
    "cards": [
        {
            "id": "c1",
            "type": "lecture",
            "title": "平面图形的面积",
            "md": r"""## 一、直角坐标：上减下

由 $y_2(x)\ge y_1(x)$ 在 $[a,b]$ 上围成：

$$A=\int_a^b\big[y_2(x)-y_1(x)\big]dx$$

如果边界更适合写成 $x$ 的函数（左右两条曲线），就对 $y$ 积分：

$$A=\int_c^d\big[x_2(y)-x_1(y)\big]dy\quad(\text{右减左})$$

**例**：$y=x^2$ 与 $y=x$ 围成。交点 $(0,0),(1,1)$，在 $(0,1)$ 上 $x\ge x^2$：

$$A=\int_0^1(x-x^2)dx=\frac12-\frac13=\frac16$$

## 二、极坐标：$\frac12\rho^2d\theta$

曲边扇形的一个小扇形元素

$$dA=\frac12\rho^2(\theta)\,d\theta\ \Longrightarrow\ A=\frac12\int_\alpha^\beta\rho^2(\theta)\,d\theta$$

**例 1** 心形线 $\rho=a(1+\cos\theta)$ 所围面积：

$$A=\frac12\int_0^{2\pi}a^2(1+\cos\theta)^2d\theta=\frac{a^2}{2}\cdot3\pi=\frac{3\pi a^2}{2}$$

（用到 $\int_0^{2\pi}\cos\theta\,d\theta=0$，$\int_0^{2\pi}\cos^2\theta\,d\theta=\pi$。）

**例 2** $\rho=3\cos\theta$ 与 $\rho=1+\cos\theta$ 的公共部分面积 $=\dfrac{5\pi}{4}$。做法：先求交角 $\pm\dfrac{\pi}{3}$，再分区间取"里层那条曲线"当 $\rho$。

## 三、注意两个坑

1. **极坐标的 $\rho$ 必须是该角度下真正的外边界**。两条曲线围成的公共区域，$\rho$ 要取小的那个（公共部分），或者按角度分段。
2. **面积永远是正的**。用参数方程算时 $dx$ 可能为负，记得取绝对值或调换上下限。"""
        },
        {
            "id": "c2",
            "type": "lecture",
            "title": "体积与弧长",
            "md": r"""## 一、旋转体体积

### 圆盘法（垫片法）：绕 $x$ 轴

$$V_x=\pi\int_a^b f^2(x)\,dx$$

两条曲线之间：

$$V_x=\pi\int_a^b\big[f^2(x)-g^2(x)\big]dx\quad(\text{外半径平方减内半径平方})$$

绕 $y$ 轴同理，写成 $y$ 的函数：$V_y=\pi\int_c^d\big[\varphi^2(y)-\psi^2(y)\big]dy$。

### 柱壳法：绕 $y$ 轴，但函数是 $y=f(x)$

$$V_y=2\pi\int_a^b x\,f(x)\,dx$$

道理：半径 $x$ 处一圈薄壳，周长 $2\pi x$，高 $f(x)$，厚 $dx$。

**例**：$y=\sin x$（$0\le x\le\pi$）与 $x$ 轴绕 $y$ 轴：

$$V_y=2\pi\int_0^\pi x\sin x\,dx=2\pi\big[{-x\cos x+\sin x}\big]_0^\pi=2\pi\cdot\pi=2\pi^2$$

### 已知平行截面面积

$$V=\int_a^b A(x)\,dx$$

## 二、弧长

| 曲线形式 | 弧长公式 |
|---|---|
| $y=f(x)$ | $s=\displaystyle\int_a^b\sqrt{1+y'^2}\,dx$ |
| $\begin{cases}x=\varphi(t)\\y=\psi(t)\end{cases}$ | $s=\displaystyle\int_\alpha^\beta\sqrt{\varphi'^2+\psi'^2}\,dt$ |
| $\rho=\rho(\theta)$ | $s=\displaystyle\int_\alpha^\beta\sqrt{\rho^2+\rho'^2}\,d\theta$ |

**三个标准结果，背下来**

- 星形线 $x=a\cos^3t,\ y=a\sin^3t$：面积 $\dfrac{3\pi a^2}{8}$，全长 $6a$
- 心形线 $\rho=a(1+\cos\theta)$：面积 $\dfrac{3\pi a^2}{2}$，全长 $8a$
- 摆线一拱：面积 $3\pi a^2$，弧长 $8a$

## 三、弧长里最容易丢分的一步

开方之后是 $\sqrt{\cdots}=|\cdots|$，**绝对值不能直接扔**。处理办法：

1. 用对称性把区间切到第一象限（或 $\theta\in[0,\pi]$），那里正负确定
2. 或者分区间讨论

星形线、心形线、圆、椭圆都能靠对称性绕过绝对值。"""
        },
        {
            "id": "c3",
            "type": "choice",
            "question": r"""曲线 $y=\ln x$ 与 $y$ 轴、直线 $y=\ln a$、$y=\ln b$（$0<a<b$）所围图形的面积为（　）""",
            "options": [r"""$b-a$""", r"""$\ln\dfrac{b}{a}$""", r"""$b-a-\ln\dfrac{b}{a}$""", r"""$a-b$"""],
            "answer": [0],
            "explain": r"""**答案：$b-a$。**

边界更适合写成 $x$ 的函数：从 $y=\ln x$ 得 $x=e^y$，而 $y$ 轴就是 $x=0$。对 $y$ 积分（右减左）：

$$A=\int_{\ln a}^{\ln b}(e^y-0)\,dy=\big[e^y\big]_{\ln a}^{\ln b}=b-a$$

**换个看法**：$\ln x$ 与 $y$ 轴围成的区域，把坐标轴交换就是 $y=e^x$ 下方面积，$\int_{\ln a}^{\ln b}e^y dy=b-a$。

选第二项是把"面积"误当成了"$\ln$ 的差"；第三项是多减了一块。"""
        },
        {
            "id": "c4",
            "type": "choice",
            "question": r"""曲线 $y=x^2$ 与 $x=y^2$ 所围图形绕 $x$ 轴旋转所得体积为（　）""",
            "options": [
                r"""$\pi\displaystyle\int_0^1(\sqrt{x}-x^2)^2dx$""",
                r"""$\pi\displaystyle\int_0^1(x-x^4)dx$""",
                r"""$\pi\displaystyle\int_0^1(x^2-\sqrt{x})^2dx$""",
                r"""$\pi\displaystyle\int_0^1(x^4-x)dx$"""
            ],
            "answer": [1],
            "explain": r"""**答案：第二项。**

两曲线交点 $(0,0)$、$(1,1)$。在 $0<x<1$ 上，$y=\sqrt{x}$ 在 $y=x^2$ 上方。

绕 $x$ 轴用垫片法：**外半径平方减内半径平方**

$$V=\pi\int_0^1\big[(\sqrt{x})^2-(x^2)^2\big]dx=\pi\int_0^1(x-x^4)dx=\pi\Big(\frac12-\frac15\Big)=\frac{3\pi}{10}$$

**错项分析**

- 第一项：把"半径之差"平方了。垫片是环形，面积是 $\pi(R^2-r^2)$，不是 $\pi(R-r)^2$。
- 第三项：内外半径颠倒，且同样平方错。
- 第四项：$x^4-x$ 在被积区间为负，体积不可能为负。"""
        },
        {
            "id": "c5",
            "type": "blank",
            "question": r"""星形线 $x=a\cos^3t,\ y=a\sin^3t\ (a>0)$ 所围图形的面积 $A=$ ____，全长 $s=$ ____。""",
            "blanks": [["\\frac{3\\pi a^2}{8}", "3\\pi a^2/8", "3/8\\pi a^2"],
                       ["6a"]],
            "explain": r"""**面积**

四分之一区域（第一象限）的面积，用参数方程：

$$A=4\int_0^{a}y\,dx\quad(\text{换成 }t)$$

$x$ 从 $0$ 到 $a$ 对应 $t$ 从 $\dfrac{\pi}{2}$ 到 $0$，$dx=-3a\cos^2t\sin t\,dt$，所以

$$A=4\int_{\pi/2}^{0}a\sin^3t\cdot(-3a\cos^2t\sin t)\,dt=12a^2\int_0^{\pi/2}\sin^4t\cos^2t\,dt$$

$$\int_0^{\pi/2}\sin^4t\cos^2t\,dt=\frac{\pi}{32}\ \Longrightarrow\ A=12a^2\cdot\frac{\pi}{32}=\frac{3\pi a^2}{8}$$

**全长**

$$dx=-3a\cos^2t\sin t\,dt,\qquad dy=3a\sin^2t\cos t\,dt$$

$$ds=\sqrt{dx^2+dy^2}=3a|\sin t\cos t|\,dt$$

用对称性，取第一象限再乘 4（那里 $\sin t\cos t\ge0$，绝对值可去）：

$$s=4\int_0^{\pi/2}3a\sin t\cos t\,dt=12a\cdot\frac12=6a$$

**记法**：星形线面积 $\dfrac{3\pi a^2}{8}$、周长 $6a$，两个都要背。"""
        },
        {
            "id": "c6",
            "type": "text",
            "question": r"""求摆线 $\begin{cases}x=a(t-\sin t)\\y=a(1-\cos t)\end{cases}$ 的一拱（$0\le t\le 2\pi$）与 $x$ 轴所围成的面积，以及这一拱的弧长。""",
            "explain": r"""**面积**

$$A=\int_0^{2\pi}y\,dx=\int_0^{2\pi}a(1-\cos t)\cdot a(1-\cos t)\,dt=a^2\int_0^{2\pi}(1-\cos t)^2dt$$

展开：

$$(1-\cos t)^2=1-2\cos t+\cos^2 t$$

$$\int_0^{2\pi}1\,dt=2\pi,\quad \int_0^{2\pi}\cos t\,dt=0,\quad \int_0^{2\pi}\cos^2t\,dt=\pi$$

$$A=a^2(2\pi+\pi)=3\pi a^2$$

**弧长**

$$dx=a(1-\cos t)dt,\qquad dy=a\sin t\,dt$$

$$ds=a\sqrt{(1-\cos t)^2+\sin^2t}\,dt=a\sqrt{2-2\cos t}\,dt=2a\left|\sin\frac t2\right|dt$$

在 $[0,2\pi]$ 上 $\sin\dfrac t2\ge0$，去掉绝对值：

$$s=\int_0^{2\pi}2a\sin\frac t2\,dt=2a\Big[-2\cos\frac t2\Big]_0^{2\pi}=2a\cdot4=8a$$

**注意**：这里用了半角公式 $1-\cos t=2\sin^2\dfrac t2$，是摆线的标准套路。"""
        }
    ]
}


# ============================================================
# 6.3 定积分在物理学上的应用
# ============================================================
L63 = {
    "id": "math/6-3",
    "title": "6.3 定积分在物理学上的应用",
    "subtitle": "变力做功 · 水压力 · 引力",
    "cards": [
        {
            "id": "c1",
            "type": "lecture",
            "title": "三类物理量的元素法",
            "md": r"""## 一、变力做功

恒力做功 $W=F\cdot s$；力随位置变化时用元素法：

$$dW=F(x)\,dx\ \Longrightarrow\ W=\int_a^b F(x)\,dx$$

**三个常见模型**

1. **弹簧**：$F=kx$（$x$ 为伸长量），$W=\displaystyle\int_0^{s}kx\,dx=\frac12ks^2$
2. **抽水**：把一层水（体积 $dV$）提到池口，提升距离 $h(y)$
 $$dW=\rho g\,A(y)\,h(y)\,dy$$
3. **气体膨胀**：$W=\displaystyle\int_{V_1}^{V_2}p\,dV$

**单位**：SI 制里 $\rho=1000\ \mathrm{kg/m^3}$，$g=9.8\ \mathrm{m/s^2}$，$\rho g=9800\ \mathrm{N/m^3}$。

## 二、水压力

深度 $y$ 处压强 $p=\rho g y$。取一块水平窄条，宽 $w(y)$、高 $dy$：

$$dP=\rho g\,y\,w(y)\,dy\ \Longrightarrow\ P=\rho g\int_{y_1}^{y_2}y\,w(y)\,dy$$

**关键在 $w(y)$**：把薄板放在坐标系里，写出深度 $y$ 处的宽度。三角形、梯形、圆都要现推。

## 三、引力

细棒对质点的引力：

$$dF=\frac{G\,m\,\lambda\,dx}{r^2}$$

方向沿连线，往往要分解成 $x$、$y$ 分量再积分。

## 四、做题顺序

1. **画图，定坐标**（原点放水面、池口或支点，$\boldsymbol{y}$ 轴朝下或朝上想清楚）
2. **写几何关系**：$A(y)$、$w(y)$、$h(y)$ 用相似三角形推
3. **写微元**，注意单位统一（cm 与 m 别混）
4. **积分**，检查量纲和数量级"""
        },
        {
            "id": "c2",
            "type": "blank",
            "question": r"""弹簧拉伸时所需力 $F=ks$（$s$ 为伸长量，单位 m）。已知用 $5\,\mathrm{N}$ 的力可把它拉长 $0.01\,\mathrm{m}$。

则 $k=$ ____ $\mathrm{N/m}$；把弹簧从自然长度拉长 $0.1\,\mathrm{m}$ 所作的功 $W=$ ____ $\mathrm{J}$。""",
            "blanks": [["500"], ["2.5"]],
            "explain": r"""**求 $k$**

$$5=k\cdot0.01\ \Longrightarrow\ k=500\ \mathrm{N/m}$$

**求功**

力在过程中变化（$F=500s$），必须积分：

$$W=\int_0^{0.1}500s\,ds=500\cdot\frac{s^2}{2}\Big|_0^{0.1}=250\cdot0.01=2.5\ \mathrm{J}$$

**常见错误**：直接用 $W=F\cdot s=5\times0.1=0.5\ \mathrm{J}$。错在把 $0.1\,\mathrm{m}$ 处的力（$50\,\mathrm{N}$）当成了全程的力。变力必须积分。"""
        },
        {
            "id": "c3",
            "type": "text",
            "question": r"""一圆锥形贮水池，深 $15\,\mathrm{m}$，池口直径 $20\,\mathrm{m}$，盛满水。把水全部抽到池口，需作多少功？（$\rho g=9800\,\mathrm{N/m^3}$）""",
            "explain": r"""**建坐标系**

原点取池底，$y$ 轴向上，水面在 $y=15$。

**写半径**

池口半径 $10\,\mathrm{m}$，池底半径 $0$。相似三角形：

$$r(y)=\frac{10}{15}y=\frac{2y}{3}$$

**取水层**

高度 $y$ 处厚 $dy$ 的一层水，体积

$$dV=\pi r^2(y)\,dy=\pi\cdot\frac{4y^2}{9}\,dy$$

**提升高度**

这一层要提到池口，提升距离 $15-y$。

**微元与积分**

$$dW=\rho g\,dV\,(15-y)=9800\cdot\frac{4\pi y^2}{9}(15-y)\,dy$$

$$W=9800\cdot\frac{4\pi}{9}\int_0^{15}(15y^2-y^3)\,dy$$

$$\int_0^{15}(15y^2-y^3)dy=\frac{15\cdot15^3}{3}-\frac{15^4}{4}=\frac{15^4}{3}-\frac{15^4}{4}=\frac{15^4}{12}=4218.75$$

$$W=9800\cdot\frac{4\pi}{9}\cdot4218.75=9800\pi\cdot1875\approx5.77\times10^7\ \mathrm{J}$$

**答案**：$W=1.8375\times10^7\pi\ \mathrm{J}\approx5.77\times10^7\ \mathrm{J}$。

**检查**：水的总重 $\rho g\cdot\dfrac{\pi\cdot10^2\cdot15}{3}=9800\cdot500\pi\approx1.54\times10^7\ \mathrm{N}$，平均提升约 $\dfrac{15}{4}$ 米，乘积约 $5.8\times10^7\ \mathrm{J}$，量级吻合。"""
        }
    ]
}

for d in (L61, L62, L63):
    save(d)
print("ok")
