# Operations Runbooks — Cloud-360

> 本文件必須同時包含中文版與英文版。
> This document must include both Chinese and English versions.

## 中文版

- Status: Living document（隨故障累積更新）
- Scope: 自有 staging 環境 `192.168.10.10` / `cloud360.danniel.cc`（見 ADR-0007）
- Related: [[0008-continuous-construction-operations]]、`.aidlc-overrides/continuous-delivery.md`

補齊 ADR-0008 點名的 Operations 待辦：本文件涵蓋 **SLO**、**observability 現況**、**incident playbooks**。每一則 playbook 都對應本專案實際發生過或明確可能的故障。

### 1. Service Level Objectives（staging 等級）

| 指標 | 目標 | 量測方式 |
|---|---|---|
| `cloud360.danniel.cc` 可用性 | 週內 ≥ 99%（staging，非 production SLA） | 外部探測 `GET /`（見第 2 節） |
| Deploy 成功率 | ≥ 90% 的 merge-to-ut 部署綠燈 | `Deploy` workflow 成功率 |
| Deploy 失敗復原 | 失敗後 self-heal（rollback + revert PR + Deploy Doctor）自動觸發 | 見 playbook C |
| UI 回歸 | PR 上 6/6 通過才可 merge | UI Regression workflow |

> 這是 staging 目標，非對外承諾。production SLA 不在範圍（ADR-0007）。

### 2. Observability 現況

**現有（不需額外工具）**：
- **容器健康檢查**：`db` / `backend` / `frontend` 皆有 compose healthcheck；`docker compose ps` 一眼看 healthy。
- **部署健康檢查**：`deploy.yml` 內建兩段（內網 8090 + 公開網址），失敗即擋 + 觸發 self-heal。
- **CI 關卡**：每 PR 的 contract / lint / build / docker / UI 回歸。
- **每日彙整**：Daily Digest agentic workflow 彙整 CI/deploy/agent 狀態（進 main 後啟用）。

**尚缺（待補）**：主動式外部探測 + 告警（服務掛掉時主動通知，而非等人發現）。工具選型見 Telegram 討論；決定後在此補上 §2 的 monitor 章節與告警去向。

### 3. Incident Playbooks

每則格式：**症狀 → 判斷 → 處置 → 驗證**。所有指令在 `192.168.10.10`（`~/deploy/cloud-360` 為 compose 目錄）。

#### A. 網站回 Cloudflare Error 1033

- **症狀**：瀏覽器顯示 `Error 1033 Cloudflare Tunnel error`。
- **判斷**：tunnel 沒連上。cloud360 的 cloudflared 是 **compose 容器**（`cloud360-cloudflared-1`），非 systemd。
- **處置**：
  ```bash
  docker ps -a --filter name=cloud360-cloudflared   # 看是否 Restarting
  docker logs cloud360-cloudflared-1 --tail 30       # 找 "permission denied" 等
  # 憑證權限問題（歷史故障）：compose 已設 user: "1000:1000"，確認憑證檔存在且可讀
  ls -l ~/.cloudflared/b460a579-9e0d-42f1-a31d-c84d35bef065.json
  docker compose -f deploy/docker-compose.deploy.yml --env-file deploy/.env up -d cloudflared
  ```
- **驗證**：`curl -fsS -o /dev/null -w "%{http_code}" https://cloud360.danniel.cc/` → 200。

#### B. 網站回 502（tunnel 通但 origin 連不到）

- **症狀**：HTTP 502。
- **判斷**：tunnel 連上了，但打不到後面的服務。歷史故障：port 對映錯（服務內部聽的 port 與對映不符）。
- **處置**：
  ```bash
  docker compose -f deploy/docker-compose.deploy.yml ps        # frontend 是否 healthy
  curl -sk -o /dev/null -w "%{http_code}" http://127.0.0.1:8090/  # 本機直打 nginx
  docker compose -f deploy/docker-compose.deploy.yml logs frontend --tail 40
  ```
- **驗證**：本機 8090 回 200 後，公開網址即恢復。

#### C. Deploy 失敗

- **症狀**：`Deploy (ut → 192.168.10.10)` workflow 紅。
- **判斷 + 處置**：**多半不需手動** —— rollback job 會自動把服務滾回 last-good、開 revert PR、並叫 Deploy Doctor 開 issue 分析根因。先看那張 issue。
- **人工介入時機**：last-good 不存在（首次部署就失敗）→ 讀 Deploy Doctor issue，修 root cause 後重推。
- **驗證**：`https://cloud360.danniel.cc/` 回 200，且 `docker compose ps` 全 healthy。

#### D. 憑證外洩 / 預設密碼可登入

- **症狀**：可用已知/預設帳密登入（歷史故障：`admin/admin123`）。
- **處置**：立即改密碼（bcrypt，與 auth.py 同套）：
  ```bash
  NEW=$(openssl rand -base64 15 | tr -d '/+=' | head -c 20)
  H=$(docker exec cloud360-backend-1 python -c "import bcrypt;print(bcrypt.hashpw('$NEW'.encode(),bcrypt.gensalt()).decode())")
  docker exec cloud360-db-1 psql -U postgres -d cloud360 -c "UPDATE users SET password_hash='$H' WHERE username='admin';"
  ```
- **根治**：見 issue #425（schema 不應內建明文預設密碼）。
- **驗證**：舊密碼登入回 401、新密碼回 200。

#### E. 資料庫容器 unhealthy

- **症狀**：`cloud360-db-1` 非 healthy；backend 起不來。
- **處置**：
  ```bash
  docker compose -f deploy/docker-compose.deploy.yml logs db --tail 50
  docker compose -f deploy/docker-compose.deploy.yml restart db
  ```
- **注意**：`schema_rbac.sql` 只在**空 volume** 首次初始化跑；既有資料不會被重播。切勿刪 `cloud360_db` volume（會清空資料且 admin 回到預設密碼）。

#### F. Self-hosted runner 離線

- **症狀**：CI/deploy 卡在 queued；`cloud360-10-10` 顯示 offline。
- **處置**：
  ```bash
  sudo systemctl status actions.runner.opendiamonds-cloud-360.cloud360-10-10.service
  sudo systemctl restart actions.runner.opendiamonds-cloud-360.cloud360-10-10.service
  ```
- **注意**：10.10 上另有 `dev-platform` 的 runner，勿誤動。

#### G. 磁碟接近滿

- **症狀**：部署/build 失敗於 no space。10.10 跑多個服務。
- **處置**：`docker system df` 看用量 →  `docker image prune -f` / `docker builder prune -f`（勿 `-a --volumes`，會誤刪其他服務資料）。

### 4. 告警去向（待補）

主動告警（服務掛掉、部署失敗、憑證問題）目前靠人看。決定 observability 工具後，告警優先送 Telegram（Dan ↔ Claude Code 頻道），此節補上實際路由。

---

## English Version

- Status: Living document (updated as incidents accrue)
- Scope: self-hosted staging `192.168.10.10` / `cloud360.danniel.cc` (see ADR-0007)
- Related: [[0008-continuous-construction-operations]], `.aidlc-overrides/continuous-delivery.md`

This fills the Operations to-dos named in ADR-0008: **SLOs**, **observability status**, and **incident playbooks**. Every playbook maps to a failure this project has actually hit or clearly could.

### 1. Service Level Objectives (staging-grade)

| Metric | Target | Measured by |
|---|---|---|
| `cloud360.danniel.cc` availability | ≥ 99% weekly (staging, not a production SLA) | external probe of `GET /` (see §2) |
| Deploy success rate | ≥ 90% of merge-to-ut deploys green | `Deploy` workflow success rate |
| Deploy-failure recovery | self-heal (rollback + revert PR + Deploy Doctor) fires automatically | see playbook C |
| UI regression | 6/6 pass required before merge | UI Regression workflow |

> These are staging targets, not external commitments. Production SLAs are out of scope (ADR-0007).

### 2. Observability — current state

**In place (no extra tooling):**
- **Container healthchecks**: `db` / `backend` / `frontend` all have compose healthchecks; `docker compose ps` shows health at a glance.
- **Deploy healthchecks**: `deploy.yml` has two (LAN 8090 + public URL); failure blocks and triggers self-heal.
- **CI gates**: per-PR contract / lint / build / docker / UI regression.
- **Daily summary**: the Daily Digest agentic workflow rolls up CI/deploy/agent status (active once on main).

**Still missing (to build):** active external probing + alerting (be told when a service is down instead of finding out). Tool choice is under discussion on Telegram; once decided, add the monitor section and alert routing here.

### 3. Incident Playbooks

Each is **Symptom → Diagnosis → Action → Verify**. All commands on `192.168.10.10` (`~/deploy/cloud-360` is the compose dir).

#### A. Site returns Cloudflare Error 1033

- **Symptom**: browser shows `Error 1033 Cloudflare Tunnel error`.
- **Diagnosis**: the tunnel is not connected. cloud360's cloudflared is a **compose container** (`cloud360-cloudflared-1`), not systemd.
- **Action**:
  ```bash
  docker ps -a --filter name=cloud360-cloudflared   # is it Restarting?
  docker logs cloud360-cloudflared-1 --tail 30       # look for "permission denied" etc.
  # Known credential-permission failure: compose sets user: "1000:1000"; confirm creds exist and are readable
  ls -l ~/.cloudflared/b460a579-9e0d-42f1-a31d-c84d35bef065.json
  docker compose -f deploy/docker-compose.deploy.yml --env-file deploy/.env up -d cloudflared
  ```
- **Verify**: `curl -fsS -o /dev/null -w "%{http_code}" https://cloud360.danniel.cc/` → 200.

#### B. Site returns 502 (tunnel up, origin unreachable)

- **Symptom**: HTTP 502.
- **Diagnosis**: the tunnel connected but cannot reach the service behind it. Known failure: wrong port mapping (the port the service listens on inside vs what is mapped).
- **Action**:
  ```bash
  docker compose -f deploy/docker-compose.deploy.yml ps        # is frontend healthy?
  curl -sk -o /dev/null -w "%{http_code}" http://127.0.0.1:8090/  # hit nginx locally
  docker compose -f deploy/docker-compose.deploy.yml logs frontend --tail 40
  ```
- **Verify**: once local 8090 returns 200, the public URL recovers.

#### C. Deploy failed

- **Symptom**: the `Deploy (ut → 192.168.10.10)` workflow is red.
- **Diagnosis + action**: **usually no manual step** — the rollback job restores the service to last-good, opens a revert PR, and calls Deploy Doctor to open a root-cause issue. Read that issue first.
- **When to step in**: no last-good recorded (the very first deploy failed) → read the Deploy Doctor issue, fix the root cause, re-push.
- **Verify**: `https://cloud360.danniel.cc/` returns 200 and `docker compose ps` is all healthy.

#### D. Credential leak / default password logs in

- **Symptom**: a known/default credential logs in (past incident: `admin/admin123`).
- **Action**: rotate immediately (bcrypt, same as auth.py):
  ```bash
  NEW=$(openssl rand -base64 15 | tr -d '/+=' | head -c 20)
  H=$(docker exec cloud360-backend-1 python -c "import bcrypt;print(bcrypt.hashpw('$NEW'.encode(),bcrypt.gensalt()).decode())")
  docker exec cloud360-db-1 psql -U postgres -d cloud360 -c "UPDATE users SET password_hash='$H' WHERE username='admin';"
  ```
- **Root fix**: see issue #425 (the schema should not ship a plaintext default password).
- **Verify**: the old password returns 401, the new one 200.

#### E. Database container unhealthy

- **Symptom**: `cloud360-db-1` not healthy; backend won't start.
- **Action**:
  ```bash
  docker compose -f deploy/docker-compose.deploy.yml logs db --tail 50
  docker compose -f deploy/docker-compose.deploy.yml restart db
  ```
- **Caution**: `schema_rbac.sql` runs only on **first init of an empty volume**; existing data is not replayed. Never delete the `cloud360_db` volume (it wipes data and resets admin to the default password).

#### F. Self-hosted runner offline

- **Symptom**: CI/deploy stuck queued; `cloud360-10-10` shows offline.
- **Action**:
  ```bash
  sudo systemctl status actions.runner.opendiamonds-cloud-360.cloud360-10-10.service
  sudo systemctl restart actions.runner.opendiamonds-cloud-360.cloud360-10-10.service
  ```
- **Caution**: 10.10 also hosts the `dev-platform` runner — do not touch that one.

#### G. Disk nearly full

- **Symptom**: deploy/build fails with no space. 10.10 runs several services.
- **Action**: `docker system df` to see usage → `docker image prune -f` / `docker builder prune -f` (never `-a --volumes` — it would wipe other services' data).

### 4. Alert routing (to build)

Active alerting (service down, deploy failed, credential issues) currently relies on a human looking. Once the observability tool is chosen, alerts route to Telegram (the Dan ↔ Claude Code channel) first; this section will carry the actual routing.
