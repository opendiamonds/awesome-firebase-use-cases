# Unit Test Execution

## 中文版

### 現況

單元測試位於 `backend/tests/`，以 SQLite in-memory 為主（不需 PostgreSQL）；`psycopg2` 在 `helpers.py` 內 mock。涵蓋：

| 檔案 | 範圍 | 類型 |
|---|---|---|
| `test_rbac.py` | normalize／seed／user_can／arch 同步 | example |
| `test_auth.py` | bcrypt 雜湊、JWT 簽發／過期／竄改、`get_current_user` | example + PBT（verify round-trip） |
| `test_collab.py` | 分享 ACL、可見圖、welcome、chat parse／serialize／隔離 | example + PBT（serialize↔parse） |
| `test_design_agent.py` | `build_system_prompt`（含 current_xml）、`format_user_prompt` | example + PBT |
| `test_diagram_builder.py` | `is_inside`、`build_mxgraph_xml`（mock n8n） | example + PBT |

相依：`hypothesis`（已列入 `backend/requirements.txt`）。

### 執行

```bash
cd backend
pip install -r requirements.txt   # 含 hypothesis、bcrypt
python3 -m unittest discover -s tests -v
```

### 預期結果（2026-07-17 實測）

- `Ran 42 tests ... OK`（0 failures）  
- SQLAlchemy drop 順序 SAWarning、auth `utcnow` DeprecationWarning 可忽略

### 測試失敗時

1. 讀 unittest 輸出定位失敗案例  
2. 對照對應 `services/*.py` 修正  
3. 重跑至全綠

### 仍待擴充

| 範圍 | 狀態 |
|---|---|
| FastAPI TestClient（login／share HTTP） | ❌ 屬整合測試，見 `integration-test-instructions.md` |
| WebSocket JWT／broadcast | ❌ 待 WS JWT 實作後補 |
| frontend 單元測試 | ❌ 無 test runner（僅 eslint／tsc） |

---

## English Version

### Current state

Unit tests in `backend/tests/` cover RBAC, auth/JWT, collab ACL + chat helpers, design-agent prompts, and diagram_builder geometry/XML (with Hypothesis PBT on round-trips / invariants). SQLite in-memory; `psycopg2` mocked in `helpers.py`.

### Run

```bash
cd backend && pip install -r requirements.txt && python3 -m unittest discover -s tests -v
```

Expected (verified 2026-07-17): `Ran 42 tests ... OK`.

### Remaining gaps

HTTP TestClient integration tests, WebSocket JWT/broadcast, and frontend unit tests — see Chinese table.
