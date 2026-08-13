# Agents Init Plugin

这是一个公开、可移植的 Agent Plugin，包含两个职责独立的中文 Skill：

- `agents-init`：创建或显式迁移项目骨架与 Project Profile；
- `project-runtime`：初始化完成后，统一管理 Task、Case、Agent Plugin、Skill、MCP、验证、进度与受控 Git 交接。

Opinion 保持独立，只负责指导和审查交付物。仓库不包含任何用户的 `global.yml`、凭据、私有路径或私有项目内容。

## 安装单元

**仓库根目录是唯一安装权威。** Agent Plugins 1.0 manifest 为 [`plugin.json`](plugin.json)，MCP 清单为 [`mcp.json`](mcp.json)。只下载 `skills/agents-init/` 会缺少必需的 `project-runtime`，初始化器会以 `runtime-required` 停止并保持目标项目零写入。

### Codex

克隆或下载完整仓库后，先预演，再应用：

```bash
python3 runtime/project_runtime_config.py bootstrap --plugin . --client codex
python3 runtime/project_runtime_config.py bootstrap --plugin . --client codex --apply
```

### Cursor

```bash
python3 runtime/project_runtime_config.py bootstrap --plugin . --client cursor
python3 runtime/project_runtime_config.py bootstrap --plugin . --client cursor --apply
```

其他支持 Agent Plugins 1.0 的客户端直接安装仓库根目录。

## 初始化项目

安装完整 Plugin 后，从 `skills/agents-init/` 运行初始化器。命令默认 dry-run：

```bash
python3 skills/agents-init/scripts/init_project.py \
  --project /path/to/project --name example \
  --project-type code --vcs github --stack python \
  --runtime local --agent-cli codex
```

审阅后追加 `--apply`。初始化器从 [`AGENT.template.md`](skills/agents-init/AGENT.template.md) 的具名中文区块生成 Markdown，并在任何写入前验证同包 runtime。

## 目录结构

```text
/
├── plugin.json                    # Agent Plugins 1.0 权威 manifest
├── mcp.json                       # 可移植 MCP 清单
├── .codex-plugin/plugin.json      # Codex adapter
├── .mcp.json                      # Codex MCP adapter
├── skills/
│   ├── agents-init/
│   └── project-runtime/
├── runtime/                       # project-runtime CLI 与 MCP server
├── scripts/export_project_runtime.py
└── tests/
```

## 维护与发布

- `tools/project-runtime` 等可信源码根通过 `scripts/export_project_runtime.py` 白名单导出；默认只检查，`--apply` 才写入。
- Skill 主体与用户可读描述使用中文；协议字段、命令和专有名词保留原名。
- `index.json` 是站点机器索引，`index.html` 是浏览器入口。
- 版本、结构或入口变化记录到 [`CHANGELOG.md`](CHANGELOG.md)。
- push 前必须完成单元测试、Plugin 校验、端到端初始化和公开敏感信息审计。
