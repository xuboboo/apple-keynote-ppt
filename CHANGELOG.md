# 更新日志

本项目的所有重要变更都记录在本文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
版本号遵循 [语义化版本 2.0.0](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### Added

- 风格效果画廊：新增 3 套风格各异的示例成品（浅色官网产品发布 InkPod / 商务年度汇报·纯色无渐变 / 英文暗黑发布会 Aurora Buds），连同原有戏仿示例共 4 套 45 页渲染图入库，全部通过代码级 QA 与逐页视觉验收
- 产品文档体系补全：上手教程（TUTORIAL）、架构文档（ARCHITECTURE）、独立 FAQ、内部贡献指南（CONTRIBUTING），README 文档导航按读者角色重组
- GitHub 仓库 About 与 topics 标签

### 计划

- gallery 版式支持 2 行阵列
- 浅色模式渐变可用性优化
- macOS/Linux 预览渲染一等支持（LibreOffice 路径脚本化）
- 演讲者备注支持（outline 每页 note 字段 → PPTX 备注页）

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
