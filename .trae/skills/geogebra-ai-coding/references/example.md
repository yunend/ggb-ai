# 金标准示例：2025 全国一卷 17 题（四棱锥 + 球面）

本文件展示两阶段输出应长什么样。遇到题目时按此结构执行，禁止跳步。

## 题目

如图，在四棱锥 P-ABCD 中：
- PA ⊥ 底面 ABCD，AB ⊥ AD，BC ∥ AD
- (1) 证明：平面 PAB ⊥ 平面 PAD
- (2) 设 PA = AB = √2，BC = 2，AD = 1 + √3，且点 P、B、C、D 均在球 O 的球面上
  - (i) 证明：点 O 在平面 ABCD 内
  - (ii) 求直线 AC 与 PO 所成角的余弦值

## 阶段一：设计蓝图（示例输出格式）

### 条件清单
- 几何约束：PA ⊥ 底面 ABCD；AB ⊥ AD；BC ∥ AD；底面为四边形 ABCD；P 为顶点
- 给定数值：PA = AB = √2；BC = 2；AD = 1 + √3
- 动态关系：P、B、C、D 四点在同一个球面上（球心 O 未知）

### 坐标系与布局
- 以 A 为原点，AB 沿 x 轴，AD 沿 y 轴，PA 沿 z 轴（右手系）
- 底面 ABCD 落在 z = 0 平面；P 在 z 轴正方向上方

### 对象创建顺序与依赖
1. 数值参数：pa = √2，bc = 2，ad = 1 + √3（先定义，供后续引用）
2. 关键点：A(0,0,0) → B(pa,0,0) → D(0,ad,0) → C(pa,bc,0) → P(0,0,pa)
3. 棱：AB、AD、BC、CD、PA、PB、PC、PD
4. 面：底面四边形 ba + 四个侧面三角形 s1–s4
5. 球面构造（核心）：BC 中垂面 pb1 → BD 中垂面 pb2 → 交线 l1 → BP 中垂面 pb3 → 球心 O = 交线 l1 ∩ pb3 → 球面 s = Sphere(O, P)
6. 度量：向量 u = AC，v = PO；cos 值 cs；角度 an；z(O) 分量 cz
7. 文本：te 显示 z(O) 与 cos(∠AC,PO)

### 动态参数方案
- 静态模型（题目无动点，不需要滑块）

### 脚本书写
- 一行一条指令；确需多指令同行时，以英文分号分隔（见脚本中 SetColor(pb…) 一行）

### 颜色与标签方案
- 关键点 A、B、C、D、P、O：红色、大点、显示标签
- 棱：深灰 (0.10,0.10,0.10)，线宽 2
- 底面 ba：浅蓝填充 (0.80,0.90,1.00)；侧面 s1–s4：四种浅色区分
- 球面 s：蓝色 (0.25,0.50,0.90)
- 辅助中垂面 pb1–pb3：橙色 (0.90,0.60,0.10)，构建后从 3D 视图隐藏
- 除关键点外全部隐藏标签

### 待确认事项
- 本题条件完整，无需假设；若题目图片中 C 的位置有歧义，需先向用户确认 C 位于 B 沿 y 正向一侧

## 阶段二：GGB 脚本（确认后的输出示例）

```ggb

# ============ 2025 全国一卷 17 题 ============
# 四棱锥 P-ABCD: PA⊥底面, AB⊥AD, BC∥AD
# PA=AB=√2, BC=2, AD=1+√3, P,B,C,D 共球面 O
# 复刻目标: 观察 O 是否在平面 ABCD 内; 观察 AC 与 PO 所成角的余弦

# --- 视图（工具依赖，环境不支持可移除） ---
SetPerspective("T")

# --- 数值参数（先定义变量，禁止内嵌调用） ---
pa = sqrt(2)
bc = 2
ad = 1 + sqrt(3)

# --- 关键点 ---
A = Point({0, 0, 0})
ShowLabel(A, true)
B = Point({pa, 0, 0})
ShowLabel(B, true)
D = Point({0, ad, 0})
ShowLabel(D, true)
C = Point({pa, bc, 0})
ShowLabel(C, true)
P = Point({0, 0, pa})
ShowLabel(P, true)

# --- 棱（线段） ---
AB = Segment(A, B)
ShowLabel(AB, false)
AD = Segment(A, D)
ShowLabel(AD, false)
BC = Segment(B, C)
ShowLabel(BC, false)
CD = Segment(C, D)
ShowLabel(CD, false)
PA = Segment(P, A)
ShowLabel(PA, false)
PB = Segment(P, B)
ShowLabel(PB, false)
PC = Segment(P, C)
ShowLabel(PC, false)
PD = Segment(P, D)
ShowLabel(PD, false)

# --- 面 ---
ba = Polygon(A, B, C, D)
ShowLabel(ba, false)
s1 = Polygon(A, B, P)
ShowLabel(s1, false)
s2 = Polygon(A, D, P)
ShowLabel(s2, false)
s3 = Polygon(B, C, P)
ShowLabel(s3, false)
s4 = Polygon(C, D, P)
ShowLabel(s4, false)

# --- 球面构造（核心：中垂面相交得球心 O，不预写答案） ---
pb1 = PlaneBisector(BC)
ShowLabel(pb1, false)
pb2 = PlaneBisector(B,D)
ShowLabel(pb2, false)
l1 = Intersect(pb1, pb2)
ShowLabel(l1, false)
pb3 = PlaneBisector(B,P)
ShowLabel(pb3, false)
O = Intersect(l1, pb3)
ShowLabel(O, true)
s = Sphere(O, P)
ShowLabel(s, false)

# --- 度量（供用户自行观察，不写结论） ---
u = Vector(A, C)
ShowLabel(u, false)
v = Vector(P, O)
ShowLabel(v, false)
cs = abs(Dot(u, v)) / (abs(u) * abs(v))
an = acos(cs)
cz = z(O)
te = Text("z(O) = " + cz + "    cos(∠AC,PO) = " + cs, A)
ShowLabel(te, false)

# --- 颜色与线型（分明清晰，不与白底重叠） ---
SetColor(A, "(0.80, 0.15, 0.15)")
SetColor(B, "(0.80, 0.15, 0.15)")
SetColor(C, "(0.80, 0.15, 0.15)")
SetColor(D, "(0.80, 0.15, 0.15)")
SetColor(P, "(0.80, 0.15, 0.15)")
SetColor(O, "(0.80, 0.15, 0.15)")
SetPointSize(A, 3)
SetPointSize(B, 3)
SetPointSize(C, 3)
SetPointSize(D, 3)
SetPointSize(P, 3)
SetPointSize(O, 3)
SetColor(AB, "(0.10, 0.10, 0.10)")
SetColor(AD, "(0.10, 0.10, 0.10)")
SetColor(BC, "(0.10, 0.10, 0.10)")
SetColor(CD, "(0.10, 0.10, 0.10)")
SetColor(PA, "(0.10, 0.10, 0.10)")
SetColor(PB, "(0.10, 0.10, 0.10)")
SetColor(PC, "(0.10, 0.10, 0.10)")
SetColor(PD, "(0.10, 0.10, 0.10)")
SetLineThickness(AB, 2)
SetLineThickness(AD, 2)
SetLineThickness(BC, 2)
SetLineThickness(CD, 2)
SetLineThickness(PA, 2)
SetLineThickness(PB, 2)
SetLineThickness(PC, 2)
SetLineThickness(PD, 2)
SetColor(ba, "(0.80, 0.90, 1.00)")
SetColor(s1, "(0.95, 0.88, 0.78)")
SetColor(s2, "(0.88, 0.95, 0.80)")
SetColor(s3, "(0.95, 0.82, 0.90)")
SetColor(s4, "(0.82, 0.90, 0.95)")
SetColor(s, "(0.25, 0.50, 0.90)")
# 多指令同行时以英文分号分隔
SetColor(pb1, "(0.90, 0.60, 0.10)"); SetColor(pb2, "(0.90, 0.60, 0.10)"); SetColor(pb3, "(0.90, 0.60, 0.10)")
# 隐藏辅助中垂面，避免遮挡
SetConditionToShowObject(s,false)
SetConditionToShowObject(l1,false)
SetConditionToShowObject(pb1,false)
SetConditionToShowObject(pb2,false)
SetConditionToShowObject(pb3,false)

# STATE_TRACKER: {view:"3D", numbers:[pa,bc,ad,cs,an,cz], points:[A,B,C,D,P,O], segments:[AB,AD,BC,CD,PA,PB,PC,PD], polygons:[ba,s1,s2,s3,s4], planes:[pb1,pb2,pb3], lines:[l1], sphere:[s], vectors:[u,v], texts:[te]}

```

## 预期观察（仅用于 agent 自查模型是否正确，绝不写入脚本）

- 拖动/旋转视角：O 的 z 坐标显示为 0 → O 落在平面 ABCD 内（即 (i) 的可观察结论）
- cos(∠AC,PO) 显示 ≈ 0.4714，即 √2/3（(ii) 的答案）
- 四个顶点 P、B、C、D 全部贴在球面 s 上，拖动确认无缝隙
