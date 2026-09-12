# 上手教程：从一句话到一套发布会 PPT

本教程用一个虚构产品「墨鱼 InkPod 智能墨水屏笔记本」的发布会为例，带你走完整个流程。全程约 15 分钟。安装步骤见 [INSTALLATION.md](INSTALLATION.md)，本教程假设已安装并通过验证。

> 如果你不想手动执行任何命令：装好 skill 后直接对 AI 助手说"用苹果发布会风格做一个墨水屏笔记本的发布会 PPT"，以下步骤 AI 会自动完成。本教程的价值在于让你看懂每一步发生了什么，以便验收和修改。

## Step 1：选叙事结构

打开 [`references/narrative.md`](../references/narrative.md)，三种结构里选一个：

| 结构 | 页数 | 适用 |
|---|---|---|
| 短版 | 6–8 | 提案开场、快速介绍 |
| 标准版 ★ | 10–14 | 产品发布、汇报主干 |
| 戏仿 15 步 | 12–15 | 把普通产品包装成苹果新品 |

「墨鱼 InkPod」是正经产品发布，选**标准版**：`cover → statement → section → split → bignum → section → split → featureGrid → compare → pricing → closing`。

## Step 2：写 outline.json

先定几条铁律（来自 `references/design-language.md`）：

- **标题即结论**：" writing latency is 0 ms" 不如「落笔，即所见」；
- 每个卖点先问能不能量化，能量化就给 `bignum` 一页；
- hero 大字 ≤12 字。

写出的 outline（节选，完整文件 11 页）：

```json
{
  "mode": "dark",
  "title": "InkPod 发布会",
  "slides": [
    {
      "type": "cover",
      "kicker": "INKPOD SPECIAL EVENT",
      "title": "InkPod",
      "subtitle": "纸，学会了思考。",
      "date": "2026.10.20"
    },
    {
      "type": "statement",
      "text": "写作，不该等待屏幕。"
    },
    {
      "type": "bignum",
      "kicker": "墨水屏响应引擎",
      "value": "0ms",
      "label": "落笔延迟",
      "caption": "笔尖触达的瞬间，字迹已经在纸上。"
    },
    {
      "type": "compare",
      "leftLabel": "普通平板",
      "rightLabel": "InkPod",
      "left": { "value": "7 天", "points": ["一天一充", "反光刺眼", "写字延迟明显"] },
      "right": { "value": "30 天", "points": ["月级续航", "类纸无反光", "0ms 落笔"] }
    },
    {
      "type": "pricing",
      "value": "¥2,399",
      "label": "InkPod 全系列",
      "config": "含手写笔，早鸟立减 400",
      "note": "* 2026.10.27 上午 9 点全渠道开售"
    },
    {
      "type": "closing",
      "title": "纸，学会了思考。",
      "subtitle": "InkPod 10.27 开售",
      "event": "InkPod Special Event · 2026.10"
    }
  ]
}
```

保存为 `outline.json`（示例里放输出目录）。

## Step 3：生成

```bash
node <skill>/scripts/build_deck.js outline.json InkPod.pptx
```

预期输出：

```
[build_deck] 已生成: ...\InkPod.pptx（11 页，mode=dark）
[gradient] 已为 4 个文本 run 写入四色渐变（无标记则原样保留）
```

两行的含义：11 页全部通过字段校验；封面标题、`0ms` 大数字、closing 标题等 4 处 hero 文字被写入了真实渐变。如果这里报错（如 `缺少必填字段 "value"`），按提示修 outline 重跑——校验故意设计得严格，宁可现在报错不要渲染后返工。

## Step 4：QA

```bash
# 第一道：代码级（秒级）
python <skill>/scripts/check_layout.py InkPod.pptx --strict
```

假设输出了一条警告：

```
[WARN] p5 疑似文本溢出：估算高 1.34in > 框高 0.90in，文本 "融合手写笔记、PDF 标注…"
```

处理方式不是调脚本，而是**删内容**——那页 caption 写了 40 个字，砍到 24 字以内重跑即可。估算有 ±10% 误差，所以还要看第二道：

```bash
# 第二道：渲染 PNG（Windows + PowerPoint/WPS）
bash <skill>/scripts/render_preview.sh InkPod.pptx preview
```

逐页打开 PNG 检查三件事：有没有文字截断/重叠；留白是否失衡（一页是不是太满）；全套风格是否统一。有 judge 子代理的环境直接交给它逐页验收。

## Step 5：交付

交付四件套：

| 文件 | 说明 |
|---|---|
| `InkPod.pptx` | 成品 |
| `preview/slide-*.png` | 逐页渲染图（验收凭证 + 群发预览用） |
| `outline.json` | 后续改文案的入口 |
| 质量结论 | QA 结果 + 已知问题（如有） |

## 常见迭代场景

- **只改文案**：编辑 outline.json 对应页 → 重跑 Step 3，10 秒出新版。
- **换浅色模式**：`"mode": "dark"` 改 `"light"`；注意浅色模式配白底图片（见 [images.md](../references/images.md)）。
- **加一页**：在 slides 数组里插入一个版式对象即可，页序即数组序。
- **渐变太多/太少**：只有 hero 类页面默认渐变；任何页加 `"gradient": true/false` 微调，一场 PPT 控制在 3–4 页。
- **上戏仿模式**：把产品名换成"Apple 雪糕"，叙事结构换 15 步模板（[narrative.md](../references/narrative.md) 第三节），记得保留戏仿声明页。

## 下一步

- [USAGE.md](USAGE.md)：全部版式的字段参考
- [ARCHITECTURE.md](ARCHITECTURE.md)：想改版式、改主题色时的内部原理
- [FAQ.md](FAQ.md)：常见问题
