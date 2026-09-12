# 贡献指南（内部）

本项目为私有仓库，面向内部协作者。改动合入前必须满足本文的验收标准。

## 环境搭建

```bash
git clone https://github.com/xuboboo/apple-keynote-ppt.git
cd apple-keynote-ppt/scripts
npm install                 # pptxgenjs
pip install python-pptx     # QA 与渐变后处理
# 可选：PowerPoint 或 WPS（渲染预览验收需要）
```

## 仓库约定

- **分支**：`main` 为可用版本；改动开特性分支（`feat/xxx`、`fix/xxx`），自验通过后合入。
- **提交信息**：Conventional Commits（`feat:` / `fix:` / `docs:` / `refactor:` / `chore:`）。
- **版本**：合入用户可感知的变更后，在 `CHANGELOG.md` 的 Unreleased 记一条；攒批发布时升 `SKILL.md` frontmatter 的 `version` 并打 tag。

## 改动分级与验收标准

### L1 文档 / references（低风险）

- 改 `references/*.md`、`docs/*`：需保证与 `apple_theme.js` 实际行为一致——规范与代码冲突时，先改代码对齐规范，或同步改两者，不允许留下矛盾。
- 验收：通读一遍 + 确认文中所有命令可执行。

### L2 outline 文案类

- 改 `scripts/example_outline.json` 或新增示例：必须通过 `check_layout.py --strict` 零错误，渲染 PNG 后逐页目检无溢出/重叠。

### L3 主题库 / 版式（高风险）

新增或修改版式的完整步骤：

1. **规范先行**：在 `references/layouts.md` 写出坐标级规格（元素、x/y/w/h、字号、颜色角色、必填字段、无图回落）。先写规范能逼你想清楚留白与层级。
2. **实现**：在 `scripts/apple_theme.js` 实现版式函数，注册进 `LAYOUTS`。坐标、字号遵循 `design-language.md`（页边距 ≥1.0in、正文 ≥16pt、注释 ≥12pt、禁边条/阴影/描边）。
3. **校验接入**：`build_deck.js` 的 `REQUIRED` 表加必填字段；`USAGE.md` 的版式表同步一行。
4. **示例**：`example_outline.json` 增加至少一页该版式。
5. **验收（硬性）**：
   ```bash
   node scripts/build_deck.js scripts/example_outline.json assets/example_deck.pptx
   python scripts/check_layout.py assets/example_deck.pptx --strict   # 零 ERROR
   bash scripts/render_preview.sh assets/example_deck.pptx assets/preview
   ```
   渲染图交 judge 子代理逐页验收（或双人目检），**12/12 全部 pass** 才能合入。有视觉改动的提交必须附渲染前后对比图。

### L4 渲染链路（build_deck / postprocess / check / preview）

- 除 L3 验收外，必须覆盖一条降级路径（如删掉 Python 验证渐变退化警告、模拟 COM 不可用验证 LibreOffice 提示）。
- 修 bug 时先在提交信息里写清根因（参考 `render_preview.sh` 中 outDir 相对路径修复的注释格式）。

## 代码风格

- `apple_theme.js`：坐标和字号一律用文档里的绝对值，不引入魔法缩放；色值必须走 `cleanHex()`。
- 所有用户可见文案、注释、文档使用中文；代码标识符英文。
- 渲染脚本中的 PowerShell 片段注意：heredoc 内 `$` 必须转义为 `\$`，且传给 COM 的路径必须为 Windows 绝对路径（历史 bug 教训，见 `render_preview.sh` 头部注释）。

## 发布清单（release）

1. `CHANGELOG.md`：Unreleased → 新版本号 + 日期，补 compare 链接
2. `SKILL.md` frontmatter `version` 同步
3. 提交 `release: v1.x.x`，打 tag `v1.x.x` 并推送
4. 确认 `assets/example_deck.pptx` 与 `assets/preview/` 为最新示例输出
