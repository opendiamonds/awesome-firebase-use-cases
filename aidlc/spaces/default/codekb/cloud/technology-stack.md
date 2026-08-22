# 技術棧（Technology Stack）

> Reverse Engineering 合成產物｜repo `cloud`｜HEAD `c3de2c8`｜intent `260819-cost-finops`｜mode **Modify overlay for C1**（版本以 developer scan 與 `requirements.txt`／`package.json` 為準）

## 執行時與語言

| 層 | 語言／執行時 | 備註 |
|---|---|---|
| Frontend | TypeScript ~6.0、React 19.2、瀏覽器 SPA | `frontend/package.json`；Vite 開發／建置 |
| Backend | Python 3、FastAPI **精確釘選** `0.141.1` | `uvicorn` 服務；`fastapi[standard]==0.141.1` |
| Data | PostgreSQL | `psycopg2-binary`、SQLAlchemy ORM |
| Embed | JavaScript（第三方 iframe） | embed.diagrams.net |
| Tooling | Bun（AIDLC 工具鏈）、Node（frontend）、pip | `bun` 用於 `.claude/tools` |

**未在棧上的 C1 相關技術**：無 boto3、無 Google Cloud Billing SDK、無 Azure Retail Prices 客戶端、無獨立 cost microservice。不要為本 overlay 發明 SKU 或價目 API 版本。

## 框架與主要程式庫版本

### Frontend（npm）

| 套件 | 版本約束 | 用途 |
|---|---|---|
| `react`／`react-dom` | ^19.2.6 | UI |
| `react-router-dom` | ^6.22.0 | SPA 路由 |
| `vite` | ^8.0.12 | 建置／dev server |
| `typescript` | ~6.0.2 | 型別 |
| `tailwindcss`＋`@tailwindcss/postcss` | ^4.3.0 | 樣式 |
| `html2canvas`／`jspdf` | ^1.4.1／^4.2.1 | 匯出 |
| `eslint` 生態 | eslint ^10、typescript-eslint ^8 | Lint |
| `@playwright/test` | ^1.56.0 | e2e（`frontend/tests/e2e/regression.spec.ts`） |
| `openapi-typescript` | 7.13.0（`gen:types` npx） | 從 `openapi.json` 寫入 `src/types/api.d.ts` |

腳本：`dev`、`build`（`tsc -b && vite build`）、`lint`、`test:e2e`、`gen:types`、`check:types`。無 React 單元測試 runner（無 Jest／Vitest）。

### Backend（pip，`backend/requirements.txt`）

| 套件 | 版本 | 用途 |
|---|---|---|
| `fastapi[standard]` | **==0.141.1**（精確等值釘選） | HTTP API；與 OpenAPI dump 位元決定性綁定 |
| `pydantic` | **==2.13.4** | 請求／回應模型；同上，跨版本會讓規格漂移檢查誤紅 |
| `uvicorn` | 未釘選 | ASGI 伺服器 |
| `sqlalchemy`、`psycopg2-binary` | 未釘選 | ORM／DB |
| `passlib[bcrypt]`、`bcrypt`、`pyjwt` | 未釘選 | 認證 |
| `claude-agent-sdk` | 未釘選 | Agent 編排 |
| `httpx` | 未釘選 | **僅** n8n 圖示 webhook 與 diagrams.net PNG export——**非價目表** |
| `python-dotenv` | 未釘選 | 環境 |
| `hypothesis` | 未釘選 | Property-based testing（ADR-0006）；既有落點不含 cost calculator |

升版 FastAPI／Pydantic 時必須在**同一個 PR** 重 dump `openapi.json` 並重產前端型別。其餘 pip 套件仍未 pin。

## 建置、部署、LLM 與品質工具

| 能力 | 工具 |
|---|---|
| Frontend build | Vite 8 + `tsc -b`（不依賴 backend 執行） |
| OpenAPI 契約 | `backend/scripts/dump_openapi.py` → `openapi.json`；CI `--check` 擋漂移（post-`8c90f40`） |
| Backend image | `backend/Dockerfile` |
| Compose staging | `deploy/` |
| CI | `.github/workflows/ci.yml`：repo contract → lint／build → **OpenAPI spec drift** → unittest → Docker build |
| Deploy | `.github/workflows/deploy.yml`（合併至 `ut`） |
| LLM | `LLM_PROVIDER`：OpenRouter 環境映射 **或** claude CLI（`llm_provider.py`，提交 `c683c1f` 引入） |
| n8n | 圖示 webhook + Basic Auth（`diagram_builder.py`） |
| Contract | `scripts/validate_repo_contract.py`、`scripts/validate_env_contract.py` |
| Agentic WF | gh-aw：contract-guard、pr-reviewer、ui-regression、deploy-doctor、spec-sync 等 |
| Specs | Markdown、Mermaid、draw.io；AIDLC v2 於 `aidlc/` |
| 測試 | backend `python -m unittest discover -s tests -v`（無 `pytest.ini`、無 coverage 門檻）；frontend Playwright |

安全基線延伸（ADR-0006）預設啟用，與本技術棧並行；production 雲帳號不在本 repo 技術棧範圍。Cost calculator 被 ADR-0006 列為 PBT hard-constraint 落點，但 **模組不在棧上**，故該約束對 C1 現況為 N/A（非豁免、非違反）。
