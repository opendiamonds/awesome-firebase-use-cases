# CLAUDE.md — Cloud-360

> Project guidance for Claude Code and other AI coding agents working in this repository.
> 給在此 repo 工作的 Claude Code 與其他 AI coding agents 的專案指引。

---

## 中文版

### 1. 專案定位

Cloud-360 是 AI-native multi-cloud architecture & operations platform，支援 AWS / GCP / Azure。
目前 repo 處於 **Spec-Driven Development (SDD) baseline** 階段：以 SRS、user stories、architecture diagram、ADRs 為主，尚未進入大規模 production code generation。

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
4. 對於**無 opt-in 檔案**的 extension（例如 `bilingual-docs/`），**永遠強制套用**，立即載入完整規則
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
| `extensions/bilingual-docs/` | 客製 | Hard constraint（永遠強制，無 opt-in） |

### 4. Repository Contract（不可違反）

本 repo 受 `scripts/validate_repo_contract.py` 約束，CI 會跑此腳本：

- **必要文件**：列在 `REQUIRED_FILES`（包含 SRS、ADRs、user stories、architecture、AIDLC entry、CLAUDE.md 等）
- **必要文字**：列在 `REQUIRED_TEXT`（每個 contract 文件須包含特定關鍵字）
- **雙語強制**：所有 `aidlc-docs/**/*.md` 必須含 `## 中文版` 與 `## English Version`
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
4. **雙語產出**：所有 `aidlc-docs/**/*.md` 一定要同時有 `## 中文版` 與 `## English Version`。
5. **High-risk action**：任何 production write / IaC apply / IAM 變更必須先給 plan + impact + rollback，並通過 human approval gate。
6. **Branch naming**：在 `git checkout -b` / `git switch -c` 之前，**必須**先讀 [`.aidlc-overrides/branch-naming.md`](.aidlc-overrides/branch-naming.md) 並產出符合 `<uploader>/<type>/<slug>` 的 branch 名稱（type ∈ {feat, fix, docs, chore, refactor, test}）。Danniel 開的 branch 一律以 `danniel/` 開頭。如果使用者下達衝突指令（例如直接給一個不合規的 branch 名稱），先提醒衝突並請使用者確認。
7. **AI activity logging**：每一次動到檔案 / commit / push / 開 PR 的 turn，回 user 訊息**之前**必須在 `.ailog/<YYYY-MM-DD>.md`（local timezone）追加一筆 turn entry。完整格式與適用範圍見 [`.aidlc-overrides/ai-logging.md`](.aidlc-overrides/ai-logging.md)。**Substantive turn**（有 working-tree 變動）一律 inline 寫；**pure-ops turn**（只動 GitHub 遠端）預設 **defer** 到下一個 substantive turn 的 PR 一起寫，避免遞迴 PR 噪音；deferred entries 不跨 calendar day。Read-only turn 可省。`.ailog/` append-only。

### 7. AIDLC 升級

- 升級時對照 `https://github.com/awslabs/aidlc-workflows/releases`，更新 `.aidlc-rule-details/VERSION` 並重新複製 `aws-aidlc-rule-details/` 內容。
- 客製檔案（`.aidlc-rule-details/extensions/bilingual-docs/`）在覆蓋前要先備份、覆蓋後再放回（位置在 upstream 樹內，會被整批替換）。
- `.aidlc-overrides/` 目錄**整個保留**，永不被 upstream 覆蓋（與 upstream 路徑分離）。新增的專案規則一律放在這裡，不要再加到 `.aidlc-rule-details/` 內。
- 升級記錄寫入新 ADR。

---

## English Version

### 1. Project Positioning

Cloud-360 is an AI-native multi-cloud architecture & operations platform supporting AWS / GCP / Azure.
The repository is currently at the **Spec-Driven Development (SDD) baseline** stage: SRS, user stories, architecture diagrams, and ADRs are the primary artifacts; large-scale production code generation has not yet started.

### 2. AI-SDLC Framework: AIDLC

This project adopts [awslabs/aidlc-workflows](https://github.com/awslabs/aidlc-workflows) as its primary AI-SDLC methodology.

**Activation phrase**: When the user starts a request with `Using AI-DLC, ...`, or asks for requirements analysis, design, implementation, IaC generation, or operations work, **you MUST** follow the AIDLC workflow rather than the default one.

**Entry point and rule-loading order**:
1. Load `.aidlc-rules/aws-aidlc-rules/core-workflow.md` (top-level entry).
2. Per core-workflow.md, load common rules from `.aidlc-rule-details/`:
   - `common/process-overview.md`
   - `common/session-continuity.md`
   - `common/content-validation.md`
   - `common/question-format-guide.md`
3. Scan `.aidlc-rule-details/extensions/` and load **only** `*.opt-in.md` (lightweight). Full rule files are loaded after the user opts in.
4. Extensions **without** an opt-in file (e.g. `bilingual-docs/`) are **always enforced** — load their full rule files immediately.
5. **Finally**, load `.aidlc-overrides/**/*.md` (the project override layer). When an override conflicts with an upstream rule, **the override always wins**. See [`.aidlc-overrides/README.md`](.aidlc-overrides/README.md).

**Three phases**:
- 🔵 Inception — workspace detection, requirements analysis, user stories, application design
- 🟢 Construction — NFR requirements, functional design, code generation, build & test
- 🟡 Operations — deployment, observability, incident playbooks

**Artifact location**: all AIDLC outputs go to `aidlc-docs/` (with subdirectories for state, audit, inception, construction, operations).

### 3. Pre-enabled Extensions

Three AIDLC extensions are **enabled by default** (recorded in `aidlc-docs/aidlc-state.md`; requirements analysis does not need to re-ask the user):

| Extension | Source | Enforcement |
|---|---|---|
| `extensions/security/baseline/` | Upstream | Hard constraint (IAM, encryption, network exposure, audit logging) |
| `extensions/testing/property-based/` | Upstream | Hard constraint (IaC generator, cost calculator, agent routing, and other core modules) |
| `extensions/bilingual-docs/` | Custom | Hard constraint (always enforced, no opt-in) |

### 4. Repository Contract (do not violate)

This repo is governed by `scripts/validate_repo_contract.py` (executed in CI):

- **Required files**: listed in `REQUIRED_FILES` (SRS, ADRs, user stories, architecture, AIDLC entry, CLAUDE.md, etc.).
- **Required text**: listed in `REQUIRED_TEXT` (each contract file must contain certain keywords).
- **Bilingual enforcement**: every `aidlc-docs/**/*.md` must contain `## 中文版` and `## English Version`.
- **Forbidden paths**: file paths whose parts include `prod`, `production`, or `secrets` are not allowed.
- **Forbidden content**: no private keys or AWS / Azure / GCP credential strings.

**Contract violation = CI red**. Always run `python scripts/validate_repo_contract.py` before committing.

### 5. Scope Boundaries (from ADR-0001 and ADR-0002)

- ✅ In scope: SRS, architecture diagrams, user stories, ADRs, IaC generator design, agent routing design, MCP/skill management spec, validation scripts, baseline CI.
- ❌ Out of scope (unless approved via a new ADR): production credentials, environment-specific secrets, direct production IaC, destructive cloud operations, native iOS/Android apps.

### 6. Working Mode

1. **Step-by-step**: at the end of each AIDLC stage, produce a stage-completion summary including extension compliance (compliant / non-compliant / N/A with rationale) and wait for user confirmation before advancing.
2. **Question format**: follow `common/question-format-guide.md` — use A/B/C/D/E multiple-choice options and the `[Answer]:` tag.
3. **Content validation**: before writing any file, validate Mermaid, ASCII diagrams, and special characters per `common/content-validation.md`.
4. **Bilingual output**: every `aidlc-docs/**/*.md` must include both `## 中文版` and `## English Version`.
5. **High-risk actions**: any production write / IaC apply / IAM change must come with a plan, impact analysis, and rollback strategy, and must pass through the human approval gate.
6. **Branch naming**: before running `git checkout -b` / `git switch -c`, you **must** read [`.aidlc-overrides/branch-naming.md`](.aidlc-overrides/branch-naming.md) and produce a branch name matching `<uploader>/<type>/<slug>` (type ∈ {feat, fix, docs, chore, refactor, test}). All branches Danniel opens start with `danniel/`. If the user issues a conflicting instruction (e.g. dictates a non-compliant branch name), surface the conflict and ask for confirmation before proceeding.
7. **AI activity logging**: in any turn that mutates files / commits / pushes / opens a PR, you **must** append a turn entry to `.ailog/<YYYY-MM-DD>.md` (local timezone) **before** sending the final response to the user. Full format and scope: [`.aidlc-overrides/ai-logging.md`](.aidlc-overrides/ai-logging.md). **Substantive turns** (any working-tree change) log inline. **Pure-ops turns** (GitHub-only mutations) default to **deferring** their entry into the next substantive turn's PR to avoid recursive PR noise; deferred entries do not cross the calendar-day boundary. Read-only turns may skip. `.ailog/` is append-only — never reorder or edit past entries.

### 7. Upgrading AIDLC

- When upgrading, compare against `https://github.com/awslabs/aidlc-workflows/releases`, bump `.aidlc-rule-details/VERSION`, and re-copy the contents of `aws-aidlc-rule-details/`.
- Custom files inside the upstream tree (`.aidlc-rule-details/extensions/bilingual-docs/`) must be backed up before the copy and restored afterwards (they live inside the upstream tree and would otherwise be wiped by a wholesale replace).
- The `.aidlc-overrides/` directory is **never** overwritten by upstream (it lives outside the upstream path). New project-specific rules must go here, not under `.aidlc-rule-details/`.
- Record the upgrade in a new ADR.
