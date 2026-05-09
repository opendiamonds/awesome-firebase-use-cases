# AI Activity Logging Rule

> Project override rule. Mandates that every AI turn touching the repository is logged in `.ailog/`.
> 專案 override 規則。每一次 AI 動到本 repo 的對話 turn 都必須在 `.ailog/` 留下紀錄。

## 中文版

### 規範

每一次 AI（Claude Code 與其他 AI agent）在本 repo 內**生成檔案、修改檔案、刪除檔案、執行 commit/push、開 PR**等任一動作後，**必須**在 `.ailog/<YYYY-MM-DD>.md` 追加一筆 turn entry。同一個 user 對話 turn 只寫一筆，無論該 turn 跑了多少 tool call。

### 何時寫 log

依該 turn 是否有 **working-tree 檔案變動** 區分為 **substantive** 與 **pure-ops** 兩類；後者支援 deferred logging（見下方 Deferred Logging 條款）。

| 情境 | 必寫？ | 立即 vs deferred |
|---|---|---|
| **Substantive turn**：用 Write / Edit / NotebookEdit / `git mv` / `git rm` 等動到 working tree 的檔案 | ✅ 必寫 | ❌ 不可 defer，立刻 append 到當前 branch 並 commit |
| **Pure-ops turn**：只動 GitHub 遠端（`git push --delete`、`gh pr merge`、`gh pr edit`、`gh pr close`、`gh release *`、`gh issue *`），working tree 無變動 | ✅ 必寫 | ✅ 可 defer 到下一個 substantive turn 的 PR（預設行為，避免遞迴 PR 噪音） |
| **Read-only turn**：純粹回答問題、查資料、跑 `grep` / `git log` / `gh pr view` 等 | ⏸ 可選（建議寫，量大時可省） | — |
| **自動化任務（cron / loop / 背景 watcher）** | ✅ 必寫，每跑一次寫一筆 | 若該 watcher 純粹動到 GitHub 遠端視為 pure-ops，可 defer |

### 檔案格式

- 路徑：`.ailog/<YYYY-MM-DD>.md`（依**當地時區**的日期；本專案預設 +0800）
- 一個檔案 = 一天份所有 turn 的累積；append-only，不重排、不刪減過去條目
- 每筆 turn entry 結構（H2/H3 階層）：

```markdown
## Turn N — HH:MM:SS +TZ

**User request**: <verbatim user message，原文照抄；中英混雜可接受>
**Branch**: <當前 git branch；若中途換 branch 也記下>
**Files**:
- A <path>      ← Added
- M <path>      ← Modified
- D <path>      ← Deleted
- R <old> -> <new>  ← Renamed (git mv)
**Tool calls (selected)**: <可選；列出有副作用的指令，例如 `gh pr create`、`git push`>
**Summary**: <1–3 句話描述這個 turn 做了什麼以及 why；不需要逐行解說>
**Commits (if any)**: <commit hash; 多個用逗號>
**PRs (if any)**: <PR URL 或 #number>
```

- Turn 編號 N 在每天從 1 開始，依時間順序遞增
- 時間使用 24h 格式，標明時區（例如 `14:35:12 +0800`）

### 範例

```markdown
## Turn 1 — 16:48:20 +0800

**User request**: 幫我在git增加一個folder叫做.ailog，另外加入一個規則檔...
**Branch**: danniel/feat/ai-activity-logging
**Files**:
- A `.ailog/README.md`
- A `.ailog/2026-05-09.md`
- A `.aidlc-overrides/ai-logging.md`
- M `CLAUDE.md`
- M `scripts/validate_repo_contract.py`
- M `aidlc-docs/audit.md`
**Summary**: Established the AI activity logging mechanism: created `.ailog/` daily-log folder, authored the override rule, wired it into CLAUDE.md and the repo contract.
**Commits**: cf28bfa, ...
**PRs**: opendiamonds/cloud-360#13
```

### Deferred Logging — pure-ops turn 可延後

**問題**：pure-ops turn（例如 `gh pr merge`、`git push --delete`）唯一的「檔案變動」是 log entry 本身。如果嚴格要求 turn 結束前必須開 PR 把 entry 送進 main，會形成「**為了寫 log 而開 PR → 那個 PR 開出來又是新 turn → 又要寫 log**」的遞迴噪音；2026-05-09 PR #15 / Turn 3-4 已實際發生過。

**規則**：

1. **Pure-ops turn 的 entry 可以 defer 到下一個 substantive turn 的 PR branch**，**不必為 pure-ops turn 單獨開 PR**。Defer 為預設行為。
2. Substantive turn 寫自己的 entry 時，把累積的 deferred entries 一併補進 `.ailog/<YYYY-MM-DD>.md`，依**原 turn 時間順序**排在前面；每筆都加 `**Deferred from**: <原 turn 時間 +TZ> (<context, 例如 watcher id>)` 標記。
3. 多個連續 pure-ops turn 可累積批次處理。
4. **不跨 calendar day**：deferred entries 必須在當天內被某個 substantive turn 帶進 main。若一直沒 substantive turn 而當地時間（+0800）即將跨日，AI 必須**主動開 chore PR** 把當天的 deferred entries 送進 main，以免日誌斷點。
5. **Substantive turn 永遠 inline 寫**：不能 defer 自己。

**判斷自己**：當前 turn 結束時，working tree 有沒有 commit-able 變動？

- **有** → substantive → 立刻 append 並 commit。
- **無** → pure-ops → 預設 defer（也可選擇立刻開小 PR，但通常沒必要）。

**Deferred entry 範例**：

```markdown
## Turn 7 — 09:30:15 +0800

**User request**: <substantive turn 的 user 訊息>
**Branch**: danniel/feat/cost-calc-rewrite
**Files**: <substantive turn 自己的檔案變動 …>
**Summary**: <substantive turn 自己做了什麼>

> **Deferred entries appended below in chronological order:**

### Turn 5 (deferred) — 08:12:03 +0800

**Deferred from**: pure-ops turn at 2026-05-10 08:12:03 +0800 (watcher xyz123)
**Original user request**: 砍掉 stale branches
**GitHub-side mutations**:
- DEL origin/old/feature-a
- DEL origin/old/feature-b
**Tool calls**: `git push origin --delete x2`
**Summary**: Background watcher cleaned up two stale branches after PR #99 merged.

### Turn 6 (deferred) — 08:30:47 +0800

**Deferred from**: pure-ops turn at 2026-05-10 08:30:47 +0800
**Original user request**: 把 PR #100 description 補上 test plan
**GitHub-side mutations**: edited PR #100 body
**Tool calls**: `gh pr edit 100 --body ...`
**Summary**: Added test plan section per user request.
```

> 注意 H3 (`###`) 用於 deferred 子條目，避免跟 substantive turn 的 H2 (`##`) 衝突。每筆 deferred 仍然 append-only：未來 substantive turn 補 deferred 時，**不修改**已存在的 entries。

### 隱私與資安

- **禁止記錄秘密**：任何 token、API key、production credential 都絕對不可寫入 `.ailog/`。`scripts/validate_repo_contract.py` 的 `FORBIDDEN_CONTENT_PATTERNS` 會掃，違反等同 contract 違規。
- 使用者貼進 prompt 的 raw 內容會被照抄到 `User request` 區塊；如果 user 在某 turn 提供了**敏感資料**（key、密碼、憑證），AI 必須在 log 中遮罩（例如用 `[REDACTED]`）並提醒 user。
- `.ailog/` 隨 commit 進 git，會被 push 到 GitHub。請不要把不該公開的內容放進對話。
- 不要把**其他專案 / 其他 session** 的內容混進來；`.ailog/` 只記錄本 repo 內的 AI 操作。

### 與 `aidlc-docs/audit.md` 的差別

| 對象 | 內容 | 粒度 |
|---|---|---|
| `aidlc-docs/audit.md` | AIDLC 階段事件（stage transitions、extension toggles、approvals、重大決策） | 粗：每個重要決策 1 筆 |
| `.ailog/<date>.md` | 每一次 AI turn 的活動紀錄 | 細：每個 turn 1 筆 |

兩者並存：audit.md 是 AIDLC workflow 的官方記錄；`.ailog/` 是底層全活動 log。當 turn 牽涉 AIDLC 決策（例如階段完成、extension 變更）時，**兩處都要寫**：細節進 `.ailog/`，摘要進 `audit.md`。

### 與 upstream AIDLC rules 的關係

upstream `awslabs/aidlc-workflows` 沒有對應規則，本規則為**純疊加**。`.aidlc-overrides/` 載入順序在 upstream 之後，故衝突時本規則勝出（目前無已知衝突）。

### Enforcement

- **AI agent**：在當前 turn 結束、回 user 訊息**之前**，先 append 該 turn 的 log entry；若已在跑 commit/push，把 commit hash / PR URL 補上。
- **PR reviewer**：review 時檢查 `.ailog/<當天>.md` 是否有對應條目，且檔案清單是否與該 PR 的 git diff 一致。
- **未來自動化**（可選，未強制）：CI 可加 step 比對「PR commits 觸碰的檔案」與「`.ailog/` 該日 entry 列出的 Files」一致性，不一致就 fail。本 override 暫不強制 CI 檢查，先以 review + AI 自律為主。

### 套用範圍

- ✅ 適用：所有 AI 在本 repo 內的對話 turn（透過 Claude Code、Cursor、其他 AI agent）。
- ✅ 適用：自動化 cron / loop 任務每次執行。
- ⏸ 不溯及：本規則建立**之前**的對話 turn 不必補登（`aidlc-docs/audit.md` 已記錄 PR1–PR3 的關鍵事件）。
- ❌ 不適用：人類直接 commit、CI 自動 commit（dependabot 等）。

---

## English Version

### Rule

After every AI turn (Claude Code or any other AI agent) that **creates / modifies / deletes a file, runs a commit/push, or opens/edits a PR** in this repository, the AI **MUST** append a turn entry to `.ailog/<YYYY-MM-DD>.md`. Exactly one entry per user-visible turn, regardless of how many tool calls run inside that turn.

### When to Log

Turns are classified by whether they produce **working-tree file changes** — `substantive` vs `pure-ops`. Pure-ops turns support deferred logging (see the Deferred Logging clause below).

| Situation | Required? | Inline vs deferred |
|---|---|---|
| **Substantive turn**: Write / Edit / NotebookEdit / `git mv` / `git rm` and similar working-tree mutations | ✅ Required | ❌ Cannot defer — append immediately on the current branch and commit |
| **Pure-ops turn**: GitHub-only mutations (`git push --delete`, `gh pr merge`, `gh pr edit`, `gh pr close`, `gh release *`, `gh issue *`) with no working-tree change | ✅ Required | ✅ MAY defer to the next substantive turn's PR (default — avoids recursive PR noise) |
| **Read-only turn**: questions, lookups, `grep`, `git log`, `gh pr view`, etc. | ⏸ Optional (recommended; skip when noisy) | — |
| **Automated tasks (cron / loop / background watcher)** | ✅ Required, one entry per run | If the watcher only mutates GitHub remote refs it counts as pure-ops and may defer |

### File Format

- Path: `.ailog/<YYYY-MM-DD>.md` (date in **local timezone**; project default is `+0800`).
- One file holds all turns of one calendar day; append-only — never reorder or delete past entries.
- Each turn entry is structured:

```markdown
## Turn N — HH:MM:SS +TZ

**User request**: <verbatim user message; mixed Chinese/English is fine>
**Branch**: <current git branch; record any switch>
**Files**:
- A <path>      ← Added
- M <path>      ← Modified
- D <path>      ← Deleted
- R <old> -> <new>  ← Renamed (git mv)
**Tool calls (selected)**: <optional; list side-effecting commands such as `gh pr create`, `git push`>
**Summary**: <1–3 sentences on what happened and why; no line-by-line walkthrough>
**Commits (if any)**: <commit hash; comma-separated for multiple>
**PRs (if any)**: <PR URL or #number>
```

- Turn numbers reset to 1 every day and increase chronologically.
- Use 24-hour time and include the timezone (e.g. `14:35:12 +0800`).

### Example

```markdown
## Turn 1 — 16:48:20 +0800

**User request**: 幫我在git增加一個folder叫做.ailog，另外加入一個規則檔...
**Branch**: danniel/feat/ai-activity-logging
**Files**:
- A `.ailog/README.md`
- A `.ailog/2026-05-09.md`
- A `.aidlc-overrides/ai-logging.md`
- M `CLAUDE.md`
- M `scripts/validate_repo_contract.py`
- M `aidlc-docs/audit.md`
**Summary**: Established the AI activity logging mechanism: created `.ailog/` daily-log folder, authored the override rule, wired it into CLAUDE.md and the repo contract.
**Commits**: cf28bfa, ...
**PRs**: opendiamonds/cloud-360#13
```

### Deferred Logging — pure-ops turns may defer

**Problem**: a pure-ops turn (e.g. `gh pr merge`, `git push --delete`) produces no file change other than the log entry itself. Strictly requiring such a turn to land its entry in a dedicated PR creates a recursive noise loop: **opening a PR just to write the log → that PR creation is another turn → which itself needs a log entry**. PR #15 / Turn 3-4 on 2026-05-09 hit this exact loop.

**Rule**:

1. A pure-ops turn's entry MAY be **deferred** and appended on the next substantive turn's PR branch — no dedicated PR is required for pure-ops alone. Deferring is the default.
2. The substantive turn, when authoring its own entry, also appends all accumulated deferred entries to `.ailog/<YYYY-MM-DD>.md` in **chronological order** ahead of its own entry; each deferred entry carries a `**Deferred from**: <original turn timestamp +TZ> (<context, e.g. watcher id>)` marker.
3. Multiple consecutive pure-ops turns may batch.
4. **No cross-day deferral**: deferred entries must land on `main` within the same calendar day (local timezone, +0800). If no substantive turn is in sight and the day is about to roll over, the AI agent **must proactively open a chore PR** to land the day's deferred entries before midnight.
5. **Substantive turns always log inline** — they cannot defer themselves.

**Quick self-check**: at the end of the current turn, is there commit-able change in the working tree?

- **Yes** → substantive turn → append the entry **immediately** to the current branch and commit.
- **No** → pure-ops turn → default to deferring (or open a small dedicated PR if you must, but it is usually unnecessary).

**Deferred entry example**:

```markdown
## Turn 7 — 09:30:15 +0800

**User request**: <the substantive turn's user message>
**Branch**: danniel/feat/cost-calc-rewrite
**Files**: <the substantive turn's own file changes …>
**Summary**: <what the substantive turn did>

> **Deferred entries appended below in chronological order:**

### Turn 5 (deferred) — 08:12:03 +0800

**Deferred from**: pure-ops turn at 2026-05-10 08:12:03 +0800 (watcher xyz123)
**Original user request**: 砍掉 stale branches
**GitHub-side mutations**:
- DEL origin/old/feature-a
- DEL origin/old/feature-b
**Tool calls**: `git push origin --delete x2`
**Summary**: Background watcher cleaned up two stale branches after PR #99 merged.

### Turn 6 (deferred) — 08:30:47 +0800

**Deferred from**: pure-ops turn at 2026-05-10 08:30:47 +0800
**Original user request**: edit PR #100 description to add a test plan
**GitHub-side mutations**: edited PR #100 body
**Tool calls**: `gh pr edit 100 --body ...`
**Summary**: Added the test plan section as requested.
```

> Deferred sub-entries use H3 (`###`) so they nest cleanly under the substantive turn's H2 (`##`). Each remains append-only: when a future substantive turn adds new deferred entries, **do not edit existing ones**.

### Privacy and Security

- **No secrets**: tokens, API keys, production credentials must never enter `.ailog/`. `scripts/validate_repo_contract.py`'s `FORBIDDEN_CONTENT_PATTERNS` will catch violations, which count as contract failures.
- Raw user prompts are copied verbatim into the `User request` block. If a user pastes **sensitive data** (a key, a password, a credential), the AI must redact it (e.g. `[REDACTED]`) in the log and warn the user.
- `.ailog/` is committed into git and pushed to GitHub. Do not paste anything you would not want public.
- Do not mix in content from **other projects or sessions**; `.ailog/` only records AI activity inside this repo.

### Difference from `aidlc-docs/audit.md`

| Target | Content | Granularity |
|---|---|---|
| `aidlc-docs/audit.md` | AIDLC stage events (transitions, extension toggles, approvals, major decisions) | Coarse: one entry per major decision |
| `.ailog/<date>.md` | Every AI turn's activity log | Fine: one entry per turn |

Both coexist: `audit.md` is the official AIDLC workflow log; `.ailog/` is the underlying full-activity log. When a turn involves an AIDLC decision (stage completion, extension change), record **in both** — the detail goes to `.ailog/`, the summary to `audit.md`.

### Relationship to Upstream AIDLC Rules

Upstream `awslabs/aidlc-workflows` has no equivalent rule; this is a **pure addition**. `.aidlc-overrides/` is loaded after upstream, so on conflict this rule wins (no known conflict today).

### Enforcement

- **AI agents**: append the turn's log entry **before** sending the final response back to the user. If commit/push has already started, fill in commit hash / PR URL.
- **PR reviewers**: during review, check that `.ailog/<that-day>.md` has the corresponding entry and that the file list matches the PR diff.
- **Future automation (optional, not enforced)**: CI may add a step that compares the files touched by a PR's commits against the `Files` list in the `.ailog/` entry for that day; mismatches would fail the build. Not enforced yet — review + AI self-discipline first.

### Scope

- ✅ Applies to every AI turn in this repo (Claude Code, Cursor, other AI agents).
- ✅ Applies to automated cron / loop runs (one entry per run).
- ⏸ Not retroactive: turns **before** this rule was introduced are not back-filled (`aidlc-docs/audit.md` already records the key events for PR1–PR3).
- ❌ Does not apply to direct human commits or automated CI commits (dependabot, etc.).
