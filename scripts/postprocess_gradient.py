#!/usr/bin/env python3
"""postprocess_gradient.py — 把标记为 grad:* 的文本框从纯色填充改为四色渐变填充。

原理：apple_theme.js 给渐变文本框写入 objectName="grad:..."，run 颜色为渐变首色。
本脚本在 OOXML 层把这些 run 的 <a:solidFill> 替换为水平四色 <a:gradFill>。
pptxgenjs 本身不支持渐变文字，这是官方能力之外的补全。

用法: python postprocess_gradient.py <file.pptx>
"""

import re
import shutil
import sys
import zipfile

GRAD_FILL = (
    '<a:gradFill><a:gsLst>'
    '<a:gs pos="0"><a:srgbClr val="8B5CF6"/></a:gs>'
    '<a:gs pos="35000"><a:srgbClr val="4F8DEB"/></a:gs>'
    '<a:gs pos="70000"><a:srgbClr val="46C7C7"/></a:gs>'
    '<a:gs pos="100000"><a:srgbClr val="58C878"/></a:gs>'
    '</a:gsLst><a:lin ang="0" scaled="1"/></a:gradFill>'
)

SOLID_RE = re.compile(r'<a:solidFill><a:srgbClr val="[0-9A-Fa-f]{6}"/></a:solidFill>')
SP_RE = re.compile(r'<p:sp>.*?</p:sp>', re.DOTALL)
NAME_RE = re.compile(r'<p:cNvPr[^>]*name="([^"]*)"')


def process_slide(xml: str):
    count = 0

    def repl_sp(m):
        nonlocal count
        block = m.group(0)
        name = NAME_RE.search(block)
        if not name or not name.group(1).startswith("grad:"):
            return block
        new_block, n = SOLID_RE.subn(GRAD_FILL, block)
        count += n
        return new_block

    return SP_RE.sub(repl_sp, xml), count


def main(path: str) -> None:
    tmp = path + ".gradtmp"
    total = 0
    with zipfile.ZipFile(path, "r") as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if re.match(r"ppt/slides/slide\d+\.xml$", item.filename):
                xml = data.decode("utf-8")
                xml, n = process_slide(xml)
                total += n
                data = xml.encode("utf-8")
            zout.writestr(item, data)
    shutil.move(tmp, path)
    print(f"[gradient] 已为 {total} 个文本 run 写入四色渐变（无标记则原样保留）")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    main(sys.argv[1])
