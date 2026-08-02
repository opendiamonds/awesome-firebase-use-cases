# AI-DLC Workflow

本專案採用 AI-DLC v2（upstream [`awslabs/aidlc-workflows`](https://github.com/awslabs/aidlc-workflows)）。

當使用者啟用 AI-DLC 時（`/aidlc`、`Using AI-DLC, ...`，或要求需求分析／設計／實作／IaC 產製／運維）：

1. 讀取並遵循 skill 入口 `.claude/skills/aidlc/SKILL.md`；框架結構見 `.claude/CLAUDE.md`。
2. 規則由 `aidlc/spaces/<active-space>/memory/` 的五層 strict-additive chain 解析（`org → team → project → phase → stage`）：
   - `org.md` — 框架預設與組織層護欄
   - `team.md` — 團隊實踐（branch 命名、commit message、文件語言、決議紀錄）
   - `project.md` — 專案特化（repo contract、範圍邊界、schema/deploy 同步、tech stack）
   - `phases/<phase>.md` — 各階段護欄
3. 較窄的層只能疊加，不得與較寬的層矛盾。新增專案規則一律寫進 `team.md` / `project.md`，不要改 `.claude/` 內的 upstream 檔。

專案指引全文見 `CLAUDE.md`。所有回應與文件產出使用繁體中文；程式碼、變數、API、識別字維持英文。
