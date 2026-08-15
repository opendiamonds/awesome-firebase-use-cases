# API Documentation — Cloud-360

> 逆向工程產出。基準 commit `8c90f40372ac810cc8f6ef41c46fc7a723031a1e`（branch `ut`，2026-08-08）。
> 端點清單由掃描 `backend/services/*_router.py` 逐條核出，共 **46 個**。

## API 面總覽

| 介面類型 | 數量 | 位置 | 對外 |
|---|---|---|---|
| REST + SSE（FastAPI） | 45 | `backend/services/*_router.py` | 是 |
| WebSocket | 1 | `backend/services/collab_router.py` | 是 |
| 行程內 MCP server | 1 tool | `backend/services/design_agent.py` | **否**（僅供 Agent SDK 內部使用） |

Router 掛載（`backend/main.py`）：

| Router | 前綴 |
|---|---|
| `agent_router` | `/api/architecture` |
| `review_router` | `/api/architecture` |
| `lens_router` | `/api/architecture` |
| `user_router` | `/api/auth` |
| `collab_router` | `/api/collab` |

**注意**：三個 router 共用 `/api/architecture` 前綴，端點命名空間靠子路徑區分
（`/generate*`、`/reviews*`、`/diagrams*`、`/lens/*`）。新增端點時要留意跨 router 的路徑衝突。

**前端 client 面**：**無集中式 API client**。所有頁面與元件直接呼叫原生 `fetch()`
搭配 `frontend/src/config/api.ts` 的 `apiUrl()`／`wsUrl()`，手動組
`Authorization: Bearer ${token}` header。共 **32 處呼叫點**散落在 8 支頁面與元件。

## 認證與授權契約

### 認證

- **機制**：JWT Bearer token，HTTP `Authorization: Bearer <token>` header。
- **演算法**：HS256。
- **效期**：8 小時（`ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8`）。
- **payload**：`sub` 為 username，`exp` 為到期時間。
- **驗證流程**（`auth.get_current_user`）：解 JWT → 取 `sub` → 查 `users` →
  檢查 `is_active`（停用者 403）→ 回傳 `User` 物件。JWT 無效或過期一律 401
  並帶 `WWW-Authenticate: Bearer`。

### 授權

授權一律以 guard 工廠注入，三種形式：

| Guard | 語意 |
|---|---|
| `get_current_user` | 只要求已登入，不檢查能力 |
| `require_story_action("<story>", "<action>")` | 檢查指定 story 的指定 action |
| `require_arch_action("<action>")` | 架構圖三合一（`A1`／`A2`／`A4`），內部改讀 `A1` |

**判定三關（順序固定）**：

1. `authorization_status != 'approved'` → 403「帳號尚未通過管理員授權」。
   **這一關在任何矩陣查詢之前**，pending／rejected 使用者一律無業務權限。
2. role 非 canonical role（含經 `ROLE_ALIASES` 正規化後）→ 拒絕。
3. 查 `role_permissions` 的 `(role, story_id)` 列：
   - `view` → `can_view OR can_edit OR can_review`
   - `edit` → `can_edit`
   - `review` → `can_review`

**錯誤碼慣例**：401 = 憑證問題；403 = 已登入但權限不足或帳號停用／未授權；
404 = 資源不存在或無權限存取（`get_accessible_diagram` 把「無權限」也回 404，避免資源探測）。

## 端點完整清單

### 根與健康檢查

| # | Method | Path | Handler | 授權 | 用途 |
|---|---|---|---|---|---|
| 1 | GET | `/` | `read_root` | 無 | health check（Dockerfile HEALTHCHECK 目標） |

### A1 架構產圖（`agent_router`）

| # | Method | Path | Handler | 授權 | 用途 |
|---|---|---|---|---|---|
| 2 | POST | `/api/architecture/generate` | `chat_and_generate` | `require_arch_action("edit")` | A1 對話產圖，SSE |
| 3 | POST | `/api/architecture/generate-wa-collab` | `chat_and_generate_wa_collab` | `require_arch_action("edit")` | A1↔A3 雙 agent 協作產圖，SSE |

### A3 評核（`review_router`）

| # | Method | Path | Handler | 授權 | 用途 |
|---|---|---|---|---|---|
| 4 | POST | `/api/architecture/reviews/detect-provider` | `detect_review_provider` | `A3.edit` | 從 XML 偵測雲別 |
| 5 | POST | `/api/architecture/reviews` | `create_review` | `A3.edit` | 建立評核（選圖或上傳 XML），SSE |
| 6 | POST | `/api/architecture/reviews/commit-collab` | `commit_collab_review_endpoint` | `A3.edit` | 將協作結果落為 review |
| 7 | GET | `/api/architecture/reviews` | `list_reviews` | `A3.view` | 評核清單 |
| 8 | GET | `/api/architecture/reviews/{review_id}` | `get_review` | `A3.view` | 單筆評核 |
| 9 | POST | `/api/architecture/reviews/{review_id}/persist-diagram` | `persist_review_diagram` | `A3.edit` | 將評核用 XML 建檔為圖 |
| 10 | DELETE | `/api/architecture/reviews/{review_id}` | `delete_review` | `A3.edit` | 刪除／封存評核 |
| 11 | POST | `/api/architecture/diagrams/render-png` | `render_diagram_png` | `A3.view` | 伺服端 PNG 轉檔 |
| 12 | POST | `/api/architecture/reviews/{review_id}/retry-suggestions` | `retry_review_suggestions` | `A3.edit` | 重試建議生成（狀態須為 `rules_only`） |

### Lens 編輯（`lens_router`）

| # | Method | Path | Handler | 授權 | 用途 |
|---|---|---|---|---|---|
| 13 | GET | `/api/architecture/lens/active` | `get_active_lens` | `A3.review` | 讀取現行 Lens（`?provider=`） |
| 14 | PUT | `/api/architecture/lens/active` | `put_active_lens` | `A3.review` | 更新現行 Lens |
| 15 | GET | `/api/architecture/lens/new-question-template` | `new_question_template` | `A3.review` | 新問題模板 |
| 16 | POST | `/api/architecture/lens/suggest-improvement-plan` | `post_suggest_improvement` | `A3.review` | AI 建議改善計畫 |
| 17 | POST | `/api/architecture/lens/validate` | `post_validate_lens` | `A3.review` | Lens JSON 驗證 |

### 身分、註冊與使用者管理（`user_router`）

| # | Method | Path | Handler | 授權 | 用途 |
|---|---|---|---|---|---|
| 18 | GET | `/api/auth/roles/catalog` | `roles_catalog` | **公開（無 guard）** | 註冊頁角色功能目錄，動態源自 `role_permissions` |
| 19 | POST | `/api/auth/register` | `register` | **公開** | 註冊；建 `authorization_status='pending'` 使用者 + 授權申請 |
| 20 | POST | `/api/auth/login` | `login` | **公開** | 登入；回 JWT + role + authorization_status |
| 21 | GET | `/api/auth/me` | `get_me` | `get_current_user` | 目前身分 + 完整 permissions map + pending_request |
| 22 | PATCH | `/api/auth/me/authorization-request` | `patch_my_authorization_request` | `get_current_user` | pending 使用者改申請角色 |
| 23 | GET | `/api/auth/roles` | `list_canonical_roles` | `get_current_user` | 回 `CANONICAL_ROLES` 與 `STORY_IDS` |
| 24 | GET | `/api/auth/list` | `list_users` | `J3a.view` | Admin 頁使用者清單 |
| 25 | GET | `/api/auth/authorization-requests` | `list_authorization_requests` | `J3a.view` | 授權申請清單（`?status=`） |
| 26 | POST | `/api/auth/authorization-requests/{request_id}/approve` | `approve_authorization_request` | `J3a.edit` | 核准（受 BR-04 限制） |
| 27 | POST | `/api/auth/authorization-requests/{request_id}/reject` | `reject_authorization_request` | `J3a.edit` | 駁回 |
| 28 | PUT | `/api/auth/{user_id}/active` | `update_user_active` | `J3a.edit` | 啟用／停用 |
| 29 | DELETE | `/api/auth/{user_id}` | `delete_user` | `J3a.edit` | 硬刪除（擁有圖表時 403） |
| 30 | PUT | `/api/auth/{user_id}/role` | `update_user_role` | `J3a.edit` | 指派角色 |
| 31 | GET | `/api/auth/role-permissions` | `get_role_permissions` | `J3b.view` | 讀權限矩陣 |
| 32 | PUT | `/api/auth/role-permissions` | `put_role_permissions` | `J3b.edit` | 寫權限矩陣（`A1`/`A2`/`A4` 三 story 同步寫入） |
| 33 | POST | `/api/auth/role-permissions/reset-defaults` | `reset_role_permissions_defaults` | `J3b.review` | 重設為預設矩陣 |

### 圖與共編（`collab_router`）

| # | Method | Path | Handler | 授權 | 用途 |
|---|---|---|---|---|---|
| 34 | WS | `/api/collab/ws/{workspace_id}` | `websocket_endpoint` | **無 guard** | 架構圖即時共編廣播 |
| 35 | GET | `/api/collab/users` | `get_users` | `require_arch_action("edit")` | 分享對象清單 |
| 36 | GET | `/api/collab/diagrams` | `list_my_diagrams` | arch `view` | 我的加上被分享的圖 |
| 37 | GET | `/api/collab/workspace/bootstrap` | `workspace_bootstrap` | arch `view` | 還原 last_opened 與該圖聊天 |
| 38 | PUT | `/api/collab/workspace/last-opened` | `set_last_opened` | arch `view` | 更新 `users.last_opened_diagram_id` |
| 39 | GET | `/api/collab/diagrams/{diagram_id}/chat` | `get_diagram_chat` | arch `view` | 讀 A4 聊天 |
| 40 | PUT | `/api/collab/diagrams/{diagram_id}/chat` | `save_diagram_chat` | arch `edit` | 存 A4 聊天 |
| 41 | DELETE | `/api/collab/diagrams/{diagram_id}/chat` | `clear_diagram_chat` | arch `edit` | 清空聊天（不刪圖） |
| 42 | GET | `/api/collab/diagrams/{diagram_id}` | `get_diagram` | arch `view` | 讀單圖 |
| 43 | POST | `/api/collab/diagrams` | `create_diagram` | arch `edit` | 建圖 |
| 44 | PUT | `/api/collab/diagrams/{diagram_id}` | `update_diagram` | arch `edit` | 更新圖 |
| 45 | DELETE | `/api/collab/diagrams/{diagram_id}` | `delete_diagram` | arch `edit` | 刪圖 |
| 46 | POST | `/api/collab/diagrams/{diagram_id}/share` | `share_diagram` | arch `edit` | 分享給使用者 |

### 端點授權分布摘要

| 授權層級 | 端點數 | 端點 |
|---|---|---|
| 完全公開 | 4 | #1（health）、#18、#19、#20 |
| 僅需登入 | 3 | #21、#22、#23 |
| 需 `A3` 能力 | 14 | #4–#17 |
| 需架構圖能力 | 14 | #2、#3、#35–#46 |
| 需 `J3a` 能力 | 7 | #24–#30 |
| 需 `J3b` 能力 | 3 | #31–#33 |
| **無任何 guard 的業務端點** | **1** | **#34（WebSocket）** |

## SSE 串流契約

三個端點回傳 `text/event-stream`（#2、#3、#5，加上 #12 重試）。
共同形狀：每個 chunk 為 `data: {JSON}\n\n`，JSON 一律含 `type` 欄位，
序列化時 `ensure_ascii=False`（中文不轉義）。

### A1 產圖（`POST /api/architecture/generate`）

模組 docstring 明載「契約（前端依賴，請勿變更）」：

- **request**：`{ messages: [{role, content}], current_xml?: string }`
- **response 事件 type**：`message`／`progress`／`xml`／`error`

### A1↔A3 協作（`POST /api/architecture/generate-wa-collab`）

- **request**：`{ messages, current_xml?, provider?, diagram_id?, persist_review?,
  baseline_findings?, baseline_overall_score? }`
- **response 事件 type**：`message`／`progress`／`xml_preview`／`score`／`complete`／`error`
- `score` 事件額外帶 `round`、`overall_score`、`pillar_scores`、`findings`、
  `high_risk_count`、`passed`
- 最多 2 輪；目標為 lens 總分 ≥ 80（`TARGET_SCORE`）且無 `HIGH_RISK`

### A3 評核（`POST /api/architecture/reviews`）

- **事件序**：`rules_done` → `lens_done` → 多個 `suggestion_delta` → `complete`；
  任一階段可改送 `error`
- `suggestion_delta` 帶 `content` 與 `review_id`，是逐塊串流的建議文字
- 逾時保護：Review Agent 75 秒（`AGENT_TIMEOUT_SEC`），lens agent 90 秒
  （`LENS_AGENT_TIMEOUT_SEC`）。逾時**不中斷串流**，改以 `rules_only` 狀態收尾
- 重試端點（#12）若狀態非 `rules_only`，回 `error` 且 `code` 為 `invalid_status`

### 基礎設施要求（不可省略）

`frontend/nginx.conf` 為 SSE 特別設定：**`proxy_buffering off`** 與 **600 秒 timeout**。
任何反向代理層變更都必須保留這兩項，否則串流會被緩衝或提前中斷。

## WebSocket 契約

- **路徑**：`/api/collab/ws/{workspace_id}`
- **用途**：架構圖即時共編廣播
- **前端**：`frontend/src/hooks/useCollaboration.ts`（64 LOC）
- **nginx**：`/api/` location 已設 WS upgrade header
- **授權**：**無**。連線層不做 JWT 檢查，是 46 個端點中唯一無 guard 的業務端點。
  這是已登記的安全債（見 `code-quality-assessment.md` 的 T8）

## 前端路由與權限對照

`frontend/src/App.tsx`：

| 路由 | 元件 | Guard |
|---|---|---|
| `/login` | `LoginPage` | 無 |
| `/403` | `ForbiddenPage` | 無 |
| `/waiting-approval` | `WaitingApprovalPage` | `ProtectedRoute` |
| `/workspace` | `WorkspacePage` | `ProtectedRoute` + `CapabilityRoute storyId="A1" action="view"` |
| `/assessment` | `AssessmentPage` | `A3.view` |
| `/admin/users` | `AdminPage` | `J3a.view` |
| `/admin/authorization-requests` | `AuthorizationRequestsPage` | `J3a.view` |
| `/admin/role-permissions` | `RolePermissionsPage` | `J3b.view` |
| `/admin` | redirect → `/admin/users` | — |
| `/` 與 `*` | `DefaultRedirect` | 依序 pending → `canArch('view')` → `A3` → `J3a` → `J3b` → `/403` |

**前端 guard 不是安全邊界**，只是體驗優化；每次業務呼叫後端都會重跑完整判定。

## 資料契約

### `UserSchema`（`user_router.py:111-120`）

`GET /api/auth/list`（#24）的回應元素，也是 Admin 頁表格的資料來源：

| 欄位 | 型別 | 備註 |
|---|---|---|
| `id` | int | |
| `username` | str | |
| `role` | Optional[str] | pending 使用者為 `null` |
| `is_active` | bool | |
| `authorization_status` | str | default `'approved'` |
| `requested_role` | Optional[str] | 由 `_pending_request_for_user()` 額外查得 |

**前端鏡像**：`AdminPage.tsx:6-13` 的 `DbUser` interface 是**手寫副本**，
無型別產生機制，一致性只靠人工維持。Admin 表格目前 **5 欄**：
使用者 / 授權狀態 / 角色 / 操作 / 啟用。

### `User.to_dict()`

回傳 6 個欄位，**不含 `password_hash`**。

### 角色與 story 常數

- `GET /api/auth/roles`（#23）回傳 `CANONICAL_ROLES`（11 個）與 `STORY_IDS`（28 個）。
- `STORY_IDS` 於 `rbac.py:37` **由 `DEFAULT_ROLE_PERMISSIONS` 動態導出**，非硬編碼。

## API 面的已知缺口

1. **零 HTTP 層測試**：repo 內沒有任何測試使用 `TestClient`，
   **46 個端點沒有一個被實際打過**。所有測試都在 service 層以下。
2. **WebSocket 無驗證**（#34）。
3. **公開端點可觸發 seed**：`roles_catalog`（#18，公開無驗證）在回應前呼叫
   `ensure_role_permissions_seeded(db, force=False)` —— 匿名請求可觸發 seed 邏輯。
   實際影響有限（`force=False` 時表非空即 return），但這是一條匿名可達的寫入路徑。
4. **無 API 版本化**：路徑無 `/v1/` 之類的版本段。契約變更沒有並存機制，
   靠 docstring 內的「請勿變更」註記與人工紀律維持。
5. **無 OpenAPI 契約測試**：FastAPI 自動產生 `/docs` 與 `/openapi.json`，
   但 CI 無任何 schema 快照或契約回歸檢查。
6. **死碼 guard**：`auth.py` 的 `RoleChecker` 三個常數（`require_admin`、
   `require_architect`、`require_any_user`）**無任何端點使用**，是與 `rbac` 並行的
   舊粗粒度授權機制殘留。新端點不應使用。
