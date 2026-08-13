# AGENT.template.md v5

> 适用范围：可移植的项目初始化与迁移。运行期项目管理和 Opinion 规则由外部能力负责。

## 1. 设计契约

生成的项目严格分离四类职责：

1. **项目契约**——`AGENTS.md` 与机器可读的 Project Profile 描述仓库。
2. **项目运行时**——唯一的外部 `project-runtime` Skill 管理工作容器、能力路由、验证、进度和 Git。
3. **指导/审查**——独立的 Opinion provider 解析全局、场景与项目规则。
4. **交付能力**——领域 Skill 与确定性 Tool 创建或检查交付物。

模板必须保持通用。禁止发布个人偏好、组织数据、凭据、私有文件系统路径或复制的私有 Skill。

## 2. 标准目录结构

```text
<project>/
├── AGENTS.md
├── AGENT.RULES.md
├── OPINION.md
├── CLAUDE.md
├── AGENT.md
├── .agents/
│   ├── plugin.json
│   ├── mcp.json
│   ├── skills/
│   └── moe.sakanano.project-runtime/
│       └── project.json
├── .agent-doc/
│   ├── plan.md
│   ├── progress.md
│   └── chat-summary.md
└── docs/
    ├── refs/README.md
    └── drafts/.gitkeep
```

Agent Plugins 1.0 可移植文件直接位于 `.agents/`：`plugin.json`、`skills/` 和 `mcp.json`。反向域名目录保存客户端扩展 Project Profile，避免与未来标准组件碰撞。

## 3. Project Profile

生成 `.agents/moe.sakanano.project-runtime/project.json`：

```json
{
  "$schema": "https://skill.sakanano.moe/skills/agents-init/project.schema.json",
  "schema_version": "1.0",
  "initializer_version": "5.1.0",
  "name": "PROJECT_NAME",
  "profile": {
    "project_type": ["PROJECT_TYPE"],
    "vcs": "VCS",
    "stack": ["STACK"],
    "runtime": "RUNTIME",
    "agent_cli": ["AGENT_CLI"]
  },
  "runtime": {
    "skill": "project-runtime",
    "required": true,
    "commit_policy": "explicit",
    "push_policy": "explicit"
  },
  "opinion": {
    "provider": null,
    "project_overlay": "OPINION.md",
    "strict_mode": "smart"
  },
  "capabilities": {
    "plugin_roots": [".agents"],
    "plugin_dirs": [],
    "skill_roots": [".agents/skills"],
    "mcp_sources": [".agents/mcp.json"],
    "native_mcp_sources": [],
    "credential_env_file": null,
    "mcp_client_policy": {},
    "destination_skill_root": ".agents/skills",
    "destination_mcp": ".agents/mcp.json"
  },
  "work": {
    "task": null,
    "case": null
  },
  "privacy": {
    "forbidden_default_reads": [],
    "generated_outputs": []
  }
}
```

`$schema` 是公开的 Project Profile 契约。Tool 必须分别验证 `schema_version` 与 `initializer_version`。多值字段使用 JSON 数组；缺失的集成使用 `null` 或空数组，禁止杜撰命令。

## 4. AGENTS.md 模板

```markdown
# PROJECT_NAME — Agent 执行入口

## Project Profile

- 类型：PROJECT_TYPE
- VCS: VCS
- 技术栈：STACK
- Runtime：RUNTIME
- Agent 客户端：AGENT_CLI

机器可读权威源：`.agents/moe.sakanano.project-runtime/project.json`。

## Session 入口

1. 加载 `project-runtime`，作为唯一的项目管理 Skill。
2. 由它读取 Project Profile、当前 Git 状态，以及当前任务必需的入口文件。
3. 使用领域 Skill 处理具体交付物，使用确定性 Tool 执行状态变更。
4. 已配置 Opinion provider 时，实施前请求指导，交付前请求检查。

## 职责边界

- `agents-init` 只创建或迁移本骨架。
- `project-runtime` 负责 Task/Case 选择、文件落位、进度、验证编排、能力管理和 Git 交接。
- Opinion 指导并审查交付物，不管理项目生命周期。
- 领域 Skill 禁止创建无关 Task、编辑根进度、自我修改或自主提交。
- 保留无关改动。push、发布、merge、删除与破坏性迁移都需要明确授权。

## 项目专属入口

- 命令：TODO
- 测试：TODO
- 构建：TODO
- 架构/文档：TODO
- 隐私或禁止路径：未声明
```

保持入口简短。把稳定的项目专属约束放入 `AGENT.RULES.md`；禁止在任一入口文件复制完整运行时工作流。

## 5. 其他生成文件

### AGENT.RULES.md

```markdown
# 项目专属规则

本文件只保存当前仓库独有的稳定约束。通用生命周期由 `project-runtime` Skill 负责。

## 命令与验证

- 初始化：TODO
- 测试：TODO
- 构建：TODO

## 文件落位与生成输出

- 权威源：TODO
- 生成输出：TODO

## 隐私与外部系统

- 默认禁止读取：未声明
- 需要授权的外部写入：全部，除非另有明确配置
```

### OPINION.md

```markdown
# 项目 Opinion 覆盖层

尚未确认项目专属 Opinion 规则。

个人全局与场景规则归用户的私有 Opinion 权威源所有。在 `.agents/moe.sakanano.project-runtime/project.json` 中配置 provider；禁止把这些规则复制进公开项目模板。
```

### CLAUDE.md 与 AGENT.md

```markdown
# Agent 路由

读取 `AGENTS.md` 并遵循其中的 Project Profile。加载 `project-runtime` 管理项目；独立加载已配置的 Opinion provider 进行指导与审查。
```

### 流程占位文件

`.agent-doc/plan.md`:

```markdown
# 计划

当前没有活动的多步骤计划。
```

`.agent-doc/progress.md`:

```markdown
# 进度

当前没有活动的 Task 或 Case。项目工作状态由 `project-runtime` 通过已配置的项目子系统管理。
```

`.agent-doc/chat-summary.md`:

```markdown
# 会话摘要

## 待确认假设

无。

## 未解决冲突

无。

## Opinion 演化候选

无。候选规则通过已配置的 Opinion provider 提交，禁止在此晋升。
```

## 6. Agent Plugin 占位文件

`.agents/plugin.json`:

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
  "name": "PROJECT_SLUG",
  "version": "0.1.0",
  "description": "项目本地的可移植 Agent 能力包。"
}
```

`.agents/mcp.json`:

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
  "mcpServers": {}
}
```

在 `project-runtime` 导入已选择的 Skill 前，保持 `.agents/skills/` 为空。禁止从公开模板初始化包含密钥的 MCP 配置。

## 7. 初始化与迁移

### 新项目

1. 使用只读命令检查事实。
2. 填写有证据支持的 Profile 值，未确定的命令保留为 `TODO`。
3. 预演初始化器并展示碰撞项。
4. 获得授权后应用。
5. 解析 JSON 并验证路由文件。

### 既有项目

1. 保留现有文件并识别其权威性。
2. 与 v5 比较职责，不以文件名是否相同作为判断依据。
3. 先创建机器可读 Profile。
4. 只有 `project-runtime` 可用后，才精简重复的 Agent 入口说明。
5. 保持历史 Task/Case 与能力源完整，随后使用 `project-runtime` 盘点。
6. 只有得到明确授权，才能把个人 Opinion 内容移入私有权威源。

## 8. 验收标准

- 所有生成的 JSON 文档均可解析。
- `AGENTS.md` 与路由文件指向同一个 Project Profile 和 runtime。
- 只有一个 Skill 负责项目管理：`project-runtime`。
- Opinion 已配置为独立 provider，或明确标记为不存在。
- 个人规则、凭据、token、私有路径或私有 Skill 内容均未进入公开模板。
- 除非用户逐项批准替换，否则保留现有文件。
