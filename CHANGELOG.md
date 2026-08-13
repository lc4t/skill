# 更新记录

## 2026-08-13

### Fixed

- 初始化 apply 改为全有或全无：任一冲突时零写入，写入中途失败只回滚本次已知文件。
- 使用 descriptor-bound 路径遍历拒绝父目录 symlink，避免骨架写出项目根目录。
- Project Profile 可声明 `native_mcp_sources`，供 project-runtime 纳管历史或 client-local MCP。

### Changed

- 发布 `agents-init v5`，将职责收口为项目骨架初始化与版本迁移。
- 运行期 Task/Case、进度、验证、Git 与 Skill/MCP 管理统一交给外部 `project-runtime`。
- Opinion 保持独立指导/审查能力，公开模板不再内置个人或通用 Opinion 内容。
- Project Profile 使用 `.agents/moe.sakanano.project-runtime/project.json`，便携能力采用 Agent Plugins 1.0 目录。

### Added

- 新增默认 dry-run、冲突不覆盖的 `scripts/init_project.py` 及单元测试。
- 新增空的项目 Opinion 覆盖入口、Agent Plugin/MCP 占位及最小过程文档。

## 2026-07-02

### Changed

- 将 `agents-init` 元数据对齐到 `AGENT.template.md v4.0`，skill 版本更新为 `4.0.0`。
- 按模板内容补充 v4 核心变更、命令入口、治理层级、T1/T2 运行时检查器和初始化产物清单。
- 将 `agents-init` 的 `SKILL.md` 精简为执行入口，完整治理规则保留在独立 `AGENT.template.md`。
- 升级 `skill.json` 元数据，补充 `schema_version`、`entrypoints`、`files` 和 `commands` 字段。
- 明确 `assets/` 非必需目录，仅在存在图片、脚本、示例数据等资源时创建。
- 移除 workflow 中的分支级 `CNAME` 写入，避免误导为单仓库可按分支自动切换自定义域名。
- 调整发布模型为仅 `main` 分支发布到 `skill.sakanano.moe`，`test` 分支仅用于本地预览。

### Added

- 新增 GitHub Pages 自动发布 workflow：`.github/workflows/pages.yml`。
- 初始化云端 Skills 静态站点结构。
- 新增顶层浏览器首页 `index.html`。
- 新增顶层机器索引 `index.json`。
- 新增示例 skill：`agents-init`。
- 新增 `agents-init` 的 AI 执行入口、浏览器页面、结构化元数据和独立 `AGENT.template.md` 模板资源。
- 新增 `.nojekyll`，避免 GitHub Pages 对以下划线开头的路径或文件执行 Jekyll 处理。
