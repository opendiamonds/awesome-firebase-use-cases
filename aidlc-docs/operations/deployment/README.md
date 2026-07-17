# Deployment

> Operations — deployment artifacts index.
> Operations — 部署產出索引。

## 中文版

### 範圍

本目錄記錄 Cloud-360 **self-hosted staging** 部署相關的 AIDLC 產出索引。實作檔案位於：

- `deploy/docker-compose.deploy.yml`
- `deploy/cloudflared/config.yml`
- `deploy/.env.example`
- `.github/workflows/deploy.yml`

決策依據：[`ADR-0007`](../../inception/decisions/0007-self-hosted-deployment-pipeline.md)。  
人工環境變數與 DB seed 說明：[`DEPLOY.md`](../../../DEPLOY.md)。

### 待補 artifacts

- 部署驗收清單（smoke test／rollback 步驟）寫成獨立 md
- 與 `aidlc-state.md` Operations 區塊同步的 stage-completion summary

---

## English Version

### Scope

This directory indexes AIDLC artifacts for Cloud-360 **self-hosted staging** deployment. Implementation lives in:

- `deploy/docker-compose.deploy.yml`
- `deploy/cloudflared/config.yml`
- `deploy/.env.example`
- `.github/workflows/deploy.yml`

Decision record: [`ADR-0007`](../../inception/decisions/0007-self-hosted-deployment-pipeline.md).  
Manual env / DB seed guide: [`DEPLOY.md`](../../../DEPLOY.md).

### Pending artifacts

- Standalone deployment acceptance checklist (smoke tests / rollback steps)
- Stage-completion summary aligned with the Operations section of `aidlc-state.md`
