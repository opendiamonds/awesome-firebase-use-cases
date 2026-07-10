# Cloud-360 部署環境設定說明（Deploy README）

> 給要把本專案部署到**另一個環境**（staging／正式／新機器）的人。  
> 前後端分服務部署時，請特別核對 API／CORS／資料庫三塊。

---

## 中文版

### 1. 建議調整的環境變數（.env）

#### 1.1 後端 `backend/.env`

範本：`backend/.env.example` → 複製為 `backend/.env` 後修改。

| 變數 | 本機常見值 | 新環境建議 |
|---|---|---|
| `APP_ENV` | `local` | `staging`／實際環境名（勿用路徑含 `prod`／`production` 的目錄名，見 repo contract） |
| `DATABASE_URL` | `postgresql://postgres:postgres@localhost:5432/cloud360` | 改成該環境 PostgreSQL 連線字串 |
| `JWT_SECRET` | 範本預設字串 | **務必更換**成長隨機字串 |
| `CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | 改成**前端實際網址**（逗號分隔，勿結尾斜線）例：`https://app.example.com` |
| `OPENROUTER_API_KEY` | 本機金鑰 | 該環境專用金鑰（勿提交進 git） |
| `ANTHROPIC_BASE_URL` | `https://openrouter.ai/api` | 通常維持；與 OpenRouter 接法一致 |
| `ANTHROPIC_AUTH_TOKEN` | 可空（啟動時可由 OPENROUTER 映射） | 依部署方式填入或留空讓程式映射 |
| `ANTHROPIC_API_KEY` | **必須為空** | 維持空，避免 SDK 走 Anthropic 直連 |
| `LLM_MODEL`／`ANTHROPIC_DEFAULT_SONNET_MODEL` | 範本模型 slug | 依該環境要用的模型調整 |
| `N8N_WEBHOOK_URL` | 選填 | 有用動態 icon 再填 |

#### 1.2 前端 `frontend/.env`（build 時注入）

範本：`frontend/.env.example` → 複製為 `frontend/.env` 或在 CI 注入同名變數。

| 變數 | 本機常見值 | 新環境建議 |
|---|---|---|
| `VITE_API_BASE_URL` | `http://localhost:8000` | 改成**後端 API 根 URL**（勿結尾斜線）例：`https://api.example.com` |
| `VITE_WS_BASE_URL` | 可不設 | 可不設：會由 API base 自動 `http→ws`／`https→wss`；若 WS 與 HTTP 不同網域再單獨設定 |

建置範例：

```bash
cd frontend
cp .env.example .env
# 編輯 VITE_API_BASE_URL=https://api.example.com
npm ci
npm run build
```

> Vite 變數在 **build／dev 啟動時**寫進前端包；改 `.env` 後需重新 build 或重啟 `npm run dev`。

#### 1.3 前後端對照（必對齊）

```text
前端 VITE_API_BASE_URL  ──►  後端實際對外 URL
前端瀏覽器 Origin       ──►  必須出現在後端 CORS_ORIGINS
前端 WS（自動或 VITE_WS_BASE_URL）──►  後端同一主機的 /api/collab/ws/...
```

---

### 2. 資料庫：要建哪些表、預設資料怎麼塞

#### 2.1 建議做法（一支腳本搞定）

**SQL 檔位置（repo 根目錄）：**

```text
schema_rbac.sql
```

補充說明：`aidlc-docs/construction/plans/schema-rbac-notes.md`  
（`schema.sql` 僅核心 DDL 參考，**完整新環境請用 `schema_rbac.sql`**。）

執行：

```bash
# 先設好該環境的 DATABASE_URL
export DATABASE_URL='postgresql://USER:PASSWORD@HOST:5432/DBNAME'

psql "$DATABASE_URL" -f schema_rbac.sql

# 若 DB 在 Docker 內，範例：
# docker exec -i <db-container> psql -U postgres -d cloud360 < schema_rbac.sql
```

#### 2.2 這支 SQL 會建立的表／欄位

| 區塊 | 物件 | 用途 |
|---|---|---|
| A | `users` | 帳號、角色、啟用狀態 |
| A | `user_diagrams` | 架構圖 XML |
| A | `diagram_shares` | 圖分享（多對多） |
| B | `users.last_opened_diagram_id` | 上次開啟的圖 |
| B | `user_diagram_chats` | 使用者×圖 的聊天紀錄（A4） |
| C | `role_permissions` | 角色 × Story 的檢視／編輯／審核 |
| D | 預設使用者 `admin` | 見下方 |

#### 2.3 預設資料會塞什麼

執行 `schema_rbac.sql` 後：

1. **`role_permissions`**：寫入設計預設矩陣（約 **308** 列，11 角色 × 各 Story）。  
2. **`users`**：若不存在則建立  
   - 帳號：`admin`  
   - 密碼：`admin123`（**上線後請立刻改密碼**）  
   - 角色：`Platform_Admin`（可進「使用者角色」「角色細項權限」）

後端若在**空庫**啟動，`init_db()` 也會：建表、必要時 seed `role_permissions`、確保有 `admin`。  
**新環境仍建議先跑 `schema_rbac.sql`**，行為與文件一致、不依賴啟動順序。

#### 2.4 重要：若沒跑 seed，角色細項會是「全空」

| 情況 | 結果 |
|---|---|
| 只建空表、**沒有**插入 `role_permissions` | 矩陣**全空**（所有角色對所有功能都無檢視／編輯／審核）→ Sidebar 幾乎看不到功能、API 易 403 |
| 有跑 `schema_rbac.sql`（或後端空表自動 seed） | 有設計預設權限，可用 `admin` 登入再在 Admin UI 調整 |

因此：**新環境請務必執行 `schema_rbac.sql`（或確認啟動後 `role_permissions` 列數約 308）**，不要只建表不塞預設。

驗證：

```bash
psql "$DATABASE_URL" -c "SELECT count(*) FROM role_permissions;"   -- 預期約 308
psql "$DATABASE_URL" -c "SELECT username, role FROM users WHERE username='admin';"
```

#### 2.5 重跑腳本注意

- 表：`CREATE IF NOT EXISTS`，可重複執行。  
- **`role_permissions`：會先 `DELETE` 再重播預設** → 若已在 Admin UI 調過細項，重跑前請先備份。  
- 既有 `admin` 密碼：**不會**被腳本覆寫。

備份細項範例：

```bash
psql "$DATABASE_URL" -c "COPY role_permissions TO STDOUT WITH CSV HEADER" > role_permissions_backup.csv
```

---

### 3. 建議部署順序

1. 準備 PostgreSQL，設定 `DATABASE_URL`  
2. 執行 `psql "$DATABASE_URL" -f schema_rbac.sql`  
3. 設定後端 `.env`（含 `CORS_ORIGINS`、`JWT_SECRET`、LLM 金鑰）並啟動 API  
4. 設定前端 `VITE_API_BASE_URL` 後 `npm run build` 並部署靜態資源  
5. 用 `admin` / `admin123` 登入 → **立刻改密碼** → 在「使用者角色／角色細項權限」依環境調整  

---

### 4. 相關文件

| 文件 | 說明 |
|---|---|
| `schema_rbac.sql` | **建表 + 預設資料（含角色矩陣）** |
| `aidlc-docs/construction/plans/schema-rbac-notes.md` | SQL 區塊說明 |
| `aidlc-docs/construction/plans/role-permission-design.md` | 角色／細項語意 |
| `backend/.env.example`、`frontend/.env.example` | 環境變數範本 |

---

## English Version

### Env vars

- **Backend** (`backend/.env` from `.env.example`): set `DATABASE_URL`, rotate `JWT_SECRET`, set `CORS_ORIGINS` to the real frontend origin(s), and configure OpenRouter／LLM keys for that environment.  
- **Frontend** (`frontend/.env` / CI): set `VITE_API_BASE_URL` to the real API root (no trailing slash). Optional `VITE_WS_BASE_URL`; otherwise derived from the API base (`http→ws`, `https→wss`). Rebuild after changing Vite env.

### Database

**Script path (repo root):** `schema_rbac.sql`

```bash
psql "$DATABASE_URL" -f schema_rbac.sql
```

Creates: `users`, `user_diagrams`, `diagram_shares`, `user_diagram_chats`, `role_permissions`, plus `last_opened_diagram_id`.  
Seeds ~**308** `role_permissions` rows and default user **`admin` / `admin123`** (`Platform_Admin`) if missing.

**If you create empty tables without seeding `role_permissions`, the matrix is entirely empty** — no view/edit/review for any role, Sidebar stays empty, APIs return 403. Always run `schema_rbac.sql` (or confirm ~308 rows after backend empty-DB seed).

Re-running **wipes and re-seeds** `role_permissions` (backup first if customized). Does not overwrite an existing admin password. Change `admin123` immediately after first login.
