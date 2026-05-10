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

#### 2026-05-09 — 新增 `.ailog/` 與 ai-logging override（PR4）

**User request (raw)**: 「幫我在git增加一個folder叫做.ailog，另外加入一個規則檔，每次AI生成的檔案跟回答都會記錄在.ailog，這個內容就幫我增加在裡面」
**Stage**: Inception → Process governance（新增 AI 活動底層 log 機制）
**Decisions**:
- 新增 `.ailog/` 目錄作為**逐 turn AI 活動底層 log**，與 `aidlc-docs/audit.md`（粗粒度 AIDLC 階段稽核）形成上下兩層。
- 新規則寫在 `.aidlc-overrides/ai-logging.md`（不動 upstream），格式為 `.ailog/<YYYY-MM-DD>.md`，每天一檔、append-only。
- Turn entry 結構：User request、Branch、Files（A/M/D/R）、Tool calls、Summary、Commits、PRs。
- 不溯及：本機制建立前的 turn 不必補登；PR1–PR3 的關鍵事件已記錄於本檔。
- CLAUDE.md 工作模式新增第 7 條：mutating turn 在回 user 前必須先寫 `.ailog/` entry。
- `validate_repo_contract.py` 新增 `.aidlc-overrides/ai-logging.md`、`.ailog/README.md` 為 REQUIRED_FILES，並驗 REQUIRED_TEXT 雙語與關鍵字。
- 自我示範：本 PR 自身的 turn 已寫入 `.ailog/2026-05-09.md`。
**Outcome**: PR4 待合併（branch `danniel/feat/ai-activity-logging`，stacked on PR3）。
**Approver**: dannielchung@gmail.com

#### 2026-05-09 — Stacked-merge 修復（PR #14）

**User request (raw)**: 「開修復 PR」
**Stage**: Inception → Process governance（事故修復 + 流程教訓）
**Incident**:
- PR #10 (PR1) 正確 merge 進 `main`（commit `99db585`）。
- PR #11 / #12 / #13 在 GitHub UI 各別點 "Merge" 時，因 base 仍指向上一個 stacked branch、未 retarget 到 `main`，分別被 merge 進它們的上層 base：
  - PR #11 → merge 進 `feat/aidlc-framework-rules`（不是 main）
  - PR #12 → merge 進 `feat/aidlc-docs-migration`
  - PR #13 → merge 進 `danniel/feat/branch-naming-rule`
- 三個 PR 顯示 MERGED 但 `main` 並未拿到 PR2 / PR3 / PR4 的內容。
**Decisions**:
- 修復策略：開新 PR 從 `danniel/feat/ai-activity-logging` → `main`。該 branch tip 已 stacked PR2 + PR3 + PR4 三個 commit，merge 一次即把三份內容一併送進 main，保留 commit 歷史。
- 不採 cherry-pick / rebase / 重開 4 個 PR：太多噪音；現有 branch 已是正確的「未進 main」累積結果。
- 同步把這次事故與修復寫入 `.ailog/2026-05-09.md` Turn 2，作為 stacked PR 操作的反例案例。
**Lesson learned (流程教訓)**:
- Stacked PR 在 GitHub 沒有自動 base retarget。**每 merge 一個 PR，必須手動把下一個 PR 的 base 改成 `main`，再 merge**；否則會 merge 進已過時的 base。
- Memory 已新增 `feedback_stacked_pr_merge.md`（避免再犯）。
**Outcome**: 修復 PR (#14) 待合併到 main。
**Approver**: dannielchung@gmail.com

#### 2026-05-09 — ai-logging override 增補 deferred-logging 條款（PR #16）

**User request (raw)**: 「不能在同一個RP一起寫ailog嗎？」→「幫我更新 rule」
**Stage**: Inception → Process governance（rule 條款增補）
**Context**:
- PR #15 / Turn 3-4 實際遇到的遞迴問題：pure ops turn（`git push --delete`、`gh pr merge`）唯一檔案變動是 log entry → 為了寫 log 必須開 PR → 開 PR 又是新 turn → 又要寫 log。
- 之前已用「把 Turn N append 到 active PR 同一 branch」的手法閃過幾次，但缺乏明文授權。
**Decisions**:
- `.aidlc-overrides/ai-logging.md` 增 **Deferred Logging 條款**：
  1. Pure-ops turn（無 working-tree 變動）entry **預設 defer** 到下一個 substantive turn 的 PR；不必為 pure-ops 單獨開 PR。
  2. Substantive turn 補寫 deferred entries 時依時間順序排在自己前面，每筆加 `**Deferred from**: <原 turn 時間>` 標記。
  3. 多個 pure-ops turn 可累積 batch。
  4. **不跨 calendar day**：當天 deferred entries 必須在當地時間（+0800）跨日前進 main，否則 AI 須主動開 chore PR 收尾。
  5. Substantive turn 永遠 inline 寫，不能 defer 自己。
- 重新分類「何時寫 log」表為 substantive / pure-ops / read-only / automated 四類，明確標 defer 是否允許。
- CLAUDE.md item 7 同步更新摘要這個分類與 deferred 預設行為。
- validate REQUIRED_TEXT 新增 `Deferred Logging`、`Substantive turn`、`Pure-ops turn`、`Deferred from` 等關鍵字防止未來誤改。
- 自我示範：本 turn 是 substantive（有檔案變動），Turn 5 entry inline 寫於本 PR branch。
**Outcome**: PR #16 待合併到 main。
**Approver**: dannielchung@gmail.com

#### 2026-05-09 — 移除 ai-logging，改採 on-demand decisions-log（PR #17）

**User request (raw)**: 「幫我將ai-logging 規則移除，新增一個專案重要決議記錄，當使用這要求時，就記錄當下與AI對話的決議」
**Stage**: Inception → Process governance（log 機制換代，supersedes PR4 + PR #16）
**Decisions**:
- **移除** `.ailog/`（README + 2026-05-09 daily log）與 `.aidlc-overrides/ai-logging.md`（per-turn 強制 log + deferred-logging clause）。歷史紀錄保留在 git（PR4 / PR #14 / PR #15 / PR #16 commits）。
- **新增** `.aidlc-overrides/decisions-log.md` 規則：**僅**在使用者明確要求時（如「記錄這個決議」、「log this decision」），把當下對話達成的決議寫進 `aidlc-docs/decisions-log.md`，雙語、append-only。
- 觸發判斷以**語意**而非死記字串為準；不確定時先反問。
- 與其他 log 區隔：AIDLC 階段事件仍寫 `audit.md`；架構級決策仍開 ADR；`decisions-log.md` 只記錄 user-driven 一般決議。
- CLAUDE.md item 7 改寫為 decisions-log（on-demand），明確標示舊 per-turn `.ailog/` 已移除。
- `.aidlc-overrides/README.md` Current Overrides 表新增 `decisions-log.md` 列。
- `scripts/validate_repo_contract.py`：REQUIRED_FILES 移除 `.ailog/README.md`、`.aidlc-overrides/ai-logging.md`，新增 `.aidlc-overrides/decisions-log.md`、`aidlc-docs/decisions-log.md`；REQUIRED_TEXT 同步換鎖鑰字。
- 自我示範：「移除 ai-logging、改採 on-demand decisions-log」這個決議本身已寫成 `aidlc-docs/decisions-log.md` 第一筆。
**Outcome**: PR #17 待合併到 main。
**Approver**: dannielchung@gmail.com

#### 2026-05-10 — 新增 wave-based 開發計劃 HTML（PR #18）

**User request (raw)**: 「幫我把SRS 裡 9 個 pillar、26 條 user stories 整理成一個開發計劃，輸出成一個HTML給我」
**Stage**: Inception → Workflow Planning（pillar 級 wave 規劃）
**Decisions**:
- 新增 `aidlc-docs/inception/plans/development-plan.html`：依 SRS pillars 與 user-stories 整理，分 4 個 wave（W0 Foundation、W1 Core Differentiators、W2 FinOps/Ops/Mobile、W3 Extensions），含相依圖（Mermaid）、story table、pillar 細節、NFR、已知風險、下一步建議。
- 採單檔 HTML（inline CSS、Mermaid via CDN），可直接 `open` 瀏覽，亦可離線閱讀（Mermaid 不可用時純文字仍可看）。
- 新增 `aidlc-docs/inception/plans/README.md`（雙語），說明 plans/ 目錄角色與其他 inception 子目錄的關係。
- 不對 SRS / user-stories 原檔做改動；本計劃為衍生 artifact。
- 此計劃尚未對 SRS scope 加 / 減 pillar，所以不需要新 ADR；後續 wave 拆細時若改變 scope 再開 ADR。
**Outcome**: PR #18 待合併到 main。
**Approver**: dannielchung@gmail.com

#### 2026-05-10 — PR #18 補強：HTML 改 kanban + 開 GitHub Project

**User request (raw)**: 「剛剛的PR請調整HTML，輸出的HTML以看板模式呈現，或者輸出到Project看板功能裡」（決議：兩個都做、欄位依 Wave）
**Stage**: Inception → Workflow Planning（視覺化 + 線上 live 看板）
**Decisions**:
- 在 PR #18 同一 branch 補 commit：HTML 把 §2 從堆疊式 wave cards 改為 4 欄 kanban board（W0/W1/W2/W3），每個 user story 為卡片，含 ID、title、pillar tag、deps；保留相依圖、story table、pillar 細節等其他段落。
- 新增 GitHub Project: **Cloud-360 Development Plan**（owner=Dannielchung，public，URL: <https://github.com/users/Dannielchung/projects/1>）。Org-level project 因 `opendiamonds` 是 user account 而非 org，無法在該 owner 下建 Project，故掛 Dannielchung 個人；可連結 opendiamonds/cloud-360 的 issues / PRs。
- Project 自訂 3 個欄位：Wave（W0–W3 single-select）、Pillar（A–I single-select）、Story ID（text）。內建 Status 欄位保留。
- 寫入 26 個 draft items（每條 user story 一個），自動填上 Wave / Pillar / Story ID。
- HTML header 加入 "View on GitHub Project" 按鈕；plans/README.md 表格新增 live project 列。
- Auth：因 `gh` token 缺 `project` scope，請 user 手動跑 `gh auth refresh -h github.com -s project` 後才得以建 Project。
**Outcome**: PR #18 取得新 commit；Project 公開可看。
**Approver**: dannielchung@gmail.com

#### 2026-05-10 — PR #18 修正：改用 opendiamonds/projects/16 + 計劃內容繁中化

**User request (raw)**: 「https://github.com/users/opendiamonds/projects/16 這才是Github Project的位置，不要額外另開一個，另外計劃內容要用繁體中文！」
**Stage**: Inception → Workflow Planning（修正 Project 位置 + 完整翻 Traditional Chinese）
**Decisions**:
- 把 26 個 items 加到既有 `opendiamonds/projects/16`（標題前綴 `[Cloud-360]` 區分另外 4 個現有 items），並在該 project 上補建 3 個自訂欄位 Wave / Pillar / Story ID（皆繁中選項）；Status 沿用內建欄位，預設值設為 Backlog。
- 刪除上一輪誤建的 Dannielchung project 1（`gh project delete 1`），避免有兩個來源的混淆。
- HTML 內容繁中化：story titles、kanban 卡片、story table 標頭與內容、9 個 pillar block 標題、stat 卡片 label、相依圖節點、NFR/Risks/Next Steps 段落標題、footer。技術名詞（Mermaid、draw.io、IaC、MCP、OPA、Sentinel、Terraform、Spot/Preemptible 等）保留英文。
- HTML header CTA 與 footer 連結指向 `https://github.com/users/opendiamonds/projects/16`。
- README 更新為新位置、文字繁中化（指出 26 items 標題前綴 `[Cloud-360]`、自訂欄位、Status 流程）。
- 不動 SRS / user stories 原檔（仍英中混合）；只改開發計劃 artifact。
**Outcome**: PR #18 第 3 個 commit；live kanban 在 opendiamonds/projects/16；HTML 完全繁中。
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

#### 2026-05-09 — Add `.ailog/` and ai-logging override (PR4)

**User request (raw)**: "幫我在git增加一個folder叫做.ailog，另外加入一個規則檔，每次AI生成的檔案跟回答都會記錄在.ailog，這個內容就幫我增加在裡面"
**Stage**: Inception → Process governance (introduce a per-turn AI activity log)
**Decisions**:
- Create `.ailog/` as the **per-turn AI activity log**, layered below `aidlc-docs/audit.md` (which remains the coarse AIDLC stage audit).
- The new rule lives in `.aidlc-overrides/ai-logging.md` (upstream untouched). Format: `.ailog/<YYYY-MM-DD>.md`, one file per day, append-only.
- Turn entry structure: User request / Branch / Files (A/M/D/R) / Tool calls / Summary / Commits / PRs.
- Not retroactive: turns before this rule are not back-filled; PR1–PR3 key events already exist in this file.
- CLAUDE.md "Working Mode" gains item 7: mutating turns must append a `.ailog/` entry before sending the final response.
- `validate_repo_contract.py` adds `.aidlc-overrides/ai-logging.md` and `.ailog/README.md` to `REQUIRED_FILES`, with bilingual sentinels and key terms in `REQUIRED_TEXT`.
- Self-applied: this PR's own turn was logged to `.ailog/2026-05-09.md`.
**Outcome**: PR4 pending merge (branch `danniel/feat/ai-activity-logging`, stacked on PR3).
**Approver**: dannielchung@gmail.com

#### 2026-05-09 — Stacked-merge remediation (PR #14)

**User request (raw)**: "開修復 PR"
**Stage**: Inception → Process governance (incident remediation + lesson learned)
**Incident**:
- PR #10 (PR1) merged into `main` correctly (commit `99db585`).
- PR #11 / #12 / #13 were each merged via GitHub UI without retargeting their bases to `main`. They were merged **into their stacked base branches** instead of `main`:
  - PR #11 → merged into `feat/aidlc-framework-rules` (not main)
  - PR #12 → merged into `feat/aidlc-docs-migration`
  - PR #13 → merged into `danniel/feat/branch-naming-rule`
- All three show as MERGED, but `main` never received the PR2 / PR3 / PR4 content.
**Decisions**:
- Remediation: open a new PR from `danniel/feat/ai-activity-logging` → `main`. The branch tip already stacks PR2 + PR3 + PR4 commits on top of PR1; one merge brings everything in, with each commit's history preserved.
- Did NOT cherry-pick / rebase / reopen four PRs — too noisy; the existing branch is the correct "not-yet-on-main" accumulation.
- Logged the incident and remediation in `.ailog/2026-05-09.md` Turn 2 as a counter-example for stacked-PR handling.
**Lesson learned**:
- GitHub does not auto-retarget stacked PR bases. **Every time a PR merges, manually change the next PR's base to `main` before merging**; otherwise merging lands the change into the now-stale base.
- Added memory `feedback_stacked_pr_merge.md` so this doesn't repeat.
**Outcome**: remediation PR (#14) pending merge into main.
**Approver**: dannielchung@gmail.com

#### 2026-05-09 — ai-logging override gains deferred-logging clause (PR #16)

**User request (raw)**: "不能在同一個RP一起寫ailog嗎？" → "幫我更新 rule"
**Stage**: Inception → Process governance (clause amendment)
**Context**:
- PR #15 / Turn 3-4 actually triggered the recursion: a pure-ops turn (`git push --delete`, `gh pr merge`) produces no file change other than the log entry → opening a PR just to write the log is itself a new turn → which also needs a log entry.
- The "append Turn N to the active PR's branch" workaround had been used a few times without explicit authorization in the rule.
**Decisions**:
- `.aidlc-overrides/ai-logging.md` gains a **Deferred Logging clause**:
  1. A pure-ops turn (no working-tree change) defaults to **deferring** its entry to the next substantive turn's PR; pure-ops alone does not require a dedicated PR.
  2. The substantive turn appends deferred entries in chronological order ahead of its own, with a `**Deferred from**: <original turn timestamp>` marker.
  3. Multiple consecutive pure-ops turns may batch.
  4. **No cross-day deferral**: deferred entries must reach `main` within the same calendar day (+0800); otherwise the AI must proactively open a chore PR before midnight.
  5. Substantive turns always log inline — they cannot defer themselves.
- Reclassified the "When to log" table into substantive / pure-ops / read-only / automated, with deferral eligibility per row.
- CLAUDE.md item 7 updated to summarize the classification and deferral default.
- `validate_repo_contract.py` `REQUIRED_TEXT` now requires keywords `Deferred Logging`, `Substantive turn`, `Pure-ops turn`, `Deferred from` to prevent future drift.
- Self-applied: this turn is substantive (file changes), so Turn 5 is logged inline on this PR's branch.
**Outcome**: PR #16 pending merge to main.
**Approver**: dannielchung@gmail.com

#### 2026-05-09 — Remove ai-logging, adopt on-demand decisions-log (PR #17)

**User request (raw)**: "幫我將ai-logging 規則移除，新增一個專案重要決議記錄，當使用這要求時，就記錄當下與AI對話的決議"
**Stage**: Inception → Process governance (logging mechanism replacement, supersedes PR4 + PR #16)
**Decisions**:
- **Removed** `.ailog/` (README + the 2026-05-09 daily log) and `.aidlc-overrides/ai-logging.md` (per-turn forced-log mechanism + deferred-logging clause). Historical entries remain in git (PR4 / PR #14 / PR #15 / PR #16 commits).
- **Added** `.aidlc-overrides/decisions-log.md` rule: **only** when the user explicitly asks (e.g. "log this decision", "記錄這個決議") does the AI capture the conversation's decision into `aidlc-docs/decisions-log.md`, bilingual, append-only.
- Triggering relies on **semantic judgment** rather than literal string matching; the AI confirms with the user when uncertain.
- Separation from other logs: AIDLC stage events still go to `audit.md`; architecture decisions still get an ADR; `decisions-log.md` is for user-driven general decisions only.
- CLAUDE.md item 7 rewritten as decisions-log (on-demand), explicitly noting that the old per-turn `.ailog/` mechanism is gone.
- `.aidlc-overrides/README.md` Current Overrides table now lists `decisions-log.md`.
- `scripts/validate_repo_contract.py`: `REQUIRED_FILES` drops `.ailog/README.md` and `.aidlc-overrides/ai-logging.md`, adds `.aidlc-overrides/decisions-log.md` and `aidlc-docs/decisions-log.md`; `REQUIRED_TEXT` keys swapped accordingly.
- Self-applied: the decision itself ("remove ai-logging, adopt on-demand decisions-log") is the first entry in `aidlc-docs/decisions-log.md`.
**Outcome**: PR #17 pending merge to main.
**Approver**: dannielchung@gmail.com

#### 2026-05-10 — Add wave-based development plan HTML (PR #18)

**User request (raw)**: "幫我把SRS 裡 9 個 pillar、26 條 user stories 整理成一個開發計劃，輸出成一個HTML給我"
**Stage**: Inception → Workflow Planning (pillar-level wave plan)
**Decisions**:
- Added `aidlc-docs/inception/plans/development-plan.html`: SRS pillars and user stories organized into four waves (W0 Foundation, W1 Core Differentiators, W2 FinOps/Ops/Mobile, W3 Extensions). Contains a dependency graph (Mermaid), full story table, pillar details, NFRs, known risks, and recommended next steps.
- Single-file HTML (inline CSS, Mermaid via CDN) — can be opened directly in a browser and remains readable offline (text-only fallback if Mermaid is unavailable).
- Added `aidlc-docs/inception/plans/README.md` (bilingual) describing the role of `plans/` and its relationship to other inception subdirectories.
- No changes to SRS or user-stories source files; this plan is a derived artifact.
- Plan does not add or remove SRS pillars, so no new ADR is required; if future wave breakdowns change scope, a new ADR will be opened.
**Outcome**: PR #18 pending merge to main.
**Approver**: dannielchung@gmail.com

#### 2026-05-10 — PR #18 follow-up: HTML kanban + GitHub Project

**User request (raw)**: "剛剛的PR請調整HTML，輸出的HTML以看板模式呈現，或者輸出到Project看板功能裡" (decision: both, columns by Wave)
**Stage**: Inception → Workflow Planning (visualization + live online board)
**Decisions**:
- Added a follow-up commit to the same PR #18 branch: HTML §2 switched from stacked wave cards to a 4-column kanban board (W0/W1/W2/W3); every user story is a card showing ID, title, pillar tag, and dependencies. Other sections (dependency graph, story table, pillar details) preserved.
- Created GitHub Project **Cloud-360 Development Plan** (owner=Dannielchung, public, URL: <https://github.com/users/Dannielchung/projects/1>). Project lives under Dannielchung because `opendiamonds` is a user account (not an organization), so we cannot create projects under that owner; the project still links to issues / PRs in opendiamonds/cloud-360.
- Project has three custom fields: Wave (single-select W0–W3), Pillar (single-select A–I), Story ID (text). Built-in Status field retained.
- Seeded with 26 draft items (one per user story) with Wave / Pillar / Story ID populated.
- HTML header gains a "View on GitHub Project" button; `plans/README.md` table lists the live project row.
- Auth note: the `gh` CLI was missing the `project` scope, so the user manually ran `gh auth refresh -h github.com -s project` before project creation could proceed.
**Outcome**: PR #18 receives a new commit; the GitHub Project is public.
**Approver**: dannielchung@gmail.com

#### 2026-05-10 — PR #18 fix-up: use opendiamonds/projects/16 + Traditional Chinese plan content

**User request (raw)**: "https://github.com/users/opendiamonds/projects/16 這才是Github Project的位置，不要額外另開一個，另外計劃內容要用繁體中文！"
**Stage**: Inception → Workflow Planning (correct project location + full Traditional Chinese rendering)
**Decisions**:
- Added the 26 items into the **existing** `opendiamonds/projects/16` (titles prefixed `[Cloud-360]` to distinguish from the 4 unrelated items already there) and created three custom fields on that project: Wave / Pillar / Story ID (Traditional Chinese option labels). Status reuses the built-in field, defaulting to Backlog for new items.
- Deleted the misplaced Dannielchung project 1 created earlier (`gh project delete 1`) to avoid two sources of truth.
- Localized the HTML to Traditional Chinese: story titles, kanban cards, story-table headers and rows, 9 pillar block titles, stat-card labels, dependency-graph node text, section headers for NFR/Risks/Next Steps, and the footer. Technical proper nouns (Mermaid, draw.io, IaC, MCP, OPA, Sentinel, Terraform, Spot/Preemptible, etc.) remain in English.
- HTML header CTA and footer link now point to `https://github.com/users/opendiamonds/projects/16`.
- README updated to the new project location and rephrased in Traditional Chinese (noting the `[Cloud-360]` prefix, custom fields, and Status flow).
- Source SRS / user-stories files are not modified (still mixed English/Chinese); only the planning artifact is localized.
**Outcome**: PR #18 third commit; live kanban now lives at opendiamonds/projects/16; HTML fully in Traditional Chinese.
**Approver**: dannielchung@gmail.com
