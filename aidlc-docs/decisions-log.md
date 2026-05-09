# Project Decisions Log

> Important project decisions captured on explicit user request. Rule: [`.aidlc-overrides/decisions-log.md`](../.aidlc-overrides/decisions-log.md).
> 在使用者明確要求時記錄的專案重要決議。規則見 [`.aidlc-overrides/decisions-log.md`](../.aidlc-overrides/decisions-log.md)。

## 中文版

### 紀錄

#### 2026-05-09 23:29:39 +0800 — 換掉 ai-logging，改用 on-demand decisions-log

**Decision / 決議**: 移除 per-turn 強制 log 機制（`.ailog/` 與 `.aidlc-overrides/ai-logging.md`），改為**僅在使用者明確要求時記錄**的 `aidlc-docs/decisions-log.md`。重點從「逐 turn 操作」轉為「重要決議」，大幅降低 log 雜訊與 PR 遞迴噪音。
**Context / 背景**: ai-logging 機制（PR4 引入、PR #16 加 deferred-logging clause）強制每個 turn append entry，pure-ops turn 還會引發單一 PR 遞迴；實際使用後發現絕大多數 turn 細節不值得記，需要被保留的是「重要決議」而非「每個 keystroke」。
**Trigger / 觸發語**: 「幫我將ai-logging 規則移除，新增一個專案重要決議記錄，當使用這要求時，就記錄當下與AI對話的決議」
**Related / 相關**:
- PR #17（本 PR；branch `danniel/feat/decisions-log-rule`）
- Supersedes PR4（`.ailog/` 與 ai-logging.md 引入）與 PR #16（deferred-logging clause）
- 舊 `.ailog/2026-05-09.md` Turn 1–4 內容保留在 git 歷史（PR4 / PR #14 / PR #15 commits）

---

## English Version

### Records

#### 2026-05-09 23:29:39 +0800 — Replace ai-logging with on-demand decisions-log

**Decision**: Remove the per-turn forced-logging mechanism (`.ailog/` directory and `.aidlc-overrides/ai-logging.md`) and replace it with `aidlc-docs/decisions-log.md`, which is **only written when the user explicitly asks**. The focus shifts from "every turn's actions" to "important decisions", dramatically reducing log noise and the recursive PR churn that pure-ops turns produced.
**Context**: The ai-logging mechanism (introduced in PR4, extended with the deferred-logging clause in PR #16) required an entry every turn; pure-ops turns even triggered single-file PR recursion. In practice the per-turn details aren't worth keeping — what deserves preservation is **important decisions**, not every keystroke.
**Trigger**: "幫我將ai-logging 規則移除，新增一個專案重要決議記錄，當使用這要求時，就記錄當下與AI對話的決議"
**Related**:
- PR #17 (this PR; branch `danniel/feat/decisions-log-rule`)
- Supersedes PR4 (introduced `.ailog/` and ai-logging.md) and PR #16 (added the deferred-logging clause)
- The old `.ailog/2026-05-09.md` Turn 1–4 entries are preserved in git history via the PR4 / PR #14 / PR #15 commits.
