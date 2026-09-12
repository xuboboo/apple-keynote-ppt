# 更新日志

本项目的所有重要变更都记录在本文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
版本号遵循 [语义化版本 2.0.0](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### 计划

- gallery 版式支持 2 行阵列
- 浅色模式渐变可用性优化
- macOS/Linux 预览渲染一等支持（LibreOffice 路径脚本化）
- split / productHero 图片路径的 AI 配图全自动流水线

## [1.1.0] - 2026-09-13

基于 4 套示例 47 页实测反馈的进化版本。

### Added

- **SaaS 标准化文档体系**：安装指南、使用指南、上手教程（TUTORIAL）、架构文档（ARCHITECTURE）、独立 FAQ、宿主兼容性说明（WorkBuddy 等）、内部贡献指南（CONTRIBUTING），README 按读者角色重组
- **风格效果画廊**：4 套风格各异的示例成品（暗黑戏仿 / 浅色产品发布 / 商务汇报 / 英文暗黑），47 页渲染图入库，全部通过代码级 QA 与逐页视觉验收
- **bars 条形对比版式**：2–4 项量化对比，原生形状绘制（PowerPoint 内可编辑），支持 highlight 强调
- **timeline 里程碑版式**：3–4 节点横向时间线，轴线 + 圆点 + 节点说明
- **演讲者备注**：每页可选 `note` 字段，写入 PPTX 备注页
- **顶层渐变开关**：outline 顶层 `"gradient": false` 全篇关闭渐变（商务汇报风），页内可显式覆盖
- **路径围栏**：build_deck.js 所有动态路径经 `safeResolve` 根目录校验，防路径穿越
- 商务示例升级为 13 页（新增 bars 季度轨迹页与 timeline 里程碑页，含备注示例）

### Fixed

- featureGrid / compare / split 多行正文显式顶端对齐，修复 pptxgenjs 默认垂直居中导致的多列首行起点不齐（实测列间偏差约 25px）

### Changed

- check_layout.py 新增告警：渐变页数 >4 时提示违反设计语言（一场最多 3–4 页）
- 文档同步：layouts 坐标规格、SKILL/USAGE 字段参考、架构文档图表限制说明

### 验收

- 商务示例 13/13 逐页视觉验收通过（bars 条长与数值比例、timeline 节点结构、全篇零渐变均经确认）
- valign 修复经不等行数场景（3 行 vs 2 行）复验，列首行对齐偏差 ≤5px

## [1.0.0] - 2026-09-13

### Added

- 六步工作流（收集 → 大纲 → 图片 → 生成 → QA → 交付）写入 `SKILL.md`
- 12 种坐标级版式：cover / statement / section / bignum / productHero / split / featureGrid / compare / gallery / quote / pricing / closing
- `apple_theme.js` 主题库：双模式色板（dark/light）、四色渐变、中西文字体自动选择、大数字单位自动缩放
- OOXML 渐变文字后处理（`postprocess_gradient.py`），补齐 pptxgenjs 不支持渐变文字的能力
- 代码级 QA（`check_layout.py`）：字号下限、CJK 加权溢出估算、文本框重叠、显式字体检查、图片拉伸检测
- PNG 预览渲染（`render_preview.sh`）：PowerPoint COM 优先、WPS 兜底、LibreOffice 降级提示
- `outline.json` 内容与样式分离的大纲格式 + 示例（戏仿 Apple Milk Tea 发布会，12 页）
- 四份 references：设计语言、版式坐标、叙事结构（含戏仿 15 步模板）、图片策略
- SaaS 标准化文档：README、安装指南、使用指南、宿主兼容性说明（兼容 WorkBuddy）
- 示例成品通过视觉验收 12/12

[Unreleased]: https://github.com/xuboboo/apple-keynote-ppt/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/xuboboo/apple-keynote-ppt/releases/tag/v1.0.0
