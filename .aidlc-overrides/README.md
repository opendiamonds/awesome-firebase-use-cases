# Cloud-360 AIDLC Overrides

> Project-specific rules that **layer on top of** upstream AIDLC rules in `.aidlc-rule-details/`.
> 在 upstream AIDLC rules 之上**疊加**的專案規則層。

## 中文版

### 目的

本目錄存放 Cloud-360 專屬的 AIDLC override 規則。Upstream（`awslabs/aidlc-workflows`）發版時 `.aidlc-rule-details/` 會被整批替換，但 `.aidlc-overrides/` 永遠由本專案維護、永不被 upstream 覆蓋。

### 載入順序與優先權

CLAUDE.md 指示 Claude Code（與其他 AI agent）依下列順序載入規則：

1. `.aidlc-rules/aws-aidlc-rules/core-workflow.md`（AIDLC 入口）
2. `.aidlc-rule-details/common/`、`.aidlc-rule-details/inception|construction|operations/`、enabled extensions（upstream 規則）
3. **最後**載入 `.aidlc-overrides/**/*.md`（本目錄）

當 upstream 規則與 override 規則衝突時，**override 永遠勝出**。

### 現有 overrides

| 檔案 | 規範 | 對應 upstream |
|---|---|---|
| `branch-naming.md` | Cloud-360 git branch 命名規範 | upstream 無此規則，純疊加 |
| `decisions-log.md` | 使用者明確要求時，把對話決議記錄到 `aidlc-docs/decisions-log.md` | upstream 無此規則，純疊加（取代 PR #17 移除的 `ai-logging.md`） |

### 撰寫新 override 的原則

1. **不修改 `.aidlc-rule-details/`**：upstream 規則保持原狀，便於同步新版本。
2. **bilingual**：每個 override 檔必須包含 `## 中文版` 與 `## English Version`，對齊 ADR-0005。
3. **明確標示覆蓋對象**：若 override 是為了改寫 upstream 某條規則，要在檔案內明確說明覆蓋的 upstream 路徑與條目。
4. **記錄到 audit.md**：新增、移除或修改 override 時，附 audit log entry。

---

## English Version

### Purpose

This directory holds Cloud-360-specific AIDLC override rules. When upstream `awslabs/aidlc-workflows` cuts a new release, `.aidlc-rule-details/` is replaced wholesale; `.aidlc-overrides/` is owned by this project and is never overwritten by upstream.

### Loading Order and Precedence

`CLAUDE.md` instructs Claude Code (and other AI agents) to load rules in this order:

1. `.aidlc-rules/aws-aidlc-rules/core-workflow.md` (AIDLC entry)
2. `.aidlc-rule-details/common/`, `.aidlc-rule-details/inception|construction|operations/`, and enabled extensions (upstream rules)
3. **Finally**, load `.aidlc-overrides/**/*.md` (this directory)

When an upstream rule conflicts with an override, **the override always wins**.

### Current Overrides

| File | Rule | Corresponding Upstream |
|---|---|---|
| `branch-naming.md` | Cloud-360 git branch naming convention | No upstream equivalent — pure addition |
| `decisions-log.md` | On explicit user request, capture the conversation's decision into `aidlc-docs/decisions-log.md` | No upstream equivalent — pure addition (replaces the `ai-logging.md` removed in PR #17) |

### Authoring New Overrides

1. **Never modify `.aidlc-rule-details/`**: keep upstream rules untouched so future syncs stay clean.
2. **Bilingual**: every override file must include `## 中文版` and `## English Version`, aligning with ADR-0005.
3. **State the override target clearly**: if an override is meant to replace a specific upstream rule, name the upstream path and clause it overrides.
4. **Log it in audit.md**: add an audit entry whenever an override is added, removed, or modified.
