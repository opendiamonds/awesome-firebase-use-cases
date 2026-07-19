# Unit of Work

> Cloud-360 inception — logical units of work for Construction.  
> Brownfield monolith：以 Module 切分；部署上仍為單一 backend + frontend。  
> Scope of this document: units that cover **developed stories A1 / A2 / A4 / A5 / J**.

## 中文版

### 1. 拆分原則

| 原則 | 說明 |
|---|---|
| 部署模型 | **Monolith**：一個 FastAPI 服務 + 一個 React SPA；Unit = 邏輯 Module，非獨立 microservice |
| 邊界依據 | 對齊 `frontend-backend-specification.md` 的 API 模組：`/api/architecture`、`/api/collab`、`/api/auth` |
| Story 對齊 | 已開發 story 各對一開發 unit；J1–J5 合併為單一 Identity／RBAC unit（J5 為新增目標） |
| 產品權限語意 | Admin 矩陣把 **A1＝A2＝A4** 視為「架構圖生成」同一欄（見 `role-permission-design.md`）；**開發 unit 仍分開**，方便 Construction 追溯 |
| 未涵蓋 | A3、B–H 尚未進 Construction，本文件不建立對應 unit（之後 Units Generation 再擴充） |

### 2. Unit 一覽

| Unit ID | 名稱 | 類型 | Stories | Construction 目錄（現況） |
|---|---|---|---|---|
| `U-J` | Identity & RBAC | Module | J1, J2, J3, J4, J5 | `construction/j/`（`code/` + `functional-design/`）+ `plans/role-permission-*.md`、`j5-*.md` |
| `U-A1` | Architecture Design Generation | Module | A1 | `construction/a1/`（`code/` + `functional-design/`）+ `plans/a1-*.md` |
| `U-A2` | Canvas Collaborative Editing | Module | A2 | `construction/a2/`（`code/` + `functional-design/`） |
| `U-A4` | Chat & Last-Opened Persistence | Module | A4 | `construction/a4/`（`code/` + `functional-design/`）+ `plans/a4-*.md` |
| `U-A5` | Diagram Sharing & Real-time Collab | Module | A5 | `construction/a5/`（`code/` + `functional-design/`；實作併在 collab） |

### 3. Unit 定義

#### U-J — Identity & RBAC

- **職責**：登入／JWT、角色 allowlist、角色×Story 細項矩陣、Admin 使用者與細項 UI、Sidebar／路由可見性；含註冊無預設角色、授權申請核准、刪除使用者（J5）。
- **擁有實體**：`users`、`role_permissions`、`role_authorization_requests`；API 前綴 `/api/auth`。
- **主要程式**：`user_router.py`、`rbac.py`；前端 AuthContext、Admin／AuthorizationRequests／WaitingApproval。
- **狀態**：J1–J5 Core done；WebSocket JWT／手動 E2E 待補。

#### U-A1 — Architecture Design Generation

- **職責**：自然語言 → Agent SDK／OpenRouter → draw.io XML；SSE 串流回前端。
- **擁有介面**：`POST /api/architecture/generate`（及相關 architecture 路由）。
- **主要程式**：`agent_router.py`、`design_agent.py`、`diagram_builder.py`、prompts；前端 ChatBox 產圖流程。
- **狀態**：Code done；FD 已補；待手動 E2E。

#### U-A2 — Canvas Collaborative Editing

- **職責**：畫布局部 AI 編輯、連線保留、架構圖 CRUD、多檔切換、進入工作區載入草稿（與 A4 bootstrap 銜接）。
- **擁有介面**：`/api/collab/diagrams` CRUD；前端 WorkspacePage／DrawioCanvas 編輯與儲存。
- **主要程式**：collab diagram APIs、WorkspacePage diagram selector、agent partial-update 路徑。
- **狀態**：核心完成；FD 已補；框選抽取、AI Undo、游標等 AC 未滿（游標屬 A5）。

#### U-A4 — Chat & Last-Opened Persistence

- **職責**：`user × diagram` 聊天持久化、清空對話、`last_opened_diagram_id`、workspace bootstrap。
- **擁有實體**：`user_diagram_chats`、`users.last_opened_diagram_id`。
- **主要程式**：collab chat／bootstrap／last-opened endpoints；前端進場還原。
- **狀態**：Code done；FD 已補；待手動 E2E。

#### U-A5 — Diagram Sharing & Real-time Collab

- **職責**：分享彈窗與 `diagram_shares`、WebSocket XML 廣播、協作／單機狀態、檢視／編輯／審核歡迎詞隔離。
- **擁有實體／介面**：`diagram_shares`；`WS /api/collab/ws/{workspace_id}`；ShareModal。
- **主要程式**：`collab_router` WebSocket／share API；前端連線狀態列。
- **狀態**：分享＋XML 同步已有；FD 已補；多人游標未做；WS JWT 強化待補。

### 4. 文字結構圖

```text
[U-J Identity & RBAC]
        |
        +-- auth for all APIs / UI gates
        |
        v
[U-A1 Architecture Design] ---- XML drafts ----> [U-A2 Canvas Editing]
                                                      |
                                                      +-- diagram_id --> [U-A4 Chat Persistence]
                                                      |
                                                      +-- share / WS --> [U-A5 Sharing & Realtime]
```

---

## English Version

### 1. Decomposition principles

| Principle | Detail |
|---|---|
| Deployment model | **Monolith**: one FastAPI service + one React SPA; a Unit is a logical Module, not a microservice |
| Boundary basis | Align with API modules in `frontend-backend-specification.md`: `/api/architecture`, `/api/collab`, `/api/auth` |
| Story alignment | Each developed story maps to a development unit; J1–J5 form one Identity/RBAC unit (J5 is a new target) |
| Product permission semantics | Admin matrix treats **A1 = A2 = A4** as one “Architecture generation” column; **development units stay separate** for Construction traceability |
| Out of scope here | A3 and pillars B–H have no Construction units yet |

### 2. Unit catalogue

| Unit ID | Name | Kind | Stories | Construction path (today) |
|---|---|---|---|---|
| `U-J` | Identity & RBAC | Module | J1–J5 | `construction/j/` (`code/` + `functional-design/`) + role-permission / j5 plans |
| `U-A1` | Architecture Design Generation | Module | A1 | `construction/a1/` (`code/` + `functional-design/`) + `plans/a1-*.md` |
| `U-A2` | Canvas Collaborative Editing | Module | A2 | `construction/a2/` (`code/` + `functional-design/`) |
| `U-A4` | Chat & Last-Opened Persistence | Module | A4 | `construction/a4/` (`code/` + `functional-design/`) + `plans/a4-*.md` |
| `U-A5` | Diagram Sharing & Real-time Collab | Module | A5 | `construction/a5/` (`code/` + `functional-design/`; code under collab) |

### 3. Unit definitions

See Chinese section for full responsibility / entity / code ownership; English names and story IDs are identical (`U-J` … `U-A5`).

### 4. Text structure

```text
[U-J Identity & RBAC]
        |
        +-- auth for all APIs / UI gates
        |
        v
[U-A1 Architecture Design] ---- XML drafts ----> [U-A2 Canvas Editing]
                                                      |
                                                      +-- diagram_id --> [U-A4 Chat Persistence]
                                                      |
                                                      +-- share / WS --> [U-A5 Sharing & Realtime]
```
