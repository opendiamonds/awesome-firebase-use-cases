# Technology Stack — Cloud-360

> 逆向工程產出。基準 commit `8c90f40372ac810cc8f6ef41c46fc7a723031a1e`（branch `ut`，2026-08-08）。
> 版本欄位為掃描時**宣告檔內的字面值**，非實際解析後的鎖定版本。

## 語言與執行環境

| 語言 | 版本 | 範圍 | 規模 |
|---|---|---|---|
| Python | 3.12（Dockerfile 與 CI 一致） | `backend/`、`scripts/` | 7,171 LOC 產品碼 + 1,510 LOC 測試 + 379 LOC 驗證腳本 |
| TypeScript | `~6.0.2` | `frontend/` | 7,431 LOC TS/TSX |
| CSS | — | `frontend/` | 234 LOC |
| SQL | PostgreSQL 方言 | `schema.sql`(79 行)、`schema_rbac.sql`(523 行) | — |
| Node.js | 22 | frontend build、backend runtime（僅供 Claude Code CLI）、CI | — |
| Markdown / Mermaid / draw.io XML | — | specs、prompts、圖形資產 | — |

## Backend 技術堆疊

宣告於 `backend/requirements.txt`，共 11 個依賴（加上測試用的 `hypothesis` 共 12 條）。

| 套件 | 版本 | 角色 | 備註 |
|---|---|---|---|
| `fastapi[standard]` | **未 pin** | Web framework | `[standard]` extra 帶入 uvicorn、httptools、websockets 等 |
| `uvicorn` | **未 pin** | ASGI server | 啟動指令 `uvicorn main:app --host 0.0.0.0 --port 8000` |
| `pydantic` | **未 pin** | 請求／回應 schema 驗證 | **程式碼仍用 v1 風格** `class Config: orm_mode = True`。pydantic v2 下此寫法已 deprecated |
| `sqlalchemy` | **未 pin** | ORM | declarative + `Table` 關聯表 |
| `psycopg2-binary` | **未 pin** | PostgreSQL driver | 測試中被 `MagicMock` 掉，改走 in-memory SQLite |
| `httpx` | **未 pin** | 非同步 HTTP client | n8n webhook 等外部呼叫 |
| `python-dotenv` | **未 pin** | `.env` 載入 | `load_dotenv(override=True)` |
| `bcrypt` | **未 pin** | 密碼雜湊 | `auth.py` 與 `database.py` **各自實作一份**逐字相同的 hash 函式 |
| `passlib[bcrypt]` | **未 pin** | （宣告但未使用） | 程式碼**未見任何 `passlib` import**，是可移除的殘留 |
| `pyjwt` | **未 pin** | JWT 簽發與驗證 | HS256，8 小時效期 |
| `claude-agent-sdk` | **未 pin** | Anthropic Agent SDK | **會 spawn Claude Code CLI 子行程**，見「隱性硬依賴」 |
| `hypothesis` | **未 pin** | Property-based testing | ADR-0006 hard constraint 的落點 |

**測試工具**：Python 內建 `unittest`（`python -m unittest discover -s tests -v`）
與 `unittest.mock`。**未使用 pytest。**

**Backend 完全沒有**：linter、formatter、type checker、coverage 工具、`pyproject.toml`、
`setup.py`、lockfile。

## Frontend 技術堆疊

### Runtime 依賴

| 套件 | 版本 | 角色 |
|---|---|---|
| `react` | `^19.2.6` | UI framework |
| `react-dom` | `^19.2.6` | DOM renderer |
| `react-router-dom` | `^6.22.0` | 路由 |
| `html2canvas` | `^1.4.1` | 瀏覽器端截圖（PNG／PDF 匯出） |
| `jspdf` | `^4.2.1` | WA review PDF 匯出 |

### 建置與開發依賴

| 套件 | 版本 | 角色 | 備註 |
|---|---|---|---|
| `vite` | `^8.0.12` | bundler / dev server | `vite.config.ts` 僅掛 react plugin，無 proxy／alias／build 調校 |
| `@vitejs/plugin-react` | `^6.0.1` | React 支援 | |
| `typescript` | `~6.0.2` | 型別系統 | `tsconfig` project references 三分檔 |
| `eslint` | `^10.3.0` | linter | flat config |
| `@eslint/js` | `^10.0.1` | ESLint 基礎規則 | |
| `typescript-eslint` | `^8.59.2` | TS 規則 | |
| `eslint-plugin-react-hooks` | `^7.1.1` | React hooks 規則 | **含 `set-state-in-effect`，已影響 `AdminPage` 的資料抓取寫法** |
| `eslint-plugin-react-refresh` | `^0.5.2` | HMR 規則 | **迫使 `AuthContext` 拆兩檔** |
| `tailwindcss` | `^4.3.0` | CSS framework | Tailwind v4 |
| `@tailwindcss/postcss` | `^4.3.0` | PostCSS 整合 | v4 的新整合方式 |
| `postcss` | `^8.5.15` | CSS 處理 | |
| `autoprefixer` | `^10.5.0` | 前綴補齊 | |
| `@playwright/test` | `^1.56.0` | e2e 測試 | chromium 單一 project |
| `@types/node` | `^24.12.3` | Node 型別 | |
| `@types/react` | `^19.2.14` | React 型別 | |
| `@types/react-dom` | `^19.2.3` | ReactDOM 型別 | |
| `@types/react-router-dom` | `^5.3.3` | 路由型別 | **版本錯配**：v5 型別搭 v6 runtime（react-router-dom v6 起自帶型別，此套件應移除） |
| `globals` | `^17.6.0` | ESLint globals | |

**ESLint flat config 組成**：`js.recommended` + `tseslint.recommended` +
`react-hooks.flat.recommended` + `react-refresh.vite`；ignore `dist`。

**根目錄無 `.prettierrc`** —— `org.md` 預設的 Prettier 在本 repo 未配置。

## 基礎設施技術

| 技術 | 版本 | 用途 | 備註 |
|---|---|---|---|
| PostgreSQL | **15**-alpine（本機）／**16**-alpine（staging） | 唯一持久層 | **兩環境版本不一致** |
| nginx | alpine | SPA 服務 + `/api/` 反向代理 | 唯一對外的容器 |
| Docker / Compose | — | 本機與 staging | 三份 compose：根、`deploy/*.deploy.yml`、`deploy/*.test.yml` |
| Cloudflare Tunnel（`cloudflared`） | `latest` | 對外曝露 `cloud360.danniel.cc` | 以 `user: "1000:1000"` 執行以讀取 0400 憑證 |
| adminer | `latest` | 本機 DB 管理（port 8080） | 僅本機 |
| GitHub Actions | — | CI/CD | `ci.yml` + `deploy.yml` + 10 組 gh-aw |
| gh-aw（agentic workflows） | — | 開發流程自動化 | `.md` 原始檔 + 編譯後 `.lock.yml` |
| Kiwi TCMS | 自架於 `tcms.danniel.cc` | 測案管理 | 於 `dc-infra` repo 維運；`ui-regression` workflow 送結果 |
| `@anthropic-ai/claude-code` | **未 pin**（`npm i -g`） | backend 容器內的 LLM 執行體 | 見「隱性硬依賴」 |
| OpenRouter | — | LLM 閘道 | `ANTHROPIC_BASE_URL=https://openrouter.ai/api` |
| n8n | — | 動態圖示 SVG webhook | 選填；失敗有 fallback |

### staging 部署目標

自有主機 `192.168.10.10`，經 Cloudflare Tunnel 對外為 `cloud360.danniel.cc`（ADR-0007）。
**雲端供應商 production 在範圍外**（ADR-0001／ADR-0002）。

## 建置系統

**類型：雙 build system，無 monorepo 工具。** 無 workspace、無 turborepo、無 nx、無 Makefile。
兩側各自獨立建置，由 CI 分 job 執行。

| 側 | 工具 | lockfile | 產出 |
|---|---|---|---|
| Backend | `pip` + `requirements.txt` | **無** | Docker image（無中間 artifact） |
| Frontend | `npm` + `package.json` | **`package-lock.json` 已 commit** | `dist/` 靜態資產 → nginx image |

### npm scripts

| script | 指令 |
|---|---|
| `dev` | `vite` |
| `build` | `tsc -b && vite build`（**型別檢查在此發生**） |
| `lint` | `eslint .` |
| `preview` | `vite preview` |
| `test:e2e` | `playwright test` |

### 建置相依關係

- `frontend` build **不依賴** `backend`（只需要 build 時的 `VITE_API_BASE_URL` 字串）。
- `deploy` stack 啟動順序：`db` → `backend` → `frontend`(nginx) → `cloudflared`。
- `db` 初始化掛載 `../schema_rbac.sql` 至 `/docker-entrypoint-initdb.d/01-schema_rbac.sql`，
  **僅在資料 volume 為空時執行一次**。

### Playwright 設定

`testDir: ./tests/e2e`；`BASE_URL` 預設 `http://localhost:8090`；timeout 30 秒；
workers 1；CI 下 retries 1；reporter 為 `list` + `json`(`pw-report.json`) + `junit`(`junit.xml`)。

## 版本治理現況

這是本堆疊最需要注意的一件事，獨立成節。

### Backend 依賴 100% 未 pin

`backend/requirements.txt` 的 **11 個依賴無一有版本約束**（`fastapi[standard]`、`pydantic`、
`uvicorn`、`httpx`、`python-dotenv`、`sqlalchemy`、`psycopg2-binary`、`passlib[bcrypt]`、
`bcrypt`、`pyjwt`、`claude-agent-sdk`，加上 `hypothesis`），且**沒有任何 lockfile**
（無 `requirements.lock`、無 `poetry.lock`、無 `pyproject.toml`）。

**後果**：三個地方各自在執行當下解析最新版，彼此可能不同：

1. CI 的 `backend` job（`pip install`）
2. Docker image build（`backend/Dockerfile`）
3. staging 部署（`docker compose up --build`）

意即「CI 綠燈」與「staging 跑得起來」用的可能不是同一組套件版本，
且**上游任何一次 breaking release 都會直接打到部署**，沒有緩衝。這也讓
「CI 綠但部署紅」這類故障難以重現。

**已可見的相關風險**：`pydantic` 未 pin，而程式碼仍用 v1 風格的 `class Config: orm_mode = True`。
pydantic v2 對此僅發出 deprecation warning，但若 v3 移除該相容層，部署會在無程式碼變更的情況下失效。

**對照**：frontend 有已 commit 的 `package-lock.json`，前後端在這件事上治理水準不對等。

### 其他未 pin 的執行期元件

| 元件 | 現況 |
|---|---|
| `@anthropic-ai/claude-code` | `npm i -g` 無版本，backend image 每次 build 取最新 |
| `cloudflared` | image tag `latest` |
| `adminer` | image tag `latest`（僅本機，影響小） |

### 已 pin 或已鎖定的部分

| 元件 | 鎖定方式 |
|---|---|
| frontend npm 依賴 | `package-lock.json`（已 commit） |
| GitHub Actions | `.github/aw/actions-lock.json` |
| Python 執行環境 | `python:3.12-slim`（Dockerfile 與 CI 一致） |
| Node（frontend build） | `node:22-alpine` |
| PostgreSQL | image tag 有指定 major（15／16），但兩環境不同 |

### 版本錯配清單

1. **PostgreSQL 15（本機）vs 16（staging）** —— 本機測不到的行為差異會在 staging 才出現。
2. **`@types/react-router-dom@^5.3.3` vs `react-router-dom@^6.22.0`** ——
   v6 起自帶型別，此 `@types` 套件不但多餘，且型別描述的是 v5 API。
3. **pydantic v1 風格程式碼 + 未 pin 的 pydantic** —— 見上。
