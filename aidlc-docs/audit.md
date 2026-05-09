# AIDLC Audit Log

> Append-only log of AIDLC workflow events: user requests, stage transitions, extension toggles, approvals.
> 僅追加（append-only）的 AIDLC 工作流程稽核紀錄。

## 中文版

### 紀錄格式

每筆紀錄使用以下格式：

```markdown
### YYYY-MM-DD HH:MM TZ — <event-type>
**User request (raw)**: ...
**Stage**: ...
**Outcome**: ...
**Approver**: ...
```

### 事件紀錄

#### 2026-05-09 — AIDLC 框架導入（PR1）

**User request (raw)**: 「https://github.com/awslabs/aidlc-workflows/tree/main 我想用這個框架來當作這個專案的AI-SDLC開發框架，讓Claude Code開發更準確，需求可以更完善開發」
**Decisions**:
- Install mode: Hybrid（rules tree + 客製 CLAUDE.md）
- Docs layout: 重新對應到 AIDLC 規範路徑（PR2 執行）
- Extensions enabled: security/baseline、testing/property-based、bilingual-docs
- Execution: 拆 2 個 PR（PR1 = rules + CLAUDE.md；PR2 = docs migration）
- ADR location: `aidlc-docs/inception/decisions/`（PR2 才會搬）
**Stage**: Inception → Workspace Detection
**Outcome**: PR1 待合併。AIDLC v0.1.8 安裝至 `.aidlc-rule-details/`，CLAUDE.md 完成，aidlc-state.md / audit.md 建立。
**Approver**: dannielchung@gmail.com

#### 2026-05-09 — AIDLC docs migration（PR2）

**User request (raw)**: 「繼續做 PR2 docs migration」
**Stage**: Inception → Workspace Detection（artifact migration）
**Decisions**:
- 用 `git mv` 把 `docs/srs|architecture|user-stories|adr/` 全部搬到 `aidlc-docs/inception/{requirements,application-design,user-stories,decisions}/` 以保留 git history。
- `docs/README.md` 與 `docs/` 目錄移除（`aidlc-docs/README.md` 取代）。
- ADR-0001 在 in-place 更新路徑與 amendment note；ADR-0005 加 amendment 把雙語 scope 擴及 `aidlc-docs/`；ADR-0006 標記 PR1+PR2 已完成。
- `validate_repo_contract.py` REQUIRED_FILES / REQUIRED_TEXT 改指 `aidlc-docs/inception/...`；雙語掃描固定為 `aidlc-docs/**/*.md`。
- README、CLAUDE.md、bilingual-docs.md 全面移除 `docs/` 引用。
**Outcome**: PR2 待合併（branch `feat/aidlc-docs-migration`，stacked on PR1）。所有 cross-link 皆已更新並通過 validation。
**Approver**: dannielchung@gmail.com

---

## English Version

### Entry Format

Each entry uses the following structure:

```markdown
### YYYY-MM-DD HH:MM TZ — <event-type>
**User request (raw)**: ...
**Stage**: ...
**Outcome**: ...
**Approver**: ...
```

### Events

#### 2026-05-09 — AIDLC framework adoption (PR1)

**User request (raw)**: "https://github.com/awslabs/aidlc-workflows/tree/main 我想用這個框架來當作這個專案的AI-SDLC開發框架，讓Claude Code開發更準確，需求可以更完善開發"
**Decisions**:
- Install mode: Hybrid (rules tree + customized CLAUDE.md)
- Docs layout: remap to AIDLC paths (executed in PR2)
- Extensions enabled: security/baseline, testing/property-based, bilingual-docs
- Execution: split into 2 PRs (PR1 = rules + CLAUDE.md; PR2 = docs migration)
- ADR location: `aidlc-docs/inception/decisions/` (moved during PR2)
**Stage**: Inception → Workspace Detection
**Outcome**: PR1 pending merge. AIDLC v0.1.8 installed under `.aidlc-rule-details/`, CLAUDE.md authored, aidlc-state.md / audit.md created.
**Approver**: dannielchung@gmail.com

#### 2026-05-09 — AIDLC docs migration (PR2)

**User request (raw)**: "繼續做 PR2 docs migration"
**Stage**: Inception → Workspace Detection (artifact migration)
**Decisions**:
- Used `git mv` to relocate all of `docs/srs|architecture|user-stories|adr/` into `aidlc-docs/inception/{requirements,application-design,user-stories,decisions}/`, preserving git history.
- Removed `docs/README.md` and the `docs/` directory (superseded by `aidlc-docs/README.md`).
- Updated paths in ADR-0001 in place with an amendment note; added an amendment to ADR-0005 extending the bilingual scope to `aidlc-docs/`; marked ADR-0006 as PR1+PR2 completed.
- `validate_repo_contract.py` `REQUIRED_FILES` / `REQUIRED_TEXT` now point at `aidlc-docs/inception/...`; the bilingual scan is fixed to `aidlc-docs/**/*.md`.
- Removed all `docs/` references from README, CLAUDE.md, and bilingual-docs.md.
**Outcome**: PR2 pending merge (branch `feat/aidlc-docs-migration`, stacked on PR1). All cross-links updated and validation passes.
**Approver**: dannielchung@gmail.com
