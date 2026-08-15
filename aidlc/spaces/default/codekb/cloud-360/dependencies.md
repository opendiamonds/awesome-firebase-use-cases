# Dependencies — Cloud-360

> 逆向工程產出。基準 commit `8c90f40372ac810cc8f6ef41c46fc7a723031a1e`（branch `ut`，2026-08-08）。
> 套件版本清單見 `technology-stack.md`；本檔聚焦**依賴關係與其風險含義**。

## 外部套件依賴

### Backend（`backend/requirements.txt`，12 條，全部未 pin）

依「若此依賴消失或 breaking change，影響多大」分級：

| 依賴 | 爆炸半徑 | 說明 |
|---|---|---|
| `fastapi[standard]` + `uvicorn` | **全系統** | 整個 HTTP 面。`[standard]` extra 是隱性依賴來源（httptools、websockets 等未直接宣告） |
| `sqlalchemy` + `psycopg2-binary` | **全系統** | 唯一持久層存取途徑 |
| `pydantic` | **全系統** | 所有 request/response schema。**程式碼仍用 v1 風格 `class Config: orm_mode = True`** |
| `claude-agent-sdk` | **A1 + A3 建議階段** | 產圖與改善建議都經此；失效時 A3 降級為 `rules_only`，A1 完全無法產圖 |
| `pyjwt` + `bcrypt` | **全部驗證** | 登入與 token 驗證 |
| `httpx` | 局部 | n8n webhook 等外部呼叫；失敗有 fallback |
| `python-dotenv` | 啟動 | `.env` 載入 |
| `hypothesis` | 僅測試 | property-based 測試 |
| `passlib[bcrypt]` | **零** | **宣告但程式碼未 import**，可安全移除 |

**未宣告但實際被使用的傳遞依賴**：`fastapi[standard]` extra 帶入的 uvicorn workers、
httptools、websockets 等。WebSocket 端點實際依賴 `websockets`，但該套件**未在
`requirements.txt` 直接列出**，靠 extra 傳遞。若 FastAPI 改變 extra 內容，
WebSocket 功能可能無聲失效。

### Frontend（`frontend/package.json`）

| 依賴 | 爆炸半徑 | 說明 |
|---|---|---|
| `react` + `react-dom` (v19) | **全前端** | |
| `react-router-dom` (v6) | **全前端** | 路由與 guard 組合 |
| `html2canvas` + `jspdf` | 局部 | 僅 A3 的 PDF 匯出與 PNG 匯出 |

**唯一有 lockfile 的依賴集合**（`package-lock.json` 已 commit）。

## 外部服務依賴

| 服務 | 必要性 | 失敗行為 | 設定 |
|---|---|---|---|
| **PostgreSQL** | **必要** | 系統無法啟動 | compose 內的 `db` 服務 |
| **OpenRouter** | **A1／A3 建議必要** | `agent_router._ensure_llm_keys()` 在缺金鑰時直接回 **500**；A3 建議階段降級為 `rules_only` | `ANTHROPIC_BASE_URL=https://openrouter.ai/api`；`OPENROUTER_API_KEY` 於 startup 映射為 `ANTHROPIC_AUTH_TOKEN`。**`ANTHROPIC_API_KEY` 必須留空**以避免直連 Anthropic |
| **n8n webhook** | **選填** | 用灰底 fallback 圖示，不中斷產圖 | `N8N_WEBHOOK_URL` |
| **Cloudflare Tunnel** | staging 對外必要 | 外部無法連線；主機內部仍可運作 | `deploy/cloudflared/config.yml`，憑證 0400、以 uid 1000 讀取 |
| **Kiwi TCMS**（`tcms.danniel.cc`） | 流程用，非執行期 | `ui-regression` workflow 無法回報結果 | 於 `dc-infra` repo 維運 |

### 環境變數依賴

| 變數 | 用途 | 未設定時的行為 |
|---|---|---|
| `JWT_SECRET` | JWT 簽章金鑰 | **靜默 fallback 到程式碼內的預設字串**（見「依賴風險摘要」R2） |
| `OPENROUTER_API_KEY` | LLM 存取 | A1／A3 建議端點回 500 |
| `ANTHROPIC_BASE_URL` / `ANTHROPIC_AUTH_TOKEN` | Agent SDK 導向 OpenRouter | 由 `configure_openrouter_env()` 從 `OPENROUTER_API_KEY` 推導 |
| `ANTHROPIC_API_KEY` | — | **必須留空**，否則 Agent SDK 會直連 Anthropic 而非 OpenRouter |
| `N8N_WEBHOOK_URL` | 動態圖示 | fallback 灰底圖示 |
| `CORS_ORIGINS` | CORS allowlist（逗號分隔） | 預設 `http://localhost:5173,http://127.0.0.1:5173` |
| `VITE_API_BASE_URL` | 前端 API base（**build ARG，非 runtime**） | 改值必須**重建 frontend image**，不能只重啟容器 |
| DB 連線變數 | PostgreSQL | 見 `DEPLOY.md` 與 `.env.example` |

## 隱性硬依賴

這一節是本檔最重要的部分 —— 這些依賴**不在任何依賴宣告檔內**，但缺了系統就壞。

### H1 — backend runtime 需要 Node 22 + Claude Code CLI

`claude-agent-sdk` 的運作方式是 **spawn 一個 `claude` CLI 子行程**，不是純 Python 的
HTTP client。因此 backend 容器內必須具備：

1. **Node.js 22 runtime**
2. **全域安裝的 `@anthropic-ai/claude-code`**（可執行檔 `claude` 在 PATH 上）

這兩者寫在 `backend/Dockerfile` 與 `DEPLOY.md` §0，**但不在 `requirements.txt`**。
一個「只看 requirements.txt 就以為能跑」的環境（例如本機 venv、或某個精簡過的 base image）
會在 A1 產圖時才失敗，且錯誤訊息未必指向缺少 CLI。

**判定為硬依賴的理由**：影響 A1 全部與 A3 的建議階段，涵蓋系統的兩條核心價值鏈。

**版本治理現況**：`@anthropic-ai/claude-code` 以 `npm i -g` 安裝且**無版本 pin**，
每次 image build 取最新版。

### H2 — `schema_rbac.sql` 只在空 volume 時執行

`deploy/docker-compose.deploy.yml` 把 repo 根目錄的 `schema_rbac.sql` 掛載為
`/docker-entrypoint-initdb.d/01-schema_rbac.sql`。PostgreSQL 官方 image 的行為是
**只在資料目錄為空時執行 initdb 腳本**。

**後果**：既有環境更新 `schema_rbac.sql` **不會**自動生效。schema 演進實際上依賴
`backend/database.py` 的三個 `_ensure_*_schema()` 在每次啟動時執行的 `ALTER TABLE`。
換句話說，**部署腳本與執行期 schema 是兩條分開的演進路徑**，這正是技術債 T1 的機制。

### H3 — nginx 的 SSE 設定是功能性依賴

`frontend/nginx.conf` 的 `proxy_buffering off` 與 600 秒 timeout **不是效能調校，是功能前提**。
少了它們，A1 與 A3 的 SSE 串流會被緩衝住（使用者看到長時間空白後一次爆出）或提前斷線。
任何反向代理層的更動都必須保留這兩項。

### H4 — `ci.yml` 的檔名是 load-bearing

`scripts/validate_repo_contract.py` 的 `REQUIRED_FILES` 包含 `.github/workflows/ci.yml`
這個路徑本身。**改名 CI 檔會讓 repo contract 驗證失敗**。

### H5 — 測試依賴 `helpers.py` 的 import 順序

`backend/tests/helpers.py` 必須在**任何資料庫模組 import 之前**執行
`sys.modules.setdefault("psycopg2", MagicMock())`，測試才能改走 in-memory SQLite。
測試檔的 import 順序因此是有意義的，不能自由重排。

## 內部跨模組依賴

### 依賴方向（Backend）

```
main.py
  └─> 5 個 router
        ├─> rbac ──────> auth ──> models ──> database
        ├─> 各自的 orchestrator / service / agent
        └─> models

orchestrator 層
  ├─> wa_rule_engine   (葉節點，零依賴)
  ├─> wa_lens_engine   (葉節點，零依賴)
  ├─> review_agent / design_agent ──> 外部 CLI 子行程
  └─> models

design_agent ──> diagram_builder ──> (選填) n8n webhook
```

**無循環依賴**（掃描未發現）。依賴方向一致由外向內：router → service → engine／model。

### 關鍵內部依賴

| 依賴邊 | 性質 | 風險 |
|---|---|---|
| 5 個 router → `rbac` | 全域橫切，設計意圖 | `rbac` 的任何行為變更影響全部端點 |
| `rbac` → `rbac_seed_data` | **`STORY_IDS` 由 `DEFAULT_ROLE_PERMISSIONS` 動態導出** | 改 seed 資料即改變全系統的 story 清單 |
| `database.init_db` → `rbac.ensure_role_permissions_seeded` | 啟動時的 seed | 見下方「資料層依賴」 |
| `agent_router` → `review_orchestrator.get_accessible_diagram` | 跨家族依賴 | A1 協作端點需要 A3 的存取判定函式，是唯一的跨家族依賴 |
| `wa_score_service` → `wa_lens_engine` | 與 A3 同源打分 | 確保協作模式與正式評核用同一套計分 |

### 前端內部依賴

```
App.tsx ──> RouteGuard (ProtectedRoute / CapabilityRoute)
              └─> auth-context (useAuth) ──> AuthContext.tsx (Provider)
pages/* ──> config/api.ts (apiUrl / wsUrl)
         └─> 直接 fetch()，無中介層
WorkspacePage ──> ChatBox / DrawioCanvas / ShareModal / hooks/useCollaboration
AssessmentPage ──> DiagramPreviewPanel / SuggestionRichText / utils/*
```

**注意**：`AuthContext.tsx` 與 `auth-context.ts` 的拆分是 lint 規則強制的
（`eslint-plugin-react-refresh` 要求單一 component 匯出），不是自願的設計選擇。
合併兩檔會導致 CI 紅燈。

## 資料層依賴：三份 schema 來源

這是全系統最需要小心的依賴結構。

| 來源 | 宣稱角色 | 實際涵蓋 | 何時生效 |
|---|---|---|---|
| `schema_rbac.sql`（523 行） | 新環境唯一要跑的完整腳本；`DEPLOY.md` §2.1 指定 | A) users／user_diagrams／diagram_shares；B) users.last_opened_diagram_id／user_diagram_chats；C) role_permissions + 308 列 seed；D) admin 帳號；E) architecture_reviews／wa_lenses。**缺 J5 全部** | 手動 `psql -f`，或 initdb（**僅空 volume 一次**） |
| `models.py` + `database.py::_ensure_*_schema()` | ORM 定義與啟動補丁 | **7 個表全部** + J5 欄位（唯一來源） | **每次後端啟動** |
| `schema.sql`（79 行） | 精簡核心 DDL 參考 | users／user_diagrams／diagram_shares／user_diagram_chats／architecture_reviews。**缺 `wa_lenses`、`role_permissions`、J5 全部**；`users.role` 仍 `NOT NULL` | 從不自動執行 |

**執行期的真實權威是第二列。** 任何以 `.sql` 檔推斷 schema 的判斷都會出錯。

### seed 依賴（四個觸發點）

| # | 位置 | 觸發時機 | 行為 |
|---|---|---|---|
| 1 | `schema_rbac.sql` 第 178–489 行 | 手動 `psql -f`；或 initdb（僅空 volume 一次） | **`DELETE FROM role_permissions;` 後 INSERT 308 列。無條件覆寫，Admin UI 調整會遺失** |
| 2 | `rbac.ensure_role_permissions_seeded()` ← `database.init_db()` | **每次後端啟動** | `force=False`：`count > 0` 即 return 0（表為空才寫）。`force=True`（僅測試）先 DELETE 再重播 |
| 3 | `database.init_db()` | 空 DB 時 | 建 11 個 persona 帳號（密碼 `<username>123`，全部 `approved` 並帶正式角色）；每次啟動確保 `admin` 存在且 `approved` + `Platform_Admin` |
| 4 | `GET /api/auth/roles/catalog` | **任何匿名請求** | 回應前呼叫 `ensure_role_permissions_seeded(db, force=False)` —— **匿名可達的 seed 路徑** |

### 預設矩陣的雙來源

308 列預設矩陣同時存在於：

- `schema_rbac.sql` 第 180–489 行的 INSERT
- `backend/services/rbac_seed_data.py` 的 `DEFAULT_ROLE_PERMISSIONS`

後者 docstring 寫「由 `schema_rbac.sql` 產生（勿手改；改 SQL 後重跑產生腳本）」，
**但該產生腳本不存在於 repo，CI 也沒有任何一致性檢查**。兩者漂移不會被任何機制發現。

### 角色清單的三份手寫副本

`rbac.py::CANONICAL_ROLES`（11）、`user_router.py::ROLE_DISPLAY_NAMES`（11）、
`AdminPage.tsx::AVAILABLE_ROLES`（11）—— **彼此無同步機制**。新增角色需三處手改。

## 依賴風險摘要

| id | 風險 | 影響 | 現有緩解 |
|---|---|---|---|
| **R1** | Backend 依賴 **100% 未 pin 且無 lockfile** | CI／image build／staging 三處各自解析最新版；上游 breaking release 直接打到部署 | **無** |
| **R2** | `JWT_SECRET` 有程式內預設值 `os.environ.get("JWT_SECRET", "<已公開於 git 的字串>")` | 未注入時靜默用已知金鑰簽 token | `deploy.yml` 有 secrets 檢查保護 staging；**本機與其他路徑無保護** |
| **R3** | H1 隱性硬依賴（Node 22 + Claude Code CLI）不在依賴宣告內 | 環境缺件時 A1／A3 建議在執行期才失敗 | 寫在 `Dockerfile` 與 `DEPLOY.md` §0 |
| **R4** | 三份 schema 來源不一致，J5 欄位僅存在於 runtime 補丁 | 新環境的表結構與執行期不符；`.sql` 檔不可作為 schema 依據 | `_ensure_*_schema()` 每次啟動修補 |
| **R5** | 預設矩陣雙來源無同步驗證（產生腳本不存在） | 兩份 308 列可能漂移，無人察覺 | **無** |
| **R6** | `schema_rbac.sql` 的無條件 `DELETE FROM role_permissions;` | 「重跑取得新 DDL」與「保留 Admin UI 調整」互斥 —— 而 R4 的修法正需要重跑 | **無** |
| **R7** | `websockets` 靠 `fastapi[standard]` extra 傳遞，未直接宣告 | extra 內容變動時 WebSocket 可能無聲失效 | **無** |
| **R8** | `@anthropic-ai/claude-code` 與 `cloudflared` 用 `latest`／無 pin | image 重建即換版，行為可能改變 | **無** |
| **R9** | PostgreSQL 15（本機）vs 16（staging） | 本機測不到的版本差異 | **無** |
| **R10** | 前後端資料契約手寫鏡像（`UserSchema` ↔ `DbUser`） | 漏改不會有任何工具報錯 | **無**（e2e 未斷言表格內容） |

**給下游 stage 的操作提醒**：任何觸及 `users` 表的變更會同時踩到 R4、R6、R10 三條。
落地檢查清單見 `architecture.md` 的「對新變更的架構約束」。
