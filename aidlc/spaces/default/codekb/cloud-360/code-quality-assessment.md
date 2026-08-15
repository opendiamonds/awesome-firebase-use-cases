# Code Quality Assessment — Cloud-360

> 逆向工程產出。基準 commit `8c90f40372ac810cc8f6ef41c46fc7a723031a1e`（branch `ut`，2026-08-08）。
> 技術債以**根因叢集**組織，再以**嚴重度分級**排序 —— 不照掃描流水號排列，
> 因為流水號不表達修復順序，而叢集會。

## 評估摘要

Cloud-360 是一個**文件與流程紀律明顯高於平均、但驗證與一致性機制明顯不足**的專案。
這兩件事同時為真，不互相抵銷。

| 面向 | 評價 | 依據 |
|---|---|---|
| 文件品質 | **優於一般水準** | 18 支 service 模組中 16 支有載明「職責／安全邊界／契約」的模組級 docstring；DEPLOY.md 19KB；註解說明「為什麼」的比例高 |
| 程式碼衛生 | **優於一般水準** | 全 repo `TODO`／`FIXME`／`HACK`／`XXX` 標記數為 **0**；無被註解掉的死碼區塊 |
| 流程護欄 | **優於一般水準** | repo contract 驗證器（379 LOC）為 CI 第一關；10 組 agentic workflow；deploy 有 rollback job 與自癒 dispatch |
| 架構清晰度 | 良好但不均勻 | `wa_*` 與 `review`／`lens` 家族分層乾淨；`user_router`／`collab_router` 無 service 層 |
| **一致性機制** | **不足** | 三份 schema 來源、兩份權限矩陣 seed、三份角色清單、兩份前後端型別 —— **全部靠人工同步，零自動驗證** |
| **測試涵蓋** | **不足** | 46 個 HTTP 端點無一被實際打過；無覆蓋率量測；`org.md` 的 80% 門檻無法量測也無法強制 |
| **靜態檢查** | **前後端不對等** | 前端有 ESLint + `tsc` 型別檢查並在 CI 強制；後端**零** linter／formatter／type checker |
| 安全預設值 | 需處理 | JWT secret 有程式內預設、預設帳號密碼寫死、一個業務端點無驗證 |

**一句話結論**：這個 repo 的**知識**保存得很好（docstring、DEPLOY.md、ADR、agentic workflow），
但**知識的自動執行**很弱 —— 規則寫在文件裡而不是寫在檢查器裡，所以偏差會靜默累積。
技術債的主軸不是「程式碼寫得爛」，而是「同一件事有多個真實來源，且沒有任何機制發現它們分歧」。

## 品質正面訊號

這些是需要**保護**的資產，不要在後續重構中弄丟：

1. **零 TODO／FIXME／HACK／XXX 標記**。這在 7,000+ LOC 的專案中不常見，代表未完成的工作
   被追到別的地方（issue／spec）而不是留在程式碼裡。
2. **模組級 docstring 載明契約**。例如 `agent_router.py` 直接寫「契約（前端依賴，請勿變更）」
   並列出 request/response 形狀。這在缺乏 OpenAPI 契約測試的情況下是唯一的契約紀錄。
3. **一致的降級策略**。逾時落 `rules_only`、圖示失敗用 fallback、無 DB lens 回退 JSON ——
   系統面對外部失敗時的行為是**可預測的**，不是隨機爆炸。
4. **純函式引擎層**。`wa_rule_engine`／`wa_lens_engine`／`diagram_builder` 不讀 DB、不連外，
   是全系統最容易測試與演化的部分，也確實承載了大部分 property-based 測試。
5. **repo contract 驗證器**。379 LOC，涵蓋必要檔案、必要文字、文件語言、禁止路徑、禁止內容，
   且是 CI 的第一個 job。這是把規則變成檢查器的正確做法 —— **問題只在於它涵蓋的範圍太窄**。
6. **deploy 有 rollback 路徑**。`deploy.yml` 失敗時會還原 last-good、開 revert PR、
   dispatch Deploy Doctor workflow。這比多數同規模專案完整。

## 測試現況

### 規模與工具

| 側 | 位置 | 規模 | 框架 |
|---|---|---|---|
| Backend | `backend/tests/` | 15 檔（14 測試 + `helpers.py` + `__init__.py`），1,510 LOC | Python 內建 `unittest` + `hypothesis` + `unittest.mock`（**未使用 pytest**） |
| Frontend | `frontend/tests/e2e/` | 1 檔 `regression.spec.ts`，2 describe／6 case | Playwright（chromium 單一 project） |

**測試 DB 策略**：`tests/helpers.py` 在任何 DB import 前
`sys.modules.setdefault("psycopg2", MagicMock())`，改用 in-memory SQLite；
每 session 以 `ensure_role_permissions_seeded(db, force=True)` 灌入 308 列。

### 測試檔對應規模

`test_diagram_builder.py`(205)、`test_collab.py`(184)、`test_wa_rule_engine.py`(150)、
`test_wa_lens_engine.py`(146)、`test_auth.py`(124)、`test_j5_authz.py`(123)、
`test_review_authz.py`(93)、`test_lens_service.py`(86)、`test_design_agent.py`(85)、
`test_rbac.py`(56)、`test_collab_suggestions.py`(52)、`test_wa_collab.py`(48)、
`test_llm_limits.py`(41)、`test_review_agent.py`(37)

### Property-based 測試（ADR-0006 hard constraint）

**現況：5 個檔、共 8 個 `@given`**

| 檔案 | `@given` 數 |
|---|---|
| `test_diagram_builder.py` | 2 |
| `test_design_agent.py` | 2 |
| `test_wa_rule_engine.py` | 2 |
| `test_auth.py` | 1 |
| `test_collab.py` | 1 |

**約束落點問題**：`project.md` 的 `## Testing Posture` 點名三個必須有 PBT 的模組 ——
**IaC generator、cost calculator、agent routing** —— 這三者在本 repo **尚無對應實作模組**
（對照 `business-overview.md` 的能力表，D 群 IaC 與 C 群成本目前只存在於權限矩陣）。

因此該 hard constraint 目前**沒有可驗證的落點**：既沒有違反，也沒有被滿足。
**這是規則與實況的落差，不是違規**。實際存在的 8 個 `@given` 落在圖形組裝、規則引擎、
驗證與共編上，是自發的良好實踐而非規則要求。

**給下游的建議**：當 IaC generator 或 cost calculator 真的開始實作時，
這條約束會立刻生效且是 blocking 的，應在設計階段就規劃 property 的定義。

### E2E 涵蓋範圍

`regression.spec.ts` 兩個 describe：

- **身分驗證**（4 case）：登入頁顯示、錯誤密碼被拒、管理員登入進工作區、登出返回登入頁
- **角色權限存取控制 RBAC**（2 case）：`Platform_Admin` 看得到系統管理區、`Developer` 看不到

**明顯缺口**：**沒有任何 Admin 頁表格內容的 e2e 斷言**。也就是說，
Admin 使用者清單的欄位、資料正確性、載入態與錯誤態完全沒有自動化保護。
`ui-regression` agentic workflow 每 PR 對短生命週期 stack 跑這份 Playwright 並回報 Kiwi TCMS ——
流程完整，但被測的斷言很少。

### 覆蓋率

**完全不存在量測機制。** 無 `.coveragerc`、無 `coverage` 依賴、無 `pytest-cov`、
CI 無 coverage 步驟、無門檻閘門。

`org.md` 為 `feature` scope 宣告的「最低 80% line coverage」目前**既無法量測也無法強制**，
是宣告而非閘門。

### 最重要的測試缺口

**沒有任何測試會實際打 HTTP 端點** —— repo 內無 `TestClient` 使用。
46 個端點的路由、依賴注入鏈、guard 組合、request/response schema 全部沒有測試覆蓋。

**零測試的關鍵模組**：`user_router.py` 的 HTTP 層（831 LOC）、`review_orchestrator.py`
的狀態機主體（510 LOC）、`agent_router.py`（148）、`lens_router.py`（108）、
`wa_score_service.py`（104）。

其中 **`review_orchestrator` 的狀態機主體無測試**特別值得注意：它是系統中唯一有
明確狀態流轉、逾時分支與降級語意的元件，正是最需要測試的形狀。

## Linting 與靜態檢查

| 側 | linter | formatter | type checker | CI 強制 |
|---|---|---|---|---|
| Frontend | ESLint 10 flat config | 無（無 `.prettierrc`） | `tsc -b`（隨 `npm run build`） | **是**，`npm run lint` 失敗即紅燈 |
| Backend | **無** | **無** | **無** | 僅 import smoke + unittest |

**`org.md` 的落差**：該層寫「Linter: ESLint, Ruff, golangci-lint 等，在 CI 執行、失敗阻擋 PR」
與「Formatter: Prettier (JS/TS), Black (Python)，配置在 repo root」。
**在本 repo，Python 側完全不成立，前端也沒有 Prettier**。

**ESLint 規則已實質影響程式碼形狀**（不只是風格，是結構約束）：

- `eslint-plugin-react-refresh` → `AuthContext` 必須拆成 `AuthContext.tsx` + `auth-context.ts`
- `eslint-plugin-react-hooks` 的 `set-state-in-effect` → `AdminPage` 的資料抓取被迫拆成
  純抓取的 `fetchUserList`（不碰 state）與呼叫端在 `.then/.catch/.finally` 更新 state 的
  `fetchUsers`，`useEffect` 內另用 `cancelled` flag

**任何新增前端資料來源都必須沿用此形狀，否則 CI 紅燈。**

## CI/CD 護欄

### `ci.yml`

- **觸發**：`pull_request` + `push` 到 `main`／`ut`／`danniel/**`／`chore/**`
- **並行控制**：`concurrency` 取消同 ref 的舊 run
- **權限**：`contents: read`（最小權限，正確）
- **4 個 job**：
  1. `repo-contract` — 跑 `scripts/validate_repo_contract.py`
  2. `frontend` — `npm ci` → lint → build
  3. `backend` — `pip install` → import smoke → `unittest`
  4. `docker-build` — buildx 建兩個 image，`push: false`

### `deploy.yml`

- **觸發**：`pull_request closed` 到 `ut` + `workflow_dispatch`
- **runner**：`[self-hosted, linux, x64, cloud360]`
- **並行控制**：`concurrency: deploy-10-10`，`cancel-in-progress: false`（正確 —— 部署不該被中斷）
- **timeout**：30 分
- **`deploy` job**：checkout `ut` → 檢查 secrets → 生成 `deploy/.env` →
  `docker compose up --build` → 等本地 frontend → 等公開 hostname → 記錄 last-good →
  **`rm -f deploy/.env`**（正確的清理）
- **`rollback` job**：失敗時還原 last-good、開 revert PR、dispatch Deploy Doctor。
  權限提升為 `contents: write` + `pull-requests: write` + `actions: write`

### 10 組 gh-aw agentic workflows

`code-drift-alert`、`contract-guard`、`daily-digest`、`deploy-doctor`、`issue-triage`、
`lint-fix`、`pr-reviewer`、`release-watch`、`spec-sync`、`ui-regression`。
`.github/aw/actions-lock.json` 鎖定 action 版本。

**評價**：CI/CD 是本專案最成熟的部分。`repo-contract` 作為第一關、rollback 路徑完整、
並行控制正確、部署後清理 `.env` —— 這些都做對了。

## 文件品質

| 文件 | 大小 | 評價 |
|---|---|---|
| `DEPLOY.md` | 19,191 B | 詳盡；含表清單、驗證指令、升級路徑說明 |
| `CLAUDE.md` | 9,380 B | AI agent 指引，涵蓋 AIDLC 入口、repo contract、工作模式 |
| `README.md` | 8,965 B | |
| `AGENTS.md`、`frontend/README.md`、`.claude/README-cloud360.md` | — | |
| `.env.example`（三份） | — | 環境變數說明 |
| 模組級 docstring | — | **18 支 service 中 16 支有**，多數載明職責／安全邊界／契約 |

**已知文件缺陷**：

1. `CLAUDE.md` 第 2 章提到的頂層 `tools/` 與 `workflows/` 目錄**在 repo 實際不存在**。
2. `DEPLOY.md` 保留中文版與英文版兩個並列的 H2 分段（第 9 行與第 347 行），
   **違反 `team.md` 的明文禁止**（ADR-0009）。
3. `DEPLOY.md` §2.2 的表清單**缺 J5 全部物件**（見叢集 C1）。

## 技術債登記簿

### 分級準則

| 級別 | 定義 |
|---|---|
| **P1** | 已造成或即將造成**正確性或安全性**的實際失效；或會阻擋當前進行中的工作 |
| **P2** | **侵蝕型**風險：不會馬上壞，但隨每次變更放大，且缺乏發現機制 |
| **P3** | 衛生與局部問題：影響可讀性、一致性或單點行為，範圍可控 |

### 叢集 C1 — 「多源真實」（T1／T2／T3／T4，加上角色清單三副本）

**這是全 repo 最重要的技術債叢集**，四項是同一個根因的不同表現：
**同一件事實有多份手寫來源，且沒有任何機制驗證它們一致。**

| id | 級別 | 內容 |
|---|---|---|
| **T1** | **P1** | **Schema 三處來源不一致，J5 欄位僅存在於 runtime 補丁。** `users.authorization_status` 與 `role_authorization_requests` 表**只存在於 `backend/database.py::_ensure_j5_schema()`**，在 `schema_rbac.sql`、`schema.sql`、`DEPLOY.md` §2.2 表清單中**完全找不到**（已對三檔 grep 確認零命中）。`deploy/docker-compose.deploy.yml` 把 `schema_rbac.sql` 掛為 initdb，因此新環境的 `users` 建出來是 `role VARCHAR NOT NULL` 且**沒有 `authorization_status` 欄位**；J5 功能能運作純粹依賴後端啟動時執行 `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` 與 `ALTER COLUMN role DROP NOT NULL` |
| **T4** | **P1** | **`schema_rbac.sql` 宣稱可重跑，實際會破壞資料。** 第 178 行 `DELETE FROM role_permissions;` 無條件執行，使「重跑腳本取得新 DDL」與「保留 Admin UI 調整」互斥 —— **而 T1 的修法正好需要重跑** |
| **T3** | **P2** | **RBAC seed 雙來源、無同步驗證。** 308 列預設矩陣同時存在於 `schema_rbac.sql`（第 180–489 行 INSERT）與 `backend/services/rbac_seed_data.py`。後者 docstring 寫「由 `schema_rbac.sql` 產生（勿手改；改 SQL 後重跑產生腳本）」，**但該產生腳本不存在於 repo**，CI 也**沒有任何一致性檢查** |
| **T2** | **P2** | **`schema.sql` 已嚴重落後。** 缺 `wa_lenses`、`role_permissions`、J5 全部物件，且 `users.role` 仍為 `NOT NULL`。任何以此檔推斷 schema 的判斷都會出錯 |
| （附） | **P3** | **角色清單三份手寫副本**：`rbac.py::CANONICAL_ROLES`、`user_router.py::ROLE_DISPLAY_NAMES`、`AdminPage.tsx::AVAILABLE_ROLES`，彼此無同步機制 |

#### T1 為何列為最高優先（給下游 stage 的直接提醒）

T1 不只是「文件沒更新」，它是 **`project.md` blocking 規則的既存違反**
（`## Mandated` 的「變更資料庫結構時必須同步更新 `schema_rbac.sql` 與 `DEPLOY.md`」）。

更重要的是：**目前進行中的 intent（在 `users` 表加最後活動時間欄位）會踩到完全相同的路徑。**
新欄位若只加在 ORM 與 `_ensure_*_schema()` 補丁，就是再製造一次 T1；
若要正確落三處，又會撞上 T4（重跑 `schema_rbac.sql` 會清掉 Admin UI 對權限矩陣的調整）。

**因此 T1 與 T4 必須被視為一組，且在該 intent 的設計階段就處理，不能推遲。**
相關的執行期實作點與 blocking 檔案清單見 `architecture.md` 的「對新變更的架構約束」。

### 叢集 C2 — 「安全預設值與未受保護面」（T6／T7／T8／T20）

根因：**開發便利性的預設值被留在了會被部署的路徑上。**

| id | 級別 | 內容 |
|---|---|---|
| **T6** | **P1** | **JWT secret 有可用的程式內預設值。** `auth.py:13` 為 `SECRET_KEY = os.environ.get("JWT_SECRET", "<已 commit 進 git 的固定字串>")`。若未注入則**靜默**使用該公開已知字串簽 token —— 任何人都能偽造任意身分的 token。`deploy.yml` 有 secrets 檢查保護 staging 路徑；**本機與其他部署路徑無保護**，且失敗模式是靜默的（不會有警告） |
| **T7** | **P1** | **預設帳號密碼寫死。** `database.py` 在空 DB 時建立 11 個 persona 帳號，密碼為 `<username>123`，**全部 `approved` 且帶正式角色**；另建 `admin`／`admin123`（`Platform_Admin`）。`schema_rbac.sql:500` 亦 commit 了 `admin123` 的 bcrypt hash。等於任何新環境開機即帶 12 個可預測憑證的帳號，其中一個是最高權限 |
| **T8** | **P1** | **WebSocket 端點無驗證。** `/api/collab/ws/{workspace_id}` 是 46 個端點中唯一沒有任何 `Depends` guard 的業務端點。連線層不檢查 JWT，任何知道 workspace id 的連線都能收到共編廣播 |
| **T20** | **P2** | **`deploy.yml` rollback job 權限較寬**：`contents: write` + `pull-requests: write` + `actions: write`，且在 self-hosted runner 執行。功能上必要（要開 revert PR 並 dispatch workflow），但值得評估是否可用範圍更窄的 token |
| （附） | **P2** | **公開端點可觸發 seed**：`GET /api/auth/roles/catalog`（無驗證）在回應前呼叫 `ensure_role_permissions_seeded(db, force=False)`。實際影響有限（表非空即 return），但這是一條**匿名可達的寫入路徑** |

**與 ADR-0006 security baseline 的關係**：該 ADR 把 IAM、encryption、network exposure、
audit logging 列為 hard constraint。T6／T7／T8 三項都落在 **IAM 與 network exposure** 面向，
是這條 hard constraint 目前最明確的未滿足處。

### 叢集 C3 — 「驗證缺口」（T5／T10／T11／T12／T18）

根因：**規則寫在文件裡而不是寫在檢查器裡。**

| id | 級別 | 內容 |
|---|---|---|
| **T10** | **P2** | **關鍵模組零測試 + 零 HTTP 層測試。** 無任何測試使用 `TestClient`，**46 個端點沒有一個被實際打過**。零測試模組：`user_router.py` 的 HTTP 層(831)、`review_orchestrator.py` 狀態機主體(510)、`agent_router.py`(148)、`lens_router.py`(108)、`wa_score_service.py`(104) |
| **T5** | **P2** | **Backend 依賴 100% 未 pin 且無 lockfile。** 11 個依賴無一版本約束。CI、Docker build、staging 部署三處各自解析當下最新版 —— 「CI 綠燈」與「staging 跑得起來」用的可能不是同一組版本。對照之下 frontend 有已 commit 的 `package-lock.json` |
| **T11** | **P2** | **無覆蓋率量測。** `org.md` 的 80% 門檻目前是宣告而非閘門，既無法量測也無法強制 |
| **T12** | **P2** | **Python 側無 lint／format／type check。** 前端有 ESLint + `tsc` 且 CI 強制，後端完全沒有對等物 |
| **T18** | **P3** | **Hypothesis 快取（`backend/.hypothesis/`）已 commit 進 repo。** 應加入 `.gitignore` |

**這個叢集的共同特徵**：每一項都讓「偏差在合併前被發現」變得不可能。
C1 的一致性問題之所以能長期存在，正是因為 C3 沒有機制去發現它。
**修 C3 的投資報酬率高於逐項修 C1**，因為 C3 修好後 C1 不會再生。

### 叢集 C4 — 「前後端契約手工維持」（T13／T19）

| id | 級別 | 內容 |
|---|---|---|
| **T13** | **P2** | **前端無集中 API client。** 32 處 `fetch()` 散落 8 支頁面與元件，各自手寫 header、錯誤解包、提示。**無統一 401 處理、無 retry、無型別集中定義。** 後端 `UserSchema` 與前端 `DbUser` interface 是兩份手寫鏡像，**一致性只靠人工維持**，漏改不會有任何工具報錯（e2e 也未斷言表格內容） |
| **T19** | **P3** | **型別依賴版本錯配**：`@types/react-router-dom@^5.3.3` 搭配 `react-router-dom@^6.22.0`。v6 起自帶型別，此套件多餘且描述的是 v5 API |

**與進行中 intent 的關係**：在 `users` 加欄位並顯示於 Admin 表格，
必須**同時**改 `user_router.py` 的 `UserSchema` 與 `AdminPage.tsx` 的 `DbUser`，
且新增的抓取邏輯必須沿用 `fetchUserList`／`fetchUsers` 的拆分形狀（否則 lint 紅燈）。

### 叢集 C5 — 「衛生與局部」（T9／T14／T15／T16／T17）

| id | 級別 | 內容 |
|---|---|---|
| **T16** | **P3** | **`DEPLOY.md` 保留雙語分段**：檔內同時存在中文版與英文版兩個並列的 H2 分段標題（分別在第 9 行與第 347 行）。**`team.md` 明文禁止**（ADR-0009），但 `validate_docs_traditional_chinese()` **只掃 record 目錄**，故 CI 不會擋下。**這個「驗證器盲區」本身比違規更值得注意** —— 它是 C3 根因在治理層的又一個實例 |
| **T9** | **P3** | **超大檔案**：`AssessmentPage.tsx`(1,856)、`WorkspacePage.tsx`(1,170)、`wa_rule_engine.py`(973)、`user_router.py`(831)。**四者性質不同**：`wa_rule_engine` 大但高內聚（單一演算法），是可接受的；`user_router` 大且低內聚（缺 service 層），是四者中最值得拆的；兩個前端頁面是完整功能 UI，拆分收益需權衡 |
| **T14** | **P3** | **已知 deprecated API**：`main.py:41` 的 `@app.on_event("startup")`（FastAPI 已建議改用 lifespan）；`auth.py:31,34` 的 `datetime.utcnow()`（Python 3.12 已 deprecated，應改 `datetime.now(timezone.utc)`）。**與 T5 相乘會變成風險**：依賴未 pin，上游移除相容層時會無預警失效 |
| **T15** | **P3** | **密碼雜湊邏輯重複兩份**：`database.py::hash_password()` 與 `auth.py::get_password_hash()` **逐字相同**。安全相關邏輯不應有兩份副本 |
| **T17** | **P3** | **環境不一致**：PostgreSQL 15（本機 `docker-compose.yml`）vs 16（staging `deploy/docker-compose.deploy.yml`） |

### 全部 20 項的級別索引

| 級別 | 項目 | 數量 |
|---|---|---|
| **P1** | T1、T4、T6、T7、T8 | 5 |
| **P2** | T2、T3、T5、T10、T11、T12、T13、T20 | 8 |
| **P3** | T9、T14、T15、T16、T17、T18、T19 | 7 |

## 修復順序建議

排序依據是「解鎖後續工作的能力」與「阻止債務再生」，不是嚴重度單一維度。

**第一梯次 — 阻擋當前工作，必須先處理**

1. **T1 + T4 一起處理**（不可拆）。在 `schema_rbac.sql` 建立一條**不破壞資料的 schema 演進路徑**：
   把無條件的 `DELETE FROM role_permissions;` 改為冪等的 upsert，或把 seed 與 DDL 拆成兩支腳本。
   完成後把 J5 物件補進 `schema_rbac.sql` 與 `DEPLOY.md` §2.2。
   **這是所有觸及 `users` 表的工作的前置條件。**

**第二梯次 — 阻止債務再生（投報率最高）**

2. **T3 的一致性檢查**：寫一個 CI 步驟比對 `schema_rbac.sql` 的 308 列 INSERT 與
   `rbac_seed_data.py` 的 308 筆 tuple。這比補上那支「不存在的產生腳本」更直接，
   且能立刻阻止漂移。
3. **T10 的第一步**：引入 `TestClient` 並為 `user_router` 的 `J3a` 端點寫端到端測試。
   不需要一次補滿 46 個端點 —— 先讓「HTTP 層可被測試」這件事成立。
4. **T12 + T11**：加入 Ruff（lint + format）與 coverage 量測到 backend CI job。
   兩者都是設定檔層級的工作，成本低、立刻讓 `org.md` 的宣告變成可執行的閘門。
5. **T5**：產生 `requirements.lock` 或改用 `pyproject.toml` + lockfile，讓三處部署解析同一組版本。

**第三梯次 — 安全預設值**

6. **T6**：移除 `JWT_SECRET` 的程式內預設值，改為缺少時**啟動失敗**（fail fast）。
7. **T7**：把 persona 帳號的 seed 改為需明確開關（環境變數）；`admin` 預設密碼改為
   啟動時產生並要求首次登入變更，或同樣改為必須注入。
8. **T8**：為 WebSocket 端點加入 JWT 驗證（連線時以 query param 或 subprotocol 傳 token）
   並檢查該使用者對 workspace 的存取權。

**第四梯次 — 衛生**

9. T16（清 `DEPLOY.md` 雙語分段）**並同時擴大 `validate_docs_traditional_chinese()` 的掃描範圍**
   到 record 目錄以外 —— 修違規而不修盲區的話，下次還會發生。
10. T18（`.hypothesis/` 加入 `.gitignore`）、T19（移除 `@types/react-router-dom`）、
    T15（合併雜湊函式）、T14（換掉 deprecated API）、T17（統一 PostgreSQL 版本）。
11. T9 的 `user_router.py` 拆分（抽出 service 層）—— 建議在 T10 有測試保護之後才做。
12. T2（補齊或明確廢止 `schema.sql`）—— 若 `schema_rbac.sql` 已是唯一部署腳本，
    **刪掉 `schema.sql` 比維護它更誠實**。
