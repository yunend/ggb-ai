# GGB-AI

> GeoGebra + AI 联合建模助手 · 纯静态 · 零构建 · 双击即用

一个把 **GeoGebra 原生引擎** 和 **AI 辅助建模工作流** 结合的数学可视化工具。输入数学题，AI 生成 GGB 脚本，一键批量执行，2D/3D 无缝切换。

## ✨ 核心特性

| 特性 | 说明 |
|---|---|
| **零构建** | 纯 HTML + CDN 依赖，无 npm、无打包、无编译 |
| **双击即用** | 直接 `file://` 打开 `index.html`，离线可用 |
| **本地 GeoGebra** | 内置 classic + web3d 完整资源，不依赖外部服务器 |
| **2D ⇄ 3D 切换** | 一键切换视角模式，自动重建实例 |
| **批量执行指令** | 每行一条 GGB 指令，支持错误暂停、单步确认、可调节执行间隔 |
| **智能错误判断** | 识别 GeoGebra classic 的 `evalCommand` 返回值 bug（脚本命令返回 false 但实际成功），结合 getError() 多轮检测 |
| **AI Prompt 复制** | 内置建模提示词，一键复制喂给 AI（配合 Trae Skill 使用） |
| **Trae Skill 集成** | `.trae/skills/ggb-math-modeler/` 提供两阶段蓝图→代码工作流 |

## 🚀 快速开始

### 方式一：本地直接打开（推荐）

双击 `index.html`，浏览器会以 `file://` 协议打开，GeoGebra 资源已内置在 `GeoGebra/` 目录下，无需联网。

### 方式二：本地 HTTP 服务（某些浏览器限制 file:// 下的脚本加载）

    # Python 内置 server
    python -m http.server 8080

    # 或 Node
    npx serve -l 8080 .

然后浏览器访问 `http://localhost:8080` 。

## 📁 项目结构

    ggb-ai/
    ├── index.html                    # 唯一入口（单文件 Vue 应用）
    ├── logo.ico
    ├── GeoGebra/                     # 本地 GeoGebra 引擎（离线资源）
    │   ├── deployggb.js              #   加载器
    │   └── HTML5/5.0/
    │       ├── GeoGebra.html         #   原始 applet 页面
    │       ├── web/                  #   2D classic 资源
    │       └── web3d/                #   3D 资源
    ├── js/                           # 外部依赖（需自行下载）
    │   ├── vue@3.5.13-global-prod.js
    │   ├── tailwind@3.4.17.js
    │   ├── constants.js
    │   ├── geogebra.js
    │   └── code-panel.js
    └── .trae/skills/
        └── geogebra-ai-coding/       # Trae IDE Skill（AI 辅助建模）
            ├── SKILL.md
            ├── references/
            │   ├── example.md        #   2025卷1_17题完整范例
            │   ├── ggb-codebook.md   #   对象缩写表
            │   └── ggb-commands.md   #   压缩命令表
            └── scripts/
                └── validate_ggb.py   #   GGB 脚本校验器

## 🛠️ 使用流程

    ┌─────────────────────────────────────────────────────┐
    │  1. 点击导航栏「Prompt」→ 复制 AI 建模提示词         │
    │  2. 把题目（图片或文字）发给 AI，让它生成 GGB 脚本   │
    │  3. 把脚本粘贴到左侧「代码面板」                     │
    │  4. 点击「执行」→ 右侧画布实时渲染                  │
    │  5. 遇到错误自动暂停，可单步确认或跳过               │
    │  6. 工具栏切换 2D/3D、调节执行间隔                   │
    └─────────────────────────────────────────────────────┘

### 指令面板操作

| 操作 | 快捷键 / 按钮 |
|---|---|
| 执行全部指令 | `Ctrl + Enter` 或「执行」按钮 |
| 停止执行 | 「停止」按钮 |
| 清空代码 | 「清空代码」 |
| 清空画布 | 「清空画布」（重置 GeoGebra 实例） |
| 切换 2D/3D | 工具栏视角切换开关 |
| 调节执行间隔 | 工具栏滑块（ms） |

### 指令写法

每行一条 GeoGebra 指令，标准 GGB 语法即可：

    # 基础点
    A = (0, 0, 0)
    B = (sqrt(2), 0, 0)
    P = (0, 0, sqrt(2))

    # 几何构造
    AB = Segment(A, B)
    ShowLabel(AB, false)
    SetColor(AB, "#616161")

    # 视图控制（SetXxx/ShowXxx/HideXxx 前缀自动判定为脚本命令）
    SetPerspective("G3D")
    ShowGrid(false)
    SetConditionToShowObject(AB, true)

### 错误判定规则

GeoGebra classic 的 `evalCommand` 返回值有已知 bug，本项目采用以下三分支策略：

| 命令类型 | evalCommand 返回 false + getError() 空 | getError() 有内容 | 抛异常 |
|---|---|---|---|
| **脚本命令**（Set/Show/Hide/Zoom/Get/Exists/Is/Reset...） | ✅ 成功（classic bug） | ❌ 失败 | ❌ 失败 |
| **构造命令**（Circle/Polygon/Segment/Point/Sphere...） | ❌ 失败（静默错误） | ❌ 失败 | ❌ 失败 |

> 设计参考 [GGBPuppy commandGateway.js](https://github.com/yunend/GGBPuppy) 的 executeGeoGebraCommand 策略，扩展了前缀分类以覆盖更多 script 命令。

## 🤖 AI 辅助建模（Trae Skill）

本项目内置了 Trae IDE Skill `ggb-math-modeler`，定义了强制两阶段工作流：

    阶段一：题目深研 → 设计蓝图（坐标系、依赖顺序、颜色方案）
             ↓ 用户确认
    阶段二：蓝图 → GGB 脚本（每行一条指令 + STATE_TRACKER）
             ↓
    交付前校验：python3 scripts/validate_ggb.py <script.ggb>

Skill 位置：`.trae/skills/geogebra-ai-coding/`

| 文件 | 作用 |
|---|---|
| `SKILL.md` | 规则定义（目标层/知识层/行为层/规范层/协议层） |
| `references/example.md` | 完整蓝图→代码范例 |
| `references/ggb-codebook.md` | 对象缩写表 |
| `references/ggb-commands.md` | 压缩命令表 |
| `scripts/validate_ggb.py` | 脚本校验器（检查括号配对、函数套娃、STATE_TRACKER 等） |

### 校验器用法

    python .trae\skills\geogebra-ai-coding\scripts\validate_ggb.py my-script.ggb

    # 严格模式（warning 也算失败）
    python .trae\skills\geogebra-ai-coding\scripts\validate_ggb.py my-script.ggb --strict

## 🔧 技术栈

| 层级 | 技术 | 说明 |
|---|---|---|
| 视图 | Vue 3.5（global CDN） | 暴露 `window.Vue`，无需 import/export |
| 样式 | Tailwind 3.4（runtime JIT） | CDN 运行时扫描 DOM 生成样式，无需预编译 |
| 数学引擎 | GeoGebra 5.0（classic + web3d） | 本地离线资源，通过 `deployggb.js` 加载 |
| 状态管理 | Vue 3 reactivity（ref/computed） | 无额外状态库 |
| 构建 | **无** | 纯静态资源，`file://` 直接可用 |

## ⚠️ 已知限制

| 限制 | 原因 |
|---|---|
| 需要手动下载外部依赖 | `js/vue*.js` 和 `js/tailwind*.js` 不在仓库中（版权/体积） |
| Tailwind CDN 仅开发可用 | 生产应改为预编译 CSS，但零构建路线刻意保留 CDN |
| 某些 GGB 命令 classic 不识别 | 如 `ShowView`、`SetCoordSystem` 部分子参数，2D 视图下受限 |
| `SetConditionToShowObject` 批量执行时偶有延迟 | GeoGebra 内部异步刷新，已通过 120ms 延迟+重试缓解 |

## 📄 License

MIT