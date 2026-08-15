# Component Inventory — Cloud-360

> 逆向工程產出。基準 commit `8c90f40372ac810cc8f6ef41c46fc7a723031a1e`（branch `ut`，2026-08-08）。
> 本檔是元件的完整清單與職責定義。架構關係見 `architecture.md`，檔案佈局見 `code-structure.md`。

## 清單讀法

- **LOC** 為掃描時的實測行數。
- **上游** = 誰呼叫它；**下游** = 它呼叫誰。
- **測試** 欄標示是否有直接對應的測試檔（`backend/tests/`）。
- 「純函式」意指不讀資料庫、不做網路 I/O，可在無環境下直接測試。

## Backend 元件

### 應用骨架

| 元件 | LOC | 職責 | 上游 | 下游 | 測試 |
|---|---|---|---|---|---|
| `main.py` | 55 | 建立 `FastAPI(title="Cloud-360 API")`；CORS middleware（來源由 `CORS_ORIGINS` 注入，預設 localhost:5173）；掛 5 個 router；startup 事件呼叫 `init_db()` 與 `configure_openrouter_env()` | uvicorn | 5 router、`database`、`design_agent` | 無（CI 有 import smoke） |
| `models.py` | 171 | SQLAlchemy declarative Base；7 個 ORM 模型；`User.to_dict()`；relationship 定義 | 全部 service | — | 間接 |
| `database.py` | 264 | engine／`SessionLocal`／`get_db()` 依賴注入；`init_db()`（建表 + seed 帳號 + seed 矩陣）；三個 `_ensure_*_schema()` runtime DDL 補丁 | `main.py`、全部 router | `models`、`rbac` | 間接 |

### HTTP 邊界層（Router）

| 元件 | LOC | 職責 | 下游 | 測試 |
|---|---|---|---|---|
| `services/user_router.py` | 831 | 登入／註冊／使用者清單／角色指派／啟停用／刪除／J5 授權申請／J3b 權限矩陣 CRUD。**商業邏輯直寫 handler，無 service 層** | `auth`、`rbac`、`models` | **無直接測試** |
| `services/collab_router.py` | 527 | 架構圖 CRUD、分享 ACL、WebSocket 共編廣播、A4 聊天持久化、workspace bootstrap。**商業邏輯直寫 handler** | `rbac`、`models` | `test_collab.py`(184) 涵蓋部分邏輯 |
| `services/review_router.py` | 484 | A3 評核 API（SSE + JSON）、上傳 XML、provider 偵測、PNG 轉檔 | `review_orchestrator`、`rbac` | `test_review_authz.py`(93) 涵蓋授權 |
| `services/agent_router.py` | 148 | A1 SSE 適配層：驗證 JWT 與 body、把 agent 事件轉 SSE、雙 agent 協作端點。**不直接呼叫 LLM** | `design_agent`、`wa_collab_orchestrator`、`rbac` | **無** |
| `services/lens_router.py` | 108 | A3 Offline Custom Lens 編輯 API（需 `A3.review`），支援 per-cloud provider | `lens_service`、`rbac` | **無** |

### 授權與驗證核心

| 元件 | LOC | 職責 | 上游 | 測試 |
|---|---|---|---|---|
| `services/rbac.py` | 272 | **全系統授權核心**。`CANONICAL_ROLES`（11）／`STORY_IDS`（動態導出 28）／`ROLE_ALIASES`；`user_can`／`user_can_arch`；guard 工廠 `require_story_action`／`require_arch_action`；`permissions_map_for_role`；`sync_arch_permission_flags`；`ensure_role_permissions_seeded`；`admin_may_decide_role`（BR-04） | 5 個 router 全部、`database` | `test_rbac.py`(56)、`test_j5_authz.py`(123) |
| `services/auth.py` | 86 | bcrypt 雜湊與驗證；PyJWT 簽發／解碼（HS256，8 小時）；`get_current_user`（含 `is_active` 檢查）；`RoleChecker` 角色 allowlist（**死碼**） | `rbac`、`user_router` | `test_auth.py`(124) |
| `services/rbac_seed_data.py` | 314 | 純資料常數 `DEFAULT_ROLE_PERMISSIONS`：**308 筆 tuple**（11 角色 × 28 story）。docstring 宣稱「由 `schema_rbac.sql` 產生（勿手改）」，**但產生腳本不存在於 repo** | `rbac` | 間接（`STORY_IDS` 由此導出） |

### LLM Agent 與編排器

| 元件 | LOC | 職責 | 下游 | 測試 |
|---|---|---|---|---|
| `services/design_agent.py` | 359 | **A1 Design Agent**。`claude-agent-sdk` → spawn Claude Code CLI 子行程 → OpenRouter；提供行程內 MCP tool `draw_architecture_diagram`；`configure_openrouter_env()` 把 `OPENROUTER_API_KEY` 映射為 Agent SDK 所需環境變數 | `diagram_builder`、外部 CLI | `test_design_agent.py`(85)，含 2 個 `@given` |
| `services/review_agent.py` | 177 | **A3 改善建議 agent**。串流 yield TextBlock 供上游轉 SSE | 外部 CLI | `test_review_agent.py`(37) |
| `services/review_orchestrator.py` | 510 | **A3 評核狀態機**。狀態流轉（`pending`→`rules_complete`→`complete`／`rules_only`／`unsupported`）；逾時控制（75s／90s）；`_archive_previous()`；SSE 事件序；`audit_log`；`get_accessible_diagram`／`review_to_dict`／`user_can_read_review` | `wa_rule_engine`、`wa_lens_engine`、`review_agent` | **狀態機主體無直接測試** |
| `services/wa_collab_orchestrator.py` | 530 | **A1↔A3 雙 agent 協作**。Design 與 Review 互相對話最多 2 輪，目標 lens 總分 ≥ `TARGET_SCORE`(80) 且無 `HIGH_RISK`；產生 `score` 事件與 `xml_preview` | `design_agent`、`review_agent`、`wa_score_service` | `test_wa_collab.py`(48) |

### 純函式引擎（可 PBT 的核心）

| 元件 | LOC | 職責 | 外部相依 | 測試 |
|---|---|---|---|---|
| `services/wa_rule_engine.py` | **973（全 repo 最大模組）** | 解析 draw.io mxGraph XML 的 `mxCell` value 與 style，產出 Well-Architected 支柱分數與 findings。**不連 AWS API、不讀 DB** | 無 | `test_wa_rule_engine.py`(150)，含 2 個 `@given` |
| `services/wa_lens_engine.py` | 556 | Offline Custom Lens loader 與 `riskRules` 評估。相容 AWS WA Custom Lens `schemaVersion 2021-11-01`。**不呼叫 AWS API** | 無 | `test_wa_lens_engine.py`(146) |
| `services/diagram_builder.py` | 288 | groups／nodes／edges → draw.io `mxGraphModel` XML。圖示經 n8n webhook 取 SVG，**失敗用灰底 fallback** | 選填 n8n webhook | `test_diagram_builder.py`(205)，含 2 個 `@given` |

### 服務與工具模組

| 元件 | LOC | 職責 | 測試 |
|---|---|---|---|
| `services/lens_service.py` | 203 | Lens 讀寫與驗證；per-cloud active lens 管理 | `test_lens_service.py`(86) |
| `services/wa_score_service.py` | 104 | 對 XML 做 A3 同源的 lens 打分，**不強制寫入 review**；定義 `TARGET_SCORE` | **無** |
| `services/collab_suggestions.py` | 147 | 優化前後 findings 的差異摘要 | `test_collab_suggestions.py`(52) |
| `services/llm_limits.py` | 64 | LLM token 與 context 上限常數 | `test_llm_limits.py`(41) |

### 資料資產

| 資產 | 內容 | 用途 |
|---|---|---|
| `backend/lenses/cloud360-core-mvp-lens.json` | AWS lens 定義 | 無 DB 資料時的 fallback |
| `backend/lenses/cloud360-core-mvp-lens-gcp.json` | GCP lens 定義 | 同上 |
| `backend/lenses/cloud360-core-mvp-lens-azure.json` | Azure lens 定義 | 同上 |
| `backend/prompts/`（6 檔） | 3 個 system prompt（AWS／通用雲／WA review）+ 3 個 draw.io 模板 | Agent 的 prompt 與初始圖形 |

### ORM 模型（7 個表）

| 模型／表 | 時間戳 | 備註 |
|---|---|---|
| `users` | **無任何時間戳** | 見下方專節 |
| `user_diagrams` | `updated_at` | 架構圖本體，含 `xml_data` |
| `diagram_shares` | 無 | 分享 ACL 關聯表 |
| `user_diagram_chats` | `updated_at` | A4 聊天持久化 |
| `role_authorization_requests` | `created_at`／`updated_at`／`decided_at` | J5 授權申請 |
| `architecture_reviews` | `created_at`／`updated_at` | A3 評核結果 |
| `wa_lenses` | `created_at`／`updated_at` | Lens 持久化 |
| `role_permissions` | `updated_at`（+`updated_by`） | 權限矩陣，`(role, story_id)` 複合主鍵 |

**時間戳慣例**：既有時間戳一律 `DateTime(timezone=True)` + `server_default=func.now()`
（`updated_at` 另加 `onupdate=func.now()`），SQL 側為 `TIMESTAMPTZ DEFAULT now()`。

#### `users` 表詳解（執行期權威為 ORM，`models.py:22-51`）

| 欄位 | 型別 | 約束 | 定義於 |
|---|---|---|---|
| `id` | Integer | PK, index | 三處一致 |
| `username` | String | unique, index, NOT NULL | 三處一致 |
| `password_hash` | String | NOT NULL | 三處一致 |
| `role` | String | **nullable=True**（J5 pending 時為 NULL） | ORM nullable；兩支 SQL 皆 `NOT NULL`，靠 `_ensure_j5_schema()` 的 `ALTER ... DROP NOT NULL` 拉齊 |
| `is_active` | Boolean | default True | 三處一致 |
| `authorization_status` | String(32) | NOT NULL, default `'approved'`；值域 `pending`／`approved`／`rejected` | **僅 ORM + `_ensure_j5_schema()`；兩支 SQL 皆無** |
| `last_opened_diagram_id` | Integer | FK → `user_diagrams.id` ON DELETE SET NULL, nullable | 三處皆有 |

**`users` 表沒有任何時間戳欄位。** 已對 `last_login`／`last_seen`／`lastLogin`／
`login_at`／`last_active`／`logged_in_at` 六種寫法全庫 grep，**零命中**。
`login` handler（`user_router.py:352-377`）目前只做驗證、簽 token、回傳，**不寫入任何資料**。
系統對「使用者何時登入或活動過」**零既有紀錄**。

## Frontend 元件

### 頁面（8 支）

| 元件 | LOC | 職責 | 對應能力 |
|---|---|---|---|
| `AssessmentPage.tsx` | **1,856（全 repo 最大檔）** | A3 評核完整 UI：建立評核、SSE 接收、findings 展示、建議、優化流程、PDF 匯出 | `A3` |
| `WorkspacePage.tsx` | **1,170** | A1 工作區：聊天、畫布、圖清單、分享、共編 | `A1`/`A2`/`A4` |
| `AdminPage.tsx` | 269 | 使用者清單表格（5 欄：使用者／授權狀態／角色／操作／啟用）、角色指派、啟停用、刪除 | `J3a` |
| `RolePermissionsPage.tsx` | — | 11 × 28 權限矩陣編輯 UI | `J3b` |
| `AuthorizationRequestsPage.tsx` | — | 授權申請審核 | `J3a` |
| `LoginPage.tsx` | — | 登入與註冊（含角色功能目錄） | 公開 |
| `WaitingApprovalPage.tsx` | — | pending 使用者落點，可改申請角色 | 僅需登入 |
| `ForbiddenPage.tsx` | — | 403 落點 | 公開 |

### 元件（9 支）

| 元件 | 職責 |
|---|---|
| `Layout.tsx` | 頁面外框 |
| `Sidebar.tsx` | 導覽；含 4 個 `can()` 能力判定決定顯示哪些入口 |
| `RouteGuard.tsx` | `ProtectedRoute`（登入與否）與 `CapabilityRoute`（story × action） |
| `ChatBox.tsx` | A1／A4 對話介面，接收 SSE `message`／`progress` |
| `DrawioCanvas.tsx` | draw.io 畫布嵌入與 XML 載入 |
| `DiagramPreviewPanel.tsx` | 圖形預覽面板 |
| `LensCriteriaEditor.tsx` | Lens 準則編輯器（對應 `lens_router` 五個端點） |
| `ShareModal.tsx` | 分享對話框 |
| `SuggestionRichText.tsx` | 建議文字的富文本渲染 |

### 狀態與基礎設施

| 元件 | LOC | 職責 |
|---|---|---|
| `context/AuthContext.tsx` | — | Auth Provider component。**必須與型別檔分開**（`eslint-plugin-react-refresh` 要求單一 component 匯出） |
| `context/auth-context.ts` | — | 型別定義與 `useAuth` hook；持有 permissions map，供 `CapabilityRoute` 與 `Sidebar` 判定 |
| `config/api.ts` | 34 | `API_BASE_URL`／`WS_BASE_URL`／`apiUrl()`／`wsUrl()`；由 `VITE_API_BASE_URL` build ARG 注入 |
| `hooks/useCollaboration.ts` | 64 | WebSocket 共編連線 |
| `utils/`（5 支） | — | drawio viewer URL 組裝、下載 `.drawio`、瀏覽器端 PNG 匯出、WA review PDF 匯出（html2canvas + jsPDF）、建議優化 |

## 基礎設施與流程元件

### 容器與部署

| 元件 | 職責 |
|---|---|
| `backend/Dockerfile` | `python:3.12-slim` + Node 22 + 全域 `@anthropic-ai/claude-code`；非 root（uid 10001）；HEALTHCHECK 打 `/` |
| `frontend/Dockerfile` | 多階段：`node:22-alpine` build → `nginx:alpine`；`VITE_API_BASE_URL` 為 build ARG |
| `frontend/nginx.conf` | `/api/` → `backend:8000`（含 WS upgrade、**`proxy_buffering off`**、**600s timeout**）；SPA fallback |
| `deploy/docker-compose.deploy.yml` | staging stack：`db`(postgres:16-alpine) + `backend` + `frontend`(nginx) + `cloudflared`；**只有 nginx 對外**；掛 `../schema_rbac.sql` 為 initdb |
| `deploy/docker-compose.test.yml` | Playwright e2e 用的短生命週期全端 |
| `deploy/cloudflared/config.yml` | Cloudflare Tunnel ingress |
| `docker-compose.yml`（根） | 本機開發：`postgres:15-alpine`(5432) + adminer(8080)。**版本與 staging 的 16 不一致** |

### CI/CD 與治理

| 元件 | 職責 |
|---|---|
| `.github/workflows/ci.yml` | 4 個 job：`repo-contract`／`frontend`(npm ci → lint → build)／`backend`(pip install → import smoke → unittest)／`docker-build`(buildx 建兩 image，`push: false`) |
| `.github/workflows/deploy.yml` | `ut` PR closed(merged) 觸發；self-hosted runner；`deploy` job + 失敗時的 `rollback` job（還原 last-good、開 revert PR、dispatch Deploy Doctor） |
| `.github/aw/actions-lock.json` | 鎖定 GitHub Action 版本 |
| `scripts/validate_repo_contract.py` | 379 LOC。`REQUIRED_FILES`(11)／`REQUIRED_RECORD_FILES`(15)／`REQUIRED_TEXT`／`REQUIRED_RECORD_TEXT`／`validate_docs_traditional_chinese()`／`FORBIDDEN_NEW_PATH_PARTS`／`FORBIDDEN_CONTENT_PATTERNS`。**CI 第一道關卡** |

### 10 組 gh-aw agentic workflows

| Workflow | 職責 |
|---|---|
| `code-drift-alert` | 偵測 code 與 spec 漂移 |
| `contract-guard` | repo contract 護欄 |
| `daily-digest` | 每日摘要 |
| `deploy-doctor` | 部署失敗自癒（由 `deploy.yml` rollback job dispatch） |
| `issue-triage` | issue 分類 |
| `lint-fix` | 自動修 lint |
| `pr-reviewer` | PR review |
| `release-watch` | release 監看 |
| `spec-sync` | spec 與 code 一致性 |
| `ui-regression` | 每 PR 對短生命週期 stack 跑 Playwright，結果送 Kiwi TCMS |

### 測試元件

| 元件 | 內容 |
|---|---|
| `backend/tests/helpers.py` | 在任何 DB import 前 `sys.modules.setdefault("psycopg2", MagicMock())`，改用 in-memory SQLite；每 session 以 `ensure_role_permissions_seeded(db, force=True)` 灌 308 列 |
| `backend/tests/test_*.py`（14 支） | unittest + hypothesis + `unittest.mock` |
| `frontend/tests/e2e/regression.spec.ts` | 2 個 describe／6 個 case：身分驗證（4）、RBAC 存取控制（2） |

## 元件依賴摘要

**扇入最高（被最多元件依賴）**：

1. `models.py` — 全部 service 依賴
2. `rbac.py` — 5 個 router 全部依賴（唯一的全域橫切）
3. `database.py` — 全部 router 經 `get_db()` 依賴

**扇出最高（依賴最多元件）**：

1. `wa_collab_orchestrator.py` — `design_agent` + `review_agent` + `wa_score_service` +
   `wa_lens_engine` + models
2. `review_orchestrator.py` — `wa_rule_engine` + `wa_lens_engine` + `review_agent` + models
3. `main.py` — 5 router + database + design_agent

**零扇出（葉節點，最容易測試與替換）**：`wa_rule_engine.py`、`wa_lens_engine.py`、
`llm_limits.py`、`rbac_seed_data.py`

**跨行程邊界的元件**（失敗會影響大範圍）：`design_agent.py` 與 `review_agent.py`
都經 `claude-agent-sdk` spawn 外部 CLI；若 backend 容器缺 Node 22 或 Claude Code CLI，
A1 產圖與 A3 建議階段**同時失效**（A3 會降級為 `rules_only`，A1 則無法產圖）。
