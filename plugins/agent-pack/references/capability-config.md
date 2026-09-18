# Agent 能力配置

仅在盘点、迁移、同步或验证 Agent Plugin、Skill、MCP 时读取本参考。

## 可移植项目结构

`agents-init v5` 创建以下能力包：

```text
.agents/
├── plugin.json
├── skills/
├── mcp.json
└── moe.sakanano.agent-pack/
    └── project.json
```

- `plugin.json` 与 `mcp.json` 面向 Agent Plugins 1.0.0。
- `skills/` 的直接子目录包含 `SKILL.md`。
- `project.json` 是客户端扩展，也是机器可读的 Project Profile。
- 个人偏好和凭据禁止进入可移植公开模板。

## CLI

从已加载 Skill 解析插件根目录，再运行：

```bash
python3 <plugin-root>/runtime/agent_pack_config.py --output json inventory --source project:/path/to/project
python3 <plugin-root>/runtime/agent_pack_config.py --output json inventory --source client:codex
python3 <plugin-root>/runtime/agent_pack_config.py --output json inventory --source client:cursor
python3 <plugin-root>/runtime/agent_pack_config.py --output json inventory --source client:claude
python3 <plugin-root>/runtime/agent_pack_config.py --output json doctor --project /path/to/project
```

runtime 尚未安装时，bootstrap 包含本 Skill 的插件：

```bash
python3 /path/to/agent-pack/runtime/agent_pack_config.py --output json bootstrap \
  --plugin /path/to/agent-pack --client codex
python3 /path/to/agent-pack/runtime/agent_pack_config.py --output json bootstrap \
  --plugin /path/to/agent-pack --client codex --apply
```

`--client` 可取 `codex`、`cursor`、`claude`。Claude Code 没有 Agent Plugins 加载器，`bootstrap --client claude` 把插件投影成它实际读取的三处：

- `~/.claude/skills/<skill>` → 源插件 `skills/<skill>` 的符号链接；
- `~/.claude/agent-pack/plugins/<name>` → 源插件根目录的符号链接（安装记录，`inventory --source client:claude` 从这里读已安装版本）；
- 插件 `mcp.json` 中每个 server 写入 `~/.claude.json#mcpServers`（user scope）：`${PLUGIN_ROOT}` 展开为安装记录路径，`streamable-http` 映射为 `http`，丢弃 Claude 不支持的 `cwd`；其他 `${VAR}` 原样保留，由 Claude 启动时从进程环境展开。写入保留文件原权限。

Claude 端是**活链接**，不固定副本：源目录改动立即生效，版本即源 `plugin.json#version`。已存在但内容不同的链接或 MCP 条目需要 `--replace`，旧内容进入 `~/.agent-pack/recovery/<stamp>-claude-<name>/`（`replaced-skills/`、`replaced-plugins/`、`replaced-mcp.json`）。装完需重启 Claude Code 才会加载新 Skill / MCP。`sync` / `reconcile` 的项目包仍只支持 Codex 与 Cursor。

在来源与已初始化项目之间迁移选中的组件：

```bash
# 预演
python3 <plugin-root>/runtime/agent_pack_config.py --output json transfer \
  --from client:codex --to-project /path/to/project --skill example-skill

# 审阅预演结果后再应用
python3 <plugin-root>/runtime/agent_pack_config.py --output json transfer \
  --from project:/path/to/source --to-project /path/to/destination \
  --skill example-skill --mcp example-server --apply
```

为客户端构建并安装项目的可移植能力：

```bash
# 预演
python3 <plugin-root>/runtime/agent_pack_config.py --output json sync \
  --project /path/to/project --client cursor

# 获得授权后应用
python3 <plugin-root>/runtime/agent_pack_config.py --output json sync \
  --project /path/to/project --client cursor --apply
```

迁移时使用 `reconcile` 分类目标，并归档明确选择的旧组件。默认只生成只读计划：

```bash
python3 <plugin-root>/runtime/agent_pack_config.py --output json reconcile \
  --project /path/to/project --client cursor \
  --retire-skill work-engine --retire-skill ai-config-sync

python3 <plugin-root>/runtime/agent_pack_config.py --output json reconcile \
  --project /path/to/project --client cursor \
  --retire-skill work-engine --retire-skill ai-config-sync --apply
```

只退役旧组件、不安装或替换项目包时加 `--retire-only`（至少需要一个 `--retire-skill` / `--retire-plugin`）：

```bash
python3 <plugin-root>/runtime/agent_pack_config.py --output json reconcile \
  --project /path/to/project --client cursor --retire-plugin project-runtime --retire-only --apply
```

结果把组件分为 `exact`、`conflict`、`missing`、`native_only` 与 `blocked`。替换包和明确退役的组件移动到 `~/.agent-pack/recovery/`；事务失败时自动恢复。

Codex 同步会写入 `~/.agents/plugins/plugins/<name>` 可移植包、`.codex-plugin` adapter 与 `~/.agents/plugins/marketplace.json` 的 `personal` 条目。之后需在 Codex 桌面版的插件设置里启用 / 重新同步 `<name>@personal`（并确认 `~/.codex/config.toml` 有 `[plugins."<name>@personal"] enabled = true`）来激活；同步只更新 marketplace 源，Codex 自身缓存 `~/.codex/plugins/cache/personal/` 要到下次激活或重启才追平。homebrew 版 `codex-cli` 无 `codex plugin` 子命令，`plugin` / `marketplace` 命令与 UI 随 Codex 版本变化，以当前 Codex 文档为准。Cursor 同步会在本地插件根目录安装真实的 Agent Plugin 目录。

## MCP Tool

随附的 stdio server 暴露以下 Tool：

- `agent_pack_inventory`
- `agent_pack_doctor`
- `agent_pack_transfer`
- `agent_pack_sync`
- `agent_pack_bootstrap`
- `agent_pack_reconcile`

所有会修改状态的 MCP Tool 默认使用 `apply=false`。必须先展示并审阅操作计划，才能使用 `apply=true` 重试。

## 安全与碰撞规则

- 禁止把原生客户端 MCP 配置中的凭据复制进可移植包。
- 拒绝包含疑似密钥环境变量、header 或 token 字面值的 MCP 条目。
- 迁移期间禁止跟随指向来源 Skill 目录之外的 symlink。
- 禁止静默覆盖现有 Skill、MCP 名称、Agent Plugin、客户端包或 marketplace 条目。
- 在 `native_mcp_sources` 中声明历史或客户端专属 MCP 文件。可移植条目成为打包候选；包含密钥的条目保持为 `blocked`/doctor warning，并留在客户端本地。
- 原生 MCP 来源可以使用 `__PROJECT_DIR__` 与 `__REPO_ROOT__`；源文件保留占位符，生成客户端包时解析为当前本地项目路径。
- 把 `credential_env_file` 设置为项目相对路径的 dotenv 文件，权限必须为 `0600`。生成包只保存 `${VAR}` 引用；本地 launcher 在 MCP 启动时读取值，禁止复制进 Git 或插件 manifest。
- 使用 `mcp_client_policy.<server>.include` 或 `.exclude` 完成客户端路由。禁止在 MCP 定义中放入 adapter 专属 `_skip` 字段。
- `${PLUGIN_ROOT}` 用于不可变包文件，`${PLUGIN_DATA}` 用于客户端管理的可写状态。
- 客户端原生 adapter 只在安装阶段使用；Agent Plugins 1.0 文件保持权威源地位。
