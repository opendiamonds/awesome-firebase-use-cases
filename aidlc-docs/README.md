# aidlc-docs/

> AIDLC workflow artifacts root. Generated and maintained by AIDLC stages.
> AIDLC 工作流程產出根目錄。由 AIDLC 各階段自動產生與維護。

此目錄是 [awslabs/aidlc-workflows](https://github.com/awslabs/aidlc-workflows) 規範的 AI-DLC artifacts 輸出位置。

### 結構

- `aidlc-state.md` — 專案 phase / extension 狀態追蹤
- `audit.md` — append-only 稽核紀錄
- `inception/` — 🔵 Inception phase artifacts
  - `requirements/cloud-360-srs.md` — 需求分析輸出（SRS）
  - `user-stories/core-pillars.md` — user stories
  - `application-design/system-architecture.md` — 應用層設計
  - `decisions/0001..0006-*.md` — 架構決策（ADRs）
  - `plans/` — workflow planning 輸出（待 AIDLC stage 產生）
- `construction/` — 🟢 Construction phase artifacts（NFR、functional design、build-and-test、code generation 結果）
- `operations/` — 🟡 Operations phase artifacts（部署、監控、incident playbooks）

### 文件語言

每份 `aidlc-docs/**/*.md` 一律繁體中文（見 ADR-0009），由 `scripts/validate_repo_contract.py` 擋下殘留的英文版段落。

### Extension 啟用狀態

見 `aidlc-state.md` 的 **Extension Configuration** 區塊。
