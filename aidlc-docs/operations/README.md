# Operations

> AIDLC 🟡 Operations phase artifacts for Cloud-360.
> Cloud-360 Operations 階段產出根目錄。

## 中文版

### 目的

`aidlc-docs/operations/` 存放 AIDLC Operations 階段的文件產出：部署說明、可觀測性、incident playbooks。  
可執行的部署程式與 compose 設定仍放在 repo 根目錄的 `deploy/`、`.github/workflows/deploy.yml`；本目錄負責**可稽核的 Operations artifacts**，並以連結指向實作位置。

### 目錄結構

| 路徑 | 說明 | 狀態 |
|---|---|---|
| `deployment/` | 部署流程摘要、與 staging 管線對照 | 🔄 有 baseline（見下方現有來源） |
| `observability/` | 監控、日誌、告警設計與 runbook 索引 | ⏳ 待補 |
| `incident-playbooks/` | 事故應變手冊 | ⏳ 待補 |

### 現有來源（尚未全部搬進本目錄）

| 來源 | 說明 |
|---|---|
| [`deploy/`](../../deploy/) | self-hosted compose、cloudflared、環境變數範本 |
| [`DEPLOY.md`](../../DEPLOY.md) | 人工／環境變數部署說明 |
| [`.github/workflows/deploy.yml`](../../.github/workflows/deploy.yml) | push `ut` → self-hosted runner 自動部署 |
| [`ADR-0007`](../inception/decisions/0007-self-hosted-deployment-pipeline.md) | self-hosted + Cloudflare Tunnel 決策 |

### 維護準則

- 本目錄下所有 `.md` 必須含 `## 中文版` 與 `## English Version`（ADR-0005）。
- 變更部署邊界、對外暴露或 secret 處理方式時，須更新或新增 ADR，並寫入 `aidlc-docs/audit.md`。
- 禁止在本目錄放入 production credentials、private key 或環境專用密文（repo contract）。

---

## English Version

### Purpose

`aidlc-docs/operations/` holds AIDLC Operations-phase artifacts: deployment docs, observability, and incident playbooks.  
Executable deploy assets stay under repo-root `deploy/` and `.github/workflows/deploy.yml`; this directory is the **auditable Operations artifact tree**, with links to implementation locations.

### Layout

| Path | Purpose | Status |
|---|---|---|
| `deployment/` | Deployment summaries and staging pipeline index | 🔄 baseline present (see sources below) |
| `observability/` | Monitoring, logging, alerting design and runbook index | ⏳ pending |
| `incident-playbooks/` | Incident response playbooks | ⏳ pending |

### Existing sources (not all migrated here yet)

| Source | Purpose |
|---|---|
| [`deploy/`](../../deploy/) | Self-hosted compose, cloudflared, env examples |
| [`DEPLOY.md`](../../DEPLOY.md) | Manual / env-var deployment guide |
| [`.github/workflows/deploy.yml`](../../.github/workflows/deploy.yml) | Push to `ut` → self-hosted runner deploy |
| [`ADR-0007`](../inception/decisions/0007-self-hosted-deployment-pipeline.md) | Self-hosted + Cloudflare Tunnel decision |

### Maintenance

- Every `.md` under this tree must include `## 中文版` and `## English Version` (ADR-0005).
- Changes to deployment boundaries, public exposure, or secret handling require an ADR update and an `aidlc-docs/audit.md` entry.
- Do not place production credentials, private keys, or environment-specific secrets here (repo contract).
