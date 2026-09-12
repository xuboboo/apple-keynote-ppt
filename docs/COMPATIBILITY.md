# 宿主兼容性说明（Host Compatibility）

本 Skill 以**标准 Agent Skills 规范**（含 `SKILL.md` 的技能目录）发布，不绑定任何单一 Agent 宿主。

## 规范符合性

| 规范要求 | 本 Skill 状态 |
|---|---|
| 目录名与 `SKILL.md` 的 `name` 字段完全一致（小写 kebab-case，1–64 字符） | ✅ `apple-keynote-ppt` |
| frontmatter 含 `name` + `description`（description 同时描述"做什么"与"何时触发"） | ✅ |
| 渐进式披露三层：name/description 常驻 → SKILL.md 正文触发后加载（<500 行，实测 122 行）→ references 按需读取 | ✅ |
| 辅助材料放 `references/`、`scripts/`、`assets/` | ✅ |
| 技能自包含：依赖随目录安装（`scripts/node_modules`），不污染系统 | ✅ |

## 已验证与兼容宿主

| 宿主 | 安装路径 | 状态 |
|---|---|---|
| **WorkBuddy** | `~/.workbuddy/skills/apple-keynote-ppt/` | ✅ 兼容——WorkBuddy 完全兼容标准 Agent Skills（OpenClaw/Claude Code 系）格式，无需任何修改，把技能目录复制进去重启即可 |
| **ZCode** | `~/.agents/skills/apple-keynote-ppt/`（用户级）/ `<项目>/.zcode/skills/`（项目级，优先级更高） | ✅ 已实测（本 skill 的开发与验收环境） |
| **Claude Code** | `~/.claude/skills/apple-keynote-ppt/` | ✅ 结构兼容（同为 Agent Skills 规范） |
| 其他遵循 Agent Skills 规范的宿主 | 宿主各自的 skills 目录 | ✅ 预期兼容 |

> Windows 上 `~` 即 `C:\Users\<用户名>`。

## 宿主能力差异与降级行为

Skill 的完整体验依赖宿主的三个能力，缺失时按以下方式降级（不会失败）：

| 能力 | 用途 | 缺失时的降级 |
|---|---|---|
| Bash/命令执行 | 运行 `build_deck.js`、QA、渲染脚本 | 无法生成 PPTX（核心流程需要） |
| 视觉验收子代理（如 judge） | 渲染图质检 | AI 自行逐页检查渲染 PNG |
| 文生图能力 | AI 生成产品配图 | 自动回落纯排版（基线体验完整） |

## 平台差异

- **Windows**（推荐运行环境）：预览渲染走 PowerPoint/WPS COM；字体为微软雅黑 + Segoe UI。
- **macOS / Linux**：PPTX 生成与 QA 不受影响；PNG 预览需 LibreOffice + poppler（`render_preview.sh` 内含提示命令）；渲染字体回落苹方/SF Pro。
- 跨平台打开 PPTX：字体自动回落（雅黑↔苹方、Segoe UI↔SF Pro），版式不受影响。
