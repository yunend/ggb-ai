#!/usr/bin/env python3
"""
validate_ggb.py — GGB 脚本交付前校验器

用法:
    python3 validate_ggb.py <script.ggb> [--strict]

检查项（[E]=error 必须修正，[W]=warning 也要处理）:
    [E] 括号配对      : () {} [] 必须平衡（忽略字符串与整行注释）
    [E] 指令后 #      : 注释必须独占一行，禁止写在指令内容后面
    [E] 函数套娃      : 构造命令的参数必须是已定义变量，禁止内嵌命令调用
    [E] 点命名大写    : 由 Point/坐标字面量创建的对象名必须以大写字母开头
    [E] SetValue-Text : 禁止对 Text 对象调用 SetValue
    [E] STATE_TRACKER : 脚本末尾必须包含 # STATE_TRACKER: {...}
    [W] 指令分隔符    : 一行含多条顶层指令时必须用英文分号分隔
    [W] 未知命令      : 不在命令表中的调用（提示核对 ggb-commands.md）
    [W] 标签覆盖      : 图形对象未出现任何 ShowLabel 调用
    [W] 疑似自动解题  : Text 字符串出现"答案/证明"等字样

退出码: 0 = 无 error（通过），1 = 存在 error（--strict 时 warning 亦算失败）
"""

import re
import sys

# ---- 允许的命令集（与 references/ggb-commands.md 对应）----
CONSTRUCTION_COMMANDS = {
    # 几何与圆锥曲线
    "Angle", "AngleBisector", "Arc", "Area", "Centroid", "Circle",
    "CircularArc", "CircularSector", "Circumcircle", "Circumference",
    "ClosestPoint", "Conic", "Directrix", "Distance", "Eccentricity",
    "Ellipse", "Focus", "Hyperbola", "Incircle", "Intersect",
    "IntersectPath", "Line", "Locus", "Midpoint", "Parabola",
    "Perimeter", "PerpendicularBisector", "PerpendicularLine", "Point",
    "PointIn", "Polygon", "Polyline", "Radius", "Ray", "Segment",
    "Semicircle", "Sphere", "Slope", "Tangent", "Vertex",
    # 代数与函数
    "Coefficients", "CompleteSquare", "Degree", "Denominator",
    "Derivative", "Expand", "Factor", "Integral", "LeftSide", "Limit",
    "Max", "Min", "Numerator", "PartialFractions", "Polynomial",
    "RightSide", "Root", "Simplify", "Solutions", "Solve", "Substitute",
    # 变换
    "Dilate", "Reflect", "Rotate", "Translate",
    # 列表、向量
    "Cross", "Dot", "Element", "Sequence", "Vector",
    # 文本（对象构造）
    "Text", "FormulaText",
}

SCRIPTING_COMMANDS = {
    "SetColor", "SetCaption", "SetLabelMode", "SetLayer", "SetPointSize",
    "SetPointStyle", "SetLineStyle", "SetLineThickness", "SetPerspective",
    "SetVisibleInView", "SetValue", "SetViewDirection", "Slider",
    "ShowLabel", "ZoomIn", "ZoomOut",
}

FUNCTION_NAMES = {
    "sqrt", "abs", "acos", "asin", "atan", "cos", "sin", "tan",
    "exp", "ln", "log", "floor", "ceil", "round", "x", "y", "z",
}

ALLOWED_COMMANDS = CONSTRUCTION_COMMANDS | SCRIPTING_COMMANDS | FUNCTION_NAMES

TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\s*\(")
ASSIGN_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*(?::?=)\s*(.*)$")


def strip_strings(line: str) -> str:
    """把双引号字符串内容替换为空格，保留行结构。"""
    out = []
    in_str = False
    for ch in line:
        if ch == '"':
            in_str = not in_str
            out.append(" ")
        elif in_str:
            out.append(" ")
        else:
            out.append(ch)
    return "".join(out)


def split_comment(line: str):
    """返回 (代码部分, 注释部分)。注释以字符串外的第一个 # 为界。"""
    code = []
    in_str = False
    for ch in line:
        if ch == '"':
            in_str = not in_str
            code.append(ch)
        elif ch == "#" and not in_str:
            return "".join(code), line[len("".join(code)):]
        else:
            code.append(ch)
    return "".join(code), ""


def find_matching(code: str, start: int, open_ch: str, close_ch: str) -> int:
    """从 start（须指向 open_ch）起找配对的 close_ch 下标；找不到返回 -1。"""
    depth = 0
    for i in range(start, len(code)):
        if code[i] == open_ch:
            depth += 1
        elif code[i] == close_ch:
            depth -= 1
            if depth == 0:
                return i
    return -1


def extract_tokens(code: str):
    """返回 [(名称, 左括号下标, 右括号下标), ...]；右括号 -1 表示不配对。"""
    tokens = []
    for m in TOKEN_RE.finditer(code):
        name = m.group(0).rstrip()[:-1].rstrip()
        open_idx = m.end() - 1
        close_idx = find_matching(code, open_idx, "(", ")")
        tokens.append((name, open_idx, close_idx))
    return tokens


def top_level_info(code: str):
    """返回 (顶层命令数, 顶层=数, 是否含顶层分号)。用于指令分隔符检查。"""
    depth = 0
    eq_count = 0
    has_semi = False
    for ch in code:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch == "=" and depth == 0:
            eq_count += 1
        elif ch == ";" and depth == 0:
            has_semi = True
    cmd_count = 0
    for _, open_idx, _ in extract_tokens(code):
        d = 0
        for ch in code[:open_idx]:
            if ch == "(":
                d += 1
            elif ch == ")":
                d -= 1
        if d == 0:
            cmd_count += 1
    return cmd_count, eq_count, has_semi


def is_coord_literal(rhs: str) -> bool:
    """判断是否为 (x,y) / (x,y,z) / {x,y} / {x,y,z} 形式的坐标字面量。"""
    rhs = rhs.strip()
    if not rhs:
        return False
    if rhs[0] == "(":
        open_ch, close_ch = "(", ")"
    elif rhs[0] == "{":
        open_ch, close_ch = "{", "}"
    else:
        return False
    close = find_matching(rhs, 0, open_ch, close_ch)
    if close == -1:
        return False
    inner = rhs[1:close]
    # 元素个数 = 顶层逗号数 + 1；坐标只能是 2 或 3 个元素
    depth = 0
    commas = 0
    for ch in inner:
        if ch in "({[":
            depth += 1
        elif ch in ")}]":
            depth -= 1
        elif ch == "," and depth == 0:
            commas += 1
    n = commas + 1
    return n in (2, 3)


def main() -> int:
    args = sys.argv[1:]
    strict = False
    if "--strict" in args:
        strict = True
        args.remove("--strict")
    if len(args) != 1:
        print("用法: python3 validate_ggb.py <script.ggb> [--strict]")
        return 2

    try:
        with open(args[0], encoding="utf-8") as f:
            lines = f.read().splitlines()
    except OSError as e:
        print(f"[E] 无法读取文件: {e}")
        return 2

    errors: list = []
    warnings: list = []
    text_objects: set = set()
    assigned: dict = {}          # name -> (line_no, rhs)
    showlabel_names: set = set()

    # ---- 逐行检查 ----
    for ln, raw in enumerate(lines, start=1):
        code, comment = split_comment(raw)
        stripped_code = strip_strings(code)

        # 1) 指令后 #（注释存在且前面有代码）
        if comment and code.strip():
            errors.append(f"L{ln} [E] 禁止在指令后面写 #（注释必须独占一行）: {raw.strip()}")

        # 2) 括号配对（仅统计代码部分）
        for op, cl in (("(", ")"), ("{", "}"), ("[", "]")):
            if stripped_code.count(op) != stripped_code.count(cl):
                errors.append(
                    f"L{ln} [E] 括号不配对: {op} {stripped_code.count(op)} 处 vs "
                    f"{cl} {stripped_code.count(cl)} 处: {raw.strip()}"
                )

        if not code.strip():
            continue

        tokens = extract_tokens(stripped_code)
        first = tokens[0][0] if tokens else None

        # 3) 赋值解析
        m = ASSIGN_RE.match(code.strip())
        if m:
            name, rhs = m.group(1), m.group(2).strip()
            assigned[name] = (ln, rhs)
            if is_coord_literal(rhs) and not name[0].isupper():
                errors.append(f"L{ln} [E] 点的名称必须以大写字母开头: {name} = {rhs}")
            if "Text(" in rhs:
                text_objects.add(name)

        # 4) 命令名合法性 + 函数套娃 + 点命名
        for tname, _, _ in tokens:
            if tname not in ALLOWED_COMMANDS:
                warnings.append(
                    f"L{ln} [W] 未知命令/函数 '{tname}'（不在命令表中，"
                    f"核对 references/ggb-commands.md）: {raw.strip()}"
                )

        if first in CONSTRUCTION_COMMANDS and m:
            name = m.group(1)
            if first == "Point" and not name[0].isupper():
                errors.append(f"L{ln} [E] 点的名称必须以大写字母开头: {name} = Point(...)")
            open_idx, close_idx = tokens[0][1], tokens[0][2]
            if close_idx == -1:
                errors.append(f"L{ln} [E] 构造命令 '{first}' 括号不配对: {raw.strip()}")
            else:
                inner = stripped_code[open_idx + 1:close_idx]
                inner_tokens = extract_tokens(inner)
                if inner_tokens:
                    bad = ", ".join(t for t, _, _ in inner_tokens)
                    errors.append(
                        f"L{ln} [E] 禁止函数套娃（构造命令参数必须是已定义变量）: "
                        f"{first}(...) 内嵌调用 {bad}"
                    )

        # 5) 指令分隔符：一行多条指令必须以英文分号分隔
        t_cmd, t_eq, has_semi = top_level_info(stripped_code)
        if max(t_cmd, t_eq) >= 2 and not has_semi:
            warnings.append(
                f"L{ln} [W] 一行包含多条指令，应以英文分号分隔: {raw.strip()}"
            )

        # 6) SetValue 禁止作用于 Text
        for tname, open_idx, close_idx in tokens:
            if tname == "SetValue" and close_idx != -1:
                inner = stripped_code[open_idx + 1:close_idx]
                arg0 = inner.split(",")[0].strip()
                if arg0 in text_objects or arg0.startswith("Text"):
                    errors.append(f"L{ln} [E] 禁止 SetValue 用于 Text 对象: {raw.strip()}")

        # 7) ShowLabel 覆盖登记
        for tname, open_idx, close_idx in tokens:
            if tname == "ShowLabel" and close_idx != -1:
                inner = stripped_code[open_idx + 1:close_idx]
                showlabel_names.add(inner.split(",")[0].strip())

        # 8) 疑似自动解题
        if "Text(" in raw or "FormulaText(" in raw:
            for kw in ("答案", "证明", "所以", "可知"):
                if kw in raw:
                    warnings.append(
                        f"L{ln} [W] 疑似自动解题（文本含 '{kw}'），复刻模型不应替用户下结论: {raw.strip()}"
                    )

    # ---- 8) 标签覆盖（图形对象必须出现 ShowLabel）----
    for name, (ln, rhs) in assigned.items():
        tokens = extract_tokens(rhs)
        first = tokens[0][0] if tokens else None
        is_graphical = (first in CONSTRUCTION_COMMANDS) or is_coord_literal(rhs)
        if is_graphical and name not in showlabel_names:
            warnings.append(f"L{ln} [W] 图形对象 '{name}' 未调用 ShowLabel（默认应隐藏标签）")

    # ---- 9) STATE_TRACKER ----
    tracker_line = next((ln for ln, l in enumerate(lines, 1) if "STATE_TRACKER" in l), None)
    if tracker_line is None:
        errors.append("[E] 脚本缺少 # STATE_TRACKER: {...} 注释")
    else:
        last_content = next((ln for ln in range(len(lines), 0, -1) if lines[ln - 1].strip()), None)
        if last_content and tracker_line < last_content:
            warnings.append(f"L{tracker_line} [W] STATE_TRACKER 建议放在脚本末尾（当前其后还有内容）")

    # ---- 输出 ----
    print(f"文件: {args[0]}")
    for e in errors:
        print(f"  {e}")
    for w in warnings:
        print(f"  {w}")
    n_e, n_w = len(errors), len(warnings)
    print(f"结果: {n_e} 个 error, {n_w} 个 warning")

    if n_e or (strict and n_w):
        return 1
    if n_w:
        print("通过（含 warning，建议处理）")
    else:
        print("通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
