# 云端 Skills

这是一个公开的 skill 仓库，用于存放可被浏览器、人类读者、AI Agent 和程序共同读取的模板型技能文件。

仓库当前主要承载 **agents-init v5 / Project Profile 初始化器**：只负责创建或迁移通用项目骨架。运行期项目管理由外部 `project-runtime` 负责，Opinion 作为独立能力提供指导和审查。

## 读取入口

| 读者 | 入口 | 用途 |
|---|---|---|
| 浏览器 | [`index.html`](index.html) | 查看站点首页和 skill 目录 |
| 程序 | [`index.json`](index.json) | 读取全站机器索引 |
| AI Agent | [`skills/agents-init/SKILL.md`](skills/agents-init/SKILL.md) | 读取 skill 执行入口 |
| 模板消费者 | [`skills/agents-init/AGENT.template.md`](skills/agents-init/AGENT.template.md) | 读取 agents-init v5 骨架契约与迁移规则 |
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
│     ├─ AGENT.template.md
│     └─ scripts/
│        ├─ init_project.py
│        └─ test_init_project.py
└─ archive/
   └─ README.md
```

## 当前 Skill

| Skill | 版本 | 定位 | 浏览器入口 | AI 入口 | 元数据 |
|---|---:|---|---|---|---|
| `agents-init` | `5.0.0` | 初始化 Project Profile、Agent Plugins 占位与最小路由文件，不承载运行期管理或个人 Opinion | [`index.html`](skills/agents-init/index.html) | [`SKILL.md`](skills/agents-init/SKILL.md) | [`skill.json`](skills/agents-init/skill.json) |

## 文件约定

| 文件 | 角色 |
|---|---|
| `SKILL.md` | AI Agent 的执行入口，描述触发条件、必读文件和执行流程 |
| `skill.json` | 机器可读 manifest（清单文件），描述版本、路径、命令、产物和兼容性 |
| `index.html` | 浏览器可读页面 |
| `AGENT.template.md` | agents-init v5 骨架契约与迁移说明 |
| `scripts/init_project.py` | 默认 dry-run、无覆盖的确定性初始化器 |
| `index.json` | 全站索引，汇总所有 skill 的入口与元数据 |

公开模板不包含个人 `global.yml`、凭据、私有路径或私有 Skill 内容。生成的 `OPINION.md` 只含项目覆盖占位和私有 Opinion authority 配置指引。

## 维护约定

- 每个 skill 使用独立目录，目录名使用小写字母、数字和短横线。
- Markdown 执行入口统一命名为 `SKILL.md`。
- 单个 skill 的机器元数据统一命名为 `skill.json`。
- 顶层 `index.json` 只放全站索引，不承载长正文。
- 版本、结构或入口变化记录到 [`CHANGELOG.md`](CHANGELOG.md)。
