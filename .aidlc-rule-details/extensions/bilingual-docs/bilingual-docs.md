# Bilingual Documentation — Cloud-360 Custom Extension

**Extension**: Bilingual Documentation
**Status**: Always enforced (no opt-in file — see core-workflow.md "Extensions Loading")
**Source of truth**: `aidlc-docs/inception/decisions/0005-bilingual-documentation.md`

## 中文版

Cloud-360 所有 markdown 文件（`aidlc-docs/**/*.md`、ADR、SRS、user stories、application/functional design、build-and-test plans、operations runbooks）必須**同時包含中文版與英文版**，這是 hard constraint。

### 強制規則

1. 每個 `aidlc-docs/**/*.md` 文件必須同時包含 `## 中文版` 與 `## English Version` 兩個 H2 標題。
2. AIDLC 任一階段（inception / construction / operations）產生的 artifacts 都必須遵守同一規則。
3. 若 AIDLC 產生英文 artifact，必須在同一個檔案內補上對應的 `## 中文版` 段落（不得放在另一個檔案）。
4. 雙語內容須語意對等，不得只在中文版加入未經英文版同步的設計決策、需求或假設。
5. 違反此規則即為 **blocking finding**：在 stage completion summary 中標示為 non-compliant，且不得進入下一階段。

### 套用時機（applicable stages）

- Inception：requirements、user-stories、application-design、decisions、plans
- Construction：nfr-requirements、functional-design、build-and-test、code-generation 產出的 README / 設計文件
- Operations：runbooks、deployment guides、incident playbooks

### 不適用情境（mark as N/A）

- 純程式碼檔案（`.py`、`.ts`、`.tf` 等）—— 但其中的 docstring 與 user-facing 訊息仍應考量雙語。
- 機器可讀設定檔（`.json`、`.yaml`、`.toml`）。
- `aidlc-state.md`、`audit.md` 等 AIDLC 內部追蹤檔（建議仍加雙語但非強制）。

### 合規檢查

執行 `python scripts/validate_repo_contract.py`，會掃描所有 `aidlc-docs/**/*.md`，確認每份都包含 `## 中文版` 與 `## English Version`。

---

## English Version

All Cloud-360 markdown documentation (`aidlc-docs/**/*.md`, ADRs, SRS, user stories, application/functional design, build-and-test plans, operations runbooks) **MUST contain both a Chinese version and an English version**. This is a hard constraint.

### Hard Rules

1. Every `aidlc-docs/**/*.md` file must include both `## 中文版` and `## English Version` H2 headings.
2. Artifacts produced at any AIDLC phase (inception / construction / operations) must comply.
3. When AIDLC produces an English artifact, the corresponding `## 中文版` section must be added to the same file (not a separate file).
4. The two languages must be semantically equivalent. Do not introduce design decisions, requirements, or assumptions in one language without syncing them to the other.
5. Non-compliance is a **blocking finding**: mark it as non-compliant in the stage-completion summary and do not advance to the next stage until resolved.

### Applicable Stages

- Inception: requirements, user-stories, application-design, decisions, plans
- Construction: nfr-requirements, functional-design, build-and-test, READMEs / design docs produced by code-generation
- Operations: runbooks, deployment guides, incident playbooks

### Not-Applicable Contexts (mark as N/A)

- Pure source files (`.py`, `.ts`, `.tf`, …) — though docstrings and user-facing strings should still consider bilingual coverage.
- Machine-readable config (`.json`, `.yaml`, `.toml`).
- AIDLC-internal tracking files such as `aidlc-state.md` and `audit.md` (bilingual is recommended but not required).

### Compliance Check

Run `python scripts/validate_repo_contract.py`. The script scans every `aidlc-docs/**/*.md` file and verifies that each contains both `## 中文版` and `## English Version`.
