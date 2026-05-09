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

#### 2026-05-09 — 新增 branch naming override（PR3）

**User request (raw)**: 「未來分支名稱用 上傳人名字/feat/用途 這種命名規則來定義，請幫我調整流程，但不要動到aidlc框架的rule，額外疊加其他rule去蓋過」
**Stage**: Inception → Process governance（override layer 新增）
**Decisions**:
- 新建 `.aidlc-overrides/` 目錄作為**專案 override 層**，不動 upstream `.aidlc-rule-details/`，避免未來 sync upstream 時受影響。
- Override 載入順序固定為**最後一層**（CLAUDE.md 載入順序新增 step 5）；override 與 upstream 衝突時 override 永遠勝出。
- 新增 `.aidlc-overrides/branch-naming.md` 規範 branch 格式 `<uploader>/<type>/<slug>`，type ∈ {feat, fix, docs, chore, refactor, test}；Danniel 一律以 `danniel/` 開頭。
- CLAUDE.md 工作模式新增第 6 條：`git checkout -b` 之前必須先檢查 branch naming override。
- CLAUDE.md 升級流程更新：明確 `.aidlc-overrides/` 永不被 upstream 覆蓋，新規則一律放這裡。
- `validate_repo_contract.py` 把兩個 override 檔加進 REQUIRED_FILES 與 REQUIRED_TEXT，內含 enforcement 雙語與類型清單。
- 採用本規則本身來示範：本次 PR 用 `danniel/feat/branch-naming-rule` 開分支。
**Outcome**: PR3 待合併（branch `danniel/feat/branch-naming-rule`，stacked on PR2）。
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

#### 2026-05-09 — Add branch-naming override (PR3)

**User request (raw)**: "未來分支名稱用 上傳人名字/feat/用途 這種命名規則來定義，請幫我調整流程，但不要動到aidlc框架的rule，額外疊加其他rule去蓋過"
**Stage**: Inception → Process governance (introduce override layer)
**Decisions**:
- Create `.aidlc-overrides/` as the **project override layer** so we never have to modify upstream `.aidlc-rule-details/`; this keeps future upstream syncs safe.
- Overrides are loaded **last** (CLAUDE.md rule-loading order gains step 5); on conflict between upstream and override, the override always wins.
- Add `.aidlc-overrides/branch-naming.md` enforcing the format `<uploader>/<type>/<slug>` with type ∈ {feat, fix, docs, chore, refactor, test}; all Danniel branches must start with `danniel/`.
- CLAUDE.md "Working Mode" gains item 6: check the branch-naming override before any `git checkout -b`.
- CLAUDE.md "Upgrading AIDLC" updated to spell out that `.aidlc-overrides/` is never overwritten by upstream and that new project rules must go there.
- `validate_repo_contract.py` now requires both override files in `REQUIRED_FILES` and `REQUIRED_TEXT`, including the bilingual sentinels and the allowed type list.
- Self-applied: this PR itself uses the new format — branch `danniel/feat/branch-naming-rule`.
**Outcome**: PR3 pending merge (branch `danniel/feat/branch-naming-rule`, stacked on PR2).
**Approver**: dannielchung@gmail.com
