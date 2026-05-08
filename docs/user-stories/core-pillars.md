# Cloud-360 Core Pillars User Stories

> 本文件必須同時包含中文版與英文版。
> This document must include both Chinese and English versions.

## 中文版

## A. 架構設計 (Architecture Design)

### A1. 自然語言轉架構 (Natural Language to Architecture)

身為**雲端架構師**，我希望能夠以自然語言描述需求，以便 Cloud-360 能夠生成初步的雲端架構藍圖。

**驗收標準：**
- 提取工作負載、高可用性 (HA)、災難復原 (DR)、擴展性、區域、安全性與合規性需求。
- 產出 Mermaid、PlantUML 或 draw.io 格式的輸出。
- 解釋假設條件與權衡取捨 (trade-offs)。

### A2. 架構完善性評核 (Well-Architected Review)

身為 **SRE**，我希望 Cloud-360 能夠檢查架構是否符合雲端供應商的最佳實踐。

**驗收標準：**
- 涵蓋可靠性、安全性、成本優化、卓越營運與效能。
- 產出嚴重性等級、影響分析與修復建議。

### A3. AI + draw.io 協同編輯 (AI + draw.io Co-editing)

身為**雲端架構師**，我希望能夠透過 AI Chat 與 AI 共同編輯線上的 draw.io / diagrams.net 架構畫布。

**驗收標準：**
- 支援 `.drawio` / XML 原始格式。
- AI 可以增加/移除節點、更新連線並標註資料流。
- 每次 AI 修改都包含變更摘要與版本歷史。
- 圖表結構可被解析為共享的架構上下文 (shared architecture context)。

## B. 跨雲元件選型 (Cross-Cloud Component Selection)

### B1. 服務比較矩陣 (Service Comparison Matrix)

身為**技術決策者**，我希望能夠比較等效的 AWS/GCP/Azure 服務。

**驗收標準：**
- 包含 SLA、限制、相容性、成本風險、鎖定 (lock-in) 風險與營運複雜度。
- 支援運算、資料庫、儲存、網路、Kubernetes、訊息傳遞與 AI/ML 類別。

### B2. 基於工作負載的推薦 (Workload-Based Recommendation)

身為 **SRE**，我希望 Cloud-360 能夠根據工作負載特性推薦雲端服務。

**驗收標準：**
- 使用 QPS、併發數、資料量、延遲目標、區域與合規性約束作為參考。
- 提供推導邏輯、替代方案與已知限制。

## C. 成本估算與 FinOps (Cost Estimation & FinOps)

### C1. 每月總持有成本 (TCO) 估算 (Monthly TCO Estimation)

身為 **FinOps 分析師**，我希望為提議的架構估算每月成本。

**驗收標準：**
- 估算運算、資料庫、快取、儲存、網路、CDN、流量傳輸 (egress) 與可觀測性成本。
- 顯示價格假設與來源時間戳記。

### C2. Spot / 可插隊實例比較 (Spot / Preemptible Comparison)

身為 **SRE**，我希望比較按需 (On-demand) 與可中斷 (Interruptible) 的定價選項。

**驗收標準：**
- 涵蓋 AWS Spot、Azure Spot 與 GCP Spot / Preemptible。
- 包含節省預估與中斷風險評估。

### C3. 跨雲流量傳輸 (Egress) 分析 (Cross-Cloud Egress Analysis)

身為**架構師**，我希望了解多雲設計中的資料傳輸成本。

**驗收標準：**
- 區分區域內、區域間、網際網路傳輸與跨雲流量。
- 標記昂貴或高風險的流量路徑。

## D. Terraform / OpenTofu IaC Generation

### D1. Modular IaC Generation

As a platform engineer, I want Cloud-360 to generate modular Terraform / OpenTofu code.

Acceptance criteria:

- Generates `providers.tf`, `main.tf`, `variables.tf`, `outputs.tf` and `modules/`.
- Supports `aws`, `google` and `azurerm` providers.
- Does not generate plaintext secrets.

### D2. IaC Security Scan

As a security reviewer, I want generated IaC to be scanned before use.

Acceptance criteria:

- Supports tfsec, trivy or Checkov.
- Flags public storage, overly broad ingress, missing encryption and excessive IAM/RBAC.
- Produces remediation guidance.

## E. Operations Optimization Review

### E1. Right-sizing Recommendation

As an SRE, I want right-sizing recommendations based on observed utilization.

Acceptance criteria:

- Analyzes CPU, memory, IOPS, network and storage.
- Estimates cost impact after changes.
- Requires approval before changing production resources.

### E2. Architecture Modernization

As a Cloud Architect, I want modernization recommendations based on new cloud services.

Acceptance criteria:

- Identifies legacy, high-maintenance or high-cost services.
- Suggests managed, serverless, container or event-driven alternatives.
- Includes migration risk and expected benefits.

## F. AI Multi-Cloud Operations

### F1. AI Chat Cloud Query

As an SRE, I want to query AWS/GCP/Azure status through AI Chat.

Acceptance criteria:

- Supports account/project/subscription and region selection.
- Can query resource inventory, cost, metrics, logs and IAM/security findings.
- Includes data source and query time.
- Redacts secrets.

### F2. AI Chat Cloud Operation

As a platform engineer, I want to request cloud operations through AI Chat.

Acceptance criteria:

- Read-only actions can execute after policy classification.
- Write/delete/deploy/permission changes require human approval.
- Shows plan, impact, rollback and verification steps.
- Records audit log.

### F3. Agentic AI Operations

As an operations lead, I want background agents to proactively identify issues.

Acceptance criteria:

- Detects cost spikes, security risks, availability gaps and performance bottlenecks.
- Produces recommendations and remediation plans.
- Does not execute high-risk changes without explicit approval.

## G. Cloud Security Posture & Policy Advisory

### G1. Multi-Cloud Security Review

As a Security Reviewer, I want Cloud-360 to inspect security posture across AWS/GCP/Azure.

Acceptance criteria:

- Checks IAM/RBAC, network exposure, storage access, encryption, audit logging and policy guardrails.
- Produces severity, evidence, impact and remediation.

### G2. Least-Privilege Analysis

As a platform admin, I want Cloud-360 to detect over-permissive identities.

Acceptance criteria:

- Detects wildcard permissions, stale identities and unused permissions.
- Generates least-privilege recommendations.

### G3. Policy-as-Code Recommendation

As a platform engineer, I want security policies expressed as maintainable policy code.

Acceptance criteria:

- Supports Terraform patch suggestions, OPA/Rego, Sentinel, Azure Policy, GCP Org Policy and AWS Config rule recommendations.
- Requires approval before applying policy changes.

## H. Web-Based Desktop and Mobile Experience

### H1. Desktop Web Full Workspace

As a Cloud Architect, I want the desktop browser experience to provide the full Cloud-360 workspace.

Acceptance criteria:

- Supports AI Chat, draw.io editor, IaC editor, FinOps dashboard, Security dashboard, Ops dashboard and agent trace.

### H2. Mobile Web Ops Companion

As an SRE, I want a mobile browser experience for quick operations and approvals.

Acceptance criteria:

- Delivered through responsive web / PWA.
- Supports AI Chat, alerts, approvals, health digest, findings and readonly architecture diagrams.
- Does not require native iOS or Android app.

### H3. Mobile Web Approval

As a platform owner, I want to approve or reject operations from mobile web safely.

Acceptance criteria:

- Shows plan, affected resources, risk, impact and rollback.
- High-risk approval requires MFA, passkey or WebAuthn.
- Records audit log and supports timeout/escalation.

## I. MCP & Skill Management

### I1. MCP Server Registry

As a platform engineer, I want to register and manage MCP servers so that Cloud-360 can safely expose external and internal tools to agents.

Acceptance criteria:

- Supports server name, endpoint/transport, owner, environment, auth scope, enabled status and version.
- Supports health checks for availability, schema compatibility, latency and recent errors.
- Disallows secrets in stored configuration or logs.

### I2. Skill Catalog

As an AI platform operator, I want to manage reusable AI Skills so that agents can reuse approved workflows.

Acceptance criteria:

- Tracks skill name, domain, owner, version, description, required tools, risk level and change log.
- Supports enable, disable, deprecate and rollback states.
- Shows dependencies between skills, MCP tools, SDK/CLI wrappers and cloud providers.

### I3. Tool Permission and Risk Model

As a security reviewer, I want every MCP tool and Skill to have a permission/risk classification.

Acceptance criteria:

- Classifies tools as read-only, write, deploy, delete, permission-change or production-impacting.
- High-risk tools require approval before enablement or execution.
- Agent Routing Layer must use this classification before selecting tools.

### I4. MCP / Skill Approval Workflow

As a platform owner, I want risky MCP/Skill changes to require approval.

Acceptance criteria:

- Adding a new high-risk tool requires review.
- Expanding auth scope requires approval.
- Disabling critical tools requires impact summary and rollback plan.
- All changes are written to audit log.

### I5. Agent Tool Selection Observability

As an SRE, I want to see why an agent selected a specific MCP tool or Skill.

Acceptance criteria:

- Shows selected tool/skill, reason, input summary, permission level, approval status and execution result.
- Redacts secrets and sensitive payloads.
- Links tool execution back to user request, agent trace and audit log.

## English Version

This document defines Cloud-360 user stories across the core platform pillars:

- Architecture Design.
- Cross-Cloud Component Selection.
- Cost Estimation and FinOps.
- Terraform/OpenTofu IaC Generation.
- Operations Optimization Review.
- AI Multi-Cloud Operations.
- Cloud Security Posture and Policy Advisory.
- Web-Based Desktop and Mobile Experience.
- MCP and Skill Management.

Each story includes acceptance criteria so implementation work can be validated through Spec-Driven Development. The MCP and Skill Management stories require registries, catalogs, permission/risk classification, approval workflow, and observability for agent tool selection.
