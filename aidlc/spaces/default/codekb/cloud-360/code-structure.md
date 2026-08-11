# Code Structure — Cloud-360

> 逆向工程產出。基準 commit `8c90f40372ac810cc8f6ef41c46fc7a723031a1e`（branch `ut`，2026-08-08）。
> 本檔描述程式碼「放在哪、怎麼分類、寫成什麼形狀」。元件職責見 `component-inventory.md`。

## 倉庫頂層結構

```
cloud-360/
├── backend/              FastAPI 應用（單一 process monolith）
├── frontend/             Vite + React SPA
├── scripts/              驗證腳本（repo contract）
├── deploy/               staging 部署資產（compose、cloudflared）
├── .github/              CI/CD 與 10 組 gh-aw agentic workflows
├── .claude/              AIDLC v2 upstream 框架（非應用程式碼，升級時整批覆蓋）
├── .agents/              agent 規則與 workflow 定義
├── aidlc/                AIDLC 工作區（memory、knowledge、codekb、intents）
├── graphify-out/         知識圖譜產出物（非應用程式碼）
├── schema.sql            精簡核心 DDL 參考（已落後）
├── schema_rbac.sql       宣稱的完整部署腳本（523 行）
├── docker-compose.yml    本機開發（postgres 15 + adminer）
├── DEPLOY.md             部署手冊（19KB）
├── CLAUDE.md             AI agent 專案指引
├── AGENTS.md             agent 說明
└── README.md
```

**範圍註記**：`CLAUDE.md` 第 2 章提到的頂層 `tools/` 與 `workflows/` 兩個目錄
**在本 repo 實際不存在**。agentic workflows 位於 `.github/workflows/`（gh-aw `.md` 原始檔
加上編譯後的 `.lock.yml`），AIDLC 工具位於 `.claude/tools/`。這是文件與實況的既存偏差。

## Backend 模組組織

`backend/` 共 **7,171 LOC 產品碼 + 1,510 LOC 測試**，Python 3.12。

```
backend/
├── main.py                  55 LOC   entry point：app 建立、CORS、掛 5 router、startup
├── models.py               171 LOC   SQLAlchemy declarative Base，7 個模型
├── database.py             264 LOC   engine／SessionLocal／get_db；init_db；3 個 runtime DDL 補丁
├── Dockerfile                        python:3.12-slim + Node 22 + 全域 Claude Code CLI
├── requirements.txt                  11 個依賴，全部未 pin
├── services/                         18 支模組（全部業務邏輯）
├── lenses/                           3 個 JSON 資料資產（AWS／GCP／Azure）
├── prompts/                          6 個資料資產（3 system prompt + 3 draw.io 模板）
├── tests/                            15 個檔（14 測試 + helpers.py + __init__.py）
└── .hypothesis/                      Hypothesis 快取（已誤入版控）
```

### `backend/services/` 的四種模組類型

18 支模組可依「與外界的耦合程度」分成四類。這個分類直接對應可測試性：

**類型 A — Router（HTTP 邊界層，5 支）**

| 檔案 | LOC | 掛載前綴 |
|---|---|---|
| `user_router.py` | 831 | `/api/auth` |
| `collab_router.py` | 527 | `/api/collab` |
| `review_router.py` | 484 | `/api/architecture` |
| `agent_router.py` | 148 | `/api/architecture` |
| `lens_router.py` | 108 | `/api/architecture` |

**類型 B — 編排器與服務（讀寫 DB，6 支）**：`wa_collab_orchestrator.py`(530)、
`review_orchestrator.py`(510)、`lens_service.py`(203)、`collab_suggestions.py`(147)、
`wa_score_service.py`(104)、`rbac.py`(272)

**類型 C — 純函式引擎（不讀 DB、不連外，3 支）**：`wa_rule_engine.py`(973，全 repo 最大)、
`wa_lens_engine.py`(556)、`diagram_builder.py`(288，唯一例外是可選的 n8n webhook 呼叫)

**類型 D — 基礎與資料（4 支）**：`auth.py`(86)、`rbac_seed_data.py`(314，純資料常數)、
`llm_limits.py`(64，純設定常數)、`design_agent.py`(359) 與 `review_agent.py`(177)
（LLM agent，跨行程邊界）

**結構意涵**：類型 C 是最容易測試也實際被 property-based 測試涵蓋的部分；
類型 A 的 831 LOC `user_router.py` 因為商業邏輯直寫 handler，**沒有任何測試能觸及**
（repo 內無 `TestClient` 使用）。

### 分層一致性不是全域的

分層在不同模組家族有**不同的成熟度**：

| 家族 | 分層形狀 | 評價 |
|---|---|---|
| `review` / `lens` / `wa_*` | router → orchestrator/service → 純函式引擎 → model | 乾淨，三層清楚 |
| `agent` | router → agent → 引擎 | 薄 router（148 LOC），職責只有 SSE 轉換 |
| `user` | router 直接寫商業邏輯 → model | **無 service 層**，831 LOC 全在 handler |
| `collab` | router 直接寫商業邏輯 + WebSocket 狀態 → model | **無 service 層** |

## Frontend 模組組織

`frontend/` 共 **7,431 LOC TS/TSX + 234 LOC CSS**，TypeScript 6 + React 19。

```
frontend/
├── src/
│   ├── App.tsx              路由表與 guard 組合
│   ├── pages/               8 支頁面
│   ├── components/          9 支元件
│   ├── context/             2 支（AuthContext.tsx + auth-context.ts）
│   ├── config/api.ts        34 LOC：API_BASE_URL／WS_BASE_URL／apiUrl()／wsUrl()
│   ├── hooks/               1 支：useCollaboration.ts（64 LOC，WebSocket）
│   └── utils/               5 支工具
├── tests/e2e/               1 個檔：regression.spec.ts
├── Dockerfile               多階段：node:22-alpine build → nginx:alpine
├── nginx.conf               /api/ 反向代理 + WS upgrade + SPA fallback
├── package.json             + package-lock.json（已 commit）
├── vite.config.ts           僅掛 @vitejs/plugin-react，無 proxy／alias／build 調校
├── tsconfig.json            project references 三分檔（+ .app.json／.node.json）
├── eslint.config.js         flat config
├── tailwind.config.js       + postcss.config.js
└── playwright.config.ts     testDir ./tests/e2e，BASE_URL 預設 localhost:8090
```

### 頁面清單與規模

| 頁面 | 規模 | 對應 story |
|---|---|---|
| `AssessmentPage.tsx` | **1,856 LOC（全 repo 最大檔）** | `A3` |
| `WorkspacePage.tsx` | **1,170 LOC** | `A1`／`A2`／`A4` |
| `AdminPage.tsx` | 269 LOC | `J3a` |
| `RolePermissionsPage.tsx` | — | `J3b` |
| `AuthorizationRequestsPage.tsx` | — | `J3a` |
| `LoginPage.tsx` | — | 公開 |
| `WaitingApprovalPage.tsx` | — | pending 使用者 |
| `ForbiddenPage.tsx` | — | 403 落點 |

### 元件清單

`Layout`、`Sidebar`、`RouteGuard`、`ChatBox`、`DrawioCanvas`、`DiagramPreviewPanel`、
`LensCriteriaEditor`、`ShareModal`、`SuggestionRichText`。

## 程式碼模式

### 後端模式

**模式 1 — Guard 工廠（Dependency Injection）**

授權一律以工廠函式產生 FastAPI `Depends`：

- `require_story_action("A3", "edit")` — 指定 story 與 action
- `require_arch_action("edit")` — 架構圖三合一（`A1`／`A2`／`A4`）專用捷徑

工廠內部的判定順序固定為：`authorization_status` 閘門 → canonical role 檢查 →
查 `role_permissions`。**新端點一律沿用此模式**，不要自寫檢查。

**模式 2 — Async Generator 串流**

SSE 端點的形狀高度一致：

```python
async def event_generator():
    async for event in <orchestrator或agent>(...):
        chunk = json.dumps(event, ensure_ascii=False)
        yield f"data: {chunk}\n\n"
return StreamingResponse(event_generator(), media_type="text/event-stream")
```

事件一律是 `{"type": ..., ...}` 的 dict，`ensure_ascii=False`（中文不轉義）。
編排器本身也是 async generator，逐事件 yield —— 這讓「降級」得以自然表達：
逾時時改 yield 一個不同 type 的事件，而不是拋例外中斷串流。

**模式 3 — 啟動時的 Runtime DDL 補丁**

`database.py` 有三個 `_ensure_*_schema()`（a4／j5／a3），在 `init_db()` 內於
`Base.metadata.create_all()` 之後執行，用 `ALTER TABLE ... ADD COLUMN IF NOT EXISTS`
等可重跑寫法補上 `.sql` 檔沒有的欄位。**這是既有的 schema 演進機制，也是技術債 T1 的根源**
（詳見 `code-quality-assessment.md`）。

**模式 4 — Fallback 而非失敗**

外部依賴失敗一律降級：圖示 SVG 取不到用灰底、LLM 逾時落 `rules_only` 狀態、
DB 無 lens 資料回退到 `backend/lenses/` 的 JSON。

**模式 5 — 高密度模組級 docstring**

`backend/services/` 的 18 支模組中 **16 支有模組級 docstring**，多數明確載明
「職責／安全邊界／契約」三段。部分 docstring 直接寫「契約（前端依賴，請勿變更）」
並列出 request/response 形狀（例：`agent_router.py`）。這是本 repo 明顯高於一般水準的部分，
**修改這些模組時應同步維護 docstring 內的契約描述**。

### 前端模式

**模式 1 — 直接 `fetch()`，無 client 抽象**

32 處呼叫點散落 8 支頁面與元件，形狀為
`fetch(apiUrl('/path'), { headers: { Authorization: \`Bearer ${token}\` } })`，
各自手寫錯誤解包與提示。**無統一 401 處理、無 retry、無集中型別。**

**模式 2 — 前端型別是後端 schema 的手寫鏡像**

例：`AdminPage.tsx` 的 `DbUser` interface 鏡射後端 `UserSchema`。無產生機制。

**模式 3 — Context 拆兩檔（被 lint 規則強制）**

`AuthContext.tsx`（Provider component）與 `auth-context.ts`（型別 + `useAuth` hook）
必須分檔，因為 `eslint-plugin-react-refresh` 要求單一 component 匯出。

**模式 4 — 資料抓取拆兩層（被 lint 規則強制）**

`eslint-plugin-react-hooks` 的 `set-state-in-effect` 規則使 `AdminPage` 的抓取被迫拆成：

- `fetchUserList` — 純抓取，**不碰任何 state**
- `fetchUsers` — 呼叫端，在 `.then/.catch/.finally` 內更新 state
- `useEffect` 內另用 `cancelled` flag 防止卸載後 setState

**新增資料來源必須沿用此形狀，否則 CI lint 紅燈。**

**模式 5 — 兩層 Route Guard**

`ProtectedRoute`（登入與否）與 `CapabilityRoute storyId=... action=...`（能力）
組合使用；`DefaultRedirect` 依序試 pending → `canArch('view')` → `A3` → `J3a` → `J3b` → `/403`。

## 命名與檔案分類慣例

| 慣例 | 規則 | 例外／備註 |
|---|---|---|
| Python 檔名 | `snake_case.py` | 一致 |
| Python router | 一律 `*_router.py` | 5 支全部符合 |
| Python 引擎 | Well-Architected 相關一律 `wa_*` 前綴 | `wa_rule_engine`／`wa_lens_engine`／`wa_score_service`／`wa_collab_orchestrator` |
| React 元件與頁面 | `PascalCase.tsx` | 一致 |
| React 頁面 | 一律 `*Page.tsx` | 8 支全部符合 |
| 非元件 TS | `camelCase.ts` 或 `kebab-case.ts` | `auth-context.ts` 用 kebab，`useCollaboration.ts` 用 camel — **不一致** |
| 測試檔 | `test_*.py`（backend）／`*.spec.ts`（frontend） | 一致 |
| 註解與 docstring 語言 | 繁體中文為主 | 與 ADR-0009 一致 |

## 結構性風險

1. **四個超大檔**：`AssessmentPage.tsx`(1,856)、`WorkspacePage.tsx`(1,170)、
   `wa_rule_engine.py`(973)、`user_router.py`(831)。前兩者是 A3／A1 的完整 UI 邏輯，
   後兩者一個是核心演算法（單一職責，大但內聚）、一個是缺 service 層的堆積（大且低內聚）。
   **`user_router.py` 是四者中最值得拆的**。
2. **同一份資料有三份手寫副本**：11 個角色的清單同時存在於 `rbac.py` 的 `CANONICAL_ROLES`、
   `user_router.py` 的 `ROLE_DISPLAY_NAMES`、`AdminPage.tsx` 的 `AVAILABLE_ROLES`，
   **彼此無同步機制**。
3. **Python 側零靜態檢查**：無 linter、formatter、type checker 設定檔。`org.md` 描述的
   「Ruff／Black 配置於 repo root」在本 repo 不成立，前端有 ESLint 而後端沒有對等物。
4. **無 monorepo 工具**：無 workspace／turborepo／nx／Makefile。前後端各自建置，
   由 CI 分 job 執行；跨側的一致性（如型別）沒有任何工具支撐。
