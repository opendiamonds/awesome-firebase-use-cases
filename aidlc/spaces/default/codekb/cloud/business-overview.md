# 業務總覽（Business Overview）

> Reverse Engineering 合成產物｜repo `cloud`｜HEAD `c3de2c8`（`c3de2c8baa72120ca09e27d12dd57833446a6f5c`）｜intent `260819-cost-finops`｜mode **Modify overlay for C1**（保留 2026-08-06 `8c90f40` 仍成立的 A1／A3／J 敘述）

## 產品定位與價值主張

Cloud-360 是 AI-native 的多雲（AWS / GCP / Azure）架構設計與運維平台。核心價值是把「用自然語言描述架構需求 → 產生可編輯的 draw.io 架構圖 → 以 Well-Architected（WA）lens 審核與改善」串成一條連續工作流，並以 RBAC 控制誰可檢視、編輯、審核。

目前可運行能力集中在自有 staging（`cloud360.danniel.cc`，見 ADR-0007）；雲端供應商正式 production 環境仍在範圍外（ADR-0001 / ADR-0002）。方法論以 Spec-Driven Development 與 AI-DLC v2 為基礎。

**執行時產品面仍是 A1 Workspace、A3 Assessment、J Admin。** C1（Cost Estimation & FinOps / TCO）在權限種子與權限頁標籤已露出，但沒有成本頁、沒有計價 API、沒有 TCO 計算器——不可把 WA 規則引擎的 `COST-*` 啟發式 findings 當成已有成本能力。

## 主要使用者旅程

| 故事／領域 | 主角 | 目標 | 入口 | HEAD 狀態 |
|---|---|---|---|---|
| A1 架構圖生成 | 架構師／工程師 | 以聊天提示產生／迭代架構圖，於 embed.diagrams.net 畫布編輯並持久化 | `/workspace` → `WorkspacePage` | **PRESENT**（可運行） |
| A3 評估與審核 | 審核者／架構師 | 對已存架構圖執行 WA review、檢視 findings／scores、管理 lens | `/assessment` → `AssessmentPage` | **PRESENT**（可運行） |
| J 管理（權限） | 管理員 | 使用者、角色授權請求、角色–故事權限矩陣；Admin 另有最後活動時間與分頁 | `/admin/users`、`/admin/authorization-requests`、`/admin/role-permissions` | **PRESENT**（J 域增量，非 C1） |
| 協作 | 協作者 | 架構圖 CRUD、聊天歷史、分享、WebSocket 同步 | `/api/collab` + WS | **PRESENT** |
| C1 TCO 與流量預算 | FinOps／架構師（種子已定） | 從架構圖估算總擁有成本、預算與超支警示 | 應為 `/cost` 或 Sidebar「成本」組 | **ABSENT**（僅 `RolePermissionsPage` 欄名 `C1: 'TCO 與流量預算'`） |

權限以故事級旗標驅動側欄與路由守衛：`Sidebar` 依 `canArch('view')`、`can('A3','view')`、`can('J3a'|'J3b','view')` 決定可見項（`frontend/src/components/Sidebar.tsx`）。**無** `can('C1', …)`；`DefaultRedirect`（`frontend/src/App.tsx`）路徑為 A1→A3→J3a→J3b，無 C1 分支。

C1 預設矩陣（`backend/services/rbac_seed_data.py` ≡ `schema_rbac.sql`）：僅 `FinOps_Analyst` 對 C1 有 `edit`；`Project_Architect`／`Project_Editor` 僅 `view`。因頁面不存在，這些旗標目前只出現在權限矩陣 UI。

## 範圍與邊界

**In scope（目前 codekb 所見、仍可運行）**

- 後端 FastAPI：認證／RBAC、架構產生（agent）、協作圖庫、WA review／lens（`backend/main.py` 五組 router）
- 前端 React SPA：Workspace（A1）、Assessment（A3）、管理面（8 個 pages，無 `CostPage`）
- PostgreSQL schema（`schema.sql`、`schema_rbac.sql`）與 staging Docker 部署
- CI contract／lint／build／OpenAPI drift／unittest／Docker；合併至 `ut` 後部署 staging
- A1／A3 UX 修復後的殼層：可收合 Sidebar（`NavChromeContext`）、A／J 分組、draw.io save／exit、`prompt_guard`

**C1 產品面（本 overlay 結論：尚未進入執行時範圍）**

- 圖資源擷取：`parse_diagram_summary`（`backend/services/wa_rule_engine.py`）只產出 `id`／`label`／`style`，**無 SKU**
- 定價客戶端、價目表 HTTP、硬編碼 USD、TCO 計算器：**ABSENT**
- `user_diagrams` 僅 `xml_data` blob，無 sku／provider／cost／budget 欄（HEAD 與 `8c90f40` DDL 相同）
- 持久化 inbox／通知中心／budget 表：**ABSENT**

**Out of scope（除非新 ADR）**

- 雲端供應商 production credentials、destructive cloud IaC apply
- Native iOS／Android app

## 與本 intent 的業務關聯

Intent `260819-cost-finops` 要把 C1（TCO／流量預算）做成可運行能力。HEAD 上的業務事實：

1. **沒有**「從圖到金額」的產品路徑。A1 產出 mxGraph XML；A3 用同一份 XML 做 WA 關鍵字啟發式（含 `COST-OVERSIZE-HINT` 等），**不產生金額、不是 TCO**。
2. Workspace 成功卡三顆 CTA 為「繼續對話編輯」「生成 IaC 代碼」（coming-soon）「Well-Architected」——**無「估算成本／開啟 TCO」**（`WorkspacePage.tsx`）。
3. 權限頁已顯示支柱 `C: '成本與 FinOps'` 與故事 `C1`／`C2`／`C3` 欄名；這是 RBAC 標籤領先實作，不是產品頁。
4. 先前 intent `260806-a1-a3-ux` 的六項 UX 摩擦，多數已在 HEAD 關閉（見 `architecture.md`／`reverse-engineering-timestamp.md`）；它們不再是本 intent 的業務缺口，但殘項（Undo 未重驗、edge `parent` 仍 `"1"`）仍記載於品質評估。
