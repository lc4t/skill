# Agent 能力配置

仅在盘点、迁移、同步或验证 Agent Plugin、Skill、MCP 时读取本参考。

## 可移植项目结构

`agents-init v5` 创建以下能力包：

```text
.agents/
├── plugin.json
├── skills/
├── mcp.json
└── moe.sakanano.project-runtime/
    └── project.json
```

- `plugin.json` 与 `mcp.json` 面向 Agent Plugins 1.0.0。
- `skills/` 的直接子目录包含 `SKILL.md`。
- `project.json` 是客户端扩展，也是机器可读的 Project Profile。
- 个人偏好和凭据禁止进入可移植公开模板。

## CLI

从已加载 Skill 解析插件根目录，再运行：

```bash
python3 <plugin-root>/runtime/project_runtime_config.py --output json inventory --source project:/path/to/project
python3 <plugin-root>/runtime/project_runtime_config.py --output json inventory --source client:codex
python3 <plugin-root>/runtime/project_runtime_config.py --output json inventory --source client:cursor
python3 <plugin-root>/runtime/project_runtime_config.py --output json doctor --project /path/to/project
```

runtime 尚未安装时，bootstrap 包含本 Skill 的插件：

```bash
python3 /path/to/project-runtime/runtime/project_runtime_config.py --output json bootstrap \
  --plugin /path/to/project-runtime --client codex
python3 /path/to/project-runtime/runtime/project_runtime_config.py --output json bootstrap \
  --plugin /path/to/project-runtime --client codex --apply
```

在来源与已初始化项目之间迁移选中的组件：

```bash
# 预演
python3 <plugin-root>/runtime/project_runtime_config.py --output json transfer \
  --from client:codex --to-project /path/to/project --skill example-skill

# 审阅预演结果后再应用
python3 <plugin-root>/runtime/project_runtime_config.py --output json transfer \
  --from project:/path/to/source --to-project /path/to/destination \
  --skill example-skill --mcp example-server --apply
```

为客户端构建并安装项目的可移植能力：

```bash
# 预演
python3 <plugin-root>/runtime/project_runtime_config.py --output json sync \
  --project /path/to/project --client cursor

# 获得授权后应用
python3 <plugin-root>/runtime/project_runtime_config.py --output json sync \
  --project /path/to/project --client cursor --apply
```

迁移时使用 `reconcile` 分类目标，并归档明确选择的旧组件。默认只生成只读计划：

```bash
python3 <plugin-root>/runtime/project_runtime_config.py --output json reconcile \
  --project /path/to/project --client cursor \
  --retire-skill work-engine --retire-skill ai-config-sync

python3 <plugin-root>/runtime/project_runtime_config.py --output json reconcile \
  --project /path/to/project --client cursor \
  --retire-skill work-engine --retire-skill ai-config-sync --apply
```

结果把组件分为 `exact`、`conflict`、`missing`、`native_only` 与 `blocked`。替换包和明确退役的组件移动到 `~/.project-runtime/recovery/`；事务失败时自动恢复。

Codex 同步会写入个人 marketplace 包与 adapter 文件，之后需显式运行 `codex plugin add <name>@personal` 激活。Cursor 同步会在本地插件根目录安装真实的 Agent Plugin 目录。

## MCP Tool

随附的 stdio server 暴露以下 Tool：

- `project_runtime_inventory`
- `project_runtime_doctor`
- `project_runtime_transfer`
- `project_runtime_sync`
- `project_runtime_bootstrap`
- `project_runtime_reconcile`

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
