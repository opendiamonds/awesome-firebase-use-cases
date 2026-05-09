# AI Activity Logging Rule

> Project override rule. Mandates that every AI turn touching the repository is logged in `.ailog/`.
> 專案 override 規則。每一次 AI 動到本 repo 的對話 turn 都必須在 `.ailog/` 留下紀錄。

## 中文版

### 規範

每一次 AI（Claude Code 與其他 AI agent）在本 repo 內**生成檔案、修改檔案、刪除檔案、執行 commit/push、開 PR**等任一動作後，**必須**在 `.ailog/<YYYY-MM-DD>.md` 追加一筆 turn entry。同一個 user 對話 turn 只寫一筆，無論該 turn 跑了多少 tool call。

### 何時寫 log

| 情境 | 是否必寫 |
|---|---|
| AI 用 Write / Edit / NotebookEdit 建檔或改檔 | ✅ 必寫 |
| AI 用 Bash 執行 `git mv`、`git rm`、`mkdir`、`rm` 等修改 working tree 的指令 | ✅ 必寫 |
| AI 執行 `git commit` / `git push` | ✅ 必寫 |
| AI 用 `gh pr create` / `gh pr edit` / `gh pr merge` 等動到 GitHub 狀態 | ✅ 必寫 |
| AI 純粹回答問題、查資料、跑 read-only `grep` / `git log` 沒動檔案 | ⏸ 可選（建議寫，量大時可省） |
| 自動化 / 排程任務（scheduled cron job、loop） | ✅ 必寫，每跑一次寫一筆 |

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

| Situation | Required? |
|---|---|
| AI uses Write / Edit / NotebookEdit to create or change files | ✅ Required |
| AI uses Bash to run mutating commands such as `git mv`, `git rm`, `mkdir`, `rm` | ✅ Required |
| AI runs `git commit` / `git push` | ✅ Required |
| AI runs `gh pr create` / `gh pr edit` / `gh pr merge` or anything that mutates GitHub | ✅ Required |
| AI only answers questions / queries data / runs read-only `grep` / `git log` without touching files | ⏸ Optional (recommended; may skip when noisy) |
| Automated / scheduled tasks (cron, loop) | ✅ Required, one entry per run |

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
