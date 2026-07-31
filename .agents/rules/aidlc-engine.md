---
trigger: always_on
---

# Cloud-360 AI Agent Protocol

## 語言
ALWAYS communicate, generate documentation, and write logs in TRADITIONAL CHINESE (繁體中文).

## AIDLC Framework Entry Point
此專案採用 [awslabs/aidlc-workflows](https://github.com/awslabs/aidlc-workflows) AIDLC 框架。

**Rule loading 順序**（與 `.cursor/rules/ai-dlc.mdc`、`CLAUDE.md` 一致）：
1. 載入 `.aidlc/aidlc-rules/aws-aidlc-rules/core-workflow.md`（總入口）
2. 依 core-workflow.md 指示，從 `.aidlc/aidlc-rules/aws-aidlc-rule-details/` 載入 common 規則
3. 掃描 `.aidlc/aidlc-rules/aws-aidlc-rule-details/extensions/`，僅載入 `*.opt-in.md`
4. **最後**載入 `.aidlc-overrides/**/*.md`（Cloud-360 專屬覆寫層）

詳見 `CLAUDE.md` 完整說明。

## Knowledge Base
- AIDLC 規則細節：`.aidlc/aidlc-rules/aws-aidlc-rule-details/`
- AIDLC 版本：`.aidlc/aidlc-rules/VERSION`
- Cloud-360 專屬規則：`.aidlc-overrides/`
- AIDLC 產出文件：`aidlc-docs/`（state、audit、inception、construction、operations 子目錄）

## Audit Compliance
Every AIDLC stage action must be logged in `aidlc-docs/audit.md` per the protocol.
Project decisions (on explicit user request only) go to `aidlc-docs/decisions-log.md`.

## Source of Truth
Treat all local files in `.aidlc/aidlc-rules/`, `.aidlc-overrides/` as the immutable source of truth for AIDLC rules in this repository.
