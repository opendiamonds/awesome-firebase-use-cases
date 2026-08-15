# Reverse Engineering Timestamp — Cloud-360

> 本檔是 `aidlc/spaces/default/codekb/cloud-360/` 這份程式碼知識庫的**新鮮度標記**。
> 使用本 codekb 的任何 stage 都應先讀本檔，確認基準是否仍然有效。

## 掃描基準

| 項目 | 值 |
|---|---|
| **日期** | 2026-08-08 |
| **Commit** | `8c90f40372ac810cc8f6ef41c46fc7a723031a1e` |
| **Commit 訊息** | `雜項(aidlc): 補記 PR #477 合併前後的 audit shard 事件` |
| **Commit 日期** | 2026-08-03 |
| **Branch** | `ut`（整合主幹） |
| **Repository** | `cloud-360` |
| **AIDLC stage** | `reverse-engineering`（inception 2.1，pipeline mode） |
| **執行方式** | 兩環 pipeline：第一環 developer agent 掃描，第二環 architect agent 綜整 |

### 工作目錄狀態註記

掃描當下工作目錄**並非乾淨**，存在未提交的變更（屬進行中的 intent
`260802-last-login-column` 的 ideation 產出，以及 memory 層的規則累積）。

**本 codekb 描述的是 commit `8c90f40` 的狀態，不包含那些未提交的變更。**
未提交變更集中在 `aidlc/spaces/default/` 之下（intents 與 memory），
**不觸及 `backend/`、`frontend/`、`scripts/`、`deploy/`、`.github/` 等應用程式碼與流程資產**，
因此不影響本 codekb 對系統本身的描述。

## 新鮮度再確認紀錄

| 日期 | 方式 | 結果 |
|---|---|---|
| 2026-08-11（上午） | 確定性驗證（非重掃） | ~~`HEAD` 仍為 `8c90f40`…**本 codekb 對 HEAD 仍然有效。**~~ **此判定無效，見下一列。** |
| 2026-08-11（下午） | **更正** | 上一列的驗證是拿**過時的本地 `ut`**（`8c90f40`）做的，而 `origin/ut` 當時已是 `67be019`、領先 8 個 commit（PR #484、#489）。以正確基準重驗後：**本 codekb 已過期。** |

### 過期判定（2026-08-11）

`origin/ut` 的 8 個 commit 觸及應用程式碼，其中**至少一項命中本檔自訂的「觸發完整重跑」條件**：

| 觸發條件 | 命中情形 |
|---|---|
| `backend/services/` 新增或刪除模組 | **命中** —— 新增 `backend/services/prompt_guard.py`（本 codekb 記載的「Service 模組 18」已不正確） |
| 新增或刪除 API 端點 | 未逐一核對（`agent_router.py` 有變更，端點數是否仍為 46 未驗證） |
| 資料表新增或刪除 | 未命中 |
| 架構風格改變 | 未命中 |
| 權限矩陣維度改變 | 未命中 |

另有多份檔案的內容已與實況偏離（`diagram_builder.py`、`review_agent.py`、`wa_collab_orchestrator.py`、多個前端元件、`deploy/` 設定）。

**對 intent `260802-last-login-column` 的影響：無。** 該 intent 的各 stage 是在 `8c90f40` 的 codekb 上作業，而 `origin/ut` 的 8 個 commit 與該 intent 依賴的介面**零重疊** —— 逐檔核對確認未觸及 `models.py`、`database.py`、`user_router.py`、`auth.py`、`rbac.py`、`rbac_seed_data.py`、`AdminPage.tsx`、`schema_rbac.sql`。故其設計決定不需重審。

**但本 codekb 作為跨 intent 共用的資產已經過期**，下一個需要它的 stage 應觸發完整重跑，不得沿用。此處如實標記，不留「仍然有效」的錯誤宣稱。

再確認的觸發原因：intent `260802-last-login-column` 因 scope-definition Revision 2（新增
PU-6 使用者清單分頁）回跳上游，reverse-engineering 隨之重跑。應用程式碼零變更，
故以驗證取代重掃；判定理由記於該 stage 的 `memory.md` ## Deviations。

## 分析範圍

### 已掃描

| 範圍 | 內容 |
|---|---|
| `backend/` | 全部：`main.py`、`models.py`、`database.py`、`services/`(18 支)、`lenses/`(3)、`prompts/`(6)、`tests/`(15)、`Dockerfile`、`requirements.txt` |
| `frontend/` | 全部：`src/`（8 頁面、9 元件、context、config、hooks、utils）、`tests/e2e/`、`Dockerfile`、`nginx.conf`、全部設定檔 |
| `scripts/` | `validate_repo_contract.py`（379 LOC） |
| `deploy/` | `docker-compose.deploy.yml`、`docker-compose.test.yml`、`cloudflared/config.yml` |
| `.github/` | `workflows/ci.yml`、`workflows/deploy.yml`、10 組 gh-aw workflow、`aw/actions-lock.json` |
| `.agents/` | `rules/ai-dlc.md`、`rules/aidlc-engine.md`、`workflows/aidlc-{init,construction}.md` |
| repo 根目錄 | `schema.sql`、`schema_rbac.sql`、`DEPLOY.md`、`docker-compose.yml`、`CLAUDE.md`、`README.md`、`AGENTS.md` |
| 規則層 | `aidlc/spaces/default/memory/` 的 `org.md`、`team.md`、`project.md`、`phases/inception.md` |

### 量化結果

| 指標 | 數值 |
|---|---|
| Backend 產品碼 | 7,171 LOC（Python 3.12） |
| Backend 測試碼 | 1,510 LOC（15 檔） |
| Frontend | 7,431 LOC TS/TSX + 234 LOC CSS |
| 驗證腳本 | 379 LOC |
| API 端點 | **46**（含 1 WebSocket、1 root health） |
| 資料表 | 7 |
| 權限矩陣 | 11 角色 × 28 story = 308 列 |
| Service 模組 | 18 |
| 前端頁面／元件 | 8／9 |
| 前端 `fetch()` 呼叫點 | 32 |
| Property-based 測試 | 5 檔、8 個 `@given` |
| E2E case | 6 |
| agentic workflows | 10 |
| 識別的技術債 | 20 項（T1–T20），歸為 5 個根因叢集 |
| `TODO`／`FIXME`／`HACK`／`XXX` 標記 | **0** |

## 範圍外項目

以下項目**未被分析**，使用本 codekb 時不應假設它們已被涵蓋：

| 項目 | 原因 |
|---|---|
| `.claude/` | AIDLC v2 upstream 框架檔，非本專案應用程式碼；升級時整批覆蓋 |
| `graphify-out/` | 知識圖譜產出物，非應用程式碼 |
| `aidlc/spaces/default/intents/` | AIDLC 工作產出，非程式碼 |
| **執行期行為** | 本次為**靜態分析**。未啟動系統、未執行測試套件、未實測 API、未查詢資料庫 |
| **實際安裝的套件版本** | backend 依賴全部未 pin，故無法從 repo 得知實際解析出的版本。清單中的「未 pin」是宣告狀態而非實際版本 |
| **staging 環境的實際 schema** | 未連線 `192.168.10.10` 查證。schema 描述來自 ORM／SQL 檔／DDL 補丁的靜態比對 |
| **LLM agent 的實際輸出品質** | prompt 內容已讀，但未評估產圖或評核建議的實際品質 |
| **`.hypothesis/` 快取內容** | 僅記錄其存在（技術債 T18），未分析內容 |
| 效能與負載特性 | 未量測 |
| 安全滲透測試 | 未執行。安全發現（T6／T7／T8）純由靜態閱讀得出 |

### 掃描過程中發現的文件與實況偏差

| 文件宣稱 | 實況 |
|---|---|
| `CLAUDE.md` 第 2 章的頂層 `tools/` 與 `workflows/` 目錄 | **不存在**。agentic workflows 在 `.github/workflows/`，AIDLC 工具在 `.claude/tools/` |
| `org.md` 的「Ruff／Black 配置於 repo root」 | Python 側**無任何** linter／formatter 設定檔 |
| `org.md` 的「Prettier 配置於 repo root」 | **無 `.prettierrc`** |
| `rbac_seed_data.py` docstring 的「改 SQL 後重跑產生腳本」 | **該產生腳本不存在於 repo** |
| `schema_rbac.sql` 檔頭宣稱的完整涵蓋 | **缺 J5 全部物件** |

## 新鮮度與失效條件

本 codekb 在下列任一情況發生時應重新產出或局部更新：

### 觸發完整重跑

- `backend/services/` 新增或刪除模組
- 新增或刪除 API 端點（端點數不再是 46）
- 資料表新增或刪除（表數不再是 7）
- 架構風格改變（例如拆出獨立服務、引入訊息佇列或快取層）
- 權限矩陣維度改變（角色數不再是 11 或 story 數不再是 28）

### 觸發局部更新

| 變更 | 應更新的檔案 |
|---|---|
| `users` 表欄位變更 | `component-inventory.md`、`api-documentation.md`、`architecture.md` |
| 依賴版本 pin 或 lockfile 引入 | `technology-stack.md`、`dependencies.md`、`code-quality-assessment.md`（T5） |
| 任一項技術債被修復 | `code-quality-assessment.md` |
| 新增測試框架或 coverage 機制 | `code-quality-assessment.md`、`technology-stack.md` |
| 部署拓撲變更（新容器、新環境） | `architecture.md`、`technology-stack.md`、`dependencies.md` |
| 新 story 或新角色 | `business-overview.md`、`api-documentation.md` |

### 已知會很快失效的部分

進行中的 intent `260802-last-login-column`（在 `users` 表加最後活動時間欄位）
一旦落地，下列描述會過時：

- `component-inventory.md` 的 `users` 表欄位表與「無任何時間戳欄位」的敘述
- `api-documentation.md` 的 `UserSchema` 資料契約與「Admin 表格 5 欄」
- `code-quality-assessment.md` 的 T1 敘述（若該 intent 同時修復了 schema 三源問題）

## 產出清單

本次逆向工程共產出 **9 份 artifacts**，全部位於
`aidlc/spaces/default/codekb/cloud-360/`：

| # | 檔案 | 內容 | 主要下游消費者 |
|---|---|---|---|
| 1 | `business-overview.md` | 業務領域、11 角色、28 story 能力表、四條業務主線、詞彙表 | requirements-analysis、user-stories |
| 2 | `architecture.md` | 架構風格判定與替代方案、系統脈絡、分層、橫切關注點、**Interaction Diagrams**、架構約束清單 | application-design、functional-design |
| 3 | `code-structure.md` | 倉庫佈局、模組組織、程式碼模式（後端 5 種／前端 5 種）、命名慣例 | code-generation |
| 4 | `api-documentation.md` | 46 端點完整清單、認證授權契約、SSE／WebSocket 契約、資料契約 | application-design、code-generation |
| 5 | `component-inventory.md` | 全元件清單與職責、依賴摘要、`users` 表詳解 | application-design、units-generation |
| 6 | `technology-stack.md` | 語言與框架版本、建置系統、**版本治理現況** | infrastructure-design、code-generation |
| 7 | `dependencies.md` | 外部依賴、外部服務、**隱性硬依賴 H1–H5**、內部依賴、三份 schema 來源、風險 R1–R10 | application-design、infrastructure-design |
| 8 | `code-quality-assessment.md` | 測試／lint／CI 現況、**T1–T20 依 5 個根因叢集與 P1/P2/P3 分級**、修復順序 | delivery-planning、requirements-analysis |
| 9 | `reverse-engineering-timestamp.md` | 本檔 | 全部（先讀本檔確認新鮮度） |

**codekb 的層級**：本目錄位於 **space 層級**（`aidlc/spaces/default/codekb/`），
是 `memory/`、`knowledge/`、`intents/` 的同層兄弟，**跨 intent 共用**，
不屬於任何單一 intent 的 record 目錄。本次為該目錄的**首次建立**。
