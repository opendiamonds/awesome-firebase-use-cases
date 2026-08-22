# Reverse Engineering 時間戳

> Freshness marker for space-level codekb｜repo `cloud`｜HEAD `c3de2c8`｜intent `260819-cost-finops`｜mode **Modify overlay for C1**

## 掃描元資料

| 欄位 | 值 |
|---|---|
| 執行時刻（UTC） | `2026-08-19T06:26:38Z` |
| Commit（full） | `c3de2c8baa72120ca09e27d12dd57833446a6f5c` |
| Commit（short） | `c3de2c8` |
| 分支脈絡（scan 時） | `luojingting/feat/cost-estimation-finops` |
| Intent | `260819-cost-finops`（feature — Cost Estimation & FinOps / TCO） |
| 模式 | **Modify**：保留 2026-08-06（`8c90f40`、intent `260806-a1-a3-ux`）仍成立的 A1／A3／J 架構總覽，就地疊加 C1 事實並訂正已證偽的 hotspot |
| Active space | `default` |
| Codekb 目錄 | `aidlc/spaces/default/codekb/cloud/` |
| 專案類型 | brownfield（workspace 根即單一 repo `cloud`） |
| Pipeline | reverse-engineering link 2／FINAL（architect synthesis） |
| 上游輸入 | `<record>/inception/reverse-engineering/developer-scan.md`（2026-08-19；未改應用碼、未先覆寫 codekb） |

本檔為 per-repo codekb 的過期指標；condition「Always rerun for freshness」下，後續 RE 應以新 commit／新時刻覆寫此組 artifacts。

## 分析範圍與 Hotspots

**涵蓋範圍**

- `backend/`（五組 router、agents、`diagram_builder`、`prompt_guard`、`wa_rule_engine`、RBAC seed、tests）
- `frontend/`（`App.tsx` 路由、Workspace A1、Assessment A3、`NavChromeContext`／Sidebar、`DrawioCanvas`、Admin 最後活動／分頁、權限頁 C 欄標籤）
- `schema.sql`、`schema_rbac.sql`、`openapi.json`、`frontend/src/types/api.d.ts`
- `deploy/`、CI／OpenAPI drift、`backend/requirements.txt` 釘選版本
- 對抗式確認 C1 缺席：無 `*cost*`／`*pricing*`／`*tco*` 檔、無 `/api/cost*`、無 boto3／價目 HTTP

**未深入／排除**

- 未修改任何應用程式原始碼（僅覆寫 space-level codekb 9 檔）
- 未執行完整 unittest／e2e 作為本合成步驟的一部分
- 雲端供應商 production、價目 API 連線、其他 sibling repos
- 未發明 SKU、價格數字或成本端點

### 本 round 新列的 C1 hotspots

1. 圖擷取不可定價：`parse_diagram_summary` 僅 `id`／`label`／`style`；`DRAW_INPUT_SCHEMA` 無 sku／hours；`user_diagrams` 只有 `xml_data` blob。
2. Cost calculator、pricing client、public price list HTTP、硬編碼 USD **ABSENT**。
3. UI **ABSENT**：無 Sidebar C 組、無 `/cost`、無 `CostPage`、成功卡無 TCO CTA、`DefaultRedirect` 無 C1。
4. 通知／預算 **ABSENT**：無 inbox、無 budget／overspend 表或 API。
5. RBAC：C1 種子 PRESENT（僅 `FinOps_Analyst` 可 edit），執行期守衛與測試 ABSENT。
6. WA `COST-*` 啟發式易被誤認為 TCO，且 **零測試**。
7. ADR-0006 calculator PBT 目前 N/A（無模組）；落地時將變成 blocking。
8. OpenAPI／generated types 無 cost paths；新 API 必走 dump＋`gen:types`。

### 先前 A1／A3 hotspots（相對 `8c90f40` codekb）

| Hotspot（2026-08-06） | HEAD `c3de2c8` | 狀態 |
|---|---|---|
| Sidebar 不可收合、固定 `w-64` | `NavChromeContext` + `cloud360.nav.sidebarCollapsed` | **已關閉** |
| Sidebar 扁平 IA、缺 A／J 分組 | 「架構」「系統管理」可收放；仍無 C 組 | **已關閉**（C 組轉入 C1） |
| Edges 缺 exit／entry ports | `compute_edge_waypoints` + `exitX/Y` `entryX/Y` | **已關閉** |
| Edge `parent` 恆 `"1"` | 仍 `"1"` | **仍開（殘項）** |
| Draw.io save／exit 未處理 | `DrawioCanvas` 已接 `save`／`exit` | **已關閉** |
| Undo 因 autosave→load 損壞 | 註解稱已避免 echo load；scan 未重驗 UX | **仍開／未重驗** |
| 無 prompt refusal | `prompt_guard.py` PRESENT | **已關閉** |
| 無 HTTP `TestClient` | 僅 `test_user_list_endpoint.py`（auth list） | **部分關閉**（非 C1） |
| fastapi 未釘選 | `fastapi==0.141.1`、`pydantic==2.13.4` + OpenAPI drift job | **已關閉（棧債）** |

仍 Keep 的 baseline：模組化單體、五組 router、可運行故事為 A1／A3／J、`user_diagrams` 無結構化資源列、11 canonical roles 含 `FinOps_Analyst`、staging／production 雲帳號 out of scope、**無 cost API**。
