# 架构文档

本文档解释 `apple-keynote-ppt` 的内部工作原理与设计取舍。使用 skill 不需要读本文；要修改主题库、新增版式或排查渲染问题时从这里开始。

## 一、总览

```
 用户 / AI 助手
      │  六步工作流（SKILL.md 定义）
      ▼
 outline.json ──────────────►  内容与样式分离的中间格式
      │
      ▼
 build_deck.js
   ├─ 校验：必填字段 / 版式合法性 / featureGrid ≤3 项
   ├─ 渲染：apple_theme.js 的 12 个版式函数 → pptxgenjs → .pptx
   └─ 自动调用 postprocess_gradient.py（渐变文字 XML 后处理）
      ▼
 deck.pptx
   ├─ check_layout.py      代码级 QA（字号/溢出/重叠/字体/变形）
   └─ render_preview.sh    PowerPoint/WPS COM 逐页导出 PNG
      ▼
 逐页 PNG ──► 视觉验收（judge 子代理或人工）──► 修复循环（≤2 轮）
      ▼
 交付：deck.pptx + preview/ + outline.json + 质量结论
```

## 二、设计原则

1. **内容与样式分离**。AI 擅长产出结构化文案，不擅长稳定产出像素级一致的排版代码。把"写什么"（outline.json）和"怎么排"（apple_theme.js）分开，风格的每一次细节（字号、留白、色值）只实现一次、永久生效。
2. **确定性渲染**。同样的 outline 永远产出同样的 PPT。视觉风格不依赖模型的发挥，"苹果感"由固化的色板、字号阶梯、留白规则保证。
3. **渐进式披露**（Agent Skills 规范）：SKILL.md 常驻 122 行速查 → references 按需加载 → scripts 可执行。AI 不必一次读完全部规范。
4. **纯排版基线**。任何页面在没有任何图片输入时都必须成立（productHero/split 内置无图回落）。图片是增强项，不是依赖项。
5. **降级链而非失败**。渲染预览：PowerPoint COM → WPS COM → LibreOffice 命令提示；渐变后处理：Python 缺失时退化为纯色并警告。每一环都有替代路径。

## 三、模块职责

| 文件 | 职责 | 关键导出/入口 |
|---|---|---|
| `scripts/apple_theme.js` | 主题库：色板常量、字体选择、12 个版式函数 | `buildDeck(outline, path)`、`LAYOUTS`、`valueRuns` |
| `scripts/build_deck.js` | CLI 入口：校验 outline → 渲染 → 触发渐变后处理 | `node build_deck.js outline.json out.pptx` |
| `scripts/postprocess_gradient.py` | 在 OOXML 层把标记文本框改为真实渐变填充 | 自动执行，也可手动 |
| `scripts/check_layout.py` | 代码级 QA：五类静态检查 | `python check_layout.py deck.pptx [--strict]` |
| `scripts/render_preview.sh` | 生成 PNG 预览（Windows COM 优先） | `bash render_preview.sh deck.pptx outdir` |
| `references/*.md` | 设计语言 / 版式坐标 / 叙事结构 / 图片策略 | AI 按工作流阶段按需读取 |

## 四、关键机制

### 4.1 渐变文字（OOXML 后处理）

pptxgenjs 不支持渐变文字填充。方案是"生成时标记、生成后改写"：

1. `apple_theme.js` 给需要渐变的文本框设置 `objectName: "grad:eN"`，run 颜色先写渐变首色 `#8B5CF6`；
2. `postprocess_gradient.py` 用 zipfile 重写 `ppt/slides/slideN.xml`：定位 `name="grad:*"` 的 `<p:sp>` 块，把块内所有 `<a:solidFill><a:srgbClr .../></a:solidFill>` 替换为：

```xml
<a:gradFill>
  <a:gsLst>
    <a:gs pos="0"><a:srgbClr val="8B5CF6"/></a:gs>
    <a:gs pos="35000"><a:srgbClr val="4F8DEB"/></a:gs>
    <a:gs pos="70000"><a:srgbClr val="46C7C7"/></a:gs>
    <a:gs pos="100000"><a:srgbClr val="58C878"/></a:gs>
  </a:gsLst>
  <a:lin ang="0" scaled="1"/>   <!-- 水平方向，左→右 -->
</a:gradFill>
```

选择正则块级替换而非 XML 解析器重序列化，是为了不破坏 pptxgenjs 输出的其余字节（ET 重写会改动命名空间前缀，有兼容风险）。

### 4.2 大数字的单位缩放（`valueRuns`）

`bignum` / `pricing` 的 `value`（如 "2倍"、"40min"、"¥19"）按字符分类拆 run：数字与拉丁字母 100% 字号，货币符号（¥$€£）60%，CJK（"倍"、"分钟"）42%。纯 CJK 值（如"免费"）不缩放，整串按全尺寸输出。这让"数字巨大、单位克制"的苹果排版自动化。

### 4.3 中西文字体选择（`pickFont`）

按文本是否含 CJK 字符（U+2E80–9FFF 等）选择 `Microsoft YaHei` 或 `Segoe UI`，每个文本 run 显式写入 `fontFace`，不依赖主题继承——保证在任何宿主机器上打开都不回落到默认宋体。中文刻意不用 Light 字重：PPT 会随文件流转到别人机器，字重渲染不可控。

### 4.4 双道 QA 管道

| 关卡 | 手段 | 拦截什么 |
|---|---|---|
| 代码级（渲染前） | python-pptx 静态检查：<12pt 字号、CJK 加权的溢出估算、文本框两两重叠、run 未显式设字体、图片含 srcRect 修正后的拉伸变形 | 结构性错误，秒级反馈 |
| 渲染级（渲染后） | PowerPoint/WPS COM 逐页导出 1920×1080 PNG → judge 子代理按"视觉质量/布局构图/内容一致性"逐页验收 | 静态检查测不出的观感问题（渐变是否生效、留白失衡、风格漂移） |

溢出估算存在固有误差（不解析真实字形宽度），因此代码级只做"疑似溢出"告警，最终以渲染图为准。

## 五、一次渲染的数据流示例

outline 中的一页：

```json
{ "type": "bignum", "kicker": "A1 爆珠核心", "value": "3nm", "label": "制香工艺", "gradient": true }
```

1. `build_deck.js` 校验 `bignum` 必填项（`value`、`label`）通过；
2. `LAYOUTS.bignum` 被调用，按坐标规格写入 4 个元素：kicker（16pt/86868B/字距 3）、value（`valueRuns("3nm",120)` → "3"与"nm"两个 run）、label（26pt Bold）、caption（17pt/86868B）；
3. 因 `gradient: true`，value 文本框 objectName 记为 `grad:e2`，颜色暂写 `8B5CF6`；
4. pptxgenjs `writeFile` 产出 PPTX；
5. `postprocess_gradient.py` 把 `grad:e2` 框内 solidFill 改写为四色 gradFill；
6. `check_layout.py` 读回 PPTX 做五类检查；
7. `render_preview.sh` 导出 PNG，进入视觉验收。

## 六、扩展点

- **新增版式**：`apple_theme.js` 实现函数 → 注册进 `LAYOUTS` → `build_deck.js` 的 `REQUIRED` 加必填字段 → `references/layouts.md` 补坐标规格 → `example_outline.json` 加示例页 → 渲染验收。步骤详见 [CONTRIBUTING.md](../CONTRIBUTING.md)。
- **新增色彩模式**：在 `PALETTES` 加一组（bg/text/muted/panel/line/accent 六角色），版式函数自动继承。
- **接宿主文生图**：`references/images.md` 已预留 AI 配图的提示词模板与验收标准，宿主具备文生图工具时按决策树启用。

## 七、已知限制

- **渐变渲染依赖 PowerPoint**：LibreOffice 对 `a:lin gradFill` 文字的渲染接近但不完全一致；以 PowerPoint/WPS 打开为准。
- **单位缩放是启发式**：极少见的单位写法（如 "3.2µm"）分类可能不理想，可在 outline 里直接拆成 `label` 说明规避。
- **无原生图表**：需要数据图表时，当前版本建议用 bignum 大数字页表达关键数值，或插入外部图表截图（cover 裁剪）。
- **无动画/演讲者备注**：PPTX 为静态页面；动画与备注在 roadmap 中（见 CHANGELOG Unreleased）。
- **溢出估算误差**：±10% 量级，故设计上所有文本框已内置冗余；渲染预览是最终判据。
