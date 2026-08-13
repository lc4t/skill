---
name: agents-init
description: 初始化仓库或将既有仓库迁移到 agents-init v5 项目骨架。用户要求初始化 Agent 协作、创建 AGENTS.md、增加 Project Profile（项目配置）或迁移旧版 agents-init 结构时使用。本 Skill 只负责结构；project-runtime 负责持续项目管理，Opinion 负责指导与审查。
---

# Agents Init（项目初始化）

## 定位

创建一份精简、可移植、可被兼容 Agent 自动发现的项目契约。本 Skill **只负责初始化与有版本的骨架迁移**。

严格保持以下职责边界：

- `agents-init`：创建项目骨架与 Project Profile；
- `project-runtime`：管理持续工作、Task/Case 状态、能力、验证、进度与 Git 交付；
- Opinion provider（Opinion 提供方）：提供独立的指导与审查规则；
- 领域 Skill：创建或检查具体交付物。

禁止把用户的个人规则、凭据、私有路径、MCP 密钥或私有 Skill 内容写入这个公开模板。

## 必读材料

初始化或迁移项目前，完整读取 [AGENT.template.md](AGENT.template.md)。它是 v5 骨架契约与迁移指南。

## 工作流程

1. 检查仓库根目录、现有 Agent 入口文件、Git 状态、项目清单以及可能的构建/测试命令。
2. 只推断有直接证据的字段；标记不确定值。只有缺失选择会实质改变生成契约时，才集中询问一次。
3. 展示拟创建的文件计划与碰撞项。
4. 用户确认后，使用 `--apply` 运行随附初始化器；脚本无法运行时，手工创建同一组文件。
5. 初始化模式下，任一碰撞都会阻止全部写入。保留所有既有文件；迁移模式只修改用户审阅差异后明确选择的文件。
6. 解析生成的 JSON，检查入口文件路由，并报告剩余占位符。

预演示例：

```bash
python3 scripts/init_project.py --project /path/to/project \
  --name example --project-type code --vcs github \
  --stack python --runtime local --agent-cli codex
```

审阅计划后再应用：

```bash
python3 scripts/init_project.py --project /path/to/project \
  --name example --project-type code --vcs github \
  --stack python --runtime local --agent-cli codex --apply
```

迁移既有项目时，保留所有碰撞文件，只显式替换已审阅的路径。替换操作必须指定项目外恢复目录：

```bash
python3 scripts/init_project.py --mode migrate --project /path/to/project \
  --name example --project-type code --vcs github \
  --stack python --runtime local --agent-cli codex \
  --replace AGENTS.md --recovery-dir /safe/recovery/example-v5 --apply
```

## 输出契约

v5 基线结构如下：

```text
AGENTS.md
AGENT.RULES.md
OPINION.md
CLAUDE.md
AGENT.md
.agents/
├── plugin.json
├── mcp.json
├── skills/
└── moe.sakanano.project-runtime/project.json
.agent-doc/
├── plan.md
├── progress.md
└── chat-summary.md
docs/
├── refs/README.md
└── drafts/.gitkeep
```

`AGENTS.md` 是项目执行入口；`CLAUDE.md` 与 `AGENT.md` 是短路由文件；`OPINION.md` 有意保持为空白项目覆盖层，只包含维护指引。个人全局规则留在用户的私有 Opinion 权威源中，禁止复制到本模板。

## 迁移规则

- 只根据明确版本标记识别旧版本；禁止把陌生结构推断为 v4。
- 使用 `--mode migrate`；未选择的碰撞文件保持原样。写入新骨架文件前，每个 `--replace` 路径都必须备份到项目外。
- 保留项目事实与本地约束。
- 只有在 `project-runtime` 可用后，才从 Agent 入口文件移除重复的生命周期说明。
- 只有得到明确授权，才能把个人/全局规则移入用户的私有权威源；禁止提交到本公开模板。
- 禁止删除旧 Skill、MCP 条目、Task 数据或进度记录。初始化后由 `project-runtime` 盘点并迁移能力。
- 本 Skill 禁止执行项目工作、创建 Task/Case、演化 Opinion 或 commit/push。

## 完成报告

报告已生成文件、推断出的 Profile 值及证据、保留的碰撞项、验证结果，以及下一步必须安装的 runtime。初始化或迁移完成后结束。
