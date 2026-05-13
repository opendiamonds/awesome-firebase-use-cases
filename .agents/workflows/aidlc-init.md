---
description: 初始化 AIDLC 生命週期
---

請重新載入所有規則與系統規範。

初始化 AIDLC 生命週期。

請依照下列順序執行：

## 規則載入

### 步驟 1：載入 AIDLC 入口
載入：
`.aidlc-rules/aws-aidlc-rules/core-workflow.md`

### 步驟 2：載入 upstream 規則細節
依序載入 `.aidlc-rule-details/` 下的規範：
- `.aidlc-rule-details/common/process-overview.md`
- `.aidlc-rule-details/common/session-continuity.md`
- `.aidlc-rule-details/common/content-validation.md`
- `.aidlc-rule-details/common/question-format-guide.md`
- 掃描 `.aidlc-rule-details/extensions/`，僅載入 `*.opt-in.md`
- 無 opt-in 檔的 extension（如 `bilingual-docs/`）直接載入完整規則

### 步驟 3：載入 Cloud-360 專屬 override（最後載入，優先權最高）
依序載入以下 `.aidlc-overrides/` 檔案：
- `.aidlc-overrides/branch-naming.md`（Cloud-360 分支命名規則）
- `.aidlc-overrides/decisions-log.md`（決議記錄規則：僅在使用者明確要求時觸發）

當 override 與 upstream 規則衝突時，**override 永遠勝出**。

### 步驟 4：顯示歡迎訊息
顯示：
`.aidlc-rule-details/common/welcome-message.md`

---

## 初始化流程

5. 檢查：
`aidlc-docs/audit.md`
與
`aidlc-docs/aidlc-state.md`

是否存在。

6. 若不存在則建立。

7. 在 `aidlc-docs/audit.md` 新增初始化紀錄。

8. 分析目前 workspace：
- 是否為 brownfield
- 現有技術架構
- 現有 modules
- frontend/backend/workflows structure

9. 從現在開始：
- 所有回應必須使用繁體中文
- 所有規劃必須遵守 AI-DLC
- 所有 code generation 前必須先產生 plan
- 所有 architecture 必須可轉換為 draw.io XML