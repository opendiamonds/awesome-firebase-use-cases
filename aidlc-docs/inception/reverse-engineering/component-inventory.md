# Component Inventory

> Package-level inventory of the Cloud-360 workspace.  
> Cloud-360 workspace 套件／元件盤點。

## 中文版

### Application Packages

| 套件 | 目的 |
|---|---|
| `backend/` | FastAPI 應用（auth、architecture、collab、RBAC、Agent） |
| `frontend/` | React SPA（Login、Workspace、Admin、畫布、聊天） |

### Infrastructure Packages

| 套件 | 類型 | 目的 |
|---|---|---|
| `docker-compose.yml` | Compose（本機） | PostgreSQL + Adminer |
| `deploy/` | Compose + cloudflared | Staging 部署與隧道 |
| `backend/Dockerfile`、`frontend/Dockerfile` | Container | 映像建置 |
| `.github/workflows/deploy.yml` | CI/CD | self-hosted deploy |

### Shared / Spec Packages

| 套件 | 類型 | 目的 |
|---|---|---|
| `aidlc-docs/` | Docs／Artifacts | AIDLC 產出 |
| `.aidlc/aidlc-rules/` | Methodology | AIDLC 規則樹 |
| `.aidlc-overrides/` | Project rules | 分支命名、decisions-log |
| `schema.sql`、`schema_rbac.sql` | Schema | DDL + RBAC seed |
| `scripts/` | Tooling | repo contract |
| `tools/`、`workflows/` | Optional | MCP／Skill／n8n 範本 |

### Test Packages

| 套件 | 類型 | 目的 |
|---|---|---|
| `backend/tests/` | Unit | 目前主要 `test_rbac.py` |
| CI frontend jobs | Lint／typecheck／build | 無獨立前端 test suite |

### Total Count

| 類別 | 數量（邏輯套件） |
|---|---|
| Application | 2（backend、frontend） |
| Infrastructure | 4（compose 本機、deploy、Dockerfiles、deploy workflow） |
| Shared／Spec | 6+ |
| Test | 1（backend/tests；覆蓋不足） |
| **Total（主要）** | **~13** |

---

## English Version

Application: `backend/`, `frontend/`. Infrastructure: local compose, `deploy/`, Dockerfiles, deploy workflow. Shared: `aidlc-docs/`, `.aidlc/`, schemas, `scripts/`. Tests: `backend/tests/` (thin). See Chinese tables for the full inventory.
