---
description: AI-DLC Construction workflow for implementation and code generation.
---

現在進入 Construction Phase。

請調用：

`.aidlc-rule-details/construction/`

下的所有規範。

請依照 AI-DLC Construction Phase 執行：

1. Functional Design
2. NFR Requirements
3. NFR Design
4. Infrastructure Design
5. Code Generation

請先生成：

Code Generation Plan

要求：

- 必須包含 checkbox step list
- 必須包含 implementation steps
- 必須包含 affected files
- 必須包含 test strategy
- 必須包含 risk analysis
- 必須包含 rollback consideration

在獲得確認前：

禁止直接修改 code。

確認後再開始：

- 生成 code
- 更新 tests
- 更新文件
- 更新 audit.md

所有產出：
- 使用繁體中文
- code/變數/API 保持英文