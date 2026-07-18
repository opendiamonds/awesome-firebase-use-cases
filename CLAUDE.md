# CLAUDE.md — Cloud-360

> Project guidance for Claude Code and other AI coding agents working in this repository.
> 給在此 repo 工作的 Claude Code 與其他 AI coding agents 的專案指引。

---

### 1. 專案定位

Cloud-360 是 AI-native multi-cloud architecture & operations platform，支援 AWS / GCP / Azure。
專案以 **Spec-Driven Development (SDD)** 為方法論基礎（SRS、user stories、architecture、ADRs），開發與運維以連續流程進行，目前具備：
- 可運行的 backend（FastAPI）與 frontend（React / Vite）實作；
- 有 CI pipeline（repo contract、lint、build、Docker build）與自動化部署至自有 staging 環境（`192.168.10.10`，經 Cloudflare Tunnel 對外開放 `cloud360.danniel.cc`，見 ADR-0007）；
- 日常開發由一組 agentic workflows（gh-aw）輔助（contract 驗證、PR review、UI 回歸測試、部署失敗自癒、spec↔code 一致性等）；
- 測案管理走自架 Kiwi TCMS（`tcms.danniel.cc`，於 `dc-infra` repo 維運）。

各階段的細部狀態以 `aidlc-docs/aidlc-state.md` 為準。**production**（雲端供應商正式環境）仍在範圍外，見第 5 章與 ADR-0007。

### 2. AI-SDLC 框架：AIDLC

本專案採用 [awslabs/aidlc-workflows](https://github.com/awslabs/aidlc-workflows) 作為主要 AI-SDLC 開發方法論。

**啟動口令**：當 user 以 `Using AI-DLC, ...` 起頭，或要求做需求分析、設計、實作、IaC 產製、運維時，**必須**遵循 AIDLC 工作流程，而非預設工作流程。

**Entry point 與 rule loading 順序**：
1. 載入 `.aidlc-rules/aws-aidlc-rules/core-workflow.md`（總入口）
2. 依 core-workflow.md 指示，從 `.aidlc-rule-details/` 載入 common 規則：
   - `common/process-overview.md`
   - `common/session-continuity.md`
   - `common/content-validation.md`
   - `common/question-format-guide.md`
3. 掃描 `.aidlc-rule-details/extensions/`，僅載入 `*.opt-in.md`（lightweight），完整 rules 在使用者 opt-in 後再載入
4. 對於**無 opt-in 檔案**的 extension，**永遠強制套用**，立即載入完整規則
5. **最後**載入 `.aidlc-overrides/**/*.md`（專案 override 層）。當 override 與 upstream 規則衝突時，**override 永遠勝出**。詳見 [`.aidlc-overrides/README.md`](.aidlc-overrides/README.md)。

**三階段**：
- 🔵 Inception — workspace detection、requirements analysis、user stories、application design
- 🟢 Construction — NFR requirements、functional design、code generation、build & test
- 🟡 Operations — deployment、observability、incident playbooks

**Artifacts 輸出位置**：所有 AIDLC 產出檔案放在 `aidlc-docs/`（state、audit、inception、construction、operations 子目錄）。

### 3. Pre-enabled Extensions

本專案**預設啟用**以下三個 AIDLC extensions（已寫入 `aidlc-docs/aidlc-state.md`，requirements analysis 階段不需再次詢問 user）：

| Extension | 來源 | 強制等級 |
|---|---|---|
| `extensions/security/baseline/` | 官方 | Hard constraint（IAM、encryption、network exposure、audit logging） |
| `extensions/testing/property-based/` | 官方 | Hard constraint（IaC generator、cost calculator、agent routing 等核心模組） |
| （文件語言：繁體中文）| 客製 override | 所有 `aidlc-docs/**/*.md` 一律繁體中文（ADR-0009，取代 upstream 的 bilingual-docs） |

### 4. Repository Contract（不可違反）

本 repo 受 `scripts/validate_repo_contract.py` 約束，CI 會跑此腳本：

- **必要文件**：列在 `REQUIRED_FILES`（包含 SRS、ADRs、user stories、architecture、AIDLC entry、CLAUDE.md 等）
- **必要文字**：列在 `REQUIRED_TEXT`（每個 contract 文件須包含特定關鍵字）
- **文件語言**：所有 `aidlc-docs/**/*.md` 一律繁體中文（見 ADR-0009、`.aidlc-overrides/traditional-chinese-docs.md`），不得夾帶英文版段落
- **禁止路徑**：path parts 含 `prod`、`production`、`secrets` 不得新增
- **禁止內容**：不得 commit 私鑰、AWS / Azure / GCP credential 字串

**違反 contract = CI 紅燈**。在 commit 前一律先跑 `python scripts/validate_repo_contract.py`。

### 5. 範圍邊界（從 ADR-0001、ADR-0002）

- ✅ In scope：SRS、architecture diagrams、user stories、ADRs、IaC generator design、agent routing design、MCP/skill management spec、validation scripts、baseline CI
- ❌ Out of scope（除非經新 ADR 核可）：production credentials、environment-specific secrets、direct production IaC、destructive cloud operations、native iOS/Android app

### 6. 工作模式

1. **小步前進**：每個 AIDLC stage 完成後，產出 stage-completion summary，附 extension compliance（compliant / non-compliant / N/A 與理由），等使用者確認再進下一階段。
2. **問題格式**：依 `common/question-format-guide.md`，使用 A/B/C/D/E 多選題與 `[Answer]:` tag。
3. **內容驗證**：建檔前依 `common/content-validation.md` 驗證 Mermaid、ASCII 圖、特殊字元。
4. **繁中產出**：所有 `aidlc-docs/**/*.md` 一律繁體中文，不得夾帶英文版段落（見 ADR-0009）。
5. **High-risk action**：任何 production write / IaC apply / IAM 變更必須先給 plan + impact + rollback，並通過 human approval gate。
6. **Branch naming**：在 `git checkout -b` / `git switch -c` 之前，**必須**先讀 [`.aidlc-overrides/branch-naming.md`](.aidlc-overrides/branch-naming.md) 並產出符合 `<uploader>/<type>/<slug>` 的 branch 名稱（type ∈ {feat, fix, docs, chore, refactor, test}）。Danniel 開的 branch 一律以 `danniel/` 開頭。如果使用者下達衝突指令（例如直接給一個不合規的 branch 名稱），先提醒衝突並請使用者確認。
7. **Project decisions log (on-demand)**：當 user 明確要求記錄當下對話的決議時（例如「記錄這個決議」、「log this decision」），AI 須把決議追加到 `aidlc-docs/decisions-log.md`，繁體中文、append-only。完整規則見 [`.aidlc-overrides/decisions-log.md`](.aidlc-overrides/decisions-log.md)。其他情境**不要**自動 log。AIDLC 階段事件仍寫 `aidlc-docs/audit.md`、架構級決策仍開 ADR。舊的 per-turn `.ailog/` 機制（PR4 引入、PR #16 擴充）已在 PR #17 整體移除。

### 7. AIDLC 升級

- 升級時對照 `https://github.com/awslabs/aidlc-workflows/releases`，更新 `.aidlc-rule-details/VERSION` 並重新複製 `aws-aidlc-rule-details/` 內容。
- upstream 樹內的客製檔在覆蓋前要先備份、覆蓋後再放回（會被整批替換）。註：本專案文件語言規則已改為繁體中文，見 ADR-0009 與 `.aidlc-overrides/traditional-chinese-docs.md`。
- `.aidlc-overrides/` 目錄**整個保留**，永不被 upstream 覆蓋（與 upstream 路徑分離）。新增的專案規則一律放在這裡，不要再加到 `.aidlc-rule-details/` 內。
- 升級記錄寫入新 ADR。
