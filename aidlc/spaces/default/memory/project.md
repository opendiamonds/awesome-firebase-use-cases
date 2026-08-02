# Project-Level Rules

> Project-specific specialisation and corrections. Loaded after `org.md` and
> `team.md` as strict-additive guidance; contradictions with broader policy
> are rejected. Populated by practices-discovery and the self-learning loop.
>
> Cloud-360 note: 本層為本專案自有規則（見 ADR-0011），以繁體中文撰寫。
> 識別字、路徑、指令維持原文。

## Way of Working

<!-- Project-specific specialisation. Example: -->
<!-- This monorepo requires package-scoped branch names and a package owner -->
<!-- review in addition to the team's normal merge policy. -->

## Walking Skeleton

<!-- Project-specific specialisation. Example: -->
<!-- The walking skeleton must exercise the legacy service adapter as well -->
<!-- as the new service boundary. -->

## Testing Posture

**Property-based testing 為 hard constraint**（ADR-0006）。下列核心模組的測試必須包含 property-based 測試，不得只有 example-based：IaC generator、cost calculator、agent routing。其餘模組沿用 `org.md` 的預設門檻。

## Deployment

**Construction 與 Operations 是連續的，不是依序的兩個 phase**（ADR-0008）：

1. **build ↔ deploy 之間沒有 phase gate。** 從 PR → 合併進 `ut` → 部署到自有 staging（ADR-0007）是單一連續管線。「寫 code / build / test」與「部署 / 運行」屬於同一條流程，不是先後兩段。
2. **Operations 是持續的迴圈。** 內涵為「deploy + 觀測 + 應變」的持續循環，與 Construction 交織並行。任何 code 變更都同時是一次潛在的維運事件。
3. **不得以「Construction 尚未完成」為由延後 Operations 工作，反之亦然。**
4. **保留的邊界。** 本規則只改「Construction↔Operations 的關係模型」，不改**範圍邊界**（見 `## Scope Overrides`）。Operations 中尚未落地的維運學科（observability、incident playbooks、SLO/on-call）仍是真實待辦。

對 AI agent 的實務指示：規劃時把部署、回滾、觀測、告警視為與 code 實作同一條 pipeline 的環節；描述專案狀態時不要用「已進入 Construction / Operations 階段」這類線性 phase 語言，直接陳述具備哪些能力。

## Code Style

<!-- Project-specific specialisation. -->

## Tech Stack

- **Backend**：Python / FastAPI（`backend/`）
- **Frontend**：TypeScript / React / Vite（`frontend/`）
- **資料庫**：PostgreSQL；schema 以 repo 根目錄的 `schema.sql` 與 `schema_rbac.sql` 為可攜來源
- **Specs / 圖**：Markdown、Mermaid、draw.io
- **CI/CD**：GitHub Actions（`.github/workflows/ci.yml` 跑 repo contract、lint、build、Docker build；`deploy.yml` 在 `ut` 觸發部署）
- **Staging**：自有主機 `192.168.10.10`，經 Cloudflare Tunnel 對外為 `cloud360.danniel.cc`（ADR-0007）
- **測案管理**：自架 Kiwi TCMS（`tcms.danniel.cc`，於 `dc-infra` repo 維運）
- **雲端範圍**：AWS / GCP / Azure 三雲的架構與維運設計

## Decided

- DECIDED: 專案定位為 AI-native multi-cloud architecture & operations platform，方法論基礎為 Spec-Driven Development（SRS、user stories、architecture、ADRs）。(ADR-0001)
- DECIDED: `extensions/security/baseline/` 預設啟用，為 hard constraint（IAM、encryption、network exposure、audit logging）。requirements analysis 階段不需再詢問。(ADR-0006)
- DECIDED: `extensions/testing/property-based/` 預設啟用，為 hard constraint。requirements analysis 階段不需再詢問。(ADR-0006)
- DECIDED: 文件語言為繁體中文，取代 upstream bilingual-docs 與 ADR-0005 的雙語強制。(ADR-0009)
- DECIDED: commit message 與 PR 標題使用中文 type，branch 名稱維持英文 type。(ADR-0010)
- DECIDED: 採用 AI-DLC v2；專案規則層為 `aidlc/spaces/<space>/memory/`。(ADR-0011)
- DECIDED: 所有 AIDLC artifacts（含 v2 之前的歷史文件）都在作用中 intent 的 record 目錄 `<record>/` 下；baseline record 為 `aidlc/spaces/default/intents/260802-default/`。(ADR-0011)
- DECIDED: 專案狀態的細部來源為 `<record>/aidlc-state.md`。

## Scope Overrides

- ✅ **In scope**：SRS、architecture diagrams、user stories、ADRs、IaC generator design、agent routing design、MCP/skill management spec、validation scripts、baseline CI、自有 staging 的部署與維運。
- ❌ **Out of scope（除非經新 ADR 核可）**：雲端供應商 production 環境、production credentials、environment-specific secrets、direct production IaC、destructive cloud operations、native iOS/Android app。

## Forbidden

- NEVER 新增 path parts 含 `prod`、`production`、`secrets` 的檔案 — `scripts/validate_repo_contract.py` 會擋（CI 紅燈）。
- NEVER commit 私鑰或 AWS / Azure / GCP 的 credential 字串。實際被擋的樣式列在 `scripts/validate_repo_contract.py` 的 `FORBIDDEN_CONTENT_PATTERNS`（涵蓋私鑰 PEM 標頭與三雲的 secret 環境變數）。**不要把那些樣式照字面複製到任何 contract 檔案裡** — 掃描器不分辨「示範」與「洩漏」，會直接紅燈。
- NEVER 在未取得 human approval 的情況下執行 production write、IaC apply 或 IAM 變更。
- NEVER 直接編輯 `.claude/` 下的 upstream 框架檔來表達專案規則 — 專案規則一律寫在 `aidlc/spaces/<space>/memory/{team,project}.md`，否則下次升級會被整批覆蓋。

## Mandated

- ALWAYS 在 commit 前執行 `python3 scripts/validate_repo_contract.py`。違反 repo contract = CI 紅燈。contract 涵蓋 repo 層必要文件（`REQUIRED_FILES`／`REQUIRED_TEXT`）、record 層 baseline artifacts（`REQUIRED_RECORD_FILES`／`REQUIRED_RECORD_TEXT`，執行時動態解析 record 目錄）、文件語言（record 內不得有 `## English Version`）、禁止路徑與禁止內容。
- ALWAYS 在變更**資料庫結構或部署必知的 schema／seed 行為**時同步更新部署資產（blocking，未完成不得標示相關 Construction／部署階段為完成）：
  - 觸發條件：新增／刪除／更名表；新增／刪除／更名／改型欄位；索引／唯一約束／外鍵變更；seed／預設資料語意變更（如 `role_permissions` 矩陣、預設帳號）；ORM／啟動補丁引入新 DDL（`models.py`、`database.py` 的 `_ensure_*_schema`）。
  - **不觸發**：僅資料內容／應用層 JSON 形狀變更（如 `scores_json`／`findings_json`）且無 DDL。
  - 必做 1 — `schema_rbac.sql`（repo 根目錄）：把對應 DDL 與必要 COMMENT 寫進適當區塊；使用 `IF NOT EXISTS` 等可重跑安全寫法；新增表／物件時更新檔頭涵蓋清單與驗證註解；僅改 seed 時標註重跑會覆寫的風險。
  - 必做 2 — `DEPLOY.md`（repo 根目錄）：更新「這支 SQL 會建立的表／欄位」表；新表與重要欄位補說明與建議的 `psql` 驗證指令；若影響既有環境升級，寫明「重跑 `schema_rbac.sql`」或與後端 `_ensure_*_schema` 的關係。
  - 建議一併更新（非 blocking）：`schema.sql`、`<record>/construction/plans/schema-rbac-notes.md`。
- ALWAYS 在任何 high-risk action（production write、IaC apply、IAM 變更）前先給 plan + impact + rollback，並通過 human approval gate。
- ALWAYS 讓引擎把 AIDLC 階段事件寫進 `<record>/audit/` 的 per-clone shard（不要手動編輯 shard）；架構級決策開 ADR 於 `<record>/inception/decisions/NNNN-*.md`。

## Corrections

<!-- Project-specific corrections from human feedback. -->
<!-- Format: NEVER/ALWAYS [behavior] (learned [date]) -->
