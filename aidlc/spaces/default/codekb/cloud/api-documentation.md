# API 文件（API Documentation）

> Reverse Engineering 合成產物｜repo `cloud`｜HEAD `c3de2c8`｜intent `260819-cost-finops`｜mode **Modify overlay for C1**

## 公開 HTTP 表面

後端於 `backend/main.py:47-51` 掛載**五組** router（皆需依端點搭配 Bearer／cookie 認證與 RBAC；細節以原始碼 `Depends` 為準）。**無第六組。**

### ABSENT：`/api/cost*`

**Cost／pricing／TCO 端點不存在。** `openapi.json` 對 `cost|pricing|tco|finops|budget` 的命中只有 schema 名 `CommitCollabReviewBody`（false positive）。`frontend/src/types/api.d.ts` 對上述關鍵字：**0**。HEAD `/api/*` 路徑集合與 2026-08-06 相同前綴；新增欄位在 `/api/auth/list` 的 `last_activity_at`／分頁，**不是**成本端點。落地 C1 時必須跑 `backend/scripts/dump_openapi.py` 與 `frontend` `npm run gen:types`，否則 CI OpenAPI drift 紅燈。

不得發明下列契約：`GET/POST /api/cost`、`/api/cost/estimate`、`/api/pricing`、SKU 查價、budget CRUD。下列三節為實際存在的表面。

### `/api/architecture`（產生、審核、Lens）

| 方法 | 路徑 | 用途 | 主要消費者 |
|---|---|---|---|
| POST | `/generate` | 架構產生（基礎路徑） | Workspace／agent |
| POST | `/generate-wa-collab` | WA 協作產生（A1 主路徑） | `WorkspacePage` |
| POST | `/reviews/detect-provider` | 偵測雲端供應商（A3 雲別，非成本 Override） | `AssessmentPage` |
| POST | `/reviews` | 建立審核 | A3 |
| POST | `/reviews/commit-collab` | 提交協作審核結果 | A3 |
| GET | `/reviews` | 列表（支援 `diagram_id`、`ephemeral`） | A3 |
| GET | `/reviews/{review_id}` | 審核詳情 | A3 |
| POST | `/reviews/{review_id}/persist-diagram` | 審核結果回寫圖 | A3 |
| DELETE | `/reviews/{review_id}` | 刪除審核 | A3 |
| POST | `/reviews/{review_id}/retry-suggestions` | 重試改善建議 | A3 |
| POST | `/diagrams/render-png` | 圖轉 PNG（httpx → convert.diagrams.net／exp.draw.io） | 匯出／預覽 |
| GET/PUT | `/lens/active` | 作用中 lens | A3 lens tab |
| GET | `/lens/new-question-template` | 新問題範本 | Lens 編輯 |
| POST | `/lens/suggest-improvement-plan` | 改善計畫建議 | A3 |
| POST | `/lens/validate` | Lens 驗證 | Lens 編輯 |

實作：`agent_router.py`、`review_router.py`、`lens_router.py`。`detect-provider` 回傳 `{ provider, scores }`；前端送審時 `auto_detect_provider: false` 並帶 `body.provider`（`AssessmentPage.tsx`）。這是雲別，不是單價／時數覆寫。

### `/api/collab`（圖庫與即時同步）

| 方法 | 路徑 | 用途 |
|---|---|---|
| WS | `/ws/{workspace_id}` | 工作區即時同步（圖協作 broadcast，非通知 inbox） |
| GET | `/users` | 協作用戶 |
| GET | `/diagrams` | 圖列表 |
| GET | `/workspace/bootstrap` | 工作區啟動資料 |
| PUT | `/workspace/last-opened` | 記錄上次開啟 |
| GET/PUT/DELETE | `/diagrams/{id}/chat` | 聊天歷史 |
| GET/POST/PUT/DELETE | `/diagrams`、`/diagrams/{id}` | 圖 CRUD（`xml_data` blob，無 SKU 欄） |
| POST | `/diagrams/{id}/share` | 分享 |

實作：`collab_router.py`。A1 autosave 與 A3 選圖皆依賴此面。

### `/api/auth`（使用者與權限）

涵蓋 `register`／`login`／`me`、授權請求核准／駁回、使用者啟用／角色指派、`role-permissions` 讀寫與 reset-defaults、roles catalog、`GET /list`（**NEW 欄位** `last_activity_at` 與分頁）。實作：`user_router.py`；守衛依賴 `auth.py`／`rbac.py`。無任何端點以 `require_story_action("C1")` 守衛。

健康檢查：`GET /` → `{"message": "Cloud-360 Backend is running"}`。

## 內部契約與副作用

| 內部邊界 | 契約摘要 | 副作用注意 |
|---|---|---|
| `prompt_guard` → `agent_router` | 命中平台 DB／金鑰／系統值變更則回固定拒答 | **PRESENT**（2026-08-06 codekb 寫「無」已過時） |
| `design_agent` → `diagram_builder` | LLM tool 輸出 `groups`／`nodes`／`edges` → mxGraph XML | nodes required：`id`,`name`,`x`,`y`；**無 sku／size／hours**。Edges 已有 `exitX/Y` `entryX/Y`；`parent` 仍 `"1"`。Provider 只拿去跟 n8n 要 SVG |
| `parse_diagram_summary` | mxCell → `{ nodes: {id,label,style}, edges, counts }` | 消費者全是 A3 評核路徑；style 截斷 200 字元；**不是價目表** |
| `wa_rule_engine` `COST-*` | 關鍵字啟發式 findings（無金額） | **不是 TCO**；codes 僅定義於此檔，**零測試** |
| `DrawioCanvas` ↔ iframe | `postMessage`：init、load XML、autosave、**save／exit** | Undo echo-load：註解稱已避免，未重驗 UX |
| Review orchestrator → DB | findings／scores_json 持久化 | ephemeral reviews 與 persist-diagram 語意不同 |
| `LLM_PROVIDER` | `llm_provider.configure_provider_env`：OpenRouter 映射或 claude CLI | 不得把 secret 寫入 repo／artifacts |
| n8n icon fetch | `diagram_builder` `POST` `N8N_WEBHOOK_URL`（Basic Auth） | 失敗時圖示降級；非價目 HTTP |

前端以 `apiUrl()` 組絕對路徑；CORS 由 `CORS_ORIGINS` 控制（預設 localhost Vite）。

## A1／A3／C1 序列與契約缺口

**A1 generate→canvas**

1. `POST /api/architecture/generate-wa-collab`（messages、可選 current XML）  
2. 入口經 `prompt_guard`；通過後回應 XML → `WorkspacePage.setXml` → `DrawioCanvas` load  
3. iframe autosave／save → `PUT /api/collab/diagrams/{id}`  

先前缺口「無 prompt refusal」「embed 未接 save／exit」在 HEAD **已關閉**。成功卡仍無成本 CTA。

**A3 review**

1. `GET /api/collab/diagrams/{id}` 取 XML  
2. `POST /api/architecture/reviews`（＋可選 detect-provider／lens）  
3. `GET /api/architecture/reviews*` 呈現 findings（可含 `COST-*` 字串，**無金額欄**）

**C1（不存在的序列）**

沒有「讀圖 → 查價 → 回傳 TCO」的 HTTP 步驟可寫。設計時若新增，屬全新路徑，必須同時擴充 OpenAPI 與 generated types；不得把 `COST-*` finding payload 或 `detect-provider` 回應當成估算契約。
