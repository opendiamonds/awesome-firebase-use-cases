# 程式碼品質評估（Code Quality Assessment）

> Reverse Engineering 合成產物｜repo `cloud`｜HEAD `c3de2c8`｜intent `260819-cost-finops`｜mode **Modify overlay for C1**（訂正 2026-08-06 已關閉的 A1／A3 債項；C1 以缺口而非覆蓋不足記載）

## 測試、Lint 與 CI

| 面向 | 現況 | 評估 |
|---|---|---|
| Backend unit／property | `backend/tests/`：**21** 個 `test_*.py`；unittest＋Hypothesis。7 檔共 **13** 個 `@given`（`test_design_agent` 2、`test_wa_rule_engine` 2、`test_diagram_builder` 2、`test_diagram_icons` 1、`test_collab` 1、`test_auth` 1、`test_activity` 4） | 產圖／規則／auth／activity 有 PBT 基礎。**cost calculator PBT：N/A**——模組 ABSENT，不是覆蓋率不足（ADR-0006 將在模組出現後變成 hard constraint） |
| HTTP 層 `TestClient` | **PRESENT，僅他域**：`backend/tests/test_user_list_endpoint.py` 用 `starlette.testclient.TestClient` 測 `/api/auth/list` 分頁欄位；樣板在 `tests/helpers.py` | 2026-08-06「零 HTTP 層測試」已過時。**沒有** cost 路由可測 |
| C1／pricing 測試 | **ABSENT**：無 `test_cost*`；`'C1'`／`"C1"` 在 `backend/tests/` **0** 命中；`test_rbac.py` 不覆蓋 C1／C2／C3 | FinOps 角色只出現在 A3／J3a／collab 的 deny 側（`test_review_authz`、`test_collab`、`test_j3a_view_permission`） |
| WA `COST-*` findings | codes 只定義於 `wa_rule_engine.py`（`COST-OVERSIZE-HINT`、`COST-NO-LIFECYCLE`、`COST-NAT-HINT`、`GCP-COST-NO-COMMIT`、`AZ-COST-NO-COMMIT`） | **零測試**；且 findings ≠ TCO |
| Frontend unit | 仍無 Jest／Vitest／Testing Library | 殼層與 canvas 橋幾乎無元件單元防護 |
| Frontend e2e | Playwright `frontend/tests/e2e/regression.spec.ts`：登入、RBAC 側欄、Admin 最後活動／分頁 | **無**成本頁 e2e |
| Coverage gate | ABSENT（無 `pytest.ini`／coverage 門檻）；CI `python -m unittest discover -s tests -v` | `org.md` 80% 仍是宣告而非閘門 |
| Lint／型別 | ESLint 10＋`tsc -b`；backend 依 CI unittest（`ci.yml` 前段無獨立 ruff／mypy job） | 建置期型別檢查健全 |
| Repo contract／OpenAPI | `validate_repo_contract.py`；**NEW** OpenAPI／generated types 漂移檢查 | 文件語言、禁止路徑／內容、契約位元有硬門禁 |
| CI 管線 | contract → lint／build → OpenAPI drift → unittest → Docker；`ut` → deploy | 與 org deploy-on-merge 一致 |
| 文件 | Specs／ADR／AIDLC artifacts 繁中（ADR-0009） | 方法論文檔品質高 |

總評：平台級治理（contract、CI、OpenAPI drift、deploy、specs）仍成熟。A1／A3 的「可觀察但未鎖死」互動債多數已修；**C1 是 greenfield 缺口**（無模組、無測試、RBAC 種子領先實作），不要用「補測」語言描述。

## 技術債：已關閉 vs 仍開 vs C1 新帳

**先前 A1／A3 hotspot（2026-08-06 codekb）— HEAD 狀態**

| # | 舊斷言 | HEAD | 判定 |
|---|---|---|---|
| 1 | Sidebar 固定 `w-64`、不可收合 | `NavChromeContext` + icon rail `w-14` | **已關閉** |
| 2 | Sidebar 扁平 IA、缺 A／J grouping | 可收放「架構」「系統管理」 | **已關閉**（仍無 C 組 → 轉入 C1） |
| 3 | Edges 缺 exit／entry ports | `compute_edge_waypoints` + `exitX/Y` `entryX/Y` | **已關閉**（殘項：`parent` 仍 `"1"`） |
| 4 | Draw.io save／exit 未處理 | `data.event === 'save'|'exit'` | **已關閉** |
| 5 | Undo 因 autosave→load 損壞 | 註解稱已避免 echo load；scan 未重跑 UX | **仍開／未重驗** |
| 6 | 無 prompt refusal | `prompt_guard.py` PRESENT | **已關閉** |

**其他仍真的債**

- 前端缺元件單元測試；coverage 無門檻。
- Router HTTP 測試仍極薄（僅 auth list）。
- 第三方 embed 契約未版本化。
- RBAC **種子領先實作**：權限頁已顯示「C1 TCO 與流量預算」欄，無頁面、無 router 守衛、`test_rbac.py` 不覆蓋 C1。若 intent 改 C1 預設（例如讓架構師 edit 時數），屬 seed 變更，須 allow／deny 雙向測試。

**C1 新 hotspot（greenfield）**

1. 無可定價資源擷取（無 SKU 欄位；最多 label／style 關鍵字）。
2. Cost calculator／pricing client／價目 HTTP／硬編碼價格皆 ABSENT。
3. 無 `/cost`、無 Cost 頁、無成功卡成本 CTA、無 Sidebar C 組。
4. 無 inbox／budget／overspend primitive。
5. Calculator PBT 為 N/A（無模組）；落地時 ADR-0006 要求 Hypothesis，HTTP 層可仿 `test_user_list_endpoint.py`。
6. 勿把 WA `COST-*` 當成已測的成本能力——它們連 example-based 測試都沒有。

## 建議品質護欄（C1 導向；不發明 SKU）

- 新模組（extract／calculator／pricing port）從第一個 commit 就帶 Hypothesis properties（不變量：非負金額、覆寫優先於 list price——**僅在模組存在後**適用）。
- 任何 `role_permissions` C1 預設變更：`test_rbac.py` 形狀的 allow／deny 雙向測試。
- 新 `/api/cost*`：`TestClient` + OpenAPI dump／`gen:types`，否則 CI drift 紅燈。
- 若加 budget／cost 表：blocking 同步 `schema_rbac.sql`、`DEPLOY.md`、`database.py` `_ensure_*`。
- WA `COST-*` 若繼續存在，應有獨立單元測試，並在文件標明「啟發式 ≠ TCO」。
- 維持 contract＋既有 suite 全綠；不為本 intent 引入 production 路徑或 secret 檔。
