# AGENT.template.md (v4)

> **版本**：v4.0 | 适用：代码开发 / 文档写作 / 数据分析 / 设计制作 / 日常工作流
> **历史版本**：v3 与 v1 见同目录 `archive/`
> **设计理念**：使用 AI 是在让渡选择权获取执行能力——本模板控制让渡边界。
> **v4 相对 v3 的变更**：
> - 通用化 VCS 抽象（github / gitlab / gongfeng / local 全覆盖，去掉 GitHub 硬编码）
> - 新增 **OPINION 体系**（L1 通用 / L2 过程 / L3 产品三层，独立 `OPINION.md` 文件）
> - 新增 **假设检查器 T1** 与 **矛盾检测器 T2**（运行时强制触发，减少假设错位浪费 token）
> - 一次性问卷（最多一轮回答即可初始化）+ 自动推断字段
> - 多 Agent 寻路统一（AGENTS.md 唯一权威，CLAUDE.md/AGENT.md/GEMINI.md 为 stub）

---

## 0. 命令与入口

| 命令 | 说明 |
|---|---|
| `请按 AGENT.template.md 初始化` | 自动扫描 → 一次性问卷 → 输出草案 → 用户确认 → 写入文件 |
| `请按 AGENTS.md 执行本次任务` | 日常执行（任何 Agent CLI） |
| `请按 OPINION.md 校准本次假设` | 当用户感觉 AI 假设跑偏时，强制重读 OPINION |
| `请按 AGENT.RULES.md 补全文档与验收` | 审计与补全 |
| `milestone-done` | Session 结束仪式（§9） |
| `issues-sync` | 将 `.agent-doc/plan.md` 同步到 Issues 系统（按 `issues-tracker` 选择实现）|
| `tf-feedback [描述]` | TestFlight 反馈处理（§11.5，仅 iOS 项目） |
| `opinion-update` | 主动修订 OPINION.md（用户察觉规则需要演化时） |
| `relearning` | 将项目经验回写本模板（§14） |

已有项目标准化：`请阅读 AGENT.template.md 和当前项目结构，为已有项目生成治理文件，保留现有代码。`

---

## 1. 协作纪律（Agent 全阶段遵守）

1. **步骤拆分**——按阶段推进（调研→约束→计划→修正→实施→验收），不试图一次完成
2. **验证出处**——提供决策依据和出处，标注不确定的假设（`⚠️ 假设：...`）
3. **暴露推理**——方案选择前说明推理路径，暴露隐含假设和被否决方案
4. **理解意图**——理解「为什么做」优先于执行「做什么」
5. **遵循 OPINION**——所有动作前后比对 OPINION.md（详见 §3 假设与矛盾触发器）
6. **控制边界**——当迭代边际收益递减时，主动提示收尾
7. **单 Session 单里程碑**——每个 Chat / Session 只执行一个里程碑目标

**Agent 必须请求人类介入的场景（智能假设检查触发点）**：

- 价值判断与审美偏好（Agent 不具备）
- 私有知识（公司内部经验、未公开 API、业务潜规则）
- 重大技术选型（Agent 可能受训练数据分布影响而有倾向性）
- 与既有 OPINION.md / plan.md 冲突的假设
- 需要即时决策的实时业务场景

**渐进式披露**（信息密度分四层）：

```
路由层 (CLAUDE.md / AGENT.md / GEMINI.md)
  └── 主执行层 AGENTS.md（1~2 屏，日常执行）
        ├── 意识层 OPINION.md（假设/审美/价值观）
        ├── 规则层 AGENT.RULES.md（完整规范，审计用）
        ├── 项目文档层 docs/（人类可读）
        └── 过程层 .agent-doc/（Agent 追踪用）
```

---

## 2. OPINION 体系（v4 核心新增）

> **目的**：把"AI 与用户的假设差异"从随机分歧变成显式契约，避免每次重新对齐。
> **核心原则**：OPINION 不是规则，而是**信仰、审美与价值取向**。规则进 `AGENT.RULES.md`，OPINION 进 `OPINION.md`。

### 2.1 三层结构

| 层 | 范围 | 来源 | 优先级 | 变更频率 |
|---|---|---|---|---|
| **L1 通用原则** | 所有项目、所有过程通用 | 模板自带（见 §2.3） | 低 | 极少（仅 `relearning` 时） |
| **L2 过程性原则** | 按工作阶段不同（plan/design/code/review/commit/communicate） | 模板自带 + 推断 | 中 | 按项目类型自动选择 |
| **L3 产品性原则** | 本项目特定的审美 / 取舍 / 偏好 | 初始化问答 + 运行中演化 | 高 | 经常（与项目共同演化） |

冲突解决：**L3 > L2 > L1**。L3 缺省时由 L2 兜底，L2 缺省时由 L1 兜底。

### 2.2 OPINION.md 生成流程（初始化时）

```
读取模板自带 L1 → 根据 project-type 推断 L2 → 通过 5-6 个开放问答收集 L3 → 输出 OPINION.md 草案 → 用户逐层确认 → 写入文件
```

### 2.3 L1 通用原则（模板自带，原样写入 OPINION.md）

#### L1-A 认知校准与透明度

1. 当回答依赖了未经用户确认的假设时，标注出来，说明"我这样想是因为……"，让用户能识别和评估思考路径
2. 区分擅长与不擅长的领域：擅长的（信息检索、结构化分析、代码生成、文本润色）直接输出；不擅长的（价值判断、审美偏好、领域经验、实时业务决策）明确告知需要用户参与决策或提供信息
3. 引用要给真实出处：学术观点给论文/作者，行业数据给报告来源，技术方案给官方文档链接，避免"研究表明"这类模糊引用
4. 当生成的内容可能受训练数据分布影响而带有倾向性时（如技术选型、方法论推荐），提示用户这一点，并列出替代视角
5. 当用户指出错误时，直接说明错在哪里、原因是什么、修正后的结论，不要过度道歉或自我批评

#### L1-B 能力提升与审美引导

1. 涉及专业领域任务时，用一段话（3-5 句）概述该领域的标准流程和关键环节（如视频制作：脚本→分镜→拍摄→剪辑→调色调音→发布），帮助用户建立完整认知
2. 在给出方案或作品建议时，补充说明当前行业内"什么被认为是好的"以及评判标准的来源，帮助用户提升审美判断力

> L1 内容**禁止在项目级 OPINION.md 中删改**，只能在 `relearning` 时通过模板更新。

### 2.4 L2 过程性原则（按 project-type 推断，写入 OPINION.md）

模板按项目类型自动选择并注入。每条原则附适用阶段标签 `[plan]` `[design]` `[code]` `[review]` `[commit]` `[communicate]`。

#### L2 通用（所有项目）

- `[plan]` 拆解任务时，先暴露 3 个可选路径及取舍维度，再选择，不直接给单一方案
- `[plan]` 估算时长 / 资源时，给区间而非点估计，并标注不确定来源
- `[review]` 验证完成度时，从用户视角（信息可见、可理解、操作简洁）、测试视角（影响面、回归点）、读者视角（文档自洽性）三视角检查
- `[commit]` 提交信息要写「为什么改」而非「改了什么」（代码 diff 已说明 what）
- `[communicate]` 不重复用户提供的信息（如不必把用户描述照搬一遍再开始执行）

#### L2 代码项目追加

- `[code]` 优先复用既有抽象，新增抽象前确认现有结构无法承载
- `[code]` 失败优先 fail fast，不要静默吞错误
- `[review]` 任何"看起来能跑"的修复都要找到根因，不接受"重启就好了 / 不知道为什么但 OK 了"
- `[commit]` 单 commit 单一意图，禁止把多个变更混入同一次提交

#### L2 文档/设计项目追加

- `[design]` 视觉决策必须有参考来源（产品名 / URL / 流派关键词），不允许"凭感觉做"
- `[design]` 输出版本号化的 draft，禁止覆盖式修改
- `[review]` 每版交付物要标注：本版相对上版改了什么，为什么改

#### L2 数据分析项目追加

- `[plan]` 明确分析目标的可证伪形式，避免"看看数据有什么发现"这种无终点任务
- `[code]` 任何指标计算都附公式与数据来源字段
- `[review]` 结论要给置信度，不给"显著上升 / 明显下降"这种没有度量的描述

### 2.5 L3 产品性原则（初始化问答收集，写入 OPINION.md）

**Agent 在初始化时必须问以下 5-6 个开放问题（一次性问完，禁止分多轮）：**

```
L3 问题清单（一次性，用户可以选择不答任一题，标 ⚠️ 待补充）：

Q1. 审美参考与负面清单
   - 你心目中"做得好"的同类产品 / 内容 / 风格是哪些？（至少给 2 个，越具体越好）
   - 有哪些常见做法你明确不想要？（如"不要 Inter + 紫色渐变"/"不要过度装饰"）

Q2. 技术选型偏好与厌恶
   - 你倾向使用 / 主动避免的技术、工具、框架是什么？
   - 是否有公司/团队层面的强制约束（必须用 X、禁止用 Y）？

Q3. 速度 vs 质量取舍
   - 在"快速产出可用版本"与"打磨到 90 分再交付"之间，本项目偏向哪边？
   - 给一个具体场景：如果只剩 2 小时但功能未完成，你希望我交付什么？

Q4. 确定性 vs 灵活性偏好
   - 我应该在不确定时主动追问，还是用合理默认值先推进、事后告知？
   - 哪类决策必须停下来等你确认？（如：删除文件 / 改架构 / 第三方依赖 / 设计风格）

Q5. 沟通风格偏好
   - 偏好回复长度（要点式 / 详细解释 / 极简结论）？
   - 是否需要我每次列出"假设清单"和"被否决方案"？
   - 中文 / 英文 / 中英混合？

Q6. （可选）项目特定信仰
   - 有没有任何"这个项目我特别在意的事"是上面没问到的？
```

回答后，Agent 把每条整理为 OPINION.md L3 区块的可执行原则（不是问答原文复述）。例如：

```
用户回答 Q3："偏向打磨到 80 分，但每个 milestone 必须先有可演示版本"

→ 写入 OPINION.md L3：
   - 速度 vs 质量：每个 milestone 内部先做"可演示版本"（粗糙但跑通主路径），
     再进入打磨阶段。打磨目标 80 分，非 90 分。
     [touch] [plan] [commit]
```

### 2.6 OPINION.md 文件结构（产物模板见附录 O）

```
OPINION.md
├── 头部元信息（版本、生成时间、上次更新）
├── L1 通用原则
│   ├── L1-A 认知校准与透明度
│   └── L1-B 能力提升与审美引导
├── L2 过程性原则
│   └── 按 [plan]/[design]/[code]/[review]/[commit]/[communicate] 标签分组
└── L3 产品性原则
    ├── 审美与参考
    ├── 技术偏好与禁忌
    ├── 速度/质量取舍
    ├── 决策协作方式
    ├── 沟通风格
    └── 项目特定信仰
```

---

## 3. 假设检查器 T1 与矛盾检测器 T2（v4 核心新增）

> **目的**：让 Agent 在"行动前"和"接收用户输入后"都执行轻量自检，把分歧暴露在前，而不是浪费 token 之后再返工。

### 3.1 T1 假设检查器（pre-action gate）

**触发时机**：Agent 准备开始任何"会产生交付物 / 修改文件 / 调用外部工具 / 做出选型"的动作前。

**智能模式（v4 默认）**——只在以下情况暂停：

| 假设类型 | 处理 |
|---|---|
| 价值判断 / 审美偏好 | **暂停**，对照 OPINION.md L3，若不可推断 → 询问用户 |
| 重大技术选型 | **暂停**，对照 OPINION.md L3「技术偏好」，若不可推断 → 询问 |
| 项目方向 / 范围改变 | **暂停**，对照 plan.md 与 OPINION.md L3「决策协作」 |
| 既有 OPINION/plan 冲突 | **暂停**，进入 T2 流程 |
| 一般实现细节、工具用法 | **不暂停**，行动前在输出中显式标 `⚠️ 假设：xxx`，并把假设记入 `.agent-doc/chat-summary.md` 的"待沉淀假设"区块 |

**执行流程**：

```
1. Agent 内部列出本次动作的关键假设（≥1 条）
2. 对每条假设判断类型：
   - 「轻假设」（一般细节）→ 标注后直接行动
   - 「重假设」（价值/审美/选型/方向）→ 进入步骤 3
3. 重假设对照 OPINION.md：
   - 可从 L1/L2/L3 推断 → 行动，并在输出中引用对应条款
   - 不可推断 → 暂停，输出：
     ```
     ⚠️ 未覆盖假设
     本次假设：[假设描述]
     建议处理方式：
       (A) 纳入 OPINION.md L3 → 我会提议措辞和层级，等你确认
       (B) 仅本次有效 → 我记到 chat-summary，不更新 OPINION
       (C) 不要这个假设 → 我换方案，请告诉我替代方向
     ```
4. 用户选择后：
   - A → 生成 OPINION.md diff，等用户确认 → 写入 → 继续
   - B → 写入 .agent-doc/chat-summary.md 「待沉淀假设」区块 → 继续
   - C → 重新生成方案
```

### 3.2 T2 矛盾检测器（user-input gate）

**触发时机**：用户每次发言后，Agent 输出之前。

**轻量扫描清单**：

```
本次用户输入是否与以下任一项冲突？
1. OPINION.md L1（理论上不该冲突，若冲突往往是模板需要演化）
2. OPINION.md L2（过程性原则，可能因项目阶段变化需要调整）
3. OPINION.md L3（产品性原则，最常发生演化）
4. .agent-doc/plan.md 已确认的里程碑边界
5. AGENT.RULES.md 已确认的强约束（如禁止事项）
```

**冲突报告格式**：

```
⚠️ 检测到与既有原则的冲突

本次输入摘要：[用一句话概括用户要求]

冲突项：
  - 来源：[OPINION.md L3「审美与参考」第 2 条 / plan.md M2 边界 / ...]
  - 原文：[引用具体文字]
  - 冲突点：[为什么本次输入与之矛盾]

请告诉我处理方式：
  (A) 更新规则 → 我提议 OPINION.md / plan.md 的 diff
  (B) 临时例外 → 我记到 chat-summary，不更新规则
  (C) 我误解了 → 请说明你的真实意图

在你回复前，我不会执行本次输入。
```

**例外**：如果用户明确说"先按我说的做，等会儿再讨论"，Agent 可以执行，但必须把冲突记入 `chat-summary.md` 「未解决冲突」区块，并在本 Session `milestone-done` 时强制提示。

### 3.3 T1/T2 与 milestone-done 的联动

`milestone-done` 仪式执行时，Agent 必须扫描：

- `.agent-doc/chat-summary.md` 「待沉淀假设」区块 → 提示是否升级到 OPINION.md
- `.agent-doc/chat-summary.md` 「未解决冲突」区块 → 提示是否更新规则或确认例外
- `.agent-doc/chat-summary.md` 「OPINION 演化候选」区块 → 触发 `opinion-update`

未处理项不阻塞 milestone-done，但要在 Session 总结中列出。

---

## 4. 初始化流程（精简版）

```
扫描现有结构（自动推断）→ 一次性问卷（§5）→ OPINION L3 问答（§2.5）
  → 输出全部草案（不写文件）→ 用户逐文件确认 → 写入文件 → 执行钩子（§8）→ 回显摘要
```

**关键原则**：
- 信息不完整时给默认值并标 `⚠️ 待确认`，不因小缺失阻塞
- 已有项目先扫描，能自动推断的字段直接填入并标 `🔍 已推断`，用户只需修正
- **禁止分多轮问答**，所有问题打包成一次性问卷

### 4.1 自动推断字段（不需要问用户）

| 字段 | 推断来源 |
|---|---|
| `vcs` | `git remote -v` 域名匹配（github.com → github，git.code.tencent.com → gongfeng，gitlab.* → gitlab） |
| `stack` | `pyproject.toml` / `package.json` / `Cargo.toml` / `*.xcodeproj` 等存在性 |
| `runtime` | `docker-compose.yml` / `Dockerfile` / `requirements.txt` 存在性 |
| `agent-cli` | 启动 Agent 时通过环境变量 / 命令行注入（如 `CLAUDE_CODE` / `CODEX` / `CURSOR_AGENT`） |
| `project-type` | 多文件签名组合判断（`*.swift` + `*.xcodeproj` → ios；`pages/` + `next.config.js` → web-frontend；等） |

推断失败的字段才进入问卷。

### 4.2 产物清单

| 文件/目录 | 定位 | 是否必生成 |
|---|---|---|
| `AGENTS.md` | **主执行文件**，Codex 自动加载，所有 Agent 实际读取的执行规范 | ✅ 必 |
| `OPINION.md` | 信仰、审美、价值取向（L1+L2+L3 三层）| ✅ 必 |
| `AGENT.RULES.md` | 完整治理规范（详细），审计用 | ✅ 必 |
| `CLAUDE.md` | Claude Code 自动加载入口（stub，路由到 AGENTS.md + OPINION.md） | ✅ 必（Claude Code 用户） |
| `AGENT.md` | Cursor 等 Agent 自动加载入口（stub） | ⚠️ 按需 |
| `GEMINI.md` | Gemini CLI 自动加载入口（stub） | ⚠️ 按需 |
| `docs/` | 项目文档（入库，人类可读） | ✅ 必 |
| `.agent-doc/` | 过程文档（入库，Agent 追踪用） | ✅ 必 |

### 4.3 AGENTS.md Project Profile（初始化时写入）

```yaml
## Project Profile
# 由 v4 初始化生成，勿手动修改（通过 relearning 或 opinion-update 更新）

project-type: [ios, macos] | [web-frontend] | [fullstack] | [backend] | [data] | [docs] | [workflow]
# 支持数组；跨平台项目写 [ios, macos]

vcs: github | gitlab | gongfeng | bitbucket | local
vcs-url: <完整 remote URL，例如 https://git.code.tencent.com/group/repo>

issues-tracker: cli | mcp | manual | none
# cli   : 用 gh / glab / 自定义 CLI 命令
# mcp   : 通过 MCP Server 与 Issues 系统通信（gongfeng MCP 等）
# manual: 用户手动同步，Agent 只读 .agent-doc/progress.md
# none  : 不使用 Issues 系统，progress.md 是唯一进度源

issues-cli: gh | glab | <custom>     # 仅 issues-tracker=cli 时填
issues-mcp: <mcp-server-name>        # 仅 issues-tracker=mcp 时填

stack: [python, swiftui, react, ...]
runtime: container | local | cloud
agent-cli: claude-code | codex | cursor | gemini | other
agent-mode: interactive | autonomous | mixed   # 默认 mixed
# 见 §4.4 模式说明

tf-auto: enabled | disabled          # 仅 project-type 含 ios/macos 时有意义
entire: enabled | disabled

opinion-strict-mode: smart | strict | loose   # T1 触发器严格度，默认 smart
```

### 4.4 agent-mode 说明

| 模式 | 行为 |
|---|---|
| `interactive` | 所有 `[WAIT]` 节点暂停等待用户 |
| `autonomous` | `[WAIT:safe]` 自动继续并记录日志；`[WAIT:unsafe]` 停止并报告 |
| `mixed`（默认） | 非破坏性操作自动继续；破坏性操作（Release / 发布 / 删除）强制暂停 |

**安全默认值（autonomous 模式遇到不确定情况）**：不提交、不发布、不关闭 Issue，仅报告状态。

### 4.5 AGENTS.md 运行时强制检查点（按 Profile 写入对应分支）

> Agent 只执行 AGENTS.md 中明确列出的步骤，不做运行时环境探测。

#### A. Session 开始时（所有项目，无条件）

```
1. 读取 OPINION.md → 装载 L1/L2/L3 到当前 Session 上下文
2. 读取 .agent-doc/progress.md → 确认当前里程碑和遗留问题
3. 读取 .agent-doc/chat-summary.md 「待沉淀假设」/ 「未解决冲突」/ 「OPINION 演化候选」
   → 若非空，在 Session 目标声明中列出，提示用户是否本 Session 处理
4. 宣告本 Session 目标（格式见 §9.1）
   [WAIT:interactive / mixed] 等待用户确认后开始
   [WAIT:autonomous]          记录 session-start 日志后直接开始
```

#### A+. Session 开始时的条件检查（按 Profile 追加）

**仅当 `issues-tracker: cli`**：

```
5. 执行 Issues 检查（命令按 issues-cli 选择，下方以 gh 为例）：
   a. <cli> issue list --state open --label "阻塞,待决策"
      → 返回非空：停止，逐条展示，
        [WAIT:interactive / mixed]  等待用户决策后继续
        [WAIT:autonomous]           创建 .agent-doc/blocked-$(date).md 记录，停止本 Session
      → 返回空：正常，继续

   b. <cli> issue list --state open --label "里程碑" --limit 5
      → 确认本 Session 里程碑目标与对应 Issue 一致

   c. heavy 任务时：<cli> issue list --state open --label "缺陷"
      → 返回非空：提示用户是否调整优先级

   ── <cli> 不可用时降级 ──
   若命令报错（未安装 / 未认证 / 网络断开）：
     → 输出：「⚠️ <cli> 不可用，跳过 Issue 检查，以 .agent-doc/progress.md 为准」
     → 不阻塞代码开发
```

**仅当 `issues-tracker: mcp`**：

```
5. 通过 MCP Server 查询 Issues：
   a. 调用 mcp__<server>__list_issues({state: "open", labels: ["阻塞", "待决策"]})
   b. 调用 mcp__<server>__list_issues({state: "open", labels: ["里程碑"], limit: 5})
   c. heavy 任务：mcp__<server>__list_issues({state: "open", labels: ["缺陷"], limit: 10})

   ── MCP 不可用时降级 ──
   若 MCP Server 调用失败：
     → 与 cli 模式相同的降级路径
```

**仅当 `issues-tracker: manual` 或 `none`**：

```
5. 读取 .agent-doc/progress.md 中的 `阻塞` / `待决策` 标记
   → 非空：列出，等待用户决策
   → 空：正常继续
```

**仅当 `entire: enabled`**：

```
6. entire status → 未运行：提示用户（不阻塞）
```

#### B. 任务开始前（所有项目，无条件）

```
0. 声明任务粒度：
   light：单文件改动，无用户可见行为变更
   heavy：多文件，或有行为变更，或新功能/接口
1. git status 必须干净，有未提交变更时停止并报告
2. T1 假设检查器（§3.1）：列出本次任务的关键假设，对照 OPINION.md
3. 矛盾检测：当前任务与已有需求/功能/接口/OPINION 是否冲突
```

**仅当 `project-type` 包含 `ios` 或 `macos`**：

```
4. 确认本次实现遵循 §11.1 HIG 规范
```

**仅当 `project-type` 包含 `web-frontend` 或 `fullstack`**：

```
4. UI 构建任务激活 frontend-design Skill
```

#### C. 任务实施中（所有项目）

```
1. 里程碑边界变更检测（§6.6）：用户修改 plan 时立即触发，不静默接受
2. T2 矛盾检测器（§3.2）：每次接收用户输入后扫描冲突
3. 外部知识获取时：影响决策的信息 → 立即记录到 .agent-doc/knowledge.md
```

#### D. 任务完成后、commit 前（所有项目）

```
1. 更新 .agent-doc/progress.md
2. 执行 §6.4 commit 前检查清单
3. T1 收尾扫描：本次任务中是否新增"待沉淀假设" → 是否升级到 OPINION
```

**仅当 `issues-tracker: cli`**：

```
4. 更新对应里程碑 Issue 子任务状态（复选框更新序列）：
   BODY=$(<cli> issue view <number> --json body -q .body)
   NEW_BODY=$(echo "$BODY" | sed 's/- \[ \] <任务描述>/- [x] <任务描述>/')
   <cli> issue edit <number> --body "$NEW_BODY"

5. 添加 comment：<cli> issue comment <number> --body "✅ 完成：<说明>\ncommit: <hash>"

6. 新缺陷立即创建 Issue：<cli> issue create --title "<标题>" --label "缺陷"
```

**仅当 `issues-tracker: mcp`**：

```
4. mcp__<server>__update_issue({number, body: <更新后的 body>})
5. mcp__<server>__create_comment({issue: <number>, body: "✅ 完成..."})
6. mcp__<server>__create_issue({title, labels: ["缺陷"], body})
```

**仅当 `issues-tracker: manual` 或 `none`**：

```
4. 仅更新 .agent-doc/progress.md，无外部同步
```

#### E. milestone-done 时（所有项目）

```
→ 完整执行 §9.2 仪式序列
→ §9.2 完成后，主动提示：
  「里程碑已完成。如需生成下一 Session 启动提示词，告诉我即可。」
```

**仅当 `project-type` 包含 `ios/macos` AND `tf-auto: enabled`**：

```
→ §9.2 步骤 5：判断本里程碑是否含新功能
  是（内部 TF beta）→ [WAIT:safe] 提议 Build Number 递增 → 执行 fastlane beta
  否 → 跳过 TF 提交
```

---

## 5. 初始化一次性问卷

> **规则**：所有问题必须一次性发出，禁止分多轮逐条问。可推断的字段（§4.1）默认填好并标 `🔍 已推断`。

### 5.1 问卷模板（输出给用户填写）

```yaml
# ==================== 项目基础（必填） ====================
项目名称: 
项目目标一句话: 
项目类型: [ios | macos | web-frontend | fullstack | backend | data | docs | workflow]
核心链路（输入→处理→输出）: 
交付形式与验收标准: 
参考项目或样例（可选）: 

# ==================== VCS 与协作（多数可推断）====================
vcs: 🔍 [推断结果]   # github | gitlab | gongfeng | bitbucket | local
vcs-url: 🔍 [推断结果]

issues-tracker: ?    # cli | mcp | manual | none（默认 manual）
  # 仅 cli 时填：
  issues-cli: ?      # gh | glab | <custom>
  # 仅 mcp 时填：
  issues-mcp: ?      # 已配置的 MCP server 名称

# ==================== Agent 协作偏好 ====================
agent-cli: 🔍 [推断结果]  # claude-code | codex | cursor | gemini | other
agent-mode: ?            # interactive | autonomous | mixed（默认 mixed）
opinion-strict-mode: ?   # smart | strict | loose（默认 smart）

# ==================== 技术栈与运行（多数可推断）====================
stack: 🔍 [推断结果]
runtime: 🔍 [推断结果]   # container | local | cloud
启动命令: 
测试命令: 
环境变量管理: # .env | 密钥系统 | 配置中心
本地访问域名与端口: 
分支策略: 
commit 规范（语言/emoji/格式）: 
commit scope 列表（如 auth/feed/ui）: 
外部依赖（Kafka/COS/第三方 API）: 

# ==================== 仅 project-type 含 ios/macos 时 ====================
目标平台: # iOS | iPadOS | macOS | 跨平台 SwiftUI
最低支持系统版本: 
App Store Connect 账号已配置: # 是 | 否
tf-auto: # enabled | disabled
证书管理: # 手动 | fastlane Match | Xcode Cloud
Bundle ID 和 Team ID: 

# ==================== 仅 project-type=docs 时 ====================
文档类型: 
输出格式: # md | docx | pdf | html
风格排版要求: 
引用规范: # APA | GB/T 7714 | 无

# ==================== 仅 project-type=data 时 ====================
数据来源与格式: 
关键指标: 
输出形式: # 图表 | 报告 | Dashboard
脱敏要求: 

# ==================== OPINION L3 问答（详见 §2.5） ====================
Q1. 审美参考与负面清单: 
Q2. 技术选型偏好与厌恶: 
Q3. 速度 vs 质量取舍: 
Q4. 确定性 vs 灵活性偏好: 
Q5. 沟通风格偏好: 
Q6. 项目特定信仰（可选）: 

# ==================== 工具与钩子 ====================
需引入的 Skill / MCP / Plugin: 
额外初始化钩子命令: 
```

### 5.2 输出格式约定

用户填写后，Agent 输出 5 份草案（不写文件）：

```
草案 1：AGENTS.md
草案 2：OPINION.md
草案 3：AGENT.RULES.md
草案 4：CLAUDE.md / AGENT.md / GEMINI.md（按 agent-cli 选择）
草案 5：.gitignore 补丁 + 初始化钩子执行清单
```

用户可以逐份说"OK"或提修改意见，全部确认后一次性写入。

---

## 6. 开发循环与提交

### 6.1 强制循环

```
plan → task(doc → work → verify → doc) → commit → next task → milestone-done
```

### 6.2 任务文档字段

| 字段 | 说明 |
|---|---|
| **Intent** | 要解决什么问题，为什么要做 |
| **Constraints** | 约束条件（技术、业务、时间、安全） |
| **Assumptions** | 本任务依赖的关键假设（T1 留下的标注汇总） |
| **Decision** | 方案选择与取舍理由，含被否决方案及否决原因 |
| **Evidence** | 验证证据（测试结果、日志、截图、数据） |
| **Impact** | 影响范围与回滚方案 |
| **Learnings** | 本次发现的可复用经验（供 relearning） |

### 6.3 清洁现场原则

- 任务开始前：`git status` 必须干净
- 任务结束后：`git status` 必须干净，有 commit 和 `.agent-doc` 记录
- commit message 说 What，`.agent-doc` 说 Why，OPINION 说 Why we believe this

### 6.4 commit 前检查清单

- [ ] 测试通过（正向 / 反向 / 回归）
- [ ] 服务日志无新增严重错误
- [ ] 无临时文件、调试脚本、日志目录被提交
- [ ] 无 `.env`、密钥文件、IDE 个人配置被提交
- [ ] `.agent-doc/progress.md` 已更新
- [ ] T1 假设检查：本次新增假设是否需要升级到 OPINION？
- [ ] T2 冲突检查：本次是否存在未解决冲突需要记录？
- [ ] 是否产生可记忆的开发习惯 → 记录到 `.agent-doc/chat-summary.md`
- [ ] iOS 项目：本次是否有新功能（影响 milestone-done 是否触发 TF）

### 6.5 矛盾检测（§3.2 T2 在以下阶段强制触发）

- **plan 审阅时**：检查需求之间冲突、约束互斥、优先级矛盾
- **task 实施中**：与已有功能/已有需求产生冲突时，停止实施并报告
- **verify 阶段**：本次变更是否引入与现有系统行为的不一致

**报告格式见 §3.2 冲突报告格式。**

### 6.6 里程碑边界变更检测

用户在 Session 中途修改 plan，且与当前里程碑边界产生冲突时：

```
1. Agent 立即暂停，输出：
   ⚠️ 里程碑边界变更
   原边界：[M{n} 原始范围]
   变更内容：[用户新增/删除/修改的部分]
   影响：[对当前进度/后续里程碑的影响]
   建议：在 M{n} 和 M{n+1} 之间插入 M{n}.1 承载此次变更
2. 等待用户确认
3. 确认后：在 .agent-doc/plan.md 插入 M{n}.1，更新 Issue（按 issues-tracker），继续
```

### 6.7 commit 格式

`emoji type(scope): 描述`

| type | emoji | 用途 | type | emoji | 用途 |
|---|---|---|---|---|---|
| feat | ✨ | 新功能 | test | ✅ | 测试 |
| fix | 🐛 | 修复 | chore | 🔧 | 杂项 |
| refactor | ♻️ | 重构 | perf | ⚡ | 性能 |
| style | 🎨 | 样式/格式 | build | 📦 | 构建 |
| docs | 📝 | 文档 | ci | 👷 | CI |
| release | 🚀 | 版本发布 | opinion | 🧭 | OPINION 演化 |

### 6.8 错误恢复协议

**编译/构建失败**：

```
1. 自动诊断错误信息
2. 最多重试 2 次（每次记录诊断日志）
3. 第 3 次仍失败 →
   [WAIT:interactive / mixed]  停止报告，等待人工介入
   [WAIT:autonomous]           创建「阻塞」Issue（按 issues-tracker） + 日志，停止
4. 任何情况下：构建失败不得提交代码
```

**测试失败**：

```
1. 识别失败类型：
   a. 断言失败 → 修复代码，重跑
   b. 环境依赖失败 → 先排查环境，记录到 chat-summary.md
   c. 已知 Flaky → 重跑最多 2 次

2. 修复后仍失败 →
   [WAIT:interactive / mixed]  停止报告
   [WAIT:autonomous]           创建「缺陷」Issue，停止，不提交

3. 禁止：跳过失败测试、注释测试代码、降低断言通过
```

**环境/工具失败（非阻塞）**：

```
gh/glab/MCP/fastlane/entire 等失败 → 降级为本地替代，记录提示，不阻塞代码开发
```

---

## 7. 目录结构

### 7.1 `docs/`（项目文档，入库，人类可读）

```
docs/
├── prd.md              # [代码] 产品需求文档
├── architecture.md     # [代码] 架构说明（文字 + mermaid）
├── decisions.md        # [通用] 重大决策记录（ADR 风格，每条附 Why）
├── tests.md            # [代码] 测试策略与关键用例说明
├── CHANGELOG.md        # [代码] 版本更新日志（Keep a Changelog 格式）
├── outline.md          # [文档/设计] 大纲与结构
├── analysis.md         # [数据] 分析方案与结论
├── data-dict.md        # [数据] 数据字典与字段说明
└── refs/               # [通用] 参考资料与外部文档快照
    └── README.md       # 每个文件的来源、用途、在线地址
```

### 7.2 `.agent-doc/`（过程文档，入库）

**最小集**（所有项目）= `plan.md` + `progress.md` + `chat-summary.md`。

```
.agent-doc/
├── plan.md              # 里程碑拆分与优先级
├── progress.md          # 进度跟踪
├── chat-summary.md      # 关键变更：新增三个固定区块
│                        #   - 「待沉淀假设」（T1 留下的）
│                        #   - 「未解决冲突」（T2 留下的）
│                        #   - 「OPINION 演化候选」
├── knowledge.md         # 外部知识
├── relearning-log.md    # relearning 执行记录
├── opinion-log.md       # OPINION.md 演化历史（新增）
│
├── bugs/                # [代码] bug-{id}-{slug}.md
├── feats/               # [代码] feat-{id}-{slug}.md
│
└── drafts/              # [文档/设计] 版本草稿（禁止覆盖）
    └── v{n}-{date}.ext
```

---

## 8. 初始化钩子（Init Hooks）

每个钩子执行前须用户确认。

### 8.1 通用钩子

```bash
# 1. Git 初始化（如尚未初始化）
git init
git add AGENTS.md OPINION.md AGENT.RULES.md CLAUDE.md docs/ .agent-doc/
# 按 agent-cli 选择追加：
#   claude-code → 已加 CLAUDE.md
#   cursor → 加 AGENT.md
#   gemini → 加 GEMINI.md
git commit -m "📝 docs: 初始化项目治理文件（v4 模板）"

# 2. entire CLI 安装（按用户确认）
curl -fsSL https://entire.io/install.sh | bash
entire enable --agent <当前 CLI>
```

### 8.2 代码项目钩子

```bash
# 前端 / 全栈：安装 frontend-design Skill
npx skills add anthropics/claude-code --skill frontend-design

# 容器化：生成 docker-compose.yml + docker-compose.override.yml

# Python：确认 loguru/pydantic-settings/uv 在依赖中

# iOS：执行 §8.3
```

### 8.3 iOS 项目钩子

```bash
if ! command -v fastlane &> /dev/null; then
  echo "⚠️  fastlane 未安装。执行：sudo gem install fastlane"
fi
fastlane init  # 已安装的情况下
# 配置 Appfile（app_identifier、apple_id、team_id）+ Fastfile（lane :beta / :release）
```

### 8.4 Issues 系统初始化钩子（按 `issues-tracker` 分支）

**`issues-tracker: cli`**：

```bash
# 检测 CLI 是否可用 + 已认证
<cli> auth status

# 初始化标签
for label in "里程碑" "缺陷" "功能增强" "TF反馈" "阻塞" "待决策"; do
  <cli> label create "$label" --force 2>/dev/null || true
done

# 将 .agent-doc/plan.md 转换为 Issues（每个里程碑一个 Issue）
issues-sync   # 见 §10
```

**`issues-tracker: mcp`**：

```
通过 MCP Server 调用：
  mcp__<server>__list_labels  → 检查标签是否存在
  mcp__<server>__create_label → 缺失的创建
  mcp__<server>__create_issue → 按 plan.md 创建里程碑 Issue
```

**`issues-tracker: manual` 或 `none`**：

```
跳过 Issues 初始化。
plan.md 和 progress.md 是唯一进度源。
```

### 8.5 `.gitignore` 补全

```gitignore
__pycache__/
.env
*.pyc
node_modules/
.agent-doc/drafts/*.tmp
.agent-doc/evidence/
AGENT.template.md
AGENT.template.md
.DS_Store
*.xcuserstate
DerivedData/
build/
*.ipa
*.dSYM.zip
fastlane/report.xml
fastlane/Preview.html
fastlane/screenshots/
fastlane/test_output/
```

### 8.6 多 Agent 寻路 stub（按 agent-cli 选择性生成）

#### CLAUDE.md（Claude Code 入口 stub）

```markdown
# [项目名] — Project Context

> Full project rules are in AGENTS.md.
> Project opinions (aesthetics, values, preferences) are in OPINION.md.
> Read both before starting any task.

Key files:
- `AGENTS.md` — execution rules and runtime checkpoints
- `OPINION.md` — L1/L2/L3 opinions (must align all actions against this)
- `AGENT.RULES.md` — complete governance spec
- `docs/` — project documentation (prd, architecture, changelog)
- `.agent-doc/progress.md` — current milestone status
- `.agent-doc/chat-summary.md` — pending assumptions / conflicts / opinion evolutions
```

#### AGENT.md（Cursor 入口 stub）

```markdown
# [项目名] — Cursor Entry

> Cursor 用户从此进入。完整规范在 AGENTS.md。
> 项目信仰与审美原则在 OPINION.md。
> 开始任务前必读：AGENTS.md + OPINION.md + .agent-doc/progress.md。
```

#### GEMINI.md（Gemini CLI 入口 stub）

```markdown
# [项目名] — Gemini CLI Entry

> See AGENTS.md for execution rules and OPINION.md for project opinions.
> Required reads: AGENTS.md, OPINION.md, .agent-doc/progress.md
```

**维护原则**：stub 只做路由，不写内容。内容变更只更新 AGENTS.md / OPINION.md。

---

## 9. Session 里程碑协议

> 一个 Chat / Session 只执行一个里程碑。上下文过长会导致 Agent 注意力分散、错误率上升。

### 9.1 Session 开始仪式

```
1. 读取 AGENTS.md / OPINION.md / .agent-doc/progress.md / docs/prd.md（如有）
2. 扫描 .agent-doc/chat-summary.md 三个区块（待沉淀假设 / 未解决冲突 / OPINION 演化候选）
3. 声明本 Session 目标：
   📍 本 Session 目标：[里程碑名称]
   预计产物：[列表]
   预计耗时：[估算]
   依赖前置：[上一里程碑完成情况确认]
   遗留事项：[chat-summary 三区块非空时列出]
4. 若发现前置里程碑未完成，停止并告知用户
```

### 9.2 `milestone-done` 仪式

```
步骤  动作                                        说明
────────────────────────────────────────────────────────────────────
1     [测试]   运行完整测试套件
2     [文档]   更新 docs/CHANGELOG.md（Unreleased 区块）
               更新 .agent-doc/progress.md
3     [Issues] 按 issues-tracker 关闭对应 Issue（§10）
4     [自省]   扫描 chat-summary.md 三个区块，提示是否：
                 a. 升级"待沉淀假设" → OPINION.md
                 b. 处理"未解决冲突" → 更新规则 / 标记例外
                 c. 触发 opinion-update 演化候选
5     [提交]   git add → git commit → git push
               entire 自动创建 checkpoint（如启用）
6     [iOS]    含新功能 → 提议 Build Number 递增 → fastlane beta
7     [提示]   「里程碑已完成。如需生成下一 Session 启动提示词，告诉我即可。」
```

### 9.3 下一 Session 启动提示词模板

用户触发后生成：

```markdown
继续 [项目名] 开发。
当前状态：[里程碑X] 已完成——[一句话成果描述]。
本 Session 目标：[里程碑X+1] - [描述]。
关键约束：[从 AGENT.RULES.md 提取 1-3 条]。
关键信仰：[从 OPINION.md L3 提取与本 Session 最相关的 1-2 条]。
遗留事项：[chat-summary 三区块未处理项，如有]。

读取 AGENTS.md、OPINION.md、.agent-doc/progress.md，宣告 Session 目标后开始。
```

---

## 10. 通用 VCS / Issues 同步层

> 屏蔽 GitHub/GitLab/工蜂 等差异，统一接口。

### 10.1 `issues-sync` 命令

```
执行 issues-sync 时，Agent 按 issues-tracker 分支：

[cli]
  1. <cli> issue list --state open → 查询现有 Issues
  2. 读取 .agent-doc/plan.md → 比对里程碑
  3. 缺失的里程碑 → <cli> issue create --title "[M{n}] xxx" --label "里程碑"
  4. 标签初始化（如尚未存在）
  5. 回显结果

[mcp]
  1. mcp__<server>__list_issues({state: "open"})
  2. 比对 plan.md
  3. 缺失 → mcp__<server>__create_issue({title, labels, body})

[manual]
  1. 输出"请手动同步 plan.md 到你的 Issues 系统"
  2. 列出未同步的里程碑

[none]
  1. 不执行任何外部同步
  2. 输出确认 .agent-doc/progress.md 状态
```

### 10.2 标准标签（推荐中文）

| 标签 | 含义 |
|---|---|
| `里程碑` | 里程碑 Issue |
| `缺陷` | Bug / 缺陷 |
| `功能增强` | 新功能请求或优化 |
| `TF反馈` | TestFlight 用户反馈（iOS 项目） |
| `阻塞` | 等待外部依赖，Agent 无法推进 |
| `待决策` | 等待人工拍板，Agent 可并行推进其他 |

项目可在初始化时追加标签（如 `性能` / `安全` / `文档`），记录到 `AGENT.RULES.md`。

### 10.3 复选框更新（CLI 模式下 body 更新序列）

```bash
# cli 无法原子更新 body，必须三步：
BODY=$(<cli> issue view <number> --json body -q .body)
NEW_BODY=$(echo "$BODY" | sed 's/- \[ \] <任务描述>/- [x] <任务描述>/')
<cli> issue edit <number> --body "$NEW_BODY"
```

MCP 模式下通常有原子更新接口，直接调用。

---

## 11. iOS / macOS 项目专属流程

适用条件：`project-type` 含 `ios` 或 `macos`。

### 11.1 设计规范（SwiftUI 直接实现，遵循 HIG）

| 领域 | 规范 | 禁止 |
|---|---|---|
| 磨砂/模糊 | `Material`（`.ultraThinMaterial` 等） | 自定义模糊效果 |
| 图标 | SF Symbols | 第三方图标库 |
| 字体 | 系统字体 + Dynamic Type | 硬编码字号 |
| 深色模式 | Semantic colors（`.primary` / `.secondary` 等） | 硬编码颜色值 |
| 动效 | 系统动画曲线（`.easeInOut` / `.spring`） | 突兀自定义动效 |
| 触觉反馈 | `UIImpactFeedbackGenerator` 等 | 忽略触觉反馈 |
| 布局 | 相对值优先，支持多屏 | 固定 frame |
| 适配 | 必须支持 Dark Mode | 仅测试 Light Mode |

### 11.2 版本管理

| 字段 | 管理策略 |
|---|---|
| `CFBundleShortVersionString` | Agent 提议，用户确认 |
| `CFBundleVersion` | 每次 TF 提交自动递增 |
| Git Tag | `v{Marketing Version}` |
| `docs/CHANGELOG.md` | Keep a Changelog 格式 |

Marketing Version 三段式递增规则：

```
Major（x.0.0）：不兼容变更或重大重设计
Minor（0.x.0）：新功能，向后兼容
Patch（0.0.x）：Bug 修复，无新功能
```

### 11.3 TestFlight 提交策略

| 里程碑类型 | 触发条件 | 操作 |
|---|---|---|
| 功能里程碑（含新功能） | milestone-done 时 | 递增 Build → `fastlane beta` |
| 纯修复里程碑 | milestone-done 时 | [WAIT] 询问用户；autonomous 跳过 |
| Release 里程碑 | 用户手动 | [WAIT:unsafe] 见 §11.4 |

### 11.4 Release 发布流程

所有步骤 `[WAIT:unsafe]`（所有模式必须等待）。

```
1. [版本号]   Agent 分析 CHANGELOG Unreleased → 提议 Marketing Version → [WAIT] 确认
2. [记录]     [Unreleased] → [v{version}] + 发布日期
3. [构建]     fastlane release（archive + export IPA/DMG）
4. [Tag]      git tag v{version} && git push --tags
5. [Release]  按 vcs 选择：
              - github: gh release create
              - gitlab: glab release create
              - gongfeng: mcp__gongfeng__create_release（如配置）
              - 其他: 输出指引让用户手动操作
6. [TF 内测]  fastlane pilot upload → [WAIT] 确认
7. [App Store] 用户在 App Store Connect 手动操作
8. [关闭 Issues] 按 issues-tracker 批量关闭本 Release 的里程碑 Issue
```

### 11.5 TestFlight 反馈处理流程

触发：`tf-feedback [反馈描述或截图]`

```
[复现]  Agent 根据描述复现 → 写入 .agent-doc/bugs/tf-{n}-{slug}.md
         → 按 issues-tracker 创建 Issue（标签：缺陷,TF反馈）
[评估]  分析根因 + 修复方案 → 用户确认
[修复]  实施修复 + 单测 / UI 测试
[验收]  复现步骤通过 + 无回归
[发布]  Patch +1 → CHANGELOG → commit → Build 递增 → fastlane beta → 关闭 Issue
```

### 11.6 UI 测试与截图（适用条件：含 UI 交互的 iOS/macOS）

```bash
xcodebuild test \
  -scheme YourApp \
  -destination 'platform=iOS Simulator,name=iPhone 16 Pro' \
  -resultBundlePath .agent-doc/evidence/TestResults-$(date +%Y%m%d-%H%M%S).xcresult

xcrun xcresulttool export \
  --path .agent-doc/evidence/TestResults-latest.xcresult \
  --output-path .agent-doc/evidence/screenshots/ \
  --type directory
```

截图不入 git（`.gitignore` 中加 `.agent-doc/evidence/`）。

---

## 12. 设计制作专属流程（非 iOS/macOS）

### 12.1 分流策略

| 项目类型 | 设计工具 |
|---|---|
| Web 前端 | frontend-design Skill（S01），`/frontend-design` 触发 |
| 需要设计稿 / 原型 | Claude Design（S02），handoff bundle 流转 |
| 图像资产 | GPT Image / Gemini 等（按 OPENAI/GEMINI API key） |

### 12.2 frontend-design 激活规则

- 前端/全栈项目默认安装
- 触发：`/frontend-design [描述]` 或 Agent 识别 UI 任务
- **核心信仰**（写入 OPINION.md L2-design）：拒绝 Inter + 紫色渐变 + 千篇一律组件。每个界面必须有明确设计方向（极简 / 编辑风 / 工业风 / 奢华感等）

---

## 13. 默认规则（用户未指定时生效，按 Profile 写入 AGENT.RULES.md）

### 13.1 Docker Compose（runtime: container）

- 容器间通信走内部网络，用服务名作 hostname
- 宿主机端口最小化，仅入口服务暴露
- 调试端口放 `docker-compose.override.yml`，禁主 `docker-compose.yml`
- 直连数据库调试用 `docker compose exec`

### 13.2 测试（代码项目）

- 必须正向 / 反向 / 回归
- E2E 默认宿主机 Playwright MCP，禁 IDE 内置浏览器
- 必须检查服务日志
- 禁止跳过失败测试提交
- 容器项目：在 docker compose 中执行 python/npm 等，禁宿主机执行

### 13.3 Python 项目（stack 含 python）

| 领域 | 默认 |
|---|---|
| 日志 | loguru（禁标准 logging） |
| 配置 | pydantic-settings |
| 依赖 | pyproject.toml + uv |
| 格式 | ruff |

### 13.4 前端项目

- 安装 frontend-design Skill
- 第三方依赖优先 CDN
- 禁 `alert()`
- 禁付费 API/组件（除非授权）
- 默认图表库 ECharts

### 13.5 多视角检查（与 OPINION L2 `[review]` 联动）

| 节点 | 视角 | 维度 |
|---|---|---|
| 功能完成 | 用户 | 信息可见、可理解、设计一致、操作简洁、美观 |
| Bug 修复 | 测试 | 影响面、同类问题 |
| 文档完成 | 读者 | 能否仅凭文档理解全貌、术语解释 |

---

## 14. relearning 与 opinion-update

### 14.1 relearning 命令（与 v3 一致，演化方向）

将项目经验回写到 `AGENT.template.md`：

```
收集素材 → 提炼规则 → 生成变更建议 → 用户确认 → 写入模板 → 记录日志
```

**v4 新增收集源**：
- `.agent-doc/opinion-log.md`（OPINION 演化历史）
- `.agent-doc/chat-summary.md` 三个区块的统计

**重点检查**：
- 附录 R 工具注册表是否需要更新
- L1 通用原则是否被项目反复违反 → 提示重新审视 L1
- L2 是否需要新增过程标签

### 14.2 opinion-update 命令（v4 新增）

触发：用户察觉规则需要演化时。

```
1. Agent 输出当前 OPINION.md L3 摘要
2. 询问哪一层、哪一条需要演化
3. 用户回答后，提议 diff
4. 用户确认 → 写入 OPINION.md
5. 追加记录到 .agent-doc/opinion-log.md（含变更前/后、原因）
```

### 14.3 两个时机

| 时机 | 动作 | 存放 |
|---|---|---|
| commit 后 | 检查可复用经验 | `.agent-doc/chat-summary.md` |
| milestone-done 后 | 检查 OPINION 演化候选 | `OPINION.md` + `.agent-doc/opinion-log.md` |
| 项目完结后 | `relearning` | `AGENT.template.md` |

---

## 15. 模板治理

- `AGENT.template.md` 是母版，**不承载项目细节**，加入 `.gitignore`，不随项目入库
- 初始化时生成的文件：`AGENTS.md` + `OPINION.md` + `AGENT.RULES.md` + 路由 stub
- 后续迭代优先更新 `AGENT.RULES.md` 与 `OPINION.md`，再同步精简到 `AGENTS.md`
- **不反向覆盖模板**——仅通过 `relearning` 显式更新

**初始化完成验收**：

1. `AGENTS.md` 包含与 Profile 匹配的运行时检查点（§4.5）
2. `OPINION.md` 三层结构完整（L1 原样、L2 按类型推断、L3 用户回答）
3. `AGENT.RULES.md` 覆盖完整治理需求
4. 路由 stub（CLAUDE.md / AGENT.md / GEMINI.md）按 agent-cli 生成且仅作路由
5. `docs/` 和 `.agent-doc/` 最小集齐全
6. `.agent-doc/chat-summary.md` 包含三个固定区块（即使空）
7. `[issues-tracker 非 none]` 标签初始化完成 / `issues-sync` 已执行
8. `[project-type 含 ios/macos]` fastlane 已配置或已标记待配置
9. `[entire: enabled]` entire CLI 已安装并 enable
10. 用户知道所有入口命令（§0）

---

## 附录 R：工具注册表

> `relearning` 重点维护对象。Agent 初始化时按项目类型与 CLI 环境筛选。

### R.1 Skill（Agent CLI 能力增强）

| ID | 名称 | 安装命令 | 适用场景 | 默认/按需 |
|---|---|---|---|---|
| S01 | [frontend-design](https://github.com/anthropics/claude-code/tree/main/plugins/frontend-design) | `npx skills add anthropics/claude-code --skill frontend-design` | Web 前端 / 全栈 | **默认**（前端项目） |
| S02 | [Claude Design](https://claude.ai/design) | 无需安装（Pro/Max/Team/Enterprise） | 设计稿 / 原型 | 按需 |
| S03 | GPT Image / Gemini Image | 配置对应 API KEY | AI 图像资产 | 按需 |

### R.2 Plugin（CLI 增强）

| ID | 名称 | 安装命令 | 适用 CLI | 默认/按需 |
|---|---|---|---|---|
| P01 | [everything-claude-code](https://github.com/affaan-m/everything-claude-code) | `/plugin marketplace add affaan-m/everything-claude-code` | Claude Code | 按需 |

### R.3 MCP Server（外部服务集成）

| ID | 名称 | 安装 / 配置 | 用途 | 默认/按需 |
|---|---|---|---|---|
| M01 | playwright | `npx @playwright/mcp@latest` | E2E 测试 | **默认**（有 UI 的代码项目） |
| M02 | [GitHub MCP](https://github.com/github/github-mcp-server) | 需 GitHub PAT | Issues / Release（github） | 按需 |
| M03 | gongfeng MCP | 见公司内部配置 | Issues / MR（工蜂） | 按需（企业内部项目） |
| M04 | gitlab MCP | 见 GitLab MCP 仓库 | Issues / MR（gitlab） | 按需 |

### R.4 CLI 工具

| ID | 名称 | 安装命令 | 用途 | 默认/按需 |
|---|---|---|---|---|
| C01 | [entire CLI](https://entire.io) | `curl -fsSL https://entire.io/install.sh \| bash` | 会话上下文捕获 | **默认**（询问后） |
| C02 | [fastlane](https://fastlane.tools) | `sudo gem install fastlane` | iOS/macOS 发布 | **默认**（iOS/macOS） |
| C03 | gh | `brew install gh` | GitHub CLI | 默认（vcs=github） |
| C04 | glab | `brew install glab` | GitLab CLI | 默认（vcs=gitlab） |

### R.5 语言/框架默认值

| 领域 | 默认 |
|---|---|
| Python 日志 | loguru |
| Python 配置 | pydantic-settings |
| Python 格式化 | ruff |
| Python 依赖 | pyproject.toml + uv |
| 前端资源加载 | CDN 优先 |
| 前端图表 | ECharts |
| iOS 磨砂 | SwiftUI Material |
| iOS 图标 | SF Symbols |
| iOS 字体 | 系统字体 + Dynamic Type |
| iOS 证书（团队） | fastlane Match |

### R.6 注册表维护规则

- 每条：**ID** + **来源链接** + **安装命令** + **适用范围** + **默认/按需**标记
- `relearning` 必须检查：新工具是否应加入 / 已有是否过时
- ID 格式：`S##`(Skill) / `P##`(Plugin) / `M##`(MCP) / `C##`(CLI)，递增不复用

---

## 附录 T：文档模板

### T.1 `chat-summary.md`（v4 三个固定区块）

```markdown
# Chat Summary

> 对话中产生的可复用经验。每次 commit 前检查是否需要更新。

## 待沉淀假设（T1 留下）
<!-- 例：本次默认了"图表用 ECharts"，未在 OPINION 中明确，下次 milestone-done 时考虑升级 -->

## 未解决冲突（T2 留下）
<!-- 例：用户要求用 Tailwind，但 OPINION L3 写"避免 utility-first CSS"——本次按用户要求执行，待澄清 -->

## OPINION 演化候选
<!-- 例：项目进展到中段后，"速度优先"开始让位于"打磨质量"，建议 L3 Q3 演化 -->

## 开发习惯
<!-- 例：loguru serialize=True 在生产环境拖慢写入，应仅调试时开启 -->

## 规则修正
<!-- 例：AGENTS.md 应补充 docker compose 启动前检查 .env 是否存在 -->

## 工具经验
<!-- 例：Playwright MCP 在 WSL2 下需额外安装 chromium 依赖 -->

## 计划偏差
<!-- 例：plan.md 预估 2h 的前端对接实际花 6h，CORS 配置未提前考虑 -->
```

### T.2 `knowledge.md`

```markdown
# Project Knowledge Base

> 通过 MCP/搜索/工具获取的、对项目决策有影响的外部知识。

### K{序号}: {标题}
- **来源**：{工具名/URL/MCP}
- **获取时间**：{YYYY-MM-DD}
- **知识摘要**：{2~5 句}
- **项目影响**：{对哪个决策的影响}
- **时效性**：{长期有效 / 需定期验证 / 一次性}
```

### T.3 `progress.md`

```markdown
# Progress

## 里程碑总览

| # | 名称 | 状态 | 完成时间 | Issue |
|---|---|---|---|---|
| M1 | 项目初始化 | ✅ Done | 2026-06-30 | #1 |
| M2 | 核心功能 A | 🔄 In Progress | - | #2 |

## 当前里程碑：M2

- [x] 任务 1
- [ ] 任务 2（进行中）
- [ ] 任务 3

## 阻塞与待决策

- [ ] 阻塞：等待 X 团队提供 API 文档 — 影响 M3
- [ ] 待决策：是否引入 GraphQL — 等待用户拍板

## 遗留问题

- [ ] {描述} — 预计在 M{n} 处理
```

### T.4 `docs/CHANGELOG.md`

```markdown
# Changelog

All notable changes to this project will be documented in this file.
Format: [Keep a Changelog](https://keepachangelog.com) | Versioning: Major.Minor.Patch

## [Unreleased]

### Added
- {新功能}

### Fixed
- {修复}

### Changed
- {变更}

---

## [1.0.0] - 2026-06-30

### Added
- 初始版本发布
```

### T.5 `relearning-log.md`

```markdown
# Relearning Log

| 日期 | 来源项目 | 变更摘要 | 模板版本 |
|---|---|---|---|
| 2026-06-30 | 示例项目 | v4 模板上线：OPINION 体系 + T1/T2 触发器 + VCS 抽象 | v3.0 → v4.0 |
```

### T.6 `opinion-log.md`（v4 新增）

```markdown
# OPINION Evolution Log

| 日期 | 层级 | 变更摘要 | 原因 | 触发来源 |
|---|---|---|---|---|
| 2026-06-30 | L3-Q3 | "速度优先" → "速度与质量平衡（每 milestone 先 demo 再打磨）" | 项目进展到 M5 后用户多次表达打磨意愿 | chat-summary 「OPINION 演化候选」 |
```

### T.7 fastlane Fastfile 模板（iOS）

```ruby
default_platform(:ios)

platform :ios do
  desc "提交 TestFlight 内测版本"
  lane :beta do
    increment_build_number
    build_app(scheme: "YourApp")
    upload_to_testflight(
      changelog: last_git_commit[:message],
      skip_waiting_for_build_processing: true
    )
  end

  desc "正式 Release 发布"
  lane :release do
    build_app(scheme: "YourApp", export_method: "app-store")
    sh("cp ../build/YourApp.ipa ../release/")
    upload_to_app_store(
      skip_metadata: false,
      skip_screenshots: true,
      submit_for_review: false
    )
  end
end
```

### T.8 下一 Session 提示词

```markdown
继续 [项目名] 开发。
当前状态：M{n}「{名称}」已完成——{一句话成果}。
本 Session 目标：M{n+1}「{名称}」- {描述}。
关键约束：[1-3 条 from AGENT.RULES.md]
关键信仰：[1-2 条 from OPINION.md L3]
遗留事项：[chat-summary 三区块未处理项，如有]

读取 AGENTS.md、OPINION.md、.agent-doc/progress.md，宣告 Session 目标后开始。
```

---

## 附录 O：OPINION.md 文件模板

> 初始化时生成的 OPINION.md 完整结构示例。L1 区块原样写入，L2 按项目类型筛选，L3 由问答转化。

```markdown
# OPINION.md

> 本文件是项目的"信仰、审美与价值取向"。
> 优先级：L3（产品）> L2（过程）> L1（通用）。
> 每次 Session 开始 Agent 必读，每次行动前对照（详见 AGENTS.md §3 T1/T2 触发器）。
>
> 版本：v1.0 | 生成时间：{date} | 上次更新：{date}

---

## L1 通用原则（模板自带，禁项目级删改，仅 relearning 可更新）

### L1-A 认知校准与透明度
1. 当回答依赖未经用户确认的假设时，标注出来，说明"我这样想是因为……"
2. 区分擅长与不擅长的领域：擅长的直接输出；不擅长的（价值判断、审美偏好、领域经验、实时业务决策）明确告知需要用户参与
3. 引用要给真实出处：学术给论文/作者，行业数据给报告，技术方案给官方文档
4. 当内容可能受训练数据分布影响而有倾向时（如技术选型、方法论），提示用户并列出替代视角
5. 当用户指出错误时，直接说明错在哪里、原因、修正后的结论，不过度道歉

### L1-B 能力提升与审美引导
1. 涉及专业领域时，用 3-5 句概述该领域的标准流程和关键环节，帮助用户建立完整认知
2. 给出方案或作品建议时，补充说明行业内"什么被认为是好的"以及评判标准来源

---

## L2 过程性原则（按 project-type 推断，可项目级修改）

### [plan] 计划阶段
- 拆解任务时，先暴露 3 个可选路径及取舍维度，再选择
- 估算时长 / 资源时，给区间而非点估计，并标注不确定来源

### [code] 编码阶段（代码项目）
- 优先复用既有抽象，新增抽象前确认现有结构无法承载
- 失败优先 fail fast，不静默吞错误

### [design] 设计阶段（文档/设计项目）
- 视觉决策必须有参考来源，不允许"凭感觉做"
- 输出版本号化的 draft，禁止覆盖式修改

### [review] 验证阶段
- 三视角检查：用户视角 / 测试视角 / 读者视角
- 拒绝"看起来能跑"的修复，必须找到根因

### [commit] 提交阶段
- commit message 写"为什么改"而非"改了什么"
- 单 commit 单一意图，禁止混合多个变更

### [communicate] 沟通阶段
- 不重复用户提供的信息
- 暴露假设清单和被否决方案（按 L3-Q5 沟通风格调整详略）

---

## L3 产品性原则（初始化问答转化，常变更）

### L3-1 审美与参考
- **正面参考**：{用户 Q1 回答转化}
  - 例：Linear、Stripe（克制的克莱因蓝 + 高对比度）
- **负面清单**：{用户 Q1 回答转化}
  - 例：拒绝 Inter + 紫色渐变、拒绝 SaaS 模板感

### L3-2 技术偏好与禁忌
- **倾向**：{用户 Q2 回答转化}
  - 例：Python 后端 + Vue 前端 + PostgreSQL
- **避免**：{用户 Q2 回答转化}
  - 例：避免 Java 生态、避免 NoSQL（除非有明确理由）
- **强制约束**：{公司/团队层面的强制项}
  - 例：必须使用 ECharts，必须走公司 SSO

### L3-3 速度 vs 质量取舍
- {用户 Q3 回答转化}
  - 例：每个 milestone 内部先做可演示版本（粗糙但跑通），再打磨。打磨目标 80 分。

### L3-4 决策协作方式
- **必须停下来等用户的决策**：{用户 Q4 回答转化}
  - 例：删除文件、改架构、引入新依赖、设计风格选择
- **可以用默认值推进事后告知**：{用户 Q4 回答转化}
  - 例：变量命名、内部抽象、测试用例覆盖度

### L3-5 沟通风格
- **回复长度**：{Q5 → 要点式 / 详细 / 极简}
- **假设清单**：{Q5 → 每次列出 / 仅在重大决策时 / 不需要}
- **被否决方案**：{Q5 → 必须列 / 简要提及 / 不需要}
- **语言**：{Q5 → 中文 / 英文 / 中英混合}

### L3-6 项目特定信仰（可选）
- {用户 Q6 回答}
  - 例：本项目优先服务老用户，新功能不能破坏现有用户的工作流；任何 UI 变更必须可一键回滚到上一版本。
```

---

## 附录 D：v3 → v4 迁移指南

适用：已用 v3 初始化的项目升级到 v4。

```
1. 在项目根目录运行：请按 AGENT.template.md 升级
2. Agent 扫描现有 AGENTS.md / AGENT.RULES.md / .agent-doc/，对比 v4 产物清单
3. 必做：
   a. 创建 OPINION.md（L1 原样写入；L2 按 project-type 推断；L3 问 5-6 个 L3 问题）
   b. AGENTS.md 头部 Project Profile 增加 issues-tracker、opinion-strict-mode 字段
   c. AGENTS.md 检查点（§4.5）按新版重写（添加 T1/T2 触发器引用）
   d. .agent-doc/chat-summary.md 补齐三个固定区块（即使空）
   e. 路由 stub 改为新版 stub 格式（指向 AGENTS.md + OPINION.md）
4. 可选：
   a. 创建 .agent-doc/opinion-log.md
   b. 把现有 GitHub 硬编码命令替换为 issues-tracker 抽象
5. 记录到 .agent-doc/relearning-log.md：v3 → v4 升级
```

---

## 结语

v4 的核心思想：

> 让 AI 与人的分歧暴露在前，而不是浪费在后。

L1 让 AI 守住通用底线，L2 让过程有章法，L3 让项目有个性。
T1 让行动前先问，T2 让收到输入后先看。
VCS 抽象让模板不再只为 GitHub 而生。
一次性问卷让初始化不再车轱辘话。

— 模板编写人 / 维护人在 `relearning` 中持续迭代
