# 页面版式库（12 种）

每种版式对应 `scripts/apple_theme.js` 里的一个函数，由 `build_deck.js` 按 outline.json 的 `type` 字段调用。坐标单位英寸，画布 13.33 × 7.5。`M = 1.1` 为页边距，`CW = 11.13` 为内容宽度。

通用可选字段：`kicker`（标题上方大写引导词）、`gradient`（是否渐变文字，仅 hero 类有效）。

---

## 1. cover 封面

用途：第一页。全部居中。

| 元素 | x | y | w | h | 字号 | 样式 |
|---|---|---|---|---|---|---|
| kicker | 0 | 2.00 | 13.33 | 0.4 | 16 | MUTED，全大写，charSpacing 3 |
| title | 0.67 | 2.45 | 12 | 1.9 | 64 | Bold，可渐变 |
| subtitle | 1.67 | 4.45 | 10 | 0.6 | 22 | MUTED |
| date | 0 | 6.55 | 13.33 | 0.4 | 15 | MUTED，居中 |

字段：`title`（必填）、`kicker`、`subtitle`、`date`。

## 2. statement 整页宣言

用途：情绪高潮页，一句话占满全屏。

| 元素 | x | y | w | h | 字号 |
|---|---|---|---|---|---|
| text | 1.42 | 0 | 10.5 | 7.5 | 54，Bold，valign middle 居中 |

字段：`text`（必填）。超过 14 字时字号降到 44。这是"重新定义了 X"出现的地方。

## 3. section 章节页

用途：章节分隔。左对齐。

| 元素 | x | y | w | h | 字号 |
|---|---|---|---|---|---|
| number | 1.1 | 1.35 | 5 | 1.7 | 96，Bold，MUTED |
| title | 1.1 | 3.15 | 10 | 1.3 | 48，Bold |
| subtitle | 1.1 | 4.5 | 10 | 0.6 | 20，MUTED |

字段：`number`（如 "01"）、`title`（必填）、`subtitle`。number 用渐变标记也好看。

## 4. bignum 超大数字参数页

用途：一切可量化卖点（性能、续航、销量、价格锚点）。居中。

| 元素 | x | y | w | h | 字号 |
|---|---|---|---|---|---|
| kicker | 0 | 1.15 | 13.33 | 0.4 | 16，MUTED 大写 |
| value | 0.67 | 1.7 | 12 | 2.3 | 120，Bold，默认渐变 |
| label | 0.67 | 4.15 | 12 | 0.7 | 26，Bold |
| caption | 1.67 | 4.95 | 10 | 0.9 | 17，MUTED |

字段：`value`（必填，如 "2倍"、"40 分钟"、"A1 芯片"——短字符串，≤6 字符最佳）、`label`（必填）、`kicker`、`caption`。数字带单位时单位字号随 run 拆分缩小（value 拆 runs：数字 120pt + 单位 48pt）。

## 5. product-hero 产品主图页

用途：产品第一次亮相。

| 元素 | x | y | w | h | 字号 |
|---|---|---|---|---|---|
| title | 0.67 | 0.85 | 12 | 1.0 | 36，Bold，居中 |
| subtitle | 1.67 | 1.85 | 10 | 0.55 | 20，MUTED，居中 |
| image | 3.17 | 2.55 | 7 | 4.35 | contain |

字段：`title`（必填）、`subtitle`、`image`。**无图片回落**：title 升级为 hero（54pt，y=2.6，valign middle 效果），subtitle y=4.6——纯排版依然成立。

## 6. split 图文分屏

用途：功能讲解的主力版式。一半文字一半图。

| 元素 | side=right（图在右） | side=left（图在左） |
|---|---|---|
| image | x=6.93, y=0, w=6.4, h=7.5, cover | x=0, y=0, w=6.4, h=7.5, cover |
| kicker | x=0.9, y=2.05, w=5.4 | x=7.0, y=2.05 |
| title | x=0.9, y=2.5, w=5.4, 34 Bold | x=7.0, y=2.5 |
| text | x=0.9, y=3.75, w=5.2, 17 MUTED | x=7.0, y=3.75 |

字段：`title`（必填）、`text`、`image`（必填）、`side`。文字区垂直居中于页面（上述 y 值已含）。**无图片回落**：转 statement 或 feature-grid。

## 7. feature-grid 功能点页

用途：2–3 个并列卖点。**最多 3 个**，无卡片无边框，纯排版分隔。

| 元素 | x | y | w | h | 字号 |
|---|---|---|---|---|---|
| title | 1.1 | 0.95 | 10.5 | 0.8 | 34，Bold |
| item.title | 1.1 + i×3.85 | 2.9 | 3.5 | 0.55 | 21，Bold |
| item.text | 1.1 + i×3.85 | 3.5 | 3.5 | 2.4 | 16，MUTED |

字段：`title`（必填）、`features`（必填，2–3 项 `{title, text}`）。栏间纯靠留白分隔；如果用户坚持要视觉锚点，允许在 item.title 前加一个 8pt 圆点（accent 色）——仅此一种装饰。

## 8. compare 对比页

用途：新旧对比 / 与传统方案对比。苹果格式：左旧右新，左灰右亮。

| 元素 | 左列（旧） | 右列（新） |
|---|---|---|
| label | x=1.3, y=1.5, w=4.8, 16 MUTED 大写 | x=7.23, y=1.5, 16 accent 大写 |
| value | x=1.3, y=2.0, w=4.8, h=1.1, 40 Bold，MUTED | x=7.23, y=2.0, 48 Bold，TEXT，可渐变 |
| points | x=1.3, y=3.4, w=4.8, 15 MUTED | x=7.23, y=3.4, 16 TEXT |
| divider | x=6.665, y=1.7, w=0.008, h=3.6，分隔线色 | — |

字段：`leftLabel`、`rightLabel`、`left: {value, points[]}`、`right: {value, points[]}`。points 每行一条，不用项目符号。

## 9. gallery 产品阵列

用途：多配色/多型号/系列产品。最多 4 列。

| 元素 | x | y | w | h |
|---|---|---|---|---|
| title | 0.67, 居中 | 0.75 | 12 | 0.7（30 Bold） |
| swatch/image | 1.1 + i×2.93 | 1.9 | 2.6 | 2.6（色块圆角 rectRadius 0.25 / 或 contain 图） |
| item.name | 同上，居中 | 4.75 | 2.6 | 0.5（18 Bold） |
| item.desc | 同上，居中 | 5.3 | 2.6 | 0.8（14 MUTED） |

字段：`title`、`items`（必填，2–4 项 `{name, desc, color?, image?}`）。有 `color` 无 `image` 时画色块（这是内容色板，不是装饰）；有 `image` 用 contain。**items 是 5–6 个时的变体**：列宽缩至 1.9，主题库自动适配。

## 10. quote 引言页

用途：用户评价、媒体好评、金句。

| 元素 | x | y | w | h | 字号 |
|---|---|---|---|---|---|
| text | 1.67 | 2.1 | 10 | 2.4 | 36，Bold，居中 |
| attribution | 0 | 4.9 | 13.33 | 0.5 | 17，MUTED，居中 |

字段：`text`（必填）、`attribution`（如 "— The Verde"）。不加引号装饰图形。

## 11. pricing 定价页

用途：价格揭晓。发布会真正的"one more thing"。

| 元素 | x | y | w | h | 字号 |
|---|---|---|---|---|---|
| value | 0.67 | 1.9 | 12 | 2.0 | 96，Bold，可渐变 |
| label | 0 | 4.0 | 13.33 | 0.6 | 22，Bold，居中 |
| config | 1.67 | 4.75 | 10 | 0.6 | 18，MUTED，居中 |
| note | 1.67 | 6.5 | 10 | 0.4 | 13，MUTED，居中 |

字段：`value`（必填，如 "¥19" 或 "免费"）、`label`、`config`、`note`（脚注，如免责/条件）。

## 12. closing 结尾页

用途：最后一页。slogan + 行动信息。

| 元素 | x | y | w | h | 字号 |
|---|---|---|---|---|---|
| title | 0.67 | 2.7 | 12 | 1.5 | 54，Bold，可渐变，居中 |
| subtitle | 1.67 | 4.35 | 10 | 0.6 | 20，MUTED，居中 |
| event | 0 | 6.55 | 13.33 | 0.4 | 14，MUTED，居中 |

字段：`title`（必填）、`subtitle`、`event`（如 "Apple Special Event · 2026.09"）。

## 13. bars 条形对比页

用途：2–4 项量化对比（季度走势、渠道占比）。原生形状绘制，可在 PowerPoint 里继续编辑，非贴图。

| 元素 | x | y | w | h | 样式 |
|---|---|---|---|---|---|
| kicker | 1.1 | 0.6 | 10.5 | 0.35 | 15，MUTED 大写 |
| title | 1.1 | 0.95 | 10.5 | 0.8 | 34，Bold |
| item.label | 1.1（行内垂直居中） | 2.35 + i×行高 | 2.7 | 行高 | 16，Bold |
| track 底槽 | 4.0 | 条高垂直居中 | 6.9 | ≤0.5 | panel 色 |
| bar | 4.0 | 同上 | 6.9 × value/max（≥0.35） | 同 track | `highlight` 项 accent，其余 muted |
| item.display | bar 右侧 +0.15（行内居中） | 同 label | 1.9 | 行高 | 18，Bold，highlight 项 accent |

字段：`title`（必填）、`items`（必填，2–4 项 `{label, value: 数字, display?, highlight?}`）。条长按 value/max 比例，最大值满槽。

## 14. timeline 里程碑页

用途：3–4 个关键节点（路线图、计划、节奏表）。

| 元素 | 位置 | 样式 |
|---|---|---|
| kicker / title | 同 bars | 15 大写 / 34 Bold |
| 轴线 | x 1.6→11.73，y=3.6，高 0.012 | line 分隔色 |
| 节点圆点 | slot 均分居中，r=0.08（`highlight` 0.11 + accent 色） | 普通 TEXT 色 |
| item.time | 圆点上方 y=2.65，w=2.2 居中 | 22，Bold |
| item.title | 轴下方 y=3.95，w=2.2 居中 | 16，Bold |
| item.desc | y=4.5，w=2.2，居中顶端对齐 | 14，MUTED |

字段：`title`（必填）、`items`（必填，3–4 项 `{time, title, desc?, highlight?}`）。

---

## 选择逻辑速查

- 说一个观点 → statement；亮一个数字 → bignum；秀产品 → product-hero
- 讲功能 → 图多 split，图少 feature-grid；拉踩 → compare；量化走势/占比 → bars
- 多款并列 → gallery（≤4）；引用背书 → quote；报价 → pricing；计划节奏 → timeline
- 每章开头 → section；开头 cover；结尾 closing
