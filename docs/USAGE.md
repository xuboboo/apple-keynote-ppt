# 使用指南

## 三种使用方式

### 方式一：对话驱动（推荐）

安装 skill 后，对 AI 助手说：

```
用苹果发布会风格做一个"XX 产品年度发布"的 PPT，深色模式，12 页左右
把雪糕包装成苹果新品，做一个发布会 PPT        # 戏仿模式
把我这份大纲做成苹果风 PPT：<粘贴文字>          # 带素材
```

AI 会自动执行六步工作流：**收集 → 大纲（outline.json）→ 图片策略 → 生成 → 双道 QA → 交付**。你只需要在"大纲确认"环节看一眼每页一句话结构。

### 方式二：自己写大纲，AI 只渲染

手动编辑 `outline.json`（格式见下文），然后：

```bash
node scripts/build_deck.js outline.json deck.pptx
```

适合文案已经定稿、只要苹果风排版的场景。改文案只需重新执行这一条命令。

### 方式三：开发者深度定制

在 Node 代码中直接调用主题库，绕过 outline 自由创作：

```js
const { buildDeck, LAYOUTS } = require('./scripts/apple_theme');
// 或 require 单个版式函数自行组合
```

新增版式：在 `apple_theme.js` 里实现函数并在 `LAYOUTS` 注册，坐标规范参照 `references/layouts.md`。

## outline.json 字段参考

顶层字段：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `mode` | `"dark"` \| `"light"` | 否 | 视觉模式，默认 `dark`（发布会舞台风） |
| `title` | string | 否 | deck 元数据标题（写入 PPTX 属性） |
| `slides` | array | ✅ | 页面数组，每页一个对象 |

每页通用字段：

| 字段 | 适用版式 | 说明 |
|---|---|---|
| `type` | 全部 | 版式类型，见下表 |
| `kicker` | 大部分 | 标题上方的大写引导词，如 "APPLE SPECIAL EVENT" |
| `gradient` | hero 类 | 是否四色渐变文字；cover/bignum/closing 默认 true，其余默认 false |

12 种版式与必填字段：

| `type` | 用途 | 必填字段 | 常用可选字段 |
|---|---|---|---|
| `cover` | 封面 | `title` | `kicker`, `subtitle`, `date` |
| `statement` | 整页宣言（一句话占满全屏） | `text` | `gradient` |
| `section` | 章节分隔页 | `title` | `number`（如 "01"）, `subtitle` |
| `bignum` | 超大数字参数页 | `value`, `label` | `kicker`, `caption` |
| `productHero` | 产品主图页 | `title` | `subtitle`, `image`（无图自动回落大字排版） |
| `split` | 图文分屏 | `title`, `image` | `text`, `side`（`left`/`right`，默认图在右） |
| `featureGrid` | 2–3 个功能点并列 | `title`, `features` | features 每项 `{title, text}`，**最多 3 项** |
| `compare` | 新旧/竞品对比 | `leftLabel`, `rightLabel` | `left: {value, points[]}`, `right: {value, points[]}` |
| `gallery` | 多配色/多型号阵列 | `items` | `title`；items 每项 `{name, desc, color, image}`，最多 6 项 |
| `quote` | 引言/金句 | `text` | `attribution` |
| `pricing` | 定价页 | `value`（如 "¥19"） | `label`, `config`, `note`（脚注） |
| `closing` | 结尾页 | `title` | `subtitle`, `event` |

图片路径相对 outline.json 所在目录解析。

完整示例见 [`scripts/example_outline.json`](../scripts/example_outline.json)。

## 六步工作流（AI 自动执行）

1. **收集**：主题、素材、页数、深浅模式。信息不足时 AI 按 `references/narrative.md` 的叙事模板补全并声明假设。
2. **大纲**：选定结构（短版 6–8 页 / 标准版 10–14 页 / 戏仿 15 步）写出 outline.json，交用户确认每页一句话结构。
3. **图片**：按 `references/images.md` 决策树——用户图 → AI 配图（有文生图能力时）→ 纯排版基线。
4. **生成**：`node scripts/build_deck.js outline.json deck.pptx`，自动完成校验、渲染、渐变后处理。
5. **QA**：`check_layout.py`（字号/溢出/重叠/字体/变形）→ `render_preview.sh` 渲染 PNG → 视觉验收。问题一次性修复循环（同一问题最多 2 轮）。
6. **交付**：deck.pptx + preview PNG + outline.json + 质量结论。

## QA 工具手动用法

```bash
# 代码级检查（--strict 时有错误返回非零退出码，可接 CI）
python scripts/check_layout.py deck.pptx --strict

# 渲染 PNG（Windows，PowerPoint COM 优先，WPS 兜底）
bash scripts/render_preview.sh deck.pptx preview/
# 输出 preview/slide-01.png ...（1920×1080）

# 无 PowerPoint/WPS 的替代链路
soffice --headless --convert-to pdf deck.pptx
pdftoppm -png -r 144 deck.pdf preview/slide
```

## 戏仿发布会模式

把任意普通产品包装成苹果新品。叙事结构与 15 步文案表对齐（Apple X → 这一次，我们重新定义了 → 配色阵列 → 结构/配件/芯片/连接卖点 → 参数 → 小孩子才做选择 → 成年人 → 全部都要），版式映射见 `references/narrative.md` 第三节。

红线：内容必须严肃、精致、昂贵，笑点只来自反差；交付物需含戏仿声明；不得用于误导性宣传。

## 设计速查

- **色板**：dark = `000000`/`F5F5F7`/`86868B`；light = `FBFBFD`/`1D1D1F`/`86868B`
- **渐变**：`8B5CF6→4F8DEB→46C7C7→58C878`，一场 PPT 最多 3–4 页使用，只用于 ≤12 字的 hero 大字
- **字号**：hero 60–96pt / 章节标题 44–54pt / 大数字 100–160pt / 页面标题 30–40pt / 正文 16–20pt / 最低 12pt
- **铁律**：一页一个观点；标题即结论；留白 ≥40%；禁卡片网格、边条、下划线、图标堆砌

完整规范见 `references/design-language.md`。
