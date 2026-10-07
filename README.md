# Agents Init Plugin

这是一个公开、可移植的 Agent 分发包，包含四个职责独立的 Plugin，Skill 主体均为中文：

- `agents-init`（仓库根目录）：创建或显式迁移项目骨架与 Project Profile；
- `project-orchestrator`（`plugins/project-orchestrator/`）：初始化完成后管理 Task、Case、能力路由、验证、进度与受控 Git 交接；
- `agent-pack`（`plugins/agent-pack/`）：在项目与 Codex / Cursor / Claude Code 之间盘点、校验、安装、同步、迁移与对账 Plugin、Skill、MCP。
- `opinion-manager`（`plugins/opinion-manager/`）：管理模板系列、平行变体与精确版本，生成完整 `OPINION.md` 和锁定快照，提供个人 Profile 派生与升级审阅。提供经逐文件批准的规则、平行偏好变体和场景模板。

Opinion 配置、升级和验收步骤见 [版本契约与操作说明](plugins/opinion-manager/references/versioning.md)。可以先导入自己的已确认规则；公开模板内容须单独审批。查看目录和升级默认只读，写入须使用完整预览的确认指纹。

Opinion 保持独立职责，并随完整分发包安装。公开候选目录见 `plugins/opinion-manager/catalog/README.md`；仓库不包含个人 Opinion、用户粘贴的规则、凭据、私有路径或私有项目内容。任何公开模板都要经过内容审查和用户明确同意。

## 安装单元

**仓库根目录是唯一下载单元。** 根 manifest 为 [`plugin.json`](plugin.json)；`plugins/` 下三个 Plugin 各有自己的 `plugin.json`。只下载 `skills/agents-init/` 会缺少必需的 `project-orchestrator`、`agent-pack` 与 `opinion-manager`，初始化器会以 `runtime-required` 停止并保持目标项目零写入。

用户可以直接告诉具备联网、本地 Shell 与项目写入能力的 Agent：

> 用 https://skill.sakanano.moe/ 初始化当前项目

Agent 从 [`llms.txt`](llms.txt) 发现 [`INSTALL.md`](INSTALL.md)，再调用 `scripts/bootstrap_and_init.py` 完成预演、安装、初始化与 doctor。涉及联网、用户级安装或项目写入时，宿主仍可能要求一次权限确认。

### 单独安装 Plugin

克隆或下载完整仓库后，用随包的 agent-pack 逐个安装，先预演再应用（`--client` 可取 `codex`、`cursor`、`claude`）：

```bash
python3 plugins/agent-pack/runtime/agent_pack_config.py bootstrap --plugin . --client codex
python3 plugins/agent-pack/runtime/agent_pack_config.py bootstrap --plugin plugins/project-orchestrator --client codex
python3 plugins/agent-pack/runtime/agent_pack_config.py bootstrap --plugin plugins/agent-pack --client codex
python3 plugins/agent-pack/runtime/agent_pack_config.py bootstrap --plugin plugins/opinion-manager --client codex
```

确认计划后分别追加 `--apply`。其他支持 Agent Plugins 1.0 的客户端直接安装这四个目录。

## 初始化项目

安装完成后，先创建目标项目目录，再从完整仓库根目录运行初始化器。命令默认 dry-run：

```bash
mkdir -p /path/to/project
python3 skills/agents-init/scripts/init_project.py \
  --project /path/to/project --name example \
  --project-type code --vcs github --stack python \
  --runtime local --agent-cli codex
```

审阅后追加 `--apply`。初始化器从 [`AGENT.template.md`](skills/agents-init/AGENT.template.md) 的具名中文区块生成 Markdown，并在任何写入前验证同包 `project-orchestrator`、`agent-pack` 与 `opinion-manager`。已有 v5 项目请用 `--mode migrate --recovery-dir <项目外目录>` 升级 Profile。

完整的一条命令流程：

```bash
python3 scripts/bootstrap_and_init.py \
  --client codex --project /path/to/project --name example \
  --project-type code --vcs github --stack python \
  --runtime local --agent-cli codex
```

默认只预演；确认后追加 `--apply`。

## 目录结构

```text
/
├── plugin.json                    # agents-init 的 Agent Plugins 1.0 manifest
├── .codex-plugin/plugin.json      # Codex adapter
├── skills/agents-init/            # 初始化器、模板与 Profile schema
├── plugins/
│   ├── project-orchestrator/      # 生命周期编排 Plugin 与条目式记忆工具
│   ├── agent-pack/                # 扩展能力管理 Plugin、CLI 与 MCP（白名单导出）
│   └── opinion-manager/           # Opinion 配置、组合与审查；版本化规则、平行变体与场景模板
├── scripts/export_plugins.py
├── scripts/bootstrap_and_init.py
├── INSTALL.md
├── llms.txt
└── tests/
```

## 维护与发布

- `agent-pack` 由可信源码根通过 `scripts/export_plugins.py --source <源码父目录>` 白名单导出；`project-orchestrator` 与 `opinion-manager` 在本仓库维护，后者包含管理流程、确定性工具及经过批准的公共规则和模板。
- 公开 Opinion 模板必须经过内容检查、测试和用户逐文件明确同意；个人规则禁止进入公开模板、示例、测试和文档。
- Skill 主体与用户可读描述使用中文；协议字段、命令和专有名词保留原名。
- `index.json` 是站点机器索引，`index.html` 是浏览器入口。
- 版本、结构或入口变化记录到 [`CHANGELOG.md`](CHANGELOG.md)。
- push 前必须完成单元测试、Plugin 校验、端到端初始化和公开敏感信息审计。

## Opinion 首次配置

只提供三个主入口：直接用模板、选择模板的部分条目、从空白开始迭代；另可选择基于已授权记忆提出候选规则。直接使用模板时先预览已批准的场景组合；选部分条目时集中收集选择；从空白开始时不创建空规则版本。规则来源、个人修改与完整正文集中确认一次，由 Agent 处理两份真实指纹，保存、读回与 verify。详见 [首次使用说明](plugins/opinion-manager/references/onboarding.md)。

记忆入口由 Agent 在用户已授权范围内生成私有候选，CLI 不检索记忆。未确认内容不生效。新 Session 应核对实际加载来源；同名旧包保留与升级按客户端机制和用户授权处理。
