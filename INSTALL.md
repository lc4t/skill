# Agent 一句话初始化入口

当用户说“用 `https://skill.sakanano.moe/` 初始化当前项目”或同义请求时，按本文件执行。

## 目标

安装完整 `agents-init` Plugin，并用其中的 `agents-init` 创建项目契约。初始化完成后，由同包 `project-runtime` 管理持续项目工作；Opinion provider 保持独立。

## 前提

- 需要联网下载公开 Plugin，并能在本地运行 Python 3；
- 需要写入当前项目；
- 安装到 Codex 或 Cursor 的用户级目录时，按宿主权限机制取得授权；
- 禁止读取或上传项目 `.env`、个人 Opinion 规则、凭据及私有目录内容。

## 执行

1. 读取 `https://skill.sakanano.moe/plugin.json` 的 `repository` 字段，将该完整仓库下载或克隆到新建的安全临时目录。只下载 `skills/agents-init/` 子目录不受支持。
2. 根据当前宿主选择 `--client codex` 或 `--client cursor`。
3. 从项目现有文件确认名称、项目类型、VCS、技术栈、runtime 与 Agent 客户端。无法确认且会改变生成契约时，一次性询问用户。
4. 在 Plugin 根目录运行统一编排器，默认只预演：

```bash
python3 scripts/bootstrap_and_init.py \
  --client codex \
  --project /absolute/path/to/project \
  --name example \
  --project-type code \
  --vcs github \
  --stack python \
  --runtime local \
  --agent-cli codex
```

5. 向用户展示 Plugin 安装位置、拟创建文件和碰撞项。得到确认后原样追加 `--apply`。
6. `--apply` 成功后检查输出中的 `doctor.ok=true`；报告已安装 Plugin、已创建文件和仍需填写的 `TODO`。

## 安全语义

- 默认 dry-run；没有 `--apply` 时禁止写入用户目录和项目。
- 初始化碰撞会在安装前阻断；禁止自动覆盖项目文件。
- 已安装 Plugin 内容不同会阻断；升级须单独使用 runtime 的 `bootstrap --replace` 并保留恢复副本。
- 下载、安装和项目写入可能分别触发宿主授权。这不改变用户只需提出一句自然语言请求的交互目标。
