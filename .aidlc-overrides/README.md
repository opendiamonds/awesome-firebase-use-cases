# Cloud-360 AIDLC Overrides

> Project-specific rules that **layer on top of** upstream AIDLC rules in `.aidlc-rule-details/`.
> 在 upstream AIDLC rules 之上**疊加**的專案規則層。

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
| `continuous-delivery.md` | 以連續 DevOps 迴圈取代「Construction → Operations 線性交棒」 | 覆蓋 upstream 三段式的線性假設（見 ADR-0008） |
| `traditional-chinese-docs.md` | 文件語言一律繁體中文，取代雙語強制 | 覆蓋 `extensions/bilingual-docs/`（見 ADR-0009） |
| `commit-message.md` | Commit message 與 PR 標題一律繁體中文，type 中文化 | upstream 無此規則，純疊加（見 ADR-0010） |

### 撰寫新 override 的原則

1. **不修改 `.aidlc-rule-details/`**：upstream 規則保持原狀，便於同步新版本。
2. **繁體中文**：每個 override 檔一律繁體中文（見 ADR-0009）。
3. **明確標示覆蓋對象**：若 override 是為了改寫 upstream 某條規則，要在檔案內明確說明覆蓋的 upstream 路徑與條目。
4. **記錄到 audit.md**：新增、移除或修改 override 時，附 audit log entry。
