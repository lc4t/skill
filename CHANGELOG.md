# 更新记录

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
