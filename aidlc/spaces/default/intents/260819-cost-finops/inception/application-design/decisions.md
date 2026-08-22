# Decisions — C1 成本估算

<!-- Stage: application-design。本檔 ADR 為 intent 級設計決策，不取代 repo 根 ADR-0006 等。 -->

## 上游輸入

requirements（含 OQ-1／2／5）、stories、team-practices、architecture、Q1–Q5=A、refined-mockups。

---

# ADR-C1-01：新套件 `backend/cost/` 而非塞進 `user_router`

## Status
Accepted

## Date
2026-08-19

## Context
HEAD 無 cost bounded context。team-practices 要求 C1 走三層，且不得把邏輯寫進 `user_router.py`／`wa_rule_engine.py`。

## Decision
新增 `backend/cost/`（router、service、extractor、mapper、calculator、pricing_client）。`main.py` 以 prefix `/api/cost` 掛載。前端 `CostPage` 新檔，不改 Assessment 當宿主。

## Consequences
Construction 目錄與測試 `backend/tests/test_cost_*.py` 有固定落點。OpenAPI 新 tag `cost`。

## Alternatives Considered
- 寫進 `services/collab` 或 A3：違反「COST-* ≠ TCO」與禁止污染 WA 引擎。
- 獨立微服務：超出 mvp 單體與部署模型。

## Reversibility
中等。prefix 穩定後契約難改；套件內檔案可再拆。

---

# ADR-C1-02：四種變更權用 `C1` + `C1h`／`C1r`／`C1b`／`C1o`

## Status
Accepted（Q1=A）

## Context
`Action` 只有 view／edit／review。現 C1 種子 Architect／Editor 的 `can_edit` 為 False，FinOps 為 True，無法表達四種互斥變更。

## Decision
- `C1.view`：進頁、讀快照、讀稽核、Sidebar。
- `C1h.edit`：時數；`C1r.edit`：區域；`C1b.edit`：預算；`C1o.edit`：SKU／小時價覆寫。
- 不改 `role_permissions` 表形狀。
- 新增 `ensure_missing_role_permissions()`：只插入缺失的 `(role, story_id)`，**禁止**依賴現有 `force=False` 全表 no-op。

預設 edit：Architect=`C1h`+`C1r`；FinOps=`C1o`+`C1b`；Editor=`C1b`。A 規則 allow／deny 測試。

## Consequences
Admin 矩陣多四列 story。`STORY_IDS` 與 `schema_rbac.sql` 必須列出。既有 staging 列在補缺失 ensure 後才生效。

## Alternatives Rejected
- **B 硬編碼角色**：Admin 無法調權；與矩陣單一真實來源衝突。
- **C 加四個 boolean 欄**：J3b UI＋schema 爆炸，超出本輪。

## Reversibility
低。story id 進種子與測試後不宜改名。

---

# ADR-C1-03：兩張狀態表，不把估價寫進 XML

## Status
Accepted（Q2=A）

## Context
橫幅與第二人同一總額要求伺服器持久化。XML 是畫布真實來源，但覆寫不應污染 draw.io 模型。

## Decision
`diagram_cost`（區域、預算）＋ `diagram_cost_line`（hours、sku_override、hourly_override）。PK／UK：`(diagram_id, mxcell_id)`。圖刪 cascade。每次 snapshot 以 XML 重擷取後對齊；消失的 id 刪行；新 id 時數 24。

## Consequences
`schema_rbac.sql` 名稱雖歷史，遷移仍須寫在同一部署文件鏈（schema SQL + `DEPLOY.md` + `database.py` ensure）。

## Alternatives Rejected
- JSONB 欄：稽核舊值與部分更新差；SQLite 測試分叉。
- XML 自訂屬性：與「不寫回圖模型」衝突。

## Reversibility
中等。可遷移到別的表，但 API 快照形狀宜穩。

---

# ADR-C1-04：Postgres 價目快取 TTL 24h

## Status
Accepted（Q3=A）

## Context
NFR-4 5 秒；無 Redis；禁止帳單 API。

## Decision
表 `pricing_cache` 鍵為 `(cloud, sku, region)`。命中且 `now - fetched_at < 24h` 不打外網。Miss／過期走 `pricing_client`。失敗不寫正價。無公開端點的雲：不呼叫 client。

各雲 URL 仍 OQ-3／infrastructure-design。本輪 client 介面穩定，實作可用 stub 先綠測試。

## Alternatives Rejected
- 每次即時查：難以保證 5 秒與穩定來源時間。
- 只讀 fixture 當生產官方價：違反 FR-2.1 字面。

## Reversibility
高。TTL 可調；可改 Redis 而不改 Snapshot 契約。

---

# ADR-C1-05：SKU 對照表為 repo YAML

## Status
Accepted（Q4=A）

## Context
對照需可測、可 diff；本輪無 Admin 維護故事。

## Decision
`backend/cost/sku_map.yaml` 啟動載入。一對多的建議 UI 留 functional-design；mapper 本輪回 `ambiguous` → 列 `unpriced`。

## Alternatives Rejected
- Python dict：難審。
- DB＋Admin：無故事。

## Reversibility
高。可改載入來源而不改 mapper 介面。

---

# ADR-C1-06：稽核 HTTP 綁在圖資源下

## Status
Accepted（Q5=A）

## Context
故事允許暫查 DB；Construction 需要 TestClient 掛點。

## Decision
表 `cost_audit_event`。`GET /api/cost/diagrams/{diagram_id}/audit`。寫入點：覆寫小時價、指定 SKU、改預算。時數／區域本輪不寫稽核。

## Alternatives Rejected
- 扁平 `/api/cost/audit?diagram_id=`：較不像資源。
- 本輪無 HTTP：QA 無掛點。

## Reversibility
中等。路徑進 OpenAPI 後視為契約。

---

# ADR-C1-07：USD 兩位小數

## Status
Accepted（本站定，未另問）

## Context
故事把小數位留給設計。PBT 需要固定比較。

## Decision
calculator 出口量化到小數兩位（銀行家捨入或四捨五入在 functional-design 寫死一種）。JSON number。顯示 `tabular-nums`。

## Consequences
Hypothesis 比較量化後的 Decimal，不用 raw float。

## Reversibility
中等。改位數會動 e2e 字串。

---

# ADR-C1-08：第一段不註冊預算／橫幅

## Status
Accepted（stories AC-1.16）

## Decision
第一段：不 `include` budget 路由與 `GET /banner`（或恒 404）、不在 `Layout` import `OverspendBanner`。第二段同一 service 加掛。用建置開關或第二個模組檔，不用 CSS `hidden`。

## Reversibility
高。

---

# ADR-C1-09：三雲皆 `official_list`（覆寫 OQ-3 初案）

## Status
Accepted

## Date
2026-08-23

## Context
Infrastructure-design Q&A 初案與 mockups M2 曾定「僅 AWS 官方價；GCP／Azure `manual_override_only`」。實作期間已接上 GCP Cloud Billing Catalog 與 Azure Retail Prices，且區域下拉需依圖雲過濾，living docs 與程式不一致。

## Decision
1. `pricing_coverage.yaml`：`aws`／`gcp`／`azure` 皆 `mode: official_list`。
2. Allowlist hosts：`pricing.us-east-1.amazonaws.com`、`cloudbilling.googleapis.com`、`prices.azure.com`。
3. 查價路徑：AWS Bulk JSON **或** boto3 `pricing.get_products`（禁止 Cost Explorer）；GCP Catalog HTTP + 可選 `GCP_BILLING_API_KEY`（禁止帳號型 Billing SDK）；Azure Retail Prices 公開免帳號。
4. Snapshot 增 `diagram_cloud`、`allowed_regions`；跨雲 region PUT → 400。
5. 歷史 Q&A／diary **不改寫**；以本 ADR + 更新後的 living docs 為準。

## Consequences
- 定價假設文案改為三雲「走官方價」。
- CI 仍用 `COST_PRICING_STUB=1`；本機 GCP 需 key 才有真實價。
- `cicd-pipeline` 靜態 gate 不再全面禁 `boto3`（僅禁帳單／管理面）。

## Alternatives Considered
- 維持 GCP／Azure manual-only：與已交付程式衝突，FinOps 無法對非 AWS 圖估價。
- 盲目對未映射 label 打 API：拒絕（仍需 sku_map 代表規格）。

## Reversibility
中等。改回 `manual_override_only` 需同步 YAML、UI 文案與測試。

---

## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-08-19T08:19:45Z
**Iteration:** 1

### Findings

| # | Severity | Location | Finding | Recommendation |
|---|---|---|---|---|
| 1 | Minor | `component-methods.md` GET `/diagrams/{id}` | `coverage` 欄位列於快照回應 body，但在 `component-methods.md` 與 `cost_calculator` 簽名中均無定義（公式、單位或預設值皆缺）。Construction 開發者須自行推斷其語意（定價列數 / 總列數？百分比？）。 | 在 `component-methods.md` 補一行：`coverage`：`priced` 列數 ÷ 總擷取列數（0.0–1.0），無列時為 `null`；或在 functional-design 明確定義，並在此檔標記「見 functional-design」。 |
| 2 | Minor | `ADR-C1-08` / `component-methods.md` GET `/banner` | ADR-C1-08 明確排除「budget PUT 路由」與「OverspendBanner 掛載」，但未說明 `GET /banner` 端點在第一增量是否註冊。若 TestClient 測試直接呼叫 `/banner`，`banner_for()` 需能在 `monthly_budget` 全為 NULL 時安全回傳 `{active: false}`（`is_overspent(total, None) → False` 可保證），但此行為未在 ADR 中明文確認，Construction 可能誤判需整個排除。 | 在 ADR-C1-08 補一句：「第一段可註冊 `/banner` 端點，`banner_for()` 在無預算列時恒回傳 `{active: false, count: 0}`；如不註冊則一律 404 並在 TestClient 測試中跳過。兩者皆可接受，Construction 擇一記錄於 functional-design。」 |
| 3 | Minor | `services.md` / `component-methods.md` `pricing_client` | 設計要求「無公開端點的雲：不呼叫 client」（FR-2.2），但 `pricing_client.fetch_hourly(cloud, sku, region)` 的介面未定義此偵測機制。若 OQ-3 infrastructure-design 交付的是「URL 字典」，`cost_service` 需要某種機制（空 URL？設定旗標？`PriceMiss` 子類型？）判斷「此雲本輪無端點」。目前 `PriceHit / PriceMiss` 二元無法區分「無端點」與「有端點但查詢失敗」，可能造成 `price_fetch_failed` 與 `unpriced` 混用。 | 在 `component-methods.md` 的 `pricing_client` 節補第三個回傳型態 `PriceUnsupported`（或文字說明）表示「該雲本輪無公開端點，不應計入失敗重試」；`cost_service` 針對此型態將列狀態設為 `unpriced` 而非 `price_fetch_failed`，與 FR-2.2 AC 一致。 |

### Validation Tool Results

| 工具 | 結果 | 說明 |
|---|---|---|
| 依賴矩陣循環偵測（手動） | PASS | `component-dependency.md` 矩陣為有向無環圖：router → service → {extractor, mapper, calculator, pricing_client\*, price_cache, diagrams}；calculator 與 extractor 均為葉節點，無反向邊。 |
| `force=False` no-op 驗證（`rbac.py` L63–65） | PASS（gap 已知） | 確認 `ensure_role_permissions_seeded(force=False)` 在表非空時整段 no-op；C1h／C1r／C1b／C1o 確實不在 `rbac_seed_data.py`（L82–91 僅 `C1`）。設計已在 ADR-C1-02 與 `components.md` 第 72 行明確標記此缺口為 Construction 義務，DoD 第 5 條亦覆蓋。 |
| calculator 禁止 httpx（靜態） | PASS（設計強制） | `component-methods.md` 明文禁止模組內 `httpx`、`Session`、`HTTPException`；模組尚未存在，無反例。 |
| 第一增量 overspent 洩漏檢查 | PASS | `is_overspent(total, None) → False`（`component-methods.md`）；ADR-C1-08 第一段 `overspent` 恒 `false` 可由此保證，不需 hardcode。 |
| OpenAPI dump 義務 | PASS | `dump_openapi.py --check` 確認存在；ADR-C1-01 Consequences 明列 OpenAPI 新 tag `cost`；requirements.md DoD 第 6 條強制。 |
| 跨元件引用解析 | PASS | 所有 story id（`C1`、`C1h`、`C1r`、`C1b`、`C1o`）在 requirements.md FR 中有對應；`require_story_action` 在既有 `rbac.py` 存在；`UserDiagram` ORM 模型在現有 collab stack 確認；`dump_openapi.py` 確認存在。 |

### Summary

設計結構清晰、依賴無環、三層分層正確。關鍵架構決策（ADR-C1-01 至 08）均有可追溯的 FR 根據，且明確記錄了 `force=False` 種子缺口、第一增量排除範圍與純函式計算器的禁止邊。三項 Minor 發現均不影響實作可行性：`coverage` 欄位語意可由 functional-design 補齊，`/banner` 增量規則一行即可澄清，`PriceUnsupported` 型態缺失可在 functional-design 補充介面。Construction 開發者具備足夠信息可開始實作，無需返回設計者澄清架構決策。
