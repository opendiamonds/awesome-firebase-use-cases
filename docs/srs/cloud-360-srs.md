# Cloud-360 System Requirement Specification

> 本文件必須同時包含中文版與英文版。
> This document must include both Chinese and English versions.

## 中文版

- Status: Draft v0.1
- Date: 2026-05-02
- Owner: Danniel Chung / Anita

## 1. Platform Vision

Cloud-360 是專為雲端架構師、SRE、FinOps 與 Security 團隊設計的 AI-native 多雲架構與維運管理平台。

平台深度整合 LLM、多智能體協作框架、MCP servers、Cloud SDKs、Cloud CLIs、Terraform / OpenTofu 與可重用 Skills，並提供 MCP 與 Skill 管理功能，提供涵蓋 AWS、GCP、Azure 的端到端生命週期管理能力。

## 2. Target Users

- Cloud Architect
- SRE / Platform Engineer
- FinOps Analyst
- Security Reviewer
- Engineering Manager / Technical Decision Maker

## 3. Core Pillars

### A. AI-Driven Architecture Design

Cloud-360 將自然語言需求轉成單雲或多雲架構藍圖。

Required capabilities:

- 解析 workload、HA、DR、RTO/RPO、scalability、security、compliance、latency 與 region 需求。
- 產生 Mermaid / PlantUML / draw.io 架構圖。
- 檢查 AWS / GCP / Azure Well-Architected Framework。
- 支援 Active-Active / Active-Passive cross-cloud disaster recovery design。

### B. Cross-Cloud Component Selection

Cloud-360 根據 workload profile 提供 AWS / GCP / Azure 託管服務選型建議。

Required capabilities:

- 比較同質服務，例如 AWS RDS、GCP Cloud SQL、Azure SQL Database。
- 輸出效能、SLA、限制、相容性、lock-in、維運複雜度與成本風險。
- 產生 decision matrix 與替代方案。

### C. Cost Estimation & FinOps

Cloud-360 針對架構方案與雲端元件估算多雲 TCO。

Required capabilities:

- 根據流量、運算資源、資料量、儲存、備援、observability 與 data transfer 估算月費。
- 比較 AWS Spot、Azure Spot Virtual Machines、GCP Spot / Preemptible VMs。
- 計算跨雲與跨區 Data Egress。
- 主動偵測 cost spike、idle resources、over-provisioned resources 與 right-sizing opportunity。

### D. Infrastructure as Code - Terraform / OpenTofu

Cloud-360 將確認後的架構藍圖轉為 Terraform / OpenTofu 模組草稿。

Required capabilities:

- 支援 `aws`、`google`、`azurerm` providers。
- 產出 `providers.tf`、`main.tf`、`variables.tf`、`outputs.tf` 與 `modules/` 結構。
- 不產生 production secrets。
- 所有 sensitive values 必須使用 variables、secret manager reference 或 workload identity。
- 整合 tfsec、trivy、Checkov 進行靜態掃描。

### E. Operations Optimization Review

Cloud-360 針對已部署或設計中的架構進行持續健康檢查與效能檢視。

Required capabilities:

- 分析 CPU、memory、IOPS、network、storage、latency、error rate、SLO/SLA。
- 提供 right-sizing、autoscaling、backup、multi-AZ、multi-region 與 observability 建議。
- 根據雲端新服務提出架構現代化建議。

### F. AI Multi-Cloud Operations

Cloud-360 透過 AI Chat 與 Agentic AI 管理多雲環境。

Required capabilities:

- AI Chat 主動式操作：使用者以自然語言查詢、分析與要求維運操作。
- Agentic AI 被動監控與主動分析：背景 agent 監控成本、安全、效能、可用性與政策風險。
- 串接 AWS / GCP / Azure MCP、SDK、CLI、API、Skills 與 Terraform providers。
- 所有高風險操作必須有人類審批。
- 所有操作必須記錄 audit log。

### G. Cloud Security Posture & Policy Advisory

Cloud-360 檢視多雲安全策略並提出可執行的治理建議。

Required capabilities:

- 檢查 IAM / RBAC、Security Group / Firewall / NSG、bucket / blob access、KMS / encryption、audit logging、cloud-native policy guardrails。
- 整合 AWS IAM Access Analyzer、AWS Config、Security Hub、GuardDuty、GCP Security Command Center、GCP Organization Policy、Azure Policy、Defender for Cloud、Azure Advisor 等資料來源。
- 針對 findings 產生 severity、evidence、impact、recommended policy、remediation plan、IaC patch suggestion、verification command、rollback strategy。
- 支援 Policy-as-Code 建議，例如 OPA/Rego、Sentinel、Azure Policy、GCP Org Policy、AWS Config rule。

### H. MCP & Skill Management

Cloud-360 需提供 MCP servers、MCP tools、AI Skills 與 cloud provider connectors 的集中管理功能。

Required capabilities:

- MCP Server Registry：登錄、設定、啟用/停用與檢查 MCP servers。
- Tool Catalog：列出 MCP tools、cloud SDK/CLI wrappers、Terraform tools 與 internal tools。
- Skill Catalog：管理 reusable AI Skills，例如 architecture design、FinOps、security posture review、Terraform generation、incident response。
- Permission & Risk Model：針對每個 MCP tool / Skill 標示 read-only、write、deploy、delete、permission-change、production-impacting 風險等級。
- Versioning：記錄版本、schema、owner、相依性、變更紀錄與 rollback target。
- Health Check：檢查 MCP server availability、tool schema、auth scope、latency、error rate 與最近執行狀態。
- Approval Workflow：新增、升級、停用高風險 MCP / Skill 或擴權時需 human approval。
- Agent Routing Integration：Routing Agent 需可依任務、上下文、風險與權限選擇合適 MCP / Skill。

## 4. User Experience Requirements

### Desktop Web

Desktop Web 是 Cloud-360 的完整工作台，必須支援：

- AI Chat
- draw.io / diagrams.net architecture canvas
- Terraform / policy code editor
- FinOps dashboard
- Security posture dashboard
- Operations dashboard
- Agent trace
- Audit log
- Approval gate management

### Mobile Web / Responsive Web / PWA

手機版本也以 Web 方式呈現。第一階段不做 native iOS / Android app。

Mobile Web 聚焦：

- AI Chat
- Alerts
- Approval / reject workflow
- Cloud health digest
- Cost / security / operations findings
- Readonly architecture diagram view
- Incident quick triage

Mobile Web 不作為大型 draw.io 圖面拖拉編輯或 Terraform 深度開發的主要介面。

## 5. Architecture Visualization Requirements

Cloud-360 的架構圖能力以 draw.io / diagrams.net 相容格式為核心。

Required capabilities:

- 支援 `.drawio` / XML source format。
- 支援 SVG / PNG / PDF export。
- 支援 Mermaid / PlantUML derived output。
- AI Chat 可新增元件、刪除元件、調整連線、標註資料流、補 HA/DR/security/observability 元件。
- 每次 AI 修改需產生 change summary 與 version history。
- 圖面需可解析成 internal architecture graph，供 FinOps、IaC、Ops、Security agents 使用。

## 6. Cloud Integration Requirements

Cloud-360 必須透過受控 integration layer 串接雲平台。

Integration types:

- MCP servers
- Cloud SDKs
- Cloud CLIs
- Cloud APIs
- Terraform / OpenTofu providers
- AI Skills
- MCP / Skill Registry and Management APIs

Safety requirements:

- Read-only operations may execute after policy classification。
- Write / delete / deploy / permission change / production-impacting operations require human approval。
- Before execution, system must provide plan, impact, rollback strategy, affected resources and verification steps。
- Secrets must never be logged, committed, or returned to users。

## 7. Non-Functional Requirements

- Security by default
- Auditability
- RBAC and least privilege
- Human approval gate for high-risk actions
- Multi-cloud extensibility
- Explainable AI decisions
- Reproducible IaC generation
- Clear separation between recommendation and execution
- Responsive Web support for desktop, tablet and mobile browsers
- Governed MCP / Skill lifecycle management

## 8. Initial Out of Scope

- Native iOS application
- Native Android application
- Direct production deployment without approval workflow
- Storing plaintext cloud credentials
- Autonomous destructive cloud changes
- Treating third-party collaborative branches as editable without explicit authorization

## English Version

Cloud-360 is an AI-native multi-cloud architecture, governance, security, and operations platform for Cloud Architects, SRE, FinOps, and Security teams.

The platform integrates LLMs, a multi-agent collaboration framework, MCP servers, cloud SDKs, cloud CLIs, Terraform/OpenTofu, reusable AI Skills, and MCP/Skill management capabilities to support AWS, GCP, and Azure lifecycle management.

Core requirements:

- AI-driven architecture design from natural language requirements.
- Cross-cloud component selection across AWS, GCP, and Azure.
- Cost estimation and FinOps analysis, including data egress and interruptible pricing.
- Terraform/OpenTofu generation with static security scanning.
- Operations optimization for performance, reliability, cost, SLO/SLA, and modernization.
- AI Chat driven cloud operations and Agentic AI proactive analysis.
- Cloud Security Posture and Policy Advisory.
- MCP and Skill Management covering registry, catalog, risk classification, versioning, health checks, approvals, and Agent Routing integration.
- Desktop Web as the full workspace and Mobile Web/Responsive Web/PWA as the operations companion.

Out of initial scope:

- Native iOS application.
- Native Android application.
- Direct production deployment without approval workflow.
- Plaintext cloud credentials.
- Autonomous destructive cloud changes.
