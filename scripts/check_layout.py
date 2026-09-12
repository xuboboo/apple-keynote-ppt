#!/usr/bin/env python3
"""check_layout.py — 苹果风 PPT 代码级 QA（渲染前的第一道检查）。

检查项：
  1. 最小字号（<12pt 报错）
  2. 文本溢出估算（CJK 加权；误差大时以渲染预览为准）
  3. 文本框两两重叠（背景框/满幅元素自动豁免）
  4. 缺失显式字体（run 无 font.name → 依赖主题继承，违反规范）
  5. 图片拉伸变形（含 srcRect 裁剪修正）

用法: python check_layout.py <file.pptx> [--strict]
默认只输出警告不改变退出码；--strict 时有任何 ERROR 返回 1。
"""

import math
import sys

from pptx import Presentation
from pptx.util import Emu

EMU_IN = 914400.0
MIN_PT = 12.0
# 单字符宽度系数（相对字号）：CJK≈1.0em，拉丁≈0.55em，数字≈0.55em
def char_units(text: str) -> float:
    u = 0.0
    for ch in text:
        o = ord(ch)
        if o >= 0x2E80 or ch in "，。：；！？、（）《》“”—…":
            u += 1.02
        elif ch in " .,:;!?|'\"":
            u += 0.30
        else:
            u += 0.55
    return u


def iter_text_frames(slide):
    for shape in slide.shapes:
        if shape.has_text_frame and shape.text_frame.text.strip():
            yield shape


def check_fonts(slide_idx, shape, issues):
    for para in shape.text_frame.paragraphs:
        for run in para.runs:
            sz = run.font.size.pt if run.font.size else None
            if sz is not None and sz < MIN_PT:
                issues.append(("ERROR", f"p{slide_idx} 字号 {sz:.0f}pt < 12pt: “{run.text[:18]}”"))
            if run.font.name is None:
                issues.append(("WARN", f"p{slide_idx} run 未显式设字体: “{run.text[:18]}”"))


def check_overflow(slide_idx, shape, issues):
    tf = shape.text_frame
    w_in = shape.width / EMU_IN if shape.width else 0
    h_in = shape.height / EMU_IN if shape.height else 0
    if w_in <= 0 or h_in <= 0:
        return
    total_h = 0.0
    for para in tf.paragraphs:
        text = "".join(r.text for r in para.runs)
        if not text.strip():
            total_h += 0.12
            continue
        sizes = [r.font.size.pt for r in para.runs if r.font.size]
        pt = max(sizes) if sizes else 18.0
        em_in = pt / 72.0
        usable = w_in - 0.1
        per_line = max(1.0, usable / em_in)
        lines = max(1, math.ceil(char_units(text) / per_line))
        line_h = em_in * 1.3  # 含行距余量
        total_h += lines * line_h
    if total_h > h_in * 1.12:
        issues.append((
            "WARN",
            f"p{slide_idx} 疑似文本溢出：估算高 {total_h:.2f}in > 框高 {h_in:.2f}in，文本 “{tf.text[:20]}…”",
        ))


def boxes_overlap(a, b):
    ax1, ay1 = a.left / EMU_IN, a.top / EMU_IN
    ax2, ay2 = ax1 + a.width / EMU_IN, ay1 + a.height / EMU_IN
    bx1, by1 = b.left / EMU_IN, b.top / EMU_IN
    bx2, by2 = bx1 + b.width / EMU_IN, by1 + b.height / EMU_IN
    ox = min(ax2, bx2) - max(ax1, bx1)
    oy = min(ay2, by2) - max(ay1, by1)
    return ox > 0.05 and oy > 0.05


def is_fullbleed(shape, sw, sh):
    return (
        shape.width / EMU_IN > sw * 0.9
        and shape.height / EMU_IN > sh * 0.9
    )


def check_overlap(slide_idx, shapes, slide_w, slide_h, issues):
    texts = [s for s in shapes if s.has_text_frame and s.text_frame.text.strip() and not is_fullbleed(s, slide_w, slide_h)]
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            if boxes_overlap(texts[i], texts[j]):
                issues.append((
                    "ERROR",
                    f"p{slide_idx} 文本框重叠: “{texts[i].text_frame.text[:12]}…” × “{texts[j].text_frame.text[:12]}…”",
                ))


def check_image_distortion(slide_idx, pic, issues):
    try:
        native_w, native_h = pic.image.size
    except Exception:
        return
    if not native_w or not native_h:
        return
    cl, cr = pic.crop_left, pic.crop_right
    ct, cb = pic.crop_top, pic.crop_bottom
    disp_w = pic.width / EMU_IN * (1 - cl - cr)
    disp_h = pic.height / EMU_IN * (1 - ct - cb)
    if disp_h <= 0:
        return
    native_ratio = native_w / native_h
    disp_ratio = disp_w / disp_h
    if abs(native_ratio - disp_ratio) / native_ratio > 0.08:
        issues.append(("WARN", f"p{slide_idx} 图片疑似拉伸变形（原始比 {native_ratio:.2f} vs 显示比 {disp_ratio:.2f}）"))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    strict = "--strict" in sys.argv
    if not args:
        print(__doc__)
        sys.exit(2)
    path = args[0]
    prs = Presentation(path)
    slide_w, slide_h = prs.slide_width / EMU_IN, prs.slide_height / EMU_IN
    issues = []
    for idx, slide in enumerate(prs.slides, start=1):
        shapes = list(slide.shapes)
        for shape in shapes:
            if shape.has_text_frame and shape.text_frame.text.strip():
                check_fonts(idx, shape, issues)
                check_overflow(idx, shape, issues)
            if shape.shape_type == 13:  # PICTURE
                check_image_distortion(idx, shape, issues)
        check_overlap(idx, shapes, slide_w, slide_h, issues)

    errors = [m for lvl, m in issues if lvl == "ERROR"]
    warns = [m for lvl, m in issues if lvl == "WARN"]
    if not issues:
        print("[check] 全部通过：无字号/溢出/重叠/字体/变形问题。")
    else:
        for m in errors:
            print("  [ERROR] " + m)
        for m in warns:
            print("  [WARN]  " + m)
        print(f"[check] {len(errors)} 个错误，{len(warns)} 个警告。（溢出估算存在误差，以渲染预览为准）")
    sys.exit(1 if (strict and errors) else 0)


if __name__ == "__main__":
    main()
