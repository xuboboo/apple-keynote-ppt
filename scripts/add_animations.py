#!/usr/bin/env python3
"""add_animations.py — 给苹果风 PPT 注入"编排式"转场与入场动画（OOXML 后处理）。

设计立场（代表苹果设计师）：一套 deck 只用一种连贯的编排语言（choreography），
页内按元素角色分配动效——主视觉"长"出来、正文浮上来、标注的形状从左擦除生长。
不同 deck 之间气质各异：outline.choreography 显式指定，否则按标题哈希从 5 种
方案中自动选择并带时长微抖动，保证每次制作的结果都不一样。

方案：cinematic / crisp / editorial / bold / tvos（详见 PROGRAMS）。

行 XML 结构蒸馏自 PowerPoint 16 原生输出（entrance_fade: presetID=10,
presetClass=entr, set→animEffect 组合）。缩放/擦除分别用 p:animScale 与
p:animEffect filter="wipe(left)" 组合。timing 位于 transition 之后；
p:bldP 仅为含文本的 p:sp 写入。

用法: python add_animations.py <file.pptx> [choreography|auto] [seedText]
"""

import hashlib
import re
import shutil
import sys
import zipfile

P_NS = 'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"'
P14_NS = 'xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main"'

FADE_FILTER = "fade"
WIPE_FILTER = "wipe(left)"

# —— 五种编排方案：一套 deck 一种语言，元素按角色分配 ——
# trans = (转场内部元素, 基准时长 ms)；时长写在 <p:transition p14:dur> 上
PROGRAMS = {
    "cinematic": dict(label="电影感", trans=('<p:fade/>', 700), hero="scale96", text="rise", shape="scale", order="top-down", step=160, dur=450),
    "crisp": dict(label="利落", trans=('<p:fade/>', 500), hero="rise_s", text="rise_s", shape="fade", order="top-down", step=110, dur=320),
    "editorial": dict(label="杂志", trans=('<p:fade/>', 600), hero="wipe", text="fade", shape="wipe", order="top-down", step=140, dur=400),
    "bold": dict(label="张扬", trans=('<p:fade thruBlk="1"/>', 900), hero="scale88", text="rise_b", shape="scale", order="center-out", step=200, dur=600),
    "tvos": dict(label="玻璃感", trans=('<p:fade/>', 800), hero="scale104", text="rise_w", shape="scale", order="top-down", step=190, dur=650),
}
RISE = {"rise": 0.025, "rise_s": 0.015, "rise_b": 0.04, "rise_w": 0.02}
SCALE_FROM = {"scale": 94, "scale96": 96, "scale88": 88, "scale104": 104}


def pick_program(choreography: str, seed_text: str):
    if choreography and choreography in PROGRAMS:
        return choreography, 0
    h = int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest(), 16)
    keys = list(PROGRAMS)
    return keys[h % len(keys)], h


def extract_shapes(xml: str):
    """按版面位置提取顶层 sp/pic：spid/是否文本/是否主视觉(≥55pt)/标注动效/坐标"""
    shapes = []
    for m in re.finditer(r"<p:(sp|pic)>(.*?)</p:\1>", xml, re.S):
        body = m.group(2)
        idm = re.search(r'<p:cNvPr id="(\d+)" name="([^"]*)"', body)
        if not idm:
            continue
        off = re.search(r'<a:off x="(-?\d+)" y="(-?\d+)"', body)
        x, y = (int(off.group(1)), int(off.group(2))) if off else (0, 0)
        ext = re.search(r'<a:ext cx="(\d+)" cy="(\d+)"', body)
        cx, cy = (int(ext.group(1)), int(ext.group(2))) if ext else (0, 0)
        sizes = [int(v) for v in re.findall(r'<a:rPr[^>]*\bsz="(\d+)"', body)]
        named = re.search(r'name="anim:(\w+)"', body)
        shapes.append({
            "spid": idm.group(1), "text": "<a:t>" in body,
            "hero": bool(sizes and max(sizes) >= 5500),
            "hint": named.group(1) if named else "",
            "x": x, "y": y, "cx": cx, "cy": cy,
        })
    if not shapes:
        return []
    if any(s["hint"] == "center" for s in shapes):
        pass
    return shapes


def order_shapes(shapes, mode):
    if mode == "center-out" and shapes:
        H, W = 6858000, 12192000  # EMU，13.33x7.5in
        return sorted(shapes, key=lambda s: (abs((s["y"] + s["cy"] / 2) - H / 2), s["x"]))
    return sorted(shapes, key=lambda s: (s["y"], s["x"]))


def entrance(kind: str, spid: str, delay: int, dur: int, ids: list) -> str:
    """按动效类型生成一个形状的入场行（set + 视觉行为组合）。"""
    def nid():
        ids[0] += 1
        return ids[0]

    row_id, set_id, fx_id = nid(), nid(), nid()
    set_part = (
        f'<p:set><p:cBhvr><p:cTn id="{set_id}" dur="1" fill="hold">'
        f'<p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>'
        f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>'
        f'<p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr>'
        f'<p:to><p:strVal val="visible"/></p:to></p:set>'
    )
    visual = ""
    if kind.startswith("rise"):
        visual = (
            f'<p:animEffect transition="in" filter="{FADE_FILTER}"><p:cBhvr>'
            f'<p:cTn id="{fx_id}" dur="{dur}"/>'
            f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cBhvr></p:animEffect>'
            f'<p:anim calcmode="lin" valueType="num"><p:cBhvr additive="base">'
            f'<p:cTn id="{nid()}" dur="{dur}" fill="hold"/>'
            f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>'
            f'<p:attrNameLst><p:attrName>ppt_y</p:attrName></p:attrNameLst></p:cBhvr>'
            f'<p:tavLst><p:tav tm="0"><p:val><p:strVal val="#ppt_y+{RISE[kind]}"/></p:val></p:tav>'
            f'<p:tav tm="100000"><p:val><p:strVal val="#ppt_y"/></p:val></p:tav></p:tavLst></p:anim>'
        )
    elif kind == "fade":
        visual = (
            f'<p:animEffect transition="in" filter="{FADE_FILTER}"><p:cBhvr>'
            f'<p:cTn id="{fx_id}" dur="{dur}"/>'
            f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cBhvr></p:animEffect>'
        )
    elif kind == "wipe":
        visual = (
            f'<p:animEffect transition="in" filter="{WIPE_FILTER}"><p:cBhvr>'
            f'<p:cTn id="{fx_id}" dur="{dur}"/>'
            f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cBhvr></p:animEffect>'
        )
    else:  # scale96 / scale88 / scale104：淡入 + 缩放生长/沉降
        f0 = SCALE_FROM[kind] * 1000
        visual = (
            f'<p:animEffect transition="in" filter="{FADE_FILTER}"><p:cBhvr>'
            f'<p:cTn id="{fx_id}" dur="{dur}"/>'
            f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cBhvr></p:animEffect>'
            f'<p:animScale><p:cBhvr><p:cTn id="{nid()}" dur="{dur}" fill="hold"/>'
            f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cBhvr>'
            f'<p:from x="{f0}" y="{f0}"/><p:to x="100000" y="100000"/></p:animScale>'
        )
    return (
        f'<p:par><p:cTn id="{row_id}" presetID="10" presetClass="entr" presetSubtype="0"'
        f' fill="hold" grpId="0" nodeType="withEffect">'
        f'<p:stCondLst><p:cond delay="{delay}"/></p:stCondLst>'
        f'<p:childTnLst>{set_part}{visual}</p:childTnLst></p:cTn></p:par>'
    )


def assign_effect(s, prog) -> str:
    if s["hint"]:
        return s["hint"]  # apple_theme 中的 objectName 标注（如 bars: anim:wipe）
    if s["hero"]:
        return prog["hero"]
    return prog["text"] if s["text"] else prog["shape"]


def timing_xml(shapes, prog, jitter: int) -> str:
    ordered = order_shapes(shapes, prog["order"])
    ids = [4]
    step, dur = prog["step"], prog["dur"]
    n = len(ordered)
    step = min(step, 1200 // max(1, n - 1)) if n > 1 else step
    rows = "".join(
        entrance(assign_effect(s, prog), s["spid"], i * step, dur, ids)
        for i, s in enumerate(ordered)
    )
    builds = "".join(
        f'<p:bldP spid="{s["spid"]}" grpId="0"/>' for s in ordered if s["text"]
    )
    trans_inner, base_dur = prog["trans"]
    transition = f'<p:transition {P14_NS} spd="slow" p14:dur="{base_dur + jitter}">{trans_inner}</p:transition>'
    return (
        f'{transition}'
        f'<p:timing {P_NS}><p:tnLst><p:par>'
        f'<p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>'
        f'<p:seq concurrent="1" nextAc="seek">'
        f'<p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>'
        f'<p:par><p:cTn id="3" fill="hold">'
        f'<p:stCondLst><p:cond delay="indefinite"/>'
        f'<p:cond evt="onBegin" delay="0"><p:tn val="2"/></p:cond></p:stCondLst>'
        f'<p:childTnLst><p:par><p:cTn id="4" fill="hold">'
        f'<p:stCondLst><p:cond delay="0"/></p:stCondLst>'
        f'<p:childTnLst>{rows}</p:childTnLst>'
        f'</p:cTn></p:par></p:childTnLst></p:cTn></p:par>'
        f'</p:childTnLst></p:cTn>'
        f'<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
        f'<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>'
        f'</p:seq></p:childTnLst></p:cTn></p:par></p:tnLst>'
        f'<p:bldLst>{builds}</p:bldLst></p:timing>'
    )


def process_slide(xml: str, prog, jitter: int):
    if "<p:transition" in xml or "<p:timing" in xml:
        return xml, 0, 0
    shapes = extract_shapes(xml)
    if not shapes:
        return xml, 0, 0
    return xml.replace("</p:sld>", timing_xml(shapes, prog, jitter) + "</p:sld>"), 1, len(shapes)


def main(path: str, choreography: str, seed_text: str) -> None:
    prog_key, h = pick_program(choreography, seed_text)
    prog = PROGRAMS[prog_key]
    jitter = (h // 7) % 5 * 40 - 80  # 转场时长 ±80ms 微抖动
    tmp = path + ".animtmp"
    slides = fx = 0
    with zipfile.ZipFile(path, "r") as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if re.match(r"ppt/slides/slide\d+\.xml$", item.filename):
                xml, t, n = process_slide(data.decode("utf-8"), prog, jitter)
                slides += t
                fx += n
                data = xml.encode("utf-8")
            zout.writestr(item, data)
    shutil.move(tmp, path)
    print(f"[animations] choreography: {prog_key}({prog['label']}) | 转场 {slides} 页({prog['trans'][1] + jitter}ms) | {fx} 个元素入场")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "auto", sys.argv[3] if len(sys.argv) > 3 else "")
