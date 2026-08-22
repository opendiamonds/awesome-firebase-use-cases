# 程式碼結構（Code Structure）

> Reverse Engineering 合成產物｜repo `cloud`｜HEAD `c3de2c8`｜intent `260819-cost-finops`｜mode **Modify overlay for C1**

## 頂層目錄組織

| 路徑 | 角色 |
|---|---|
| `backend/` | FastAPI 應用、服務層、prompts、lenses、unittest |
| `frontend/` | React SPA（Vite）、元件、頁面、e2e Playwright、generated `src/types/api.d.ts` |
| `deploy/` | Staging Docker Compose 與部署資產 |
| `scripts/` | `validate_repo_contract.py`、`validate_env_contract.py`、OpenAPI dump、TCMS |
| `schema.sql`、`schema_rbac.sql` | 可攜 PostgreSQL DDL／RBAC seed 來源 |
| `openapi.json` | 公開契約清冊（CI `--check` 擋漂移） |
| `aidlc/` | AI-DLC 工作區（memory、intents、codekb、knowledge） |
| `.github/workflows/` | CI、deploy、gh-aw agentic workflows |
| `.claude/` | upstream AI-DLC 框架（升級時覆蓋；規則寫在 `aidlc/.../memory`） |

應用執行時碼與 AIDLC 產物刻意分離：執行時留在 `backend/`／`frontend/`；本檔所在的 `aidlc/spaces/default/codekb/cloud/` 為 space 級程式知識庫。

**C1 檔名搜尋**（`backend/`、`frontend/`）：`*cost*`／`*pricing*`／`*tco*`／`*finops*` → **0 檔**。成本能力沒有獨立套件或目錄。

## Backend 模組分類

```
backend/
  main.py                 # FastAPI app、CORS、五組 router mount、startup init_db
  database.py             # 連線與 schema ensure（含 _ensure_last_activity_schema）
  models.py               # SQLAlchemy ORM；user_diagrams 無 sku／cost 欄
  lenses/                 # WA lens JSON
  prompts/                # design agent system prompt
  scripts/dump_openapi.py # 產出 repo 根 openapi.json
  services/
    agent_router.py       # POST /generate、/generate-wa-collab
    prompt_guard.py       # NEW since 8c90f40：平台自我竄改預檢
    llm_provider.py       # NEW：LLM_PROVIDER（OpenRouter 或 claude CLI）
    design_agent.py       # LLM 架構產生；DRAW_INPUT_SCHEMA 無 sku／hours
    diagram_builder.py    # groups/nodes/edges → mxGraph XML；n8n Basic Auth 取 SVG
    review_router.py      # reviews CRUD、PNG、retry、detect-provider
    review_agent.py / review_orchestrator.py / wa_*  # A3 審核編排
    wa_rule_engine.py     # parse_diagram_summary + COST-* 啟發式（非 TCO）
    lens_router.py / lens_service.py / wa_lens_engine.py
    collab_router.py      # diagrams、chat、share、WS
    user_router.py        # auth、users、roles、permissions、list 分頁
    activity.py           # last_activity_at
    auth.py / rbac.py / rbac_seed_data.py  # 含 FinOps_Analyst 與 C1 種子
    wa_collab_orchestrator.py
  tests/                  # 21 個 test_*.py；unittest + Hypothesis；無 test_cost*
```

模式：Router 薄、Service 厚；agent／WA 邏輯與 HTTP 邊界分離。DDL 變更須同步 `schema_rbac.sql` 與 `DEPLOY.md`（project Mandated）。C1 **沒有新表**，故目前無 schema 增量義務。

**ABSENT（對抗式搜尋，勿發明）**：`cost_calculator`、`pricing_client`、`PriceList`、`GetProducts`、`cloudbilling`、`retailprices`、`boto3`、`google.cloud`、`azure.mgmt`。`httpx` 實際呼叫僅兩處：n8n webhook（`diagram_builder.py`）、diagrams.net／draw.io PNG export（`review_router.py`）。

## Frontend 模組分類

```
frontend/src/
  App.tsx                 # 路由表；無 /cost；DefaultRedirect 無 C1
  types/api.d.ts          # 由 openapi-typescript 產生；無 cost 型別
  pages/                  # 僅 8 檔：Login、Forbidden、WaitingApproval、
                          # Workspace、Assessment、Admin、AuthorizationRequests、
                          # RolePermissions — 無 CostPage.tsx
  components/
    Layout.tsx / Sidebar.tsx / NavChromeContext.tsx  # 可收合；架構／系統管理；無 C 組
    DrawioCanvas.tsx           # init／load／autosave／save／exit
    ChatBox.tsx / DiagramPreviewPanel.tsx / ShareModal.tsx / RouteGuard.tsx
    LastActivityCell.tsx / PaginationControl.tsx     # J 域 NEW，非 C1
  context/                # auth-context（token、can、canArch）
  utils/                  # apiUrl、downloadDrawio 等
```

模式：頁面擁有資料流與 fetch；畫布透過 controlled `xml`＋`onAutosave`；權限以 hook 門禁。`CapabilityRoute` 從未以 `C1` 呼叫。`RolePermissionsPage.tsx` 僅以標籤露出 C／C1／C2／C3 支柱名。

## 慣用模式與熱點檔案

| 模式 | 說明 | 代表檔 |
|---|---|---|
| Streaming／協作生成 | Workspace 呼叫 `generate-wa-collab` 並更新 xml | `WorkspacePage.tsx`、`agent_router.py` |
| Embed 橋接 | iframe `postMessage` 裝載／autosave／save／exit | `DrawioCanvas.tsx` |
| XML 組裝 | 絕對座標 → 相對 parent → mxCell（含 exit／entry） | `diagram_builder.py` |
| Prompt 預檢 | 命中平台竄改則不呼叫 LLM | `prompt_guard.py` |
| RBAC 矩陣 | 角色 × 故事旗標；C1 種子已在、執行期無守衛 | `rbac.py`、`rbac_seed_data.py`、`RolePermissionsPage.tsx` |
| WA 啟發式 | 從 label／style 關鍵字產 findings（含 COST-*） | `wa_rule_engine.py` |
| Property-based | 產圖／規則／auth／activity；**無** cost calculator | `backend/tests/` |

與 **C1 intent** 相關的修改面（若落地，blast radius 起點；今日皆為缺口而非既有模組）：須新寫 extract overlay 或擴充 `DRAW_INPUT_SCHEMA`／mxCell、pricing client、calculator、Cost 頁與 Sidebar C 組、可選 budget／notify 表，並 `dump_openapi.py` + `gen:types`。既有可重用鉤子僅：`parse_diagram_summary` 的 label／style、`user_can(..., "C1", ...)`、權限頁欄名、`TestClient` 樣板（`backend/tests/helpers.py`、`test_user_list_endpoint.py`）。
