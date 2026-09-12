# 安装指南

## 环境要求

| 组件 | 版本要求 | 说明 |
|---|---|---|
| 操作系统 | Windows 10+ / macOS / Linux | Windows 体验最完整（PowerPoint COM 渲染预览） |
| Node.js | ≥ 18 | 生成 PPTX（`.pptx` 写入） |
| npm | ≥ 9 | 随 Node.js 附带 |
| Python | ≥ 3.10 | 代码级 QA 与渐变文字后处理 |
| Microsoft PowerPoint 或 WPS Office | 任意近期版本（可选） | 仅用于渲染 PNG 预览；二者都无时可用 LibreOffice 替代 |
| LibreOffice + poppler（可选） | — | 无 PowerPoint/WPS 时的预览渲染替代链路 |

字体无需安装：使用各平台自带字体（Windows 微软雅黑/Segoe UI，macOS 自动回落苹方/SF Pro）。

## 安装步骤

### 1. 复制 Skill 到宿主目录

按你使用的 Agent 宿主选择（目录不存在时先创建）：

| 宿主 | 安装路径 |
|---|---|
| **WorkBuddy** | `~/.workbuddy/skills/apple-keynote-ppt/` |
| **ZCode** | `~/.agents/skills/apple-keynote-ppt/`（用户级）或 `项目/.zcode/skills/`（项目级） |
| **Claude Code** | `~/.claude/skills/apple-keynote-ppt/` |
| 其他标准宿主 | 支持 Agent Skills 规范的目录，详见 [COMPATIBILITY.md](COMPATIBILITY.md) |

```bash
# Windows (Git Bash) 示例 —— WorkBuddy
mkdir -p ~/.workbuddy/skills
cp -r /path/to/apple-keynote-ppt ~/.workbuddy/skills/

# macOS / Linux 示例
cp -r apple-keynote-ppt ~/.workbuddy/skills/
```

> 从私有仓库克隆：`git clone https://github.com/xuboboo/apple-keynote-ppt.git`（需仓库访问权限）。

### 2. 安装运行依赖

```bash
cd <skills目录>/apple-keynote-ppt/scripts
npm install          # 安装 pptxgenjs（约 2 秒）

pip install python-pptx   # Python 侧依赖
```

### 3. 验证安装

```bash
cd <skills目录>/apple-keynote-ppt/scripts

# 生成示例 PPT（12 页，深色模式）
node build_deck.js example_outline.json ../assets/test_deck.pptx

# 代码级 QA
python check_layout.py ../assets/test_deck.pptx --strict

# （可选，Windows）渲染 PNG 预览
bash render_preview.sh ../assets/test_deck.pptx ../assets/test_preview
```

三条命令分别输出 `已生成`、`全部通过`、`exported via PowerPoint.Application` 即安装成功。完成后可删除 `test_deck.pptx` 和 `test_preview/`。

## 故障排查

| 现象 | 原因 | 解决 |
|---|---|---|
| `Cannot find module 'pptxgenjs'` | 未安装 Node 依赖 | 在 `scripts/` 下执行 `npm install` |
| `No module named 'pptx'` | 未安装 python-pptx | `pip install python-pptx` |
| `渐变文字后处理失败` 警告 | Python 缺失或不可用 | 安装 Python 并确保在 PATH 中；PPT 仍会生成，仅渐变退化为纯色 |
| 渲染提示 COM 不可用 | 未装 PowerPoint/WPS，或 Office 损坏 | 安装其一，或按提示改用 `soffice --headless --convert-to pdf` + `pdftoppm` |
| 渲染出的 PNG 字体与预期不同 | 预览机器缺字体被替换 | 属正常回落；宽度判定以 `check_layout.py` 为准 |
| 中文显示为方块 | 系统缺中文字体（罕见） | 安装微软雅黑或苹方 |
| Skill 未被宿主识别 | 目录名与 `name` 字段不一致，或放错目录 | 确认目录名为 `apple-keynote-ppt` 且位于宿主 skills 目录下，重启宿主 |

## 升级与卸载

- **升级**：覆盖 skills 目录下的同名文件夹，重启宿主即可。
- **卸载**：删除 `apple-keynote-ppt/` 文件夹；依赖 `pptxgenjs` 安装在 skill 内部（`scripts/node_modules`），随目录一并删除，不污染系统。
