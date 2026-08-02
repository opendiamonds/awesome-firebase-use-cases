---
description: 初始化 AIDLC 生命週期
---

請重新載入所有規則與系統規範，初始化 AI-DLC v2 生命週期。

## 規則載入

### 步驟 1：載入 AI-DLC 入口
載入 `.claude/skills/aidlc/SKILL.md`（`/aidlc` 的 skill 入口）；框架結構與工作區慣例見 `.claude/CLAUDE.md`。

### 步驟 2：載入規則層
依序載入 `aidlc/spaces/<active-space>/memory/` 下的五層 strict-additive chain：

- `org.md`（框架預設與組織層護欄）
- `team.md`（團隊實踐：branch 命名、commit message、文件語言、決議紀錄）
- `project.md`（專案特化：repo contract、範圍邊界、schema/deploy 同步、tech stack）
- `phases/<phase>.md`（ideation / inception / construction / operation 各階段護欄）

較窄的層只能疊加，不得與較寬的層矛盾。

### 步驟 3：確認框架健康
執行 `/aidlc --doctor`（或 `bun .claude/tools/aidlc-utility.ts doctor`）確認 hooks、settings、stage graph 完整。

---

## 初始化流程

4. 解析作用中 intent 的 record 目錄，確認 `<record>/aidlc-state.md` 存在；若無 intent，引擎會在首次描述需求時自動 birth。

5. 初始化紀錄由引擎寫入 `<record>/audit/` 的 per-clone shard，不要手動編輯。

6. 分析目前 workspace：
- 是否為 brownfield
- 現有技術架構
- 現有 modules
- frontend/backend/workflows structure

7. 從現在開始：
- 所有回應必須使用繁體中文
- 所有規劃必須遵守 AI-DLC
- 所有 code generation 前必須先產生 plan
- 所有 architecture 必須可轉換為 draw.io XML
