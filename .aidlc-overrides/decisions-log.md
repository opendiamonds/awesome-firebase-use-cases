# Project Decisions Log Rule

> Project override rule. On explicit user request, capture the current AI conversation's decision into `aidlc-docs/decisions-log.md`.
> 專案 override 規則。當使用者明確要求時，把當下與 AI 對話達成的決議記錄到 `aidlc-docs/decisions-log.md`。

### 規範

當使用者**明確要求**記錄當下對話的決議時，AI 必須把該決議追加到 `aidlc-docs/decisions-log.md`，並 commit + push（含此檔變動的 PR）。

**典型觸發語句（不限於這些；中英文皆可）**：

- 「記錄這個決議」
- 「把這個決定記下來」
- 「存成決議」
- 「寫進決議紀錄」
- 「log this decision」
- 「record this as a decision」
- 「save this to the decision log」

AI 應以**判斷**而非死記字串：使用者只要明確表達「想把剛剛的決定留下紀錄」，就觸發此規則。如果不確定，先反問確認再寫。

### 何時 NOT 觸發（避免誤寫）

- ❌ 使用者沒有明確要求記錄 → 不要自動寫
- ❌ AIDLC 階段事件（stage transition、extension toggle、approvals）→ 寫 `aidlc-docs/audit.md`，不寫此檔
- ❌ 架構級決策（影響系統結構、需要 review trail、多人會審）→ 開 ADR `aidlc-docs/inception/decisions/NNNN-*.md`
- ❌ Code review 對話、需求釐清、純粹詢問 → 不寫
- ❌ 使用者只是回應或閒聊 → 不寫

### 檔案格式

- 路徑：`aidlc-docs/decisions-log.md`（單檔，append-only）
- **繁體中文**（per ADR-0009）：整檔繁體中文；新 entry 直接以繁中追加
- 每筆 entry 結構（H3）：

```markdown
### YYYY-MM-DD HH:MM:SS +TZ — <短標題（5–10 字）>

**Decision / 決議**: <1–3 句獨立可懂的決議內容>
**Context / 背景**: <為何有這個決議；簡短背景，不需要逐句重述對話>
**Trigger / 觸發語**: <使用者要求記錄時的原文>
**Related / 相關**: <PR、ADR、branch、commit、issue 連結；無則寫 N/A>
```

### Self-check

當 user 觸發後，AI 應：

1. 從對話中萃取**剛剛達成的決議**（不是上下文閒聊，是實際做出的決定）。
2. 短標題用 5–10 字概述決策本身，避免「使用者問 X」這種敘述。
3. Decision 區塊寫成獨立可懂的句子，不依賴對話上下文。
4. Append 後依當前情境提交：
   - 若這個 turn 還有其他檔案變動 → 跟其他變動一起包進同一個 PR
   - 若這個 turn 只是寫 decisions-log → 開單檔 chore PR（branch type 用 `chore` 或 `docs`）

### 與其他 log 的差別

| 對象 | 路徑 | 何時寫 |
|---|---|---|
| AIDLC 階段事件 | `aidlc-docs/audit.md` | AIDLC stage 完成、extension 變更、approvals 等情境自動寫 |
| 架構決策 (ADR) | `aidlc-docs/inception/decisions/NNNN-*.md` | 重大架構決策，per-PR 一份 ADR |
| 一般專案決議 | `aidlc-docs/decisions-log.md`（本檔） | **僅在 user 明確要求時** |

### 與 upstream AIDLC rules 的關係

upstream `awslabs/aidlc-workflows` 沒有對應規則，本規則為**純疊加**，無覆蓋對象。`.aidlc-overrides/` 載入順序在 upstream 之後，故衝突時本規則勝出（目前無已知衝突）。

### 隱私與資安

同 repo contract：禁止寫入 token、API key、production credentials。若使用者在請求中提供敏感資料，AI 須遮罩（例如 `[REDACTED]`）並提醒使用者；`scripts/validate_repo_contract.py` 的 `FORBIDDEN_CONTENT_PATTERNS` 會掃此檔。

### 與舊 ai-logging 機制的關係

本規則**取代**已移除的 `.aidlc-overrides/ai-logging.md`（per-turn 強制 log 機制）。舊機制每個 turn 都得寫，pure-ops turn 還引發 PR 遞迴噪音；新機制僅在 user 主動要求時記錄重要決議，雜訊大幅降低。舊 `.ailog/` 內容在 git 歷史中保留（PR4 起），不會被搬到 `aidlc-docs/decisions-log.md`。
