---
description: AI-DLC Construction workflow for implementation and code generation.
---

現在進入 Construction Phase。

請調用 `aidlc/spaces/<active-space>/memory/phases/construction.md` 的階段護欄，以及 `team.md` / `project.md` 的專案規則。實際啟用的 stage 集合以 `/aidlc --doctor` 或編譯後的 `.claude/tools/data/stage-graph.json` 為準。

> 注意：本專案的 Construction 與 Operations 是**連續**的，不是依序交棒（ADR-0008，見 `project.md` 的 `## Deployment`）。部署、回滾、觀測與 code 實作屬同一條 pipeline。

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
- 若異動 DB schema 或部署必知的 seed 行為，同步更新 `schema_rbac.sql` 與 `DEPLOY.md`（blocking，見 `project.md` 的 `## Mandated`）

所有產出：
- 使用繁體中文
- code/變數/API 保持英文
