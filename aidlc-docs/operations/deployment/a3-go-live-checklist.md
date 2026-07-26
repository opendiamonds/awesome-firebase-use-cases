# A3 Well-Architected — 上線檢查清單

> Unit `U-A3` · 輕量 Operations 文件（非正式完整 Ops 階段）  
> 詳部署：[`DEPLOY.md`](../../../DEPLOY.md) · 程式摘要：[`lens-editor-summary.md`](../../construction/a3/code/lens-editor-summary.md)、[`well-architected-review-summary.md`](../../construction/a3/code/well-architected-review-summary.md)

## 中文版

### 0. 上線前前提

- [ ] 目標環境已有 PostgreSQL，且 `DATABASE_URL`／JWT／CORS／OpenRouter（或等價 LLM）已設定（見 `backend/.env.example`）
- [ ] Frontend `VITE_API_BASE_URL` 指向該環境 API（改完需 rebuild）
- [ ] 後端／前端映像或 process 含本分支 A3 程式（reviews、PDF、Lens 編輯、`wa_lenses`）

### 1. 資料庫

- [ ] 執行（或確認已執行）repo 根目錄：

```bash
psql "$DATABASE_URL" -f schema_rbac.sql
# 或：docker exec -i <db> psql -U postgres -d cloud360 < schema_rbac.sql
```

- [ ] 驗證表存在：

```bash
psql "$DATABASE_URL" -c "\d architecture_reviews"
psql "$DATABASE_URL" -c "\d wa_lenses"
psql "$DATABASE_URL" -c "SELECT count(*) FROM role_permissions;"   -- 約 308
```

- [ ] 確認 `Security_Reviewer` 對 A3 有 **審核**（Lens 編輯）：

```bash
psql "$DATABASE_URL" -c "SELECT role, can_view, can_edit, can_review FROM role_permissions WHERE story_id='A3' AND role='Security_Reviewer';"
```

預期：`can_review = t`（預設 VER）。若否，Admin → 角色細項權限勾選，或：

```sql
UPDATE role_permissions SET can_review = true
WHERE role = 'Security_Reviewer' AND story_id = 'A3';
```

> 注意：完整重跑 `schema_rbac.sql` 會 **DELETE 後重播** `role_permissions`；若環境有自訂矩陣請先備份。

- [ ] （可選）僅補表、不重播矩陣：重啟後端，依賴 `database._ensure_a3_schema()`（`architecture_reviews` + `wa_lenses`）

### 2. 服務啟動

- [ ] 後端啟動無錯；日誌可見 A3 schema 檢查完成（或等價）
- [ ] 前端可開 `/assessment`（需 A3.view）
- [ ] 健康檢查：`GET /` 回 200

### 3. 功能 Smoke（建議帳號）

| 步驟 | 帳號／條件 | 預期 |
|---|---|---|
| 3.1 發起評核 | 具 A3.**edit**（例：Hannah／Alex） | Assessment 選圖 → 評核完成；有總分／RiskCounts／發現 |
| 3.2 開啟歷史 | 具 A3.**view** | 可重開同一報告 |
| 3.3 下載 PDF | 報告 `complete`／`rules_only` + A3.view | PDF 下載成功 |
| 3.4 編輯 Lens | 具 A3.**review**（預設 Fiona） | 見「Lens 標準」→ 改文案／增刪題 → 儲存成功 |
| 3.5 新評核套用 | 任意可 edit 者 | **新**評核反映新標準；**舊**歷史分數不變 |
| 3.6 無權編輯 | 無 A3.review | 無「Lens 標準」分頁；`PUT /api/architecture/lens/active` → 403 |
| 3.7 工作區入口 | A3.view／edit | Workspace「Well-Architected」可進 Assessment |

### 4. 權限與安全

- [ ] pending／未核准帳號無法評核或編 Lens
- [ ] 不可讀他人無權限之 diagram／review（403）
- [ ] 預設 `admin`／測試密碼若仍為文件預設值，**上線後立刻更換**

### 5. 回滾（簡）

| 問題 | 動作 |
|---|---|
| Lens 改壞導致評核異常 | 具 A3.review 者從 UI 改回合理題目並儲存；或 DB 將該 `wa_lenses` 列 `is_active=false`（評核 fallback 檔案 `cloud360-core-mvp-lens.json`） |
| 新版後端異常 | 退回上一版映像／commit；表可保留（`IF NOT EXISTS`） |
| RBAC 被重播搞亂 | 自備份還原 `role_permissions`，或 Admin「還原設計預設」後再調 |

### 6. 完成簽核

| 項目 | 負責人 | 日期 | 結果 |
|---|---|---|---|
| DB／權限 | | | ☐ OK |
| Smoke 3.1–3.7 | | | ☐ OK |
| 回滾路徑已知 | | | ☐ OK |

---

## English Version

### Purpose

Lightweight A3 go-live checklist (not a full AIDLC Operations stage). Covers DB (`architecture_reviews`, `wa_lenses`), RBAC (A3 view/edit/**review**), smoke tests for review / PDF / Lens editor, and simple rollback.

### Checklist (summary)

1. Env vars + build with A3 code  
2. Run / verify `schema_rbac.sql`; confirm `wa_lenses` and Security_Reviewer `A3.can_review=true`  
3. Start services; open `/assessment`  
4. Smoke: start review, history, PDF, Lens edit (A3.review), new review uses new lens, 403 without review  
5. Authz / change default passwords  
6. Rollback: deactivate bad `wa_lenses` row → file fallback; redeploy previous image  

See Chinese section for full commands and sign-off table.
