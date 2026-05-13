# ADR 0006: Adopt AIDLC as the AI-SDLC Framework

> 本文件必須同時包含中文版與英文版。
> This document must include both Chinese and English versions.

## 中文版

- Status: Accepted（PR1 + PR2 已完成）
- Date: 2026-05-09
- AIDLC Version Adopted: 0.1.8
- Migration Status: ✅ PR1（rules + CLAUDE.md）合併中、✅ PR2（docs/ → aidlc-docs/inception/）合併中
- This file location: 本 ADR 已隨 PR2 從 `docs/adr/0006-adopt-aidlc-framework.md` 搬到目前路徑

### Context

Cloud-360 是 AI-native multi-cloud platform，仰賴 Claude Code 與其他 AI coding agents 從自然語言需求一路產製 SRS、architecture、user stories、IaC、code 與運維 runbooks。在沒有統一方法論的情況下，AI 產出品質會隨 prompt 變動，需求分析、設計決策、測試策略與安全規範也容易遺漏。

[awslabs/aidlc-workflows](https://github.com/awslabs/aidlc-workflows) 是 AWS Labs 開源、平台無關的 AI-Driven Development Life Cycle 方法論，提供三階段（🔵 Inception / 🟢 Construction / 🟡 Operations）的結構化規則、context-optimized 的 extension 機制，以及 audit / state 追蹤。導入後，Claude Code 將以 AIDLC 規則優先於預設工作流程，提升開發精準度。

### Decision

1. 採用 AIDLC v0.1.8 為 Cloud-360 主要 AI-SDLC 開發方法論。
2. 安裝模式：**Hybrid** —— 將官方 `aws-aidlc-rule-details/` 複製到 `.aidlc-rule-details/`，並客製化 `CLAUDE.md` 對齊既有 repository contract 與雙語規範。
3. AIDLC 入口：`.aidlc-rules/aws-aidlc-rules/core-workflow.md`；CLAUDE.md 指示載入順序。
4. Artifacts 輸出：`aidlc-docs/`（包含 `aidlc-state.md`、`audit.md`、`inception/`、`construction/`、`operations/`）。
5. **預設啟用** 三個 extensions：
   - `extensions/security/baseline/`（官方）
   - `extensions/testing/property-based/`（官方）
   - `extensions/bilingual-docs/`（客製，永遠強制，對齊 ADR-0005）
6. **遷移分兩階段（已完成）**：
   - **PR1** ✅ 安裝 rules tree、CLAUDE.md、aidlc-docs 骨架；`docs/` 不動（branch `feat/aidlc-framework-rules`）。
   - **PR2** ✅ 用 `git mv` 將 `docs/srs/`、`docs/architecture/`、`docs/user-stories/`、`docs/adr/`（含本 ADR）搬到 `aidlc-docs/inception/{requirements,application-design,user-stories,decisions}/`；移除 `docs/` 目錄；更新 README、validate script、CLAUDE.md、bilingual-docs.md 與所有 cross-link（branch `feat/aidlc-docs-migration`）。
7. 重大變更（架構、外部依賴、production 影響）必須以新 ADR 紀錄。
8. AIDLC 升級流程：對照官方 release，更新 `.aidlc-rule-details/VERSION` 與內容；客製 `extensions/bilingual-docs/` 不得被覆蓋；升級記錄寫入新 ADR。

### Consequences

**正面**：

- AI agent 開發行為一致、可審查（audit.md）、可恢復（aidlc-state.md session continuity）。
- 需求分析、設計、測試、安全在每個 stage 都會被強制檢查（hard constraints）。
- 三 extensions（security / property-based / bilingual）在每個 stage 自動套用，無須重複提醒 user。
- 與既有 SDD baseline（SRS、ADR、architecture）相容；PR1 不破壞現有路徑。

**負面 / 取捨**：

- 學習成本：team 需熟悉 AIDLC 三階段、question format、stage-completion summary。
- PR1 與 PR2 拆開造成短期路徑不一致（PR2 完成後 `docs/adr/...` 已全數搬到 `aidlc-docs/inception/decisions/...`）。
- 升級需要手動處理：客製 extension 不能被官方覆蓋。

### Repository Contract 影響

`scripts/validate_repo_contract.py` 隨 PR1 新增、PR2 重新對應到 `aidlc-docs/inception/...` 路徑。當前必要檔案包括：

- `CLAUDE.md`
- `.aidlc-rule-details/VERSION`
- `.aidlc-rules/aws-aidlc-rules/core-workflow.md`
- `.aidlc-rule-details/extensions/bilingual-docs/bilingual-docs.md`
- `aidlc-docs/aidlc-state.md`
- `aidlc-docs/audit.md`
- `aidlc-docs/README.md`
- `aidlc-docs/inception/requirements/cloud-360-srs.md`
- `aidlc-docs/inception/application-design/system-architecture.md`
- `aidlc-docs/inception/user-stories/core-pillars.md`
- `aidlc-docs/inception/decisions/0001..0006-*.md`

雙語掃描範圍 PR2 後固定為 `aidlc-docs/**/*.md`（PR1 暫過渡期同時掃 `docs/` 與 `aidlc-docs/`）。

---

## English Version

- Status: Accepted (PR1 + PR2 completed)
- Date: 2026-05-09
- AIDLC Version Adopted: 0.1.8
- Migration status: ✅ PR1 (rules + CLAUDE.md) merging, ✅ PR2 (docs/ → aidlc-docs/inception/) merging
- This file location: moved by PR2 from `docs/adr/0006-adopt-aidlc-framework.md` to its current path

### Context

Cloud-360 is an AI-native multi-cloud platform that relies on Claude Code and other AI coding agents to produce SRSs, architecture, user stories, IaC, code, and operations runbooks from natural-language requirements. Without a shared methodology, AI output quality varies with the prompt, and requirements analysis, design decisions, testing strategy, and security guardrails are easy to miss.

[awslabs/aidlc-workflows](https://github.com/awslabs/aidlc-workflows) is an open-source, platform-agnostic AI-Driven Development Life Cycle methodology from AWS Labs. It provides a three-phase structure (🔵 Inception / 🟢 Construction / 🟡 Operations), a context-optimized extension mechanism, and audit / state tracking. Adopting it makes Claude Code follow AIDLC rules ahead of its default workflow and improves development precision.

### Decision

1. Adopt AIDLC v0.1.8 as Cloud-360's primary AI-SDLC methodology.
2. Install mode: **Hybrid** — copy upstream `aws-aidlc-rule-details/` to `.aidlc-rule-details/`, and add a customized `CLAUDE.md` aligned with the existing repository contract and bilingual rule.
3. AIDLC entry point: `.aidlc-rules/aws-aidlc-rules/core-workflow.md`; CLAUDE.md prescribes the load order.
4. Artifact location: `aidlc-docs/` (containing `aidlc-state.md`, `audit.md`, `inception/`, `construction/`, `operations/`).
5. **Pre-enabled** extensions:
   - `extensions/security/baseline/` (upstream)
   - `extensions/testing/property-based/` (upstream)
   - `extensions/bilingual-docs/` (custom, always enforced, aligned with ADR-0005)
6. **Two-phase migration (completed)**:
   - **PR1** ✅ install the rules tree, CLAUDE.md, and aidlc-docs skeleton; `docs/` left untouched (branch `feat/aidlc-framework-rules`).
   - **PR2** ✅ `git mv` `docs/srs/`, `docs/architecture/`, `docs/user-stories/`, and `docs/adr/` (including this ADR) to `aidlc-docs/inception/{requirements,application-design,user-stories,decisions}/`; remove the `docs/` directory; update README, the validation script, CLAUDE.md, bilingual-docs.md, and all cross-links (branch `feat/aidlc-docs-migration`).
7. Significant changes (architecture, external dependencies, production impact) must be recorded as new ADRs.
8. AIDLC upgrade process: compare against upstream releases, bump `.aidlc-rule-details/VERSION` and refresh contents; the custom `extensions/bilingual-docs/` must not be overwritten; record the upgrade in a new ADR.

### Consequences

**Positive**:

- AI agent behavior becomes consistent, auditable (`audit.md`), and resumable (`aidlc-state.md` session continuity).
- Requirements analysis, design, testing, and security are enforced as hard constraints at each stage.
- The three extensions (security / property-based / bilingual) apply automatically at every stage without re-prompting the user.
- Compatible with the existing SDD baseline (SRS, ADRs, architecture); PR1 does not break any existing path.

**Negative / Trade-offs**:

- Learning cost: the team must familiarize themselves with AIDLC's three phases, question format, and stage-completion summaries.
- Splitting PR1 and PR2 created short-term path inconsistency, now resolved (`docs/adr/...` were fully moved into `aidlc-docs/inception/decisions/...` by PR2).
- Upgrades require manual care: custom extensions must not be overwritten by upstream.

### Repository Contract Impact

`scripts/validate_repo_contract.py` was extended in PR1 and remapped in PR2 to the `aidlc-docs/inception/...` paths. The current required files include:

- `CLAUDE.md`
- `.aidlc-rule-details/VERSION`
- `.aidlc-rules/aws-aidlc-rules/core-workflow.md`
- `.aidlc-rule-details/extensions/bilingual-docs/bilingual-docs.md`
- `aidlc-docs/aidlc-state.md`
- `aidlc-docs/audit.md`
- `aidlc-docs/README.md`
- `aidlc-docs/inception/requirements/cloud-360-srs.md`
- `aidlc-docs/inception/application-design/system-architecture.md`
- `aidlc-docs/inception/user-stories/core-pillars.md`
- `aidlc-docs/inception/decisions/0001..0006-*.md`

After PR2 the bilingual scan is fixed to `aidlc-docs/**/*.md` (during the PR1 transitional period it scanned both `docs/` and `aidlc-docs/`).
