# ADR 0007: Self-Hosted Deployment Pipeline via GitHub Actions and Cloudflare Tunnel

> 本文件必須同時包含中文版與英文版。
> This document must include both Chinese and English versions.

## 中文版

- Status: Accepted
- Date: 2026-07-12
- Supersedes: 無
- Amends: ADR-0001（repo scope）、ADR-0002（agent routing layer）的 out-of-scope 條款

### Context

ADR-0001 與 ADR-0002 把 deployment 相關能力明確列在 out of scope：production credentials、environment-specific secrets、direct production IaC、destructive cloud operations。當時 repo 處於 Spec-Driven Development baseline 階段，沒有可部署的程式碼，這個邊界是合理的。

現況已經改變：

1. `backend/`（FastAPI）與 `frontend/`（React + Vite）都已有可運行的實作，涵蓋 A1（自然語言轉架構圖）、A2（協同畫布）、A4（對話持久化）與 Pillar J（身分認證與 RBAC）。
2. `DEPLOY.md` 已存在，但描述的是**人工**部署流程：手動編輯 `.env`、手動 `psql -f schema_rbac.sql`、手動啟動服務。這個流程無法重現、無法稽核、無法回滾。
3. 團隊需要一個可驗證的執行環境，讓 user story 的驗收不再只靠 code review。

同時，出於 ADR-0001 的原始顧慮，本專案**仍然不打算**觸碰任何雲端供應商的 production 環境。需要的是一個受控的、自有的 staging 環境。

### Decision

1. **擴張範圍**：允許「部署到自有（self-hosted）環境」的自動化。雲端供應商的 production 部署、production credentials、destructive cloud operations 仍維持 out of scope，未經新 ADR 不得進行。

2. **部署目標**：`192.168.10.10`（區網內的自有主機，Docker 29.4.0）。此為 staging 性質環境（`APP_ENV=staging`），非 production。

3. **執行機制**：GitHub-hosted runner 無法連線至區網位址，因此在 `192.168.10.10` 上註冊 **self-hosted runner**（name `cloud360-10-10`，labels `self-hosted,linux,x64,cloud360`），由 `.github/workflows/deploy.yml` 指定在該 runner 上執行。工作方向由「job 連進機器」反轉為「job 跑在機器上」。

4. **觸發條件**：push 至 `ut` 分支，或手動 `workflow_dispatch`。`main` 不觸發部署。

5. **對外暴露**：透過 Cloudflare Tunnel（tunnel `cloud-360`，UUID `b460a579-9e0d-42f1-a31d-c84d35bef065`）將 `cloud360.danniel.cc` 導向 compose 內網的 nginx。

6. **網路邊界（security baseline hard constraint）**：
   - 對外只有 frontend nginx（`frontend:80`）進入 tunnel ingress。
   - backend 與 postgres **不開任何 host port**，僅存在於 compose 內部網路。
   - nginx 以 reverse proxy 將 `/api/`（含 `/api/collab/ws/{workspace_id}` WebSocket）轉發至 `backend:8000`。
   - 對內保留 `FRONTEND_HOST_PORT=8090` 供區網除錯，非公開路徑。

7. **憑證處理（security baseline hard constraint）**：
   - 所有 secret 存於 GitHub Actions secrets（`POSTGRES_PASSWORD`、`JWT_SECRET`、`OPENROUTER_API_KEY`、`N8N_WEBHOOK_URL`）。
   - `deploy.yml` 在 runner 上以 `umask 077` 產生 `deploy/.env`，並於 job 結束（`if: always()`）刪除。
   - Cloudflare tunnel 的 credentials JSON 留在主機 `~/.cloudflared/`，以 read-only 掛載進容器，**不進 repo**。
   - repo 內僅有 `deploy/.env.example`（佔位符）。`scripts/validate_repo_contract.py` 的 forbidden-content 規則仍然全面生效。

8. **ADR-0007 不放寬 repository contract**：`prod`、`production`、`secrets` 路徑仍然禁止；私鑰與雲端 credential 字串仍然禁止 commit。

### Consequences

**正面**：

- 部署從「一份人工 checklist」變成「一個可重現、可稽核、可回滾的 workflow run」。
- `ut` 分支有了實際的驗收環境，user story 的 acceptance criteria 可以被真正驗證。
- 網路邊界明確：攻擊面只有一個 nginx，backend 與 DB 不可從主機或網際網路直接觸及。
- Tunnel 取代 port forwarding 與反向 NAT，主機不需開放任何 inbound port。

**負面 / 風險**：

- self-hosted runner 對 repo 具有寫入 workspace 的能力，且在你的主機上執行 workflow 定義的任意指令。**任何能改動 `deploy.yml` 的人，等同於能在 `192.168.10.10` 上執行指令。** 這是 self-hosted runner 的本質風險，緩解方式是限制該 repo 的 write 權限，並且**永不**將此 runner 開放給 fork 的 PR。
- `192.168.10.10` 已有其他服務（n8n、investhub、dev-platform、ai-sdlc-staging）與另一個 runner（`opendiamonds/dev-platform`）。資源競爭與 port 衝突需要人為留意；本 stack 只佔用 host port 8090。
- Cloudflare tunnel 的 DNS 紀錄寫在 `danniel.cc` zone，屬於個人網域資產，非組織資產。

**後續工作**：

- 本 repo 目前**零測試**。`ci.yml` 的 backend job 只做 import check。在有 pytest 之前，deploy 的品質保證是不完整的。
- `DEPLOY.md` 的人工流程與本 ADR 的自動流程並存，需標註何者為正式路徑。

---

## English Version

- Status: Accepted
- Date: 2026-07-12
- Supersedes: none
- Amends: the out-of-scope clauses of ADR-0001 (repo scope) and ADR-0002 (agent routing layer)

### Context

ADR-0001 and ADR-0002 explicitly placed deployment capabilities out of scope: production credentials, environment-specific secrets, direct production IaC, and destructive cloud operations. At the time the repository sat at the Spec-Driven Development baseline with no deployable code, and that boundary was correct.

The situation has changed:

1. Both `backend/` (FastAPI) and `frontend/` (React + Vite) now carry working implementations covering A1 (natural language to architecture diagram), A2 (collaborative canvas), A4 (chat persistence), and Pillar J (authentication and RBAC).
2. `DEPLOY.md` exists, but it describes a **manual** procedure: hand-edit `.env`, hand-run `psql -f schema_rbac.sql`, hand-start the services. That procedure is not reproducible, not auditable, and not rollback-able.
3. The team needs a running environment where user stories can be accepted against observed behaviour rather than against a code review.

At the same time, and for the reasons ADR-0001 originally gave, this project still has **no intention** of touching a cloud provider's production environment. What is needed is a controlled, self-owned environment.

### Decision

1. **Scope extension**: automation that deploys to a **self-hosted** environment is now in scope. Cloud-provider production deployment, production credentials, and destructive cloud operations remain out of scope and require a new ADR.

2. **Target**: `192.168.10.10`, a self-owned host on the private network running Docker 29.4.0. This is a staging-grade environment (`APP_ENV=staging`), not production.

3. **Execution mechanism**: GitHub-hosted runners cannot reach a private LAN address, so a **self-hosted runner** is registered on `192.168.10.10` (name `cloud360-10-10`, labels `self-hosted,linux,x64,cloud360`), and `.github/workflows/deploy.yml` targets it. The direction of travel is inverted: the job runs on the machine rather than the machine being reachable from the job.

4. **Trigger**: push to the `ut` branch, or manual `workflow_dispatch`. `main` does not deploy.

5. **Public exposure**: a Cloudflare Tunnel (tunnel `cloud-360`, UUID `b460a579-9e0d-42f1-a31d-c84d35bef065`) routes `cloud360.danniel.cc` to the nginx container on the compose-internal network.

6. **Network boundary (security baseline hard constraint)**:
   - Only the frontend nginx (`frontend:80`) is reachable through tunnel ingress.
   - The backend and postgres publish **no host ports**; they exist only on the compose-internal network.
   - nginx reverse-proxies `/api/` — including the `/api/collab/ws/{workspace_id}` WebSocket — to `backend:8000`.
   - `FRONTEND_HOST_PORT=8090` is retained for LAN debugging only; it is not the public path.

7. **Credential handling (security baseline hard constraint)**:
   - All secrets live in GitHub Actions secrets (`POSTGRES_PASSWORD`, `JWT_SECRET`, `OPENROUTER_API_KEY`, `N8N_WEBHOOK_URL`).
   - `deploy.yml` writes `deploy/.env` on the runner under `umask 077` and deletes it when the job ends (`if: always()`).
   - The Cloudflare tunnel credentials JSON stays on the host in `~/.cloudflared/` and is mounted read-only into the container. It is **never** committed.
   - The repository carries only `deploy/.env.example`, holding placeholders. The forbidden-content rules in `scripts/validate_repo_contract.py` remain in full force.

8. **ADR-0007 does not relax the repository contract**: paths containing `prod`, `production`, or `secrets` remain forbidden, and private keys and cloud credential strings remain uncommittable.

### Consequences

**Positive**:

- Deployment moves from a manual checklist to a reproducible, auditable, rollback-able workflow run.
- The `ut` branch gains a real acceptance environment, so user-story acceptance criteria can actually be verified.
- The network boundary is explicit: the attack surface is a single nginx, and neither the backend nor the database is reachable from the host or the internet.
- The tunnel replaces port forwarding and inbound NAT; the host opens no inbound ports.

**Negative / risks**:

- A self-hosted runner executes whatever the workflow definition says, on your machine. **Anyone who can modify `deploy.yml` can run commands on `192.168.10.10`.** That is inherent to self-hosted runners. The mitigation is to keep write access to this repository tight and to **never** expose this runner to pull requests from forks.
- `192.168.10.10` already hosts other services (n8n, investhub, dev-platform, ai-sdlc-staging) and a second runner belonging to `opendiamonds/dev-platform`. Resource contention and port collisions need human attention; this stack claims only host port 8090.
- The tunnel's DNS record lives in the `danniel.cc` zone, a personal domain asset rather than an organisational one.

**Follow-up work**:

- This repository has **no tests**. The backend job in `ci.yml` performs an import check and nothing more. Until a test suite exists, the quality gate in front of deployment is incomplete.
- The manual procedure in `DEPLOY.md` now coexists with this automated one; the documents must state which is the canonical path.
