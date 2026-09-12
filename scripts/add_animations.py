#!/usr/bin/env python3
"""add_animations.py — 给苹果风 PPT 注入转场与入场动画（OOXML 后处理）。

pptxgenjs 不支持动画。本脚本在 slide XML 层注入：
  1. 页面转场：淡入交叉溶解 <p:transition spd="slow"><p:fade/></p:transition>（700ms）
  2. 元素入场：淡入(presetID=10) + 轻微上浮(ppt_y)，按元素位置自上而下级联，
     换页后自动播放（无需点击），交错 ~160ms

行 XML 结构蒸馏自 PowerPoint 16 原生输出（ppt-master/pptx_animation_presets.json），
节点规则：timing 位于 transition 之后；p:bldP 仅为含文本的 p:sp 写入，不用于 pic/形状。

用法: python add_animations.py <file.pptx>
"""

import re
import shutil
import sys
import zipfile

P_NS = 'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"'
P14_NS = 'xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main"'

TRANSITION = f'<p:transition {P14_NS} spd="slow" p14:dur="700"><p:fade/></p:transition>'

FADE_DUR = 450          # 单个元素淡入时长 ms
RISE_OFFSET = "+0.025"  # 上浮起点偏移（页面高度比例，约 19px@1080p）
STEP_MS = 160           # 级联交错间隔
MAX_SPAN = 1100         # 级联总跨度上限


def extract_shapes(xml: str):
    """按 y,x 排序提取顶层 sp/pic：[(spid, is_text, x, y)]"""
    shapes = []
    for m in re.finditer(r"<p:(sp|pic)>(.*?)</p:\1>", xml, re.S):
        body = m.group(2)
        idm = re.search(r'<p:cNvPr id="(\d+)"', body)
        if not idm:
            continue
        off = re.search(r'<a:off x="(-?\d+)" y="(-?\d+)"', body)
        x, y = (int(off.group(1)), int(off.group(2))) if off else (0, 0)
        shapes.append({"spid": idm.group(1), "text": "<a:t>" in body, "x": x, "y": y})
    shapes.sort(key=lambda s: (s["y"], s["x"]))
    return shapes


def effect_row(spid: str, is_text: bool, delay: int, ids: list) -> str:
    """单个形状的入场行：淡入 + 上浮。ids 全局递增保证 cTn id 唯一。"""
    def nid():
        ids[0] += 1
        return ids[0]

    row_id = nid()
    set_id, fx_id, anim_id = nid(), nid(), nid()
    row = (
        f'<p:par><p:cTn id="{row_id}" presetID="10" presetClass="entr" presetSubtype="0"'
        f' fill="hold" grpId="0" nodeType="withEffect">'
        f'<p:stCondLst><p:cond delay="{delay}"/></p:stCondLst><p:childTnLst>'
        # 可见性置位（原厂结构：dur=1 fill=hold）
        f'<p:set><p:cBhvr><p:cTn id="{set_id}" dur="1" fill="hold">'
        f'<p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>'
        f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>'
        f'<p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr>'
        f'<p:to><p:strVal val="visible"/></p:to></p:set>'
        # 淡入
        f'<p:animEffect transition="in" filter="fade"><p:cBhvr>'
        f'<p:cTn id="{fx_id}" dur="{FADE_DUR}"/>'
        f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cBhvr></p:animEffect>'
        # 上浮：ppt_y 从 #ppt_y{RISE_OFFSET} 回落到 #ppt_y
        f'<p:anim calcmode="lin" valueType="num"><p:cBhvr additive="base">'
        f'<p:cTn id="{anim_id}" dur="{FADE_DUR}" fill="hold"/>'
        f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>'
        f'<p:attrNameLst><p:attrName>ppt_y</p:attrName></p:attrNameLst></p:cBhvr>'
        f'<p:tavLst>'
        f'<p:tav tm="0"><p:val><p:strVal val="#ppt_y{RISE_OFFSET}"/></p:val></p:tav>'
        f'<p:tav tm="100000"><p:val><p:strVal val="#ppt_y"/></p:val></p:tav>'
        f'</p:tavLst></p:anim>'
        f'</p:childTnLst></p:cTn></p:par>'
    )
    return row


def timing_xml(shapes) -> str:
    ids = [4]  # 1=tmRoot 2=mainSeq 3=clickGroup 4=innerPar
    n = len(shapes)
    step = min(STEP_MS, MAX_SPAN // max(1, n - 1)) if n > 1 else STEP_MS
    rows = "".join(
        effect_row(s["spid"], s["text"], i * step, ids) for i, s in enumerate(shapes)
    )
    builds = "".join(
        f'<p:bldP spid="{s["spid"]}" grpId="0"/>' for s in shapes if s["text"]
    )
    return (
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
        f'</p:cTn></p:par></p:childTnLst>'
        f'</p:cTn></p:par>'
        f'</p:childTnLst></p:cTn>'
        f'<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
        f'<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>'
        f'</p:seq>'
        f'</p:childTnLst></p:cTn>'
        f'</p:par></p:tnLst><p:bldLst>{builds}</p:bldLst></p:timing>'
    )


def process_slide(xml: str):
    """返回 (新 xml, 转场数, 动画形状数)"""
    if "<p:transition" in xml or "<p:timing" in xml:
        return xml, 0, 0  # 幂等：已处理过
    shapes = extract_shapes(xml)
    if not shapes:
        return xml, 0, 0
    inject = TRANSITION + timing_xml(shapes)
    return xml.replace("</p:sld>", inject + "</p:sld>"), 1, len(shapes)


def main(path: str) -> None:
    tmp = path + ".animtmp"
    slides = fx = 0
    with zipfile.ZipFile(path, "r") as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if re.match(r"ppt/slides/slide\d+\.xml$", item.filename):
                xml, t, n = process_slide(data.decode("utf-8"))
                slides += t
                fx += n
                data = xml.encode("utf-8")
            zout.writestr(item, data)
    shutil.move(tmp, path)
    print(f"[animations] {slides} 页转场(淡入溶解)，{fx} 个元素已注入淡入+上浮入场动画")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    main(sys.argv[1])
