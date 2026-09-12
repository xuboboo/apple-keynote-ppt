# 常见问题（FAQ）

## 产品与合规

**Q: 这个工具和 Apple 有关系吗？**
没有。它是对苹果发布会视觉语言的风格化模仿，"Apple""Keynote" 等字样仅为风格描述。生成的 PPT 若为戏仿内容（如 "Apple 奶茶"），请保留戏仿声明，不得用于误导消费者或商业侵权。

**Q: 生成的 PPT 可以商用吗？**
风格不受版权保护，生成物归你使用。两点注意：① 戏仿内容慎用于商业场景；② 微软雅黑字体的商用分发遵循 Windows 授权（在 Windows 上编辑演示属正常使用，但若把 PPT 内字体单独提取分发则不在此列）。

**Q: 这是私有仓库，我能分享给别人吗？**
需作者授权。安装与使用方法见 [COMPATIBILITY.md](COMPATIBILITY.md)，技术上任何支持 Agent Skills 规范的宿主均可直接使用。

## 功能边界

**Q: 支持图表吗？**
当前版本不生成原生可编辑图表。关键数据建议用 `bignum` 大数字页表达（这本身就是苹果发布会的习惯——一场发布会几乎不放数据表格）；复杂图表可截图后用 `split` 版式插入。

**Q: 支持动画和切换效果吗？**
不支持。输出为静态页面。苹果发布会 PPT 的质感核心在排版与节奏而非动画；如需动画建议在 PowerPoint 里对少量页面手动添加淡入。

**Q: 支持演讲者备注吗？**
当前不支持（在 roadmap 中）。临时方案：把讲稿写进 outline.json 每页一个 `"note"` 之外的自定义字段不会被渲染，但会随 JSON 交付，可对照使用。

**Q: 一套 PPT 最多多少页？**
技术上无限制；设计建议 ≤20 页。苹果发布会单场信息密度极低，超过 20 页请拆成两场（两个 outline）。

**Q: 能用公司模板/品牌色吗？**
本 skill 的价值恰在于统一的苹果风视觉，不建议混入企业模板。品牌色可以在 `apple_theme.js` 的 `PALETTES` 中改 accent 角色色（占版面 ≤10%，不破坏整体风格）。

**Q: 中英混排效果如何？**
中西文按 run 级自动选字体（雅黑/Segoe UI），混排无需处理。全英文 deck 也支持，标题排版会自动适应。

## 使用与安装

**Q: 一定要装 PowerPoint 吗？**
不是。PowerPoint/WPS 只用于"渲染 PNG 预览"这一质检环节；生成 PPTX 只需 Node.js。没有两者时按 [INSTALLATION.md](INSTALLATION.md) 用 LibreOffice + poppler 替代。

**Q: 多个 AI 宿主可以共用一份 skill 吗？**
可以，但各宿主 skills 目录相互独立，需分别放置（或符号链接）。升级时同步覆盖，见 [COMPATIBILITY.md](COMPATIBILITY.md)。

**Q: 渐变文字在 WPS 里显示异常？**
极旧版本 WPS 对 `gradFill` 文字支持不完整，升级 WPS 或改用 PowerPoint 打开；文件本身没有问题。

**Q: 为什么我的页面文字看起来被压小了？**
skill 不会自动缩字号（保证风格一致），文字放不下说明内容超标。处理顺序：删一半文案 → 拆成两页 → 换信息密度更高的版式（如 featureGrid）。见 [USAGE.md](USAGE.md) 铁律一节。

## 故障排查

安装与运行报错请先查 [INSTALLATION.md](INSTALLATION.md) 的故障排查表；渲染原理与已知限制见 [ARCHITECTURE.md](ARCHITECTURE.md) 第七节。
