# 元件清冊（Component Inventory）

> Reverse Engineering 合成產物｜repo `cloud`｜HEAD `c3de2c8`｜intent `260819-cost-finops`｜mode **Modify overlay for C1**（A1／A3 元件保留並訂正狀態；C1 以 placeholder／ABSENT 列明示缺口）

## Frontend 元件

| 元件 | 路徑 | 職責 | 主要依賴 | 健康 |
|---|---|---|---|---|
| `Layout` | `frontend/src/components/Layout.tsx` | 全域殼：掛載 Sidebar＋內容區；包 `NavChromeProvider` | `Sidebar`、`NavChromeContext` | healthy |
| `NavChromeContext` | `frontend/src/components/NavChromeContext.tsx` | **NEW**：側欄收合狀態；`localStorage` `cloud360.nav.sidebarCollapsed` | `Layout`、`Sidebar`、`WorkspacePage` | healthy |
| `Sidebar` | `frontend/src/components/Sidebar.tsx` | 導覽、品牌、登出；**可收合**（展開 `w-64`／收合 `w-14`）；兩組「架構」「系統管理」；可見條件 `canArch`／A3／J3a／J3b；**無 C 組、無 `can('C1')`** | `useAuth`、`useLayoutNav`、`NavLink` | healthy（C1 掛點 ABSENT） |
| `WorkspacePage` | `frontend/src/pages/WorkspacePage.tsx` | A1：聊天、產生、collab、成功卡 CTA（編輯／IaC coming-soon／WA）；**無成本 CTA** | `ChatBox`、`DrawioCanvas`、architecture／collab API | healthy |
| `AssessmentPage` | `frontend/src/pages/AssessmentPage.tsx` | A3：reviews／lens、選圖、provider `<select>`（雲別覆寫） | `DiagramPreviewPanel`、reviews／lens／collab API | healthy |
| `DrawioCanvas` | `frontend/src/components/DrawioCanvas.tsx` | diagrams.net iframe 橋：init、load、autosave、**save／exit**；headerBanner 僅檢視／審核琥珀橫幅 | embed.diagrams.net | healthy（Undo 未重驗） |
| `ChatBox` | `frontend/src/components/ChatBox.tsx` | A1 提示輸入與訊息流 | `WorkspacePage` | healthy |
| `DiagramPreviewPanel` | `frontend/src/components/DiagramPreviewPanel.tsx` | A3／唯讀圖預覽 | Draw.io 或靜態預覽 | healthy |
| `RouteGuard` | `frontend/src/components/RouteGuard.tsx` | 路由級權限；`CapabilityRoute` 未以 `C1` 呼叫 | `auth-context` | healthy |
| `ShareModal` | `frontend/src/components/ShareModal.tsx` | 圖分享 UI | collab share API | healthy |
| `LensCriteriaEditor` | `frontend/src/components/LensCriteriaEditor.tsx` | Lens 準則編輯 | lens API | healthy |
| `RolePermissionsPage` | `frontend/src/pages/RolePermissionsPage.tsx` | 權限矩陣；支柱標籤含 `C: '成本與 FinOps'`、`C1`／`C2`／`C3`——**不是產品頁** | `/api/auth/role-permissions` | at-risk（標籤領先實作） |
| `AdminPage` | `frontend/src/pages/AdminPage.tsx` | 使用者管理；**NEW** 最後活動欄、分頁 | `/api/auth/list`、`LastActivityCell`、`PaginationControl` | healthy |
| `LastActivityCell` | `frontend/src/components/LastActivityCell.tsx` | **NEW**：顯示 `last_activity_at` | Admin | healthy |
| `PaginationControl` | `frontend/src/components/PaginationControl.tsx` | **NEW**：Admin 列表分頁 | Admin | healthy |
| `auth-context` | `frontend/src/context/*` | token、user、`can`／`canArch` | `/api/auth/me` | healthy |
| **Cost page（placeholder）** | **ABSENT**（無 `CostPage.tsx`／`FinOpsPage.tsx`／`TcoPage.tsx`；`App.tsx` 無 `path="/cost"`） | 應承載 TCO／預算 UI | 應依賴不存在的 `/api/cost*` | **degraded／absent** |
| **Notification primitive（placeholder）** | **ABSENT**（無 `NotificationCenter`／inbox；僅行程內 toast） | 應承載超支／預算警示 | 無 DB 表、無 API | **degraded／absent** |

`frontend/src/pages/` 僅 8 檔。Toast 存在於 `WorkspacePage`、`AdminPage`、`RolePermissionsPage`、`AuthorizationRequestsPage`——行程內、不入 DB，不可當 inbox。

## Backend 元件

| 元件 | 路徑 | 職責 | 主要依賴 | 健康 |
|---|---|---|---|---|
| `main` app | `backend/main.py` | 組裝 middleware、**五組** router、startup；`configure_provider_env` | FastAPI、DB init | healthy |
| `agent_router` | `backend/services/agent_router.py` | 架構產生 HTTP 面 | `design_agent`、`prompt_guard`、`wa_collab_orchestrator` | healthy |
| `prompt_guard` | `backend/services/prompt_guard.py` | **NEW**：平台自我竄改預檢；命中回 `REFUSAL_MESSAGE` | `agent_router` | healthy |
| `llm_provider` | `backend/services/llm_provider.py` | **NEW**：`LLM_PROVIDER`（OpenRouter 或 claude CLI） | `main` startup | healthy |
| `design_agent` | `backend/services/design_agent.py` | LLM 產生；`DRAW_INPUT_SCHEMA` 無 sku／hours | claude-agent-sdk、prompts | healthy |
| `diagram_builder` | `backend/services/diagram_builder.py` | 結構 → mxGraph XML；exit／entry ports；n8n Basic Auth 取 SVG | n8n webhook（可選） | healthy（parent=`"1"` 殘項） |
| `collab_router` | `backend/services/collab_router.py` | 圖 CRUD、chat、share、WS | ORM、auth | healthy |
| `review_router` | `backend/services/review_router.py` | 審核 API、detect-provider、PNG export | orchestrator、DB、httpx | healthy |
| `wa_rule_engine` | `backend/services/wa_rule_engine.py` | `parse_diagram_summary`；`detect_provider`；`COST-*` 啟發式（**非 TCO**） | 純 XML，不連 AWS API、不讀 DB | at-risk（易被誤認為成本能力；`COST-*` 零測試） |
| `review_orchestrator`／`wa_*` | `backend/services/review_*`、`wa_*` | A3 審核編排與評分 | LLM、lens engine | healthy |
| `lens_router`／`lens_service` | `backend/services/lens_*` | Lens CRUD／驗證／建議 | `lenses/*.json`、DB | healthy |
| `user_router` | `backend/services/user_router.py` | 認證與 RBAC 管理；list 分頁＋`last_activity_at` | `auth`、`rbac`、`activity` | healthy |
| `activity` | `backend/services/activity.py` | **NEW**：最後活動時間 | `users.last_activity_at` | healthy |
| `auth`／`rbac` | `backend/services/auth.py`、`rbac.py`、`rbac_seed_data.py` | JWT／password、權限評估；`CANONICAL_ROLES` 含 `FinOps_Analyst`；C1 種子 PRESENT、C1 守衛 ABSENT | PostgreSQL | at-risk（種子領先產品面） |
| **Cost calculator（placeholder）** | **ABSENT**（檔名／符號 `cost_calculator` 0 命中） | ADR-0006 點名的 PBT 落點；模組不存在故 PBT 為 N/A | 應依賴 pricing client＋圖資源 | **degraded／absent** |
| **Pricing client（placeholder）** | **ABSENT**（無 `pricing_client`、無 `pricing.amazonaws`／`cloudbilling`／`retailprices`、無 boto3） | 應查 public price list 或靜態表 | 無 httpx 價目呼叫 | **degraded／absent** |

## 外部與基礎設施元件

| 元件 | 角色 |
|---|---|
| PostgreSQL | 使用者、圖（僅 XML blob）、chat、reviews、role_permissions；**無** cost／budget／inbox 表 |
| embed.diagrams.net | 互動圖編輯運行時 |
| OpenRouter 或 claude CLI | Agent／review 推理（`LLM_PROVIDER`） |
| n8n webhook | 架構圖 SVG 圖示（Basic Auth）；失敗降級灰底 |
| Staging host + Cloudflare Tunnel | `deploy/` + `deploy.yml` → `cloud360.danniel.cc` |
| Kiwi TCMS | 測案管理（`tcms.danniel.cc`，外部 `dc-infra`） |
| 雲端價目 API | **ABSENT**（未整合） |

元件耦合觀察：A1 品質仍同時依賴 `design_agent`、`diagram_builder`、`DrawioCanvas`。C1 若落地，必須在「圖契約（SKU／規格／時數）」與「計價 port」之間劃清邊界，避免把 `wa_rule_engine` 的 `COST-*` 或 A3 `detect_provider` 接成假的 TCO 管線。
