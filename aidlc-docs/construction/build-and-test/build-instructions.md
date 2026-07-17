# Build Instructions

## 中文版

### 先決條件

| 項目 | 需求 |
|---|---|
| Python | 3.11+（backend） |
| Node.js | 20+ / npm（frontend） |
| Docker | Docker Desktop（PostgreSQL 16 + Adminer） |
| 環境變數 | `JWT_SECRET`、`DATABASE_URL`、`OPENROUTER_API_KEY`（AI 功能）；參見 `DEPLOY.md` |

### 建置步驟

#### 1. 安裝相依

```bash
cd backend && pip install -r requirements.txt
cd frontend && npm install
```

#### 2. 啟動資料庫

```bash
docker compose up -d db adminer
# db: localhost:5432 / adminer: localhost:8080
```

#### 3. 啟動服務（開發）

```bash
# backend（首啟自動建表 + seed RBAC 矩陣與 admin）
cd backend && uvicorn main:app --reload --port 8000
# frontend
cd frontend && npm run dev   # http://localhost:5173
```

#### 4. Production build（frontend）

```bash
cd frontend && npm run build   # tsc -b + vite build → dist/
```

#### 5. 驗證建置成功

- backend：`GET http://localhost:8000/docs` 開得起來、啟動 log 無 seed 錯誤  
- frontend：`npm run build` 無 tsc 錯誤，`dist/` 產出  
- repo contract：`python scripts/validate_repo_contract.py` 全綠

### 疑難排解

| 症狀 | 原因／解法 |
|---|---|
| `docker compose` 連不上 daemon | Docker Desktop 未啟動 → `open -a Docker.app` |
| backend 啟動連不到 DB | `DATABASE_URL` 未設或 db 容器未起 |
| AI 生成 500 | `OPENROUTER_API_KEY` 未設 |

---

## English Version

### Prerequisites

Python 3.11+, Node 20+/npm, Docker Desktop; env vars `JWT_SECRET`, `DATABASE_URL`, `OPENROUTER_API_KEY` (see `DEPLOY.md`).

### Steps

1. `pip install -r backend/requirements.txt`; `npm install` in `frontend/`
2. `docker compose up -d db adminer`
3. Dev: `uvicorn main:app --reload --port 8000` (auto-creates tables and seeds RBAC + admin on empty DB); `npm run dev`
4. Prod frontend build: `npm run build` (tsc + vite → `dist/`)
5. Verify: `/docs` reachable, clean build output, `python scripts/validate_repo_contract.py` passes

### Troubleshooting

Docker daemon not running → start Docker Desktop; DB connection errors → check `DATABASE_URL`/container; AI 500 → missing `OPENROUTER_API_KEY`.
