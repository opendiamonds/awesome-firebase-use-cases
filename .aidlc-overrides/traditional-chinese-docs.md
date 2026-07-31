# Cloud-360 文件語言：繁體中文

> 專案 override 規則。與 upstream 任何衝突指示相比，本規則優先。

### 規範

本專案的所有 AIDLC 文件產出**一律使用繁體中文**，取代原本的雙語（`extensions/bilingual-docs/` 與 ADR-0005）強制。詳見 ADR-0009。

1. `aidlc-docs/**/*.md`、`CLAUDE.md`、`.aidlc-overrides/**/*.md` 一律以繁體中文撰寫。
2. **不得**保留或新增 `## 中文版` / `## English Version` 的雙語分段；文件為單一語言（繁中）。
3. `scripts/validate_repo_contract.py` 會擋下任何殘留的 `## English Version` 標題（CI 紅燈）。
4. 例外：程式碼、指令、識別字、專有名詞維持原文；upstream `.aidlc/aidlc-rules/aws-aidlc-rule-details/` 內的英文規則檔不在此限（那是給 AI 讀的指令，非本專案 artifacts）。

### 對 AI agent 的指示

- 產出任何 AIDLC 文件時只寫繁體中文，不再產生英文版分段。
- 修改既有文件時，若見殘留英文版一併清除。
