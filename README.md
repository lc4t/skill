# 云端 Skills

这是一个公开的 skill 仓库，用于存放可被浏览器、人类读者、AI Agent 和程序共同读取的模板型技能文件。

仓库当前主要承载 **Project Manage v4 / AGENTS.md 初始化模板**：一套用于初始化项目治理文件的模板体系，核心文件是 `SKILL.md`、`AGENT.template.md` 和 `skill.json`。

## 读取入口

| 读者 | 入口 | 用途 |
|---|---|---|
| 浏览器 | [`index.html`](index.html) | 查看站点首页和 skill 目录 |
| 程序 | [`index.json`](index.json) | 读取全站机器索引 |
| AI Agent | [`skills/agents-init/SKILL.md`](skills/agents-init/SKILL.md) | 读取 skill 执行入口 |
| 模板消费者 | [`skills/agents-init/AGENT.template.md`](skills/agents-init/AGENT.template.md) | 读取 Project Manage v4 完整治理模板 |
| 元数据消费者 | [`skills/agents-init/skill.json`](skills/agents-init/skill.json) | 读取单个 skill 的机器元数据 |

## 发布状态

| 分支 | 目标站点 | 说明 |
|---|---|---|
| `main` | `skill.sakanano.moe` | 正式站点，由 GitHub Actions 发布 |
| `test` | 本地预览 | 草稿和测试分支，不触发 GitHub Pages 发布 |

发布由 GitHub Actions（GitHub 自动化工作流）处理。GitHub Pages 只以 `main` 分支为准；`test` 分支用于本地查看和修改验证。

## 目录结构

```text
/
├─ index.html
├─ index.json
├─ README.md
├─ CHANGELOG.md
├─ .github/
│  └─ workflows/
│     └─ pages.yml
├─ skills/
│  └─ agents-init/
│     ├─ SKILL.md
│     ├─ skill.json
│     ├─ index.html
│     └─ AGENT.template.md
└─ archive/
   └─ README.md
```

## 当前 Skill

| Skill | 版本 | 定位 | 浏览器入口 | AI 入口 | 元数据 |
|---|---:|---|---|---|---|
| `agents-init` | `4.0.0` | Project Manage v4 项目治理初始化模板，生成 `AGENTS.md`、`OPINION.md`、`AGENT.RULES.md` 等文件 | [`index.html`](skills/agents-init/index.html) | [`SKILL.md`](skills/agents-init/SKILL.md) | [`skill.json`](skills/agents-init/skill.json) |

## 文件约定

| 文件 | 角色 |
|---|---|
| `SKILL.md` | AI Agent 的执行入口，描述触发条件、必读文件和执行流程 |
| `skill.json` | 机器可读 manifest（清单文件），描述版本、路径、命令、产物和兼容性 |
| `index.html` | 浏览器可读页面 |
| `AGENT.template.md` | Project Manage v4 完整治理模板 |
| `index.json` | 全站索引，汇总所有 skill 的入口与元数据 |

`assets/` 不是固定目录；只有图片、脚本、示例数据等资源较多时再创建。

## 维护约定

- 每个 skill 使用独立目录，目录名使用小写字母、数字和短横线。
- Markdown 执行入口统一命名为 `SKILL.md`。
- 单个 skill 的机器元数据统一命名为 `skill.json`。
- 顶层 `index.json` 只放全站索引，不承载长正文。
- 版本、结构或入口变化记录到 [`CHANGELOG.md`](CHANGELOG.md)。
