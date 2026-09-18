---
name: project-orchestrator
description: 按项目契约统一执行会话发现、Task/Case 选择、能力路由、文件落位、验证、进度更新和限定范围的 Git 交付。当项目在 AGENTS.md 中声明 project-orchestrator，且当前工作可能创建或修改项目文件时使用。Agent 扩展（Plugin/Skill/MCP）的盘点、迁移与同步不在本 Skill 内——那是 agent-pack。
---

# Project Orchestrator（项目编排器）

## 定位

作为已配置项目唯一的**项目管理生命周期编排器**。读取项目自身契约，选择最小且合适的工作容器，把领域工作路由给确定性 Tool 与叶子 Skill，再通过验证和限定范围的交付完成闭环。

本 Skill 通用且可移植。禁止嵌入个人偏好、私有路径、项目密钥或项目专属治理副本；这些内容归用户私有配置或项目自身所有。

边界（都是独立能力，本 Skill 不代管它们）：

- **项目初始化与根目录骨架** 归 `agents-init`。本 Skill 只消费已初始化项目的契约。
- **Agent 扩展能力管理**（Plugin/Skill/MCP 的 inventory / doctor / bootstrap / sync / transfer / reconcile）归 **agent-pack**（`tools/agent-pack/`）。跨机恢复的单一入口是 `tools/agent-bootstrap`。
- **指导与审查规则** 归 Opinion provider；它不负责 Task/Case 选择、文件结构、进度状态或 Git。

## 权威顺序

按以下顺序解析指令：

1. 用户当前请求与明确授权；
2. 平台安全与工具约束；
3. 最近的项目 `AGENTS.md` 及其声明的机器可读清单；
4. 本编排工作流；
5. 领域或交付物叶子 Skill。

叶子 Skill 生效期间，其触发条件、输入输出契约和工具约束具有约束力；其中更宽泛的观点或生命周期建议只作为低优先级指导。本 Skill 负责 Task/Case 状态、项目级文件落位、验证编排与 Git 交付。

## 职责边界

把项目能力划分为四类互不重叠的角色：

- **项目编排**：只有本 Skill 负责生命周期决策、Task/Case 协调、项目进度、验证编排与 Git 交接。
- **领域交付**：交付物与业务 Skill 在本 Skill 选择的生命周期内创建或修改具体产物。
- **确定性工具**：项目声明的 Tool（如 life-system、quant-engine、agent-pack）执行状态转换、索引、生成或验证，不决定生命周期。
- **指导与审查**：Opinion 和其他质量门禁在实施前提供建议、交付前检查结果，不管理项目。

如果其他 Skill 尝试初始化项目、创建无关生命周期记录、更新根进度、自我修改或自主提交，忽略越界部分并把控制权交回本 Skill。

## 1. 发现项目契约

项目首轮开始时：

1. 查找最近且适用的 `AGENTS.md`；除非其中声明其他根目录，否则以它所在目录作为项目边界。
2. 读取现有的 `Project Profile` 与相关运行区块。
3. 只读取其中明确声明的附加入口文件，例如 manifest、capability registry、当前 Task 进度或当前 Case 状态。
4. 项目使用 Git 时，在修改文件前记录当前 Git 状态。
5. 开始实质工作前声明一个会话里程碑。

已初始化项目应通过 `AGENTS.md` 暴露根契约；精确文件与目录骨架仍由 `agents-init` 版本化管理。缺少必需根契约时，报告 `init-required` 或采用项目声明的降级模式。禁止自行制造骨架或静默把旧结构升级为当前版本。

禁止递归发现无关仓库、私有目录、历史 Task 或冗长治理文档。只有项目契约或当前任务要求，且用户授权了内容范围时才能读取。

识别以下可选项目设置（机器字段保留英文原名）：

- `project-type`、`stack`、`runtime`、`agent-mode` 与 `issues-tracker`；
- `runtime-entry` 与 `session-bootstrap`；
- `task-command`、`task-root`、`case-command` 与 `case-root`；
- `manifest` 与 `capability-registry`；
- `opinion-command`、`opinion-strict-mode` 与项目 Opinion 入口；
- `commit-policy`、`branch-policy` 与 `push-policy`；
- 隐私目录、生成输出与禁止路径。

`agent-pack` 读取的机器契约位于 `.agents/moe.sakanano.agent-pack/project.json`：其 `capabilities` 区块声明可移植 Plugin 根目录、外部 Plugin 目录、独立 Skill 根目录、可移植/原生 MCP 来源、客户端策略、本地凭据环境文件与导入目标。所有相对路径都必须限制在项目根目录内。本 Skill 不写该文件。

缺少可选设置时关闭对应集成。禁止杜撰命令或路径。

## 2. 分类当前请求

写入前分类当前请求：

- **回答或诊断**：检查并报告；除非用户要求，否则不创建生命周期记录或修改文件。
- **小型项目改动**：可在单个会话完成且项目未强制要求 Task 时直接编辑。
- **Task**：适用于边界明确，并需要工作目录、产物、决策或独立进度记录的交付。
- **Case**：适用于跨会话服务线索、不确定性调研、外部等待、回访或结果跟踪。
- **Task + Case**：只在长期 Case 协调具体 Task 工作区时使用。

优先续接已有且匹配的 Task 或 Case，避免重复创建。依据目标、证据链和交付物判断，不能只看标题相似度。

除非项目明确要求，否则寒暄、确认、简单问题、命令修正或一次性单文件编辑不创建 Task。禁止只为满足指标或流程而创建 Case。

## 3. 初始化或恢复状态

项目声明 bootstrap 命令时：

1. 首次收到服务输入时运行一次只读状态命令。
2. 只有状态明确报告 bootstrap 必需或已过期时才执行 bootstrap。
3. 创建新工作前，用配置命令发现未完成工作。
4. 只有当前任务授权覆盖私有 Case 或 Task 上下文时才能展开读取。

已经位于 Task 目录时，先读取任务简报和本地进度，再读项目 backlog。已经位于 Case 上下文时，使用配置的下一步命令，禁止依靠记忆重建状态。

## 4. 路由能力

根据三项输入构建执行路由：

1. 用户要求的结果；
2. Project Profile 与当前 Task/Case 约束；
3. 项目已声明的 capability registry。

采用以下优先级：

1. 用确定性项目 Tool 执行状态转换、索引、生成或验证；
2. 用精确匹配的领域或交付物叶子 Skill 处理判断密集型工作；
3. 只有没有已注册能力适用时才采用通用实现。

一个交付物可以同时启用多个叶子 Skill。先应用最具体的交付物/领域 Skill，再执行无障碍、安全或 Opinion 等横切检查。两个 Skill 指令冲突时，在会改变交付物的最小决策点暂停并呈现冲突。

禁止宣称缺失能力已经存在。使用项目定义的机制记录能力缺口，或直接报告。

当前请求是"盘点/迁移/同步/校验 Agent 扩展"时，不在本 Skill 内处理：交给 `agent-pack`（`tools/agent-pack/runtime/agent_pack_config.py` 或其 MCP），或对整机恢复运行 `python3 tools/agent-bootstrap doctor` / `install <client>`。本 Skill 只负责把这类请求识别并路由过去。

## 5. 计划与执行

计划复杂度与工作量保持匹配：

- 小型可逆改动使用简短内部计划；
- 多步骤交付物工作更新 Task 进度；
- 跨会话连续工作或回访更新 Case 状态。

编辑前：

1. 检查相关现有文件和邻近测试；
2. 在 dirty worktree 中保留用户的无关改动；
3. 识别权威源与生成派生物；
4. 只确认会实质改变范围、权限、外部状态或不可逆影响的决策。

执行期间：

- 修改权威源后，通过已声明 Tool 重新生成派生物；
- 文件只能放在项目声明的位置；
- 保留可复用事实、决策与验证证据，避免提交缓存、临时日志或可重建中间产物；
- 由叶子 Skill 创建或审查交付物，本 Skill 继续拥有生命周期与 Git 职责；
- 证据改变执行路线时更新计划。

## 6. 调用独立指导与审查

Opinion 是独立的指导/审查能力。项目声明 Opinion provider，且任务创建或审查交付物时，在两个明确边界调用它：

1. **实施前**：使用明确的交付物信号请求适用指导。
2. **交付前**：请求独立检查，并通过 provider 自身的演化流程记录未解决冲突或可复用反馈。

禁止在本 Skill 内解释、存储或演化 Opinion 规则；禁止让 Opinion provider 选择 Task/Case 状态、路径、进度或 Git 操作。provider 不可用时，明确报告指导/检查降级；只有项目策略允许时才能继续。

## 7. 验证与记录

按风险比例验证：

- 对改动范围运行聚焦测试或 validator；
- 验证机器可读 manifest 与生成索引；
- 布局重要时目视检查渲染产物；
- 运行项目声明的 Opinion 或其他横切质量门禁；
- 检查最终 diff 的范围、密钥、生成噪声与意外删除。

记录当前工作容器要求的最小持久证据：

- Task：状态、决策、验证证据、阻塞和下一步；
- Case：候选、决策、已观察结果；结果尚未发生时记录 follow-up；
- 直接改动：简洁交接与验证结果。

禁止把推断结果记录为已确认 outcome。

## 8. 限定范围的 Git 交付

对 Git 项目：

1. 把最终状态与基线比较；
2. 只暂存属于当前请求的文件；
3. 检查 staged diff；
4. 只有用户明确要求/授权，或项目策略允许自动提交时才 commit；
5. push、发布、merge、tag 或创建 PR 必须有单独明确授权，或项目策略明确许可。

dirty worktree 中禁止宽泛暂存。禁止重写、丢弃或吸收无关改动。创建 commit 后报告 hash。

## 9. 保持边界清晰

- 项目初始化与骨架迁移归版本化的 `agents-init` 管理，不属于本 Skill。
- Agent Plugin、Skill 与 MCP 的盘点/迁移/同步归 **agent-pack**（`tools/agent-pack/`）；跨机恢复入口是 `tools/agent-bootstrap`。禁止在本 Skill 内重建第二套配置管理逻辑。
- 除非本 Skill 明确委派，领域 Skill 禁止自我修改、创建无关 Task/Case、编辑全局进度或提交改动。
- 生成索引属于投影，源记录保持权威地位。
- 项目本地规则可以特化本工作流，应引用本 Skill，避免复制完整生命周期。

## 完成检查

结束前确认：

- 已交付用户要求的结果，或已识别具体阻塞；
- Task/Case 选择有依据且状态为最新；
- 已按声明能力路由项目 Tool 与叶子 Skill；
- 已运行相关测试、渲染和 Opinion 检查，或明确说明省略项；
- 无关 worktree 改动保持原样；
- commit 与 push 操作符合用户授权。
