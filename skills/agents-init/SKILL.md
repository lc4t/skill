---
name: agents-init
description: 使用同目录的 AGENT.template.md 引导项目初始化，生成 AGENTS.md、OPINION.md、AGENT.RULES.md、路由 stub 与 .agent-doc 过程文档。
argument-hint: "[init|start|audit|status|relearning|opinion-update|issues-sync]"
author: lc4t
version: 4.0.0
---

# AGENTS 初始化 Skill

## 结论

本 skill 是 **项目治理初始化入口**。当用户要求“初始化项目”“生成 AGENTS.md”“按模板建立 Agent 协作规范”时，Agent 应先读取同目录的 `AGENT.template.md`，再根据当前仓库结构和用户约束生成项目级治理文件。

`SKILL.md` 只保留执行入口、触发条件和最小流程；完整模板、问卷、OPINION 体系、验收规则和迁移说明放在 `AGENT.template.md` 中维护。当前模板事实版本为 **v4.0**。

---

## 适用场景

| 场景 | 处理方式 |
|---|---|
| 新仓库初始化 | 读取 `AGENT.template.md`，扫描仓库，生成治理文件草案 |
| 已有仓库标准化 | 保留现有代码，只补齐 Agent 协作规范 |
| 多 Agent 协作 | 生成 `AGENTS.md` 作为唯一主执行文件，其他入口文件只做路由 |
| 项目偏好沉淀 | 生成 `OPINION.md`，记录价值取向、审美偏好和协作边界 |
| 过程追踪 | 生成 `.agent-doc/`，记录计划、进度、假设、冲突和经验 |

---

## 必读文件

Agent 执行本 skill 时必须按顺序读取：

1. `SKILL.md`：当前执行入口。
2. `AGENT.template.md`：完整治理模板和初始化规则。
3. 当前项目已有文档：如 `README.md`、`AGENTS.md`、`OPINION.md`、`package.json`、`pyproject.toml`、`docker-compose.yml` 等。

如果 `AGENT.template.md` 不存在，应停止初始化并报告缺失文件。

---

## 触发方式

| 用户表达 | 对应动作 |
|---|---|
| “初始化项目治理” | 执行 `init` |
| “生成 AGENTS.md” | 执行 `init`，但重点输出 `AGENTS.md` |
| “按模板初始化” | 执行 `init`，完整读取 `AGENT.template.md` |
| “开始工作” | 执行 `start`，读取现有 `AGENTS.md` 与 `OPINION.md` |
| “审计补全” | 执行 `audit`，检查治理文件完整性 |
| “检查进度” | 执行 `status`，汇总 Git 与 `.agent-doc/` 状态 |
| “relearning” | 执行 `relearning`，沉淀经验 |
| “opinion-update” | 执行 `opinion-update`，演化 `OPINION.md` |

---

## 初始化流程

### 1. 扫描仓库

读取当前目录结构、Git 状态、配置文件和已有文档，自动推断：

- VCS（Version Control System，版本控制系统）
- 项目类型
- 技术栈
- 包管理器
- 启动、测试、构建命令
- 已有 Agent 入口文件

### 2. 读取模板

完整读取同目录的：

```text
AGENT.template.md
```

该文件是母版知识库，包含：

- 初始化问卷
- `AGENTS.md` 结构
- `OPINION.md` 三层体系
- `AGENT.RULES.md` 完整规范
- `.agent-doc/` 目录约定
- T1 假设检查器与 T2 矛盾检测器
- 审计、经验沉淀和版本升级规则

### 3. 一次性确认缺口

只询问无法从仓库推断、且会影响治理文件质量的问题。问题使用编号格式，一次性问完。

### 4. 输出草案

先输出草案，不直接写文件。默认草案包括：

- `AGENTS.md`
- `OPINION.md`
- `AGENT.RULES.md`
- `CLAUDE.md`
- 可选 `AGENT.md`
- 可选 `GEMINI.md`
- `.agent-doc/plan.md`
- `.agent-doc/progress.md`
- `.agent-doc/chat-summary.md`

### 5. 用户确认后写入

用户确认后再写入文件。写入后运行与项目类型匹配的轻量验证，例如：

- Markdown 链接与标题检查
- JSON（JavaScript Object Notation，轻量数据交换格式）解析检查
- 项目已有测试或构建命令
- Git 状态检查

---

## 生成原则

| 原则 | 要求 |
|---|---|
| 单一权威 | `AGENTS.md` 是主执行文件，其他 Agent 入口只做路由 |
| 模板独立 | `AGENT.template.md` 是母版，不混入具体项目事实 |
| 假设显式 | 无法确认的信息标注为假设或待确认 |
| 先草案后写入 | 治理文件属于长期约束，写入前需用户确认 |
| 可审计 | 生成内容必须包含质量门禁、禁止事项和维护方式 |
| 可演化 | 项目偏好进入 `OPINION.md`，运行中可通过 `opinion-update` 更新 |

---

## 输出要求

初始化完成时，Agent 应输出：

1. 已生成或更新的文件列表。
2. 自动推断的信息与来源。
3. 用户确认过的关键偏好。
4. 仍待确认的假设。
5. 已执行的验证命令与结果。
6. 下一步发布或提交建议。

---

## 版本说明

- `SKILL.md`：执行入口，保持短小、稳定、适合 AI 快速加载。
- `AGENT.template.md`：v4.0 完整模板，承载详细规则和长期演化内容。
- `skill.json`：机器可读元数据，供站点索引、自动发现、安装脚本或版本检查使用。
