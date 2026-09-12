---
name: apple-keynote-ppt
version: 1.1.0
description: >
  生成苹果发布会风格的极简 PPTX 演示文稿：纯黑/纯白双模式、超大字号、四色渐变标题、
  一页一个观点、大留白。当用户想要"苹果风 PPT"、"发布会风格演示文稿"、"Keynote 风格"、
  "极简高端 PPT"、"新品发布 PPT"，或想把任意主题/产品包装成苹果发布会（戏仿）时使用
  ——即使用户没有明说"苹果"。也适用于工作汇报、产品介绍、路演等一切想借苹果视觉语言的场景。
---

# 苹果发布会风格 PPT

把任意主题生成为苹果 Keynote 发布会风格的 PPTX。核心思路：**内容与样式分离**——你负责产出一份结构化大纲（outline.json），脚本把它确定性渲染成风格 100% 一致的幻灯片。

本 skill 与 `seedance-apple-keynote-video`（视频版）共享同一套视觉基因（四色渐变、#FBFBFD/纯黑、克制文案）。

## 目录

```
scripts/
  build_deck.js            CLI：outline.json → .pptx
  apple_theme.js           主题库：色板 + 14 种版式函数
  example_outline.json     示例大纲（戏仿奶茶发布会，12 页覆盖全部版式）
  postprocess_gradient.py  渐变文字 XML 后处理（build_deck.js 自动调用）
  check_layout.py          代码级 QA：字号/溢出/重叠/变形
  render_preview.sh        渲染 PNG 预览（PowerPoint COM，WPS 兜底）
references/
  design-language.md       完整视觉规范（改版式/新增版式时读）
  layouts.md               12 种版式的坐标级规格（写 outline 时查阅）
  narrative.md             叙事结构模板 + 戏仿 15 步模板（搭大纲前读）
  images.md                图片策略决策树 + AI 配图提示词（涉及图片时读）
assets/
  example_deck.pptx + preview/   示例成品与逐页渲染图
```

## 工作流（六步）

### 1. 收集

必须从用户拿到：**主题**（或要戏仿的产品名）。尽量拿到：已有文案/素材、图片、页数偏好、深色还是浅色、目标场合。缺失时不要阻塞——按 `references/narrative.md` 的结构模板主动补全，并把关键假设（模式选择、页数、结构）列给用户。

### 2. 大纲

读 `references/narrative.md` 选结构（短版 6–8 页 / 标准版 10–14 页 / 戏仿 15 步），然后写 outline.json（版式字段见 `references/layouts.md`，可参考 `scripts/example_outline.json`）。保存到输出目录，例如：

```json
{
  "mode": "dark",
  "title": "deck 元数据标题",
  "slides": [
    { "type": "cover", "kicker": "APPLE SPECIAL EVENT", "title": "Apple Milk Tea", "subtitle": "这一次，重新定义奶茶。", "date": "2026.09.13" },
    { "type": "bignum", "kicker": "A1 爆珠核心", "value": "3nm", "label": "制香工艺", "gradient": true }
  ]
}
```

写完先给用户过目每页一句话结构，确认后再生成（用户说"直接做"可跳过确认）。

### 3. 图片

读 `references/images.md` 的决策树：用户图 → 按规范用；无图且环境有文生图且用户接受 → AI 配图（先出主图，检查背景融合）；否则纯排版（`productHero`/`split` 的无图回落已内置）。**纯排版基线永远成立，不要为了图卡住流程。**

### 4. 生成

```bash
node <本skill目录>/scripts/build_deck.js outline.json deck.pptx
```

脚本自动完成：outline 校验（缺字段/超 3 功能点会明确报错）→ 渲染 → 渐变文字 XML 后处理。若报 pptxgenjs 缺失：`cd <skill>/scripts && npm install`。

### 5. QA（两道关卡）

```bash
# 第一道：代码级（秒级，先跑）
python <skill>/scripts/check_layout.py deck.pptx --strict

# 第二道：视觉（渲染 PNG 后交给 judge 子代理；无 judge 则自己逐页看）
bash <skill>/scripts/render_preview.sh deck.pptx preview
```

- 代码级查：字号 <12pt、文本溢出估算、文本框重叠、未显式设字体、图片拉伸变形。
- 渲染需 Windows + PowerPoint 或 WPS；都不可用时脚本会提示 LibreOffice/pdftoppm 命令。
- judge 验收维度：乱码/截断/重叠、留白与字号层级、12 页风格一致性、渐变是否只出现在 hero 类页面。
- 发现问题：改 outline.json（或 bug 时改 apple_theme.js）→ 重新生成 → 复检。**一次性修复循环**：同一问题修复尝试不超过 2 轮，仍失败则如实报告。

### 6. 交付

交付四件套：deck.pptx、preview/ 逐页 PNG、outline.json（用户后续改文案的入口）、简短质量结论（QA 结果 + 已知问题）。备注图片来源（用户图/AI 生成）；戏仿内容提醒不得用于误导性宣传。

## 速查卡

**版式 → type**（必填字段）：

| type | 用途 | 必填 |
|---|---|---|
| cover | 封面 | title |
| statement | 整页宣言 | text |
| section | 章节页 | title（+number） |
| bignum | 超大数字参数页 | value, label |
| productHero | 产品主图 | title（+image） |
| split | 图文分屏 | title, image |
| featureGrid | 2–3 功能点 | title, features |
| compare | 对比 | leftLabel, rightLabel |
| gallery | ≤6 产品/配色阵列 | items |
| quote | 引言 | text |
| pricing | 定价 | value |
| closing | 结尾 | title |
| bars | 量化条形对比（原生形状） | title, items（2–4 项，value 数字） |
| timeline | 里程碑时间线 | title, items（3–4 项） |

通用可选：`kicker`（大写引导词）、`gradient`（hero 类页面默认 true，其余默认 false）、`note`（演讲者备注，写入 PPTX 备注页）。outline 顶层 `"gradient": false` 可全篇关闭渐变（商务汇报风），页内仍可显式覆盖。

**色板**：dark = 背景 000000 / 文字 F5F5F7 / 次要 86868B；light = 背景 FBFBFD / 文字 1D1D1F / 次要 86868B；渐变 = 8B5CF6→4F8DEB→46C7C7→58C878（一场 PPT 最多 3–4 页用）。

**铁律**：一页一个观点；标题即结论（"快了 2 倍"不是"性能提升"）；留白 ≥40%；无卡片网格/边条/下划线/图标堆砌；featureGrid 最多 3 项；大字 ≤12 字。

## 常见坑

- outline 里 featureGrid 超过 3 项 → build_deck.js 会拒绝，拆页而不是硬塞。
- `gradient` 放在正文/功能点标题上 → 违反规范，渐变只给 hero 类短大字。
- 用户在 light 模式配黑底图片（或反之）→ 背景不融合，见 images.md §一.1，换图或回落纯排版。
- 中文别用 Light 字重；别把字号压到 12pt 以下塞字——删内容或拆页。
- 渲染预览时 LibreOffice 缺字体会替换字体，宽度失真属正常，以 check_layout.py 数值和 10% 余量为准。
