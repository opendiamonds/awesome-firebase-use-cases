# `.ailog/` — AI Activity Log

> Append-only per-turn activity log produced by AI agents working in this repository.
> AI agent 在本 repo 動到檔案時逐 turn 留下的 append-only 活動紀錄。

## 中文版

### 目的

`.ailog/` 是 Cloud-360 的 AI 操作底層紀錄。每一次 AI（Claude Code 與其他 AI agent）建檔、改檔、刪檔、commit / push 或開 PR，都會在此目錄當天的 markdown 檔追加一筆 turn entry。

詳細規則由 [`.aidlc-overrides/ai-logging.md`](../.aidlc-overrides/ai-logging.md) 訂定。

### 結構

- `<YYYY-MM-DD>.md` — 當天所有 turn 的累積，append-only。
- 每天一份檔案；第一筆 turn N=1，依時間順序往下加。

```text
.ailog/
├── README.md        ← 本檔（雙語說明）
├── 2026-05-09.md
├── 2026-05-10.md
└── ...
```

### 與 `aidlc-docs/audit.md` 的關係

- `aidlc-docs/audit.md` = AIDLC 階段官方稽核（粗粒度，每個重大決策 1 筆）。
- `.ailog/` = 全活動底層 log（細粒度，每個 turn 1 筆）。
- 兩者並存：當 turn 牽涉 AIDLC 階段事件時，兩處同時寫，`.ailog/` 寫細節，`audit.md` 寫摘要。

### 重要原則

1. **Append-only**：禁止重排、刪減、編輯歷史條目。發現紀錄錯誤時，加新條目修正，原條目保留。
2. **不寫秘密**：token / API key / production credential 一律不可進 `.ailog/`，`scripts/validate_repo_contract.py` 會掃。
3. **隨 commit 進 git**：每個 PR 對應的 turn entry 應與該 PR 的 commits 一起進 git。
4. **不溯及**：本機制建立前的 AI 活動不必補登；早期事件已記錄在 `aidlc-docs/audit.md`。
5. **語言**：log entry 不強制雙語（操作 log 偏機讀），但 README 與 override rule 雙語。

---

## English Version

### Purpose

`.ailog/` is Cloud-360's underlying log of AI activity. Whenever an AI (Claude Code or any other AI agent) creates / modifies / deletes a file, runs a commit/push, or opens a PR, it appends a turn entry to that day's markdown file in this directory.

The full rule is defined in [`.aidlc-overrides/ai-logging.md`](../.aidlc-overrides/ai-logging.md).

### Structure

- `<YYYY-MM-DD>.md` — accumulates every turn for that day, append-only.
- One file per day; the first turn is `N=1`, subsequent entries follow chronologically.

```text
.ailog/
├── README.md        ← this file (bilingual)
├── 2026-05-09.md
├── 2026-05-10.md
└── ...
```

### Relationship to `aidlc-docs/audit.md`

- `aidlc-docs/audit.md` = AIDLC stage audit log (coarse — one entry per major decision).
- `.ailog/` = full underlying activity log (fine — one entry per turn).
- They coexist: when a turn touches an AIDLC stage event, write to both — the detail goes to `.ailog/`, the summary to `audit.md`.

### Key Principles

1. **Append-only**: do not reorder, delete, or edit past entries. If you find a mistake, add a new entry that corrects it; keep the original.
2. **No secrets**: tokens / API keys / production credentials must never enter `.ailog/`. `scripts/validate_repo_contract.py` will catch violations.
3. **Committed with git**: turn entries belonging to a PR should be committed alongside that PR's commits.
4. **Not retroactive**: AI activity before this mechanism was introduced is not back-filled; earlier events are already in `aidlc-docs/audit.md`.
5. **Language**: log entries are not required to be bilingual (machine-readable operational log), but the README and the override rule are bilingual.
