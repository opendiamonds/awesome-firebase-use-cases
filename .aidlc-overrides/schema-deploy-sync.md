# Cloud-360 Schema & Deploy Sync

> Project override rule. Takes precedence over any conflicting upstream guidance.
> 專案 override 規則。與 upstream 任何衝突指示相比，本規則優先。

## 中文版

### 目的

每當功能異動**資料庫結構或部署必知的 schema／seed 行為**時，必須同步更新可攜部署腳本與部署說明，避免新環境漏表、漏欄位或文件與實際不符。

### 觸發條件（任一即適用）

| 類型 | 範例 |
|---|---|
| 新增／刪除／更名表 | `CREATE TABLE`、`DROP TABLE`、`RENAME` |
| 新增／刪除／更名／改型欄位 | `ALTER TABLE … ADD/DROP/ALTER COLUMN` |
| 索引／唯一約束／外鍵變更 | `CREATE INDEX`、`FOREIGN KEY` |
| Seed／預設資料語意變更 | `role_permissions` 矩陣、預設帳號、必要初始列 |
| ORM／啟動補丁引入新 DDL | `models.py`、`database.py` 的 `_ensure_*_schema` |

**不觸發**（僅資料內容／應用層 JSON，無 DDL）：例如只改 `scores_json`／`findings_json` 內的 JSON 形狀、純應用邏輯、與 schema 無關的設定。

### 強制動作（blocking）

在宣告該功能的 Code Gen／PR／階段完成**之前**，必須完成：

1. **`schema_rbac.sql`（repo 根目錄）**  
   - 把對應 DDL（與必要 COMMENT）寫進適當區塊（例：A／B／E／C／D）。  
   - 使用 `IF NOT EXISTS`／可重跑安全寫法（與既有腳本風格一致）。  
   - 更新檔頭「單一腳本涵蓋」清單與驗證註解（若新增表／物件）。  
   - 若僅改 seed：更新對應 `INSERT`／說明，並標註重跑會覆寫的風險。

2. **`DEPLOY.md`（repo 根目錄）**  
   - 更新「這支 SQL 會建立的表／欄位」表。  
   - 新表／重要欄位補簡短說明與（建議）驗證 `psql` 指令。  
   - 英文版（`## English Version`）同步語意對等更新。  
   - 若影響既有環境升級：寫明「重跑 `schema_rbac.sql`」或與後端 `_ensure_*_schema` 的關係。

### 建議一併更新（非 blocking，但強烈建議）

| 檔案 | 何時 |
|---|---|
| `schema.sql` | 核心／精簡 DDL 參考需與 `schema_rbac.sql` 對齊時 |
| `aidlc-docs/construction/plans/schema-rbac-notes.md` | 區塊清單 A／B／E／C／D 有增減時 |
| `aidlc-docs/audit.md` | AIDLC 階段事件（依既有 audit 習慣） |

### Agent／開發者檢查清單

- [ ] 本次變更是否觸發上表「觸發條件」？  
- [ ] `schema_rbac.sql` 已含同等 DDL／seed？  
- [ ] `DEPLOY.md` 中／英已更新？  
- [ ] 既有環境升級路徑已說明？  
- [ ] （建議）`schema.sql`／`schema-rbac-notes.md` 已對齊？

未完成第 1、2 項 → **不得**標示該 Construction／部署相關階段為完成。

### 與 upstream 的關係

Upstream AIDLC **無**對等規則；本檔為純疊加。不修改 `.aidlc/aidlc-rules/aws-aidlc-rule-details/`。

---

## English Version

### Purpose

Whenever a feature changes the **database schema** or **deploy-critical schema/seed behavior**, you **must** update the portable SQL script and deploy docs so new environments do not miss tables/columns and docs stay accurate.

### Triggers (any one applies)

| Kind | Examples |
|---|---|
| Add/drop/rename tables | `CREATE` / `DROP` / `RENAME` |
| Add/drop/rename/alter columns | `ALTER TABLE …` |
| Index / unique / FK changes | `CREATE INDEX`, foreign keys |
| Seed / default-data semantics | `role_permissions` matrix, default admin, required seed rows |
| ORM / startup DDL patches | `models.py`, `database._ensure_*_schema` |

**Does not trigger**: application-only JSON shape changes inside existing TEXT columns (e.g. `scores_json` / `findings_json` content) with **no** DDL.

### Mandatory actions (blocking)

Before marking Code Gen / PR / stage complete:

1. **`schema_rbac.sql` (repo root)** — add matching DDL (and COMMENTs) in the right section; keep rerunnable `IF NOT EXISTS` style; update the header inventory and verification comments when adding objects; document seed overwrite risks if reseeding.
2. **`DEPLOY.md` (repo root)** — update the tables/columns inventory; document new tables/important columns and suggested `psql` checks; keep `## English Version` semantically equivalent; describe upgrade path for existing DBs (`schema_rbac.sql` rerun and/or backend `_ensure_*_schema`).

### Strongly recommended (non-blocking)

- `schema.sql` when the slim core DDL reference should stay aligned  
- `aidlc-docs/construction/plans/schema-rbac-notes.md` when section inventory changes  
- `aidlc-docs/audit.md` for AIDLC stage events  

### Checklist

- [ ] Trigger applies?  
- [ ] `schema_rbac.sql` updated?  
- [ ] `DEPLOY.md` ZH+EN updated?  
- [ ] Existing-env upgrade noted?  
- [ ] (Recommended) `schema.sql` / `schema-rbac-notes.md` aligned?  

Skipping items 1–2 is a **blocking** finding for related Construction/deploy completion.

### Upstream relationship

No upstream equivalent — pure addition. Do not edit `.aidlc/aidlc-rules/aws-aidlc-rule-details/`.
