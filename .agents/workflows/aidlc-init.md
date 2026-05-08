---
description: 初始化 AIDLC 生命週期
---

請重新載入所有規則與系統規範。

初始化 AIDLC 生命週期。

請執行以下流程：

1. 根據：
.agents/system-instructions/core-workflow.md

執行 Workspace Detection。

2. 載入：
.agents/system-instructions/cloud360-rules.md

作為專案規範。

3. 載入：
.agents/knowledge/aidlc-specs/

下所有 AI-DLC 規範。

4. 顯示：
common/welcome-message.md

5. 檢查：
aidlc-docs/audit.md
與
aidlc-docs/aidlc-state.md

是否存在。

6. 若不存在則建立。

7. 在：
aidlc-docs/audit.md

新增初始化紀錄。

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