# Cloud-360 System Requirement Specification

> 本文件必須同時包含中文版與英文版。
> This document must include both Chinese and English versions.

## 中文版

- Status: Draft v0.2
- Date: 2026-05-22
- Owner: Danniel Chung / Anita

### 1. Platform Vision

Cloud-360 是專為雲端架構師、SRE、FinOps 與 Security 團隊設計的 AI-native 多雲架構與維運管理平台。

平台深度整合 LLM、多智能體協作框架、MCP servers、Cloud SDKs、Cloud CLIs、Terraform / OpenTofu 與可重用 Skills，並提供 MCP 與 Skill 管理功能，提供涵蓋 AWS、GCP、Azure 的端到端生命週期管理能力。

### 2. Target Users

- Cloud Architect
- SRE / Platform Engineer
- FinOps Analyst
- Security Reviewer
- Engineering Manager / Technical Decision Maker

### 3. Core Pillars

#### A. AI-Driven Architecture Design

Cloud-360 將自然語言需求轉成單雲或多雲架構藍圖。

**A1. 功能需求 (Functional Requirements)**
- **自然語言解析**: 必須能識別關鍵詞標籤，包含 workload 類型 (e.g., E-commerce, Data Processing)、HA 需求 (Multi-AZ, Multi-Region)、RTO/RPO 目標。
- **架構圖生成**: 支援生成 Mermaid、PlantUML 與符合 `.drawio` XML 規範的格式。
- **最佳實踐檢查**: 自動檢查 AWS / GCP / Azure Well-Architected Framework 的合規性。
- **災難復原設計**: 自動生成 Active-Active 或 Active-Passive 的跨雲災難復原方案建議。

**A2. 技術約束 (Technical Constraints)**
- **輸出格式**: draw.io XML 必須包含正確的雲端供應商元件圖示 (Shapes/Icons) 與 metadata。
- **架構上下文**: 生成的架構圖必須能轉換為內部 JSON 格式，供後續 Agent 讀取。

#### B. Cross-Cloud Component Selection

Cloud-360 根據 workload profile 提供 AWS / GCP / Azure 託管服務選型建議。

**B1. 功能需求 (Functional Requirements)**
- **等效服務比較**: 核心支援 Compute (VM/Container/Serverless)、Database (SQL/NoSQL/Cache)、Storage (Object/Block/File) 的對等比較。
- **選型指標**: 比較參數必須包含 SLA、硬體限制 (vCPU/Mem limits)、區域可用性、成本風險與廠商鎖定 (Vendor Lock-in) 指數。
- **決策矩陣**: 生成包含理由、優點、缺點與替代方案的決策矩陣。

**B2. 技術約束 (Technical Constraints)**
- **數據時效性**: 服務元件的規格與限制數據必須與雲端供應商官方文檔保持同步（或定義緩存過期機制）。
- **權重模型**: 推薦引擎需支援可調整的權重（例如：性能優先 vs. 成本優先）。

#### C. Cost Estimation & FinOps

Cloud-360 針對架構方案與雲端元件估算多雲 TCO。

**C1. 功能需求 (Functional Requirements)**
- **多維度成本預估**: 包含基礎設施（運算、儲存）、網路（Data Transfer/Egress）、數據服務（資料庫、快取）與維運工具。
- **計費模式比較**: 同時顯示 On-demand、Spot (AWS/Azure/GCP) 與預留實例 (RI/Savings Plan) 的對比。
- **跨雲傳輸分析**: 精確計算跨雲與跨區的 Data Egress 費用，並標註潛在的高額支出路徑。

**C2. 技術約束 (Technical Constraints)**
- **API 整合**: 必須整合 AWS Price List API、GCP Cloud Billing Catalog API 與 Azure Retail Prices API。
- **估算準確度**: 預估值需標註價格假設與數據來源的時間戳記。

#### D. Infrastructure as Code - Terraform / OpenTofu

Cloud-360 將確認後的架構藍圖轉為 Terraform / OpenTofu 模組草稿。

**Required capabilities:**
- 支援 `aws`、`google`、`azurerm` providers。
- 產出 `providers.tf`、`main.tf`、`variables.tf`、`outputs.tf` 與 `modules/` 結構。
- 不產生 production secrets。
- 所有 sensitive values 必須使用 variables、secret manager reference 或 workload identity。
- 整合 tfsec、trivy、Checkov 進行靜態掃描。

#### E. Operations Optimization Review

Cloud-360 針對已部署或設計中的架構進行持續健康檢查與效能檢視。

**Required capabilities:**
- 分析 CPU、memory、IOPS、network、storage、latency、error rate、SLO/SLA。
- 提供 right-sizing、autoscaling、backup、multi-AZ、multi-region 與 observability 建議。
- 根據雲端新服務提出架構現代化建議。

#### F. AI Multi-Cloud Operations

Cloud-360 透過 AI Chat 與 Agentic AI 管理多雲環境。

**Required capabilities:**
- AI Chat 主動式操作：使用者以自然語言查詢、分析與要求維運操作。
- Agentic AI 被動監控與主動分析：背景 agent 監控成本、安全、效能、可用性與政策風險。
- 串接 AWS / GCP / Azure MCP、SDK、CLI、API、Skills 與 Terraform providers。
- 所有高風險操作必須有人類審批。
- 所有操作必須記錄 audit log。

#### G. Cloud Security Posture & Policy Advisory

Cloud-360 檢視多雲安全策略並提出可執行的治理建議。

**Required capabilities:**
- 檢查 IAM / RBAC、Security Group / Firewall / NSG、bucket / blob access、KMS / encryption、audit logging、cloud-native policy guardrails。
- 整合 AWS IAM Access Analyzer、AWS Config、Security Hub、GuardDuty、GCP Security Command Center、GCP Organization Policy、Azure Policy、Defender for Cloud、Azure Advisor 等資料來源。
- 針對 findings 產生 severity、evidence、impact、recommended policy、remediation plan、IaC patch suggestion、verification command、rollback strategy。
- 支援 Policy-as-Code 建議，例如 OPA/Rego、Sentinel、Azure Policy、GCP Org Policy、AWS Config rule。

#### H. MCP & Skill Management

Cloud-360 需提供 MCP servers、MCP tools、AI Skills 與 cloud provider connectors 的集中管理功能。

**Required capabilities:**
- MCP Server Registry：登錄、設定、啟用/停用與檢查 MCP servers。
- Tool Catalog：列出 MCP tools、cloud SDK/CLI wrappers、Terraform tools 與 internal tools。
- Skill Catalog：管理 reusable AI Skills，例如 architecture design、FinOps、security posture review、Terraform generation、incident response。
- Permission & Risk Model：針對每個 MCP tool / Skill 標示 read-only、write、deploy、delete、permission-change、production-impacting 風險等級。
- Versioning：記錄版本、schema、owner、相依性、變更紀錄與 rollback target。
- Health Check：檢查 MCP server availability、tool schema、auth scope、latency、error rate 與最近執行狀態。
- Approval Workflow：新增、升級、停用高風險 MCP / Skill 或擴權時需 human approval。
- Agent Routing Integration：Routing Agent 需可依任務、上下文、風險與權限選擇合適 MCP / Skill。

### 4. User Experience Requirements

#### Desktop Web
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

#### Mobile Web / Responsive Web / PWA
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

### 5. Architecture Visualization Requirements

Cloud-360 的架構圖能力以 draw.io / diagrams.net 相容格式為核心。

**Required capabilities:**
- 支援 `.drawio` / XML source format。
- 支援 SVG / PNG / PDF export。
- 支援 Mermaid / PlantUML derived output。
- AI Chat 可新增元件、刪除元件、調整連線、標註資料流、補 HA/DR/security/observability 元件。
- 每次 AI 修改需產生 change summary 與 version history。
- 圖面需可解析成 internal architecture graph，供 FinOps、IaC、Ops、Security agents 使用。

### 6. Cloud Integration Requirements

Cloud-360 必須透過受控 integration layer 串接雲平台。

**Integration types:**
- MCP servers
- Cloud SDKs
- Cloud CLIs
- Cloud APIs
- Terraform / OpenTofu providers
- AI Skills
- MCP / Skill Registry and Management APIs

**Safety requirements:**
- Read-only operations may execute after policy classification。
- Write / delete / deploy / permission change / production-impacting operations require human approval。
- Before execution, system must provide plan, impact, rollback strategy, affected resources and verification steps。
- Secrets must never be logged, committed, or returned to users。

### 7. Non-Functional Requirements

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

### 8. Initial Out of Scope

- Native iOS application
- Native Android application
- Direct production deployment without approval workflow
- Storing plaintext cloud credentials
- Autonomous destructive cloud changes
- Treating third-party collaborative branches as editable without explicit authorization

---

## English Version

- Status: Draft v0.2
- Date: 2026-05-22
- Owner: Danniel Chung / Anita

### 1. Platform Vision

Cloud-360 is an AI-native multi-cloud architecture and operations management platform designed specifically for Cloud Architects, SREs, FinOps, and Security teams.

The platform deeply integrates LLMs, multi-agent collaboration frameworks, MCP servers, Cloud SDKs, Cloud CLIs, Terraform / OpenTofu, and reusable Skills. It also provides MCP and Skill management capabilities to deliver end-to-end lifecycle management across AWS, GCP, and Azure.

### 2. Target Users

- Cloud Architect
- SRE / Platform Engineer
- FinOps Analyst
- Security Reviewer
- Engineering Manager / Technical Decision Maker

### 3. Core Pillars

#### A. AI-Driven Architecture Design

Cloud-360 translates natural language requirements into single-cloud or multi-cloud architecture blueprints.

**A1. Functional Requirements**
- **Natural Language Parsing**: Must recognize keyword tags including workload types (e.g., E-commerce, Data Processing), HA requirements (Multi-AZ, Multi-Region), and RTO/RPO targets.
- **Architecture Diagram Generation**: Supports generating Mermaid, PlantUML, and formats compliant with `.drawio` XML specifications.
- **Best Practice Validation**: Automatically checks for compliance against AWS / GCP / Azure Well-Architected Frameworks.
- **Disaster Recovery Design**: Automatically generates recommendations for Active-Active or Active-Passive cross-cloud DR scenarios.

**A2. Technical Constraints**
- **Output Format**: draw.io XML must include the correct cloud provider shapes/icons and metadata.
- **Architecture Context**: The generated architecture diagram must be parseable into an internal JSON format for subsequent Agent consumption.

#### B. Cross-Cloud Component Selection

Cloud-360 provides managed service selection recommendations across AWS / GCP / Azure based on workload profiles.

**B1. Functional Requirements**
- **Equivalent Service Comparison**: Core support for peer-to-peer comparison of Compute (VM/Container/Serverless), Database (SQL/NoSQL/Cache), and Storage (Object/Block/File).
- **Selection Metrics**: Comparison parameters must include SLA, hardware limits (vCPU/Mem limits), regional availability, cost risks, and Vendor Lock-in index.
- **Decision Matrix**: Generate a decision matrix containing rationale, pros, cons, and alternatives.

**B2. Technical Constraints**
- **Data Freshness**: Service specifications and limit data must remain synchronized with official cloud provider documentation (or define a cache expiration mechanism).
- **Weighting Model**: The recommendation engine must support adjustable weights (e.g., performance-first vs. cost-first).

#### C. Cost Estimation & FinOps

Cloud-360 estimates multi-cloud TCO for architecture scenarios and cloud components.

**C1. Functional Requirements**
- **Multi-dimensional Cost Estimation**: Includes infrastructure (compute, storage), network (Data Transfer/Egress), data services (databases, caches), and operations tools.
- **Billing Model Comparison**: Displays a side-by-side comparison of On-demand, Spot (AWS/Azure/GCP), and Reserved Instances (RI/Savings Plan).
- **Cross-Cloud Transfer Analysis**: Accurately calculates cross-cloud and cross-region Data Egress costs, highlighting potential high-cost paths.

**C2. Technical Constraints**
- **API Integration**: Must integrate with AWS Price List API, GCP Cloud Billing Catalog API, and Azure Retail Prices API.
- **Estimation Accuracy**: Estimates must annotate pricing assumptions and data source timestamps.

#### D. Infrastructure as Code - Terraform / OpenTofu

Cloud-360 converts the finalized architecture blueprint into Terraform / OpenTofu module drafts.

**Required capabilities:**
- Support `aws`, `google`, and `azurerm` providers.
- Generate `providers.tf`, `main.tf`, `variables.tf`, `outputs.tf`, and `modules/` structure.
- Do not generate production secrets.
- All sensitive values must use variables, secret manager references, or workload identity.
- Integrate tfsec, trivy, and Checkov for static scanning.

#### E. Operations Optimization Review

Cloud-360 continuously performs health checks and performance reviews on deployed or designed architectures.

**Required capabilities:**
- Analyze CPU, memory, IOPS, network, storage, latency, error rate, and SLO/SLA.
- Provide right-sizing, autoscaling, backup, multi-AZ, multi-region, and observability recommendations.
- Propose architecture modernization recommendations based on new cloud services.

#### F. AI Multi-Cloud Operations

Cloud-360 manages multi-cloud environments via AI Chat and Agentic AI.

**Required capabilities:**
- AI Chat Proactive Operations: Users query, analyze, and request operations using natural language.
- Agentic AI Passive Monitoring and Proactive Analysis: Background agents monitor cost, security, performance, availability, and policy risks.
- Connect with AWS / GCP / Azure MCPs, SDKs, CLIs, APIs, Skills, and Terraform providers.
- All high-risk operations must have human approval.
- All operations must be recorded in the audit log.

#### G. Cloud Security Posture & Policy Advisory

Cloud-360 reviews multi-cloud security strategies and provides actionable governance recommendations.

**Required capabilities:**
- Inspect IAM / RBAC, Security Group / Firewall / NSG, bucket / blob access, KMS / encryption, audit logging, and cloud-native policy guardrails.
- Integrate data sources such as AWS IAM Access Analyzer, AWS Config, Security Hub, GuardDuty, GCP Security Command Center, GCP Organization Policy, Azure Policy, Defender for Cloud, and Azure Advisor.
- Generate severity, evidence, impact, recommended policy, remediation plan, IaC patch suggestion, verification command, and rollback strategy for findings.
- Support Policy-as-Code recommendations (e.g., OPA/Rego, Sentinel, Azure Policy, GCP Org Policy, AWS Config rules).

#### H. MCP & Skill Management

Cloud-360 must provide centralized management capabilities for MCP servers, MCP tools, AI Skills, and cloud provider connectors.

**Required capabilities:**
- MCP Server Registry: Register, configure, enable/disable, and inspect MCP servers.
- Tool Catalog: List MCP tools, cloud SDK/CLI wrappers, Terraform tools, and internal tools.
- Skill Catalog: Manage reusable AI Skills (e.g., architecture design, FinOps, security posture review, Terraform generation, incident response).
- Permission & Risk Model: Label risk levels (read-only, write, deploy, delete, permission-change, production-impacting) for each MCP tool / Skill.
- Versioning: Record version, schema, owner, dependencies, change log, and rollback target.
- Health Check: Check MCP server availability, tool schema, auth scope, latency, error rate, and latest execution status.
- Approval Workflow: Require human approval when adding, upgrading, disabling, or escalating privileges for high-risk MCPs/Skills.
- Agent Routing Integration: Allow the Routing Agent to select appropriate MCPs/Skills based on task, context, risk, and permissions.

### 4. User Experience Requirements

#### Desktop Web
The Desktop Web serves as the full workspace for Cloud-360 and must support:
- AI Chat
- draw.io / diagrams.net architecture canvas
- Terraform / policy code editor
- FinOps dashboard
- Security posture dashboard
- Operations dashboard
- Agent trace
- Audit log
- Approval gate management

#### Mobile Web / Responsive Web / PWA
The mobile version is also delivered via Web. A native iOS / Android app is not planned for the first phase.

Mobile Web focuses on:
- AI Chat
- Alerts
- Approval / reject workflow
- Cloud health digest
- Cost / security / operations findings
- Readonly architecture diagram view
- Incident quick triage

The Mobile Web is not intended as the primary interface for heavy draw.io diagram editing or deep Terraform development.

### 5. Architecture Visualization Requirements

Cloud-360's architecture diagram capabilities are centered around draw.io / diagrams.net compatible formats.

**Required capabilities:**
- Support `.drawio` / XML source format.
- Support SVG / PNG / PDF export.
- Support Mermaid / PlantUML derived output.
- AI Chat can add/delete components, adjust connections, annotate data flows, and supplement HA/DR/security/observability components.
- Generate a change summary and version history for each AI modification.
- Diagrams must be parseable into an internal architecture graph for FinOps, IaC, Ops, and Security agents.

### 6. Cloud Integration Requirements

Cloud-360 must connect to cloud platforms via a controlled integration layer.

**Integration types:**
- MCP servers
- Cloud SDKs
- Cloud CLIs
- Cloud APIs
- Terraform / OpenTofu providers
- AI Skills
- MCP / Skill Registry and Management APIs

**Safety requirements:**
- Read-only operations may execute after policy classification.
- Write / delete / deploy / permission change / production-impacting operations require human approval.
- Before execution, the system must provide a plan, impact analysis, rollback strategy, affected resources, and verification steps.
- Secrets must never be logged, committed, or returned to users.

### 7. Non-Functional Requirements

- Security by default
- Auditability
- RBAC and least privilege
- Human approval gate for high-risk actions
- Multi-cloud extensibility
- Explainable AI decisions
- Reproducible IaC generation
- Clear separation between recommendation and execution
- Responsive Web support for desktop, tablet, and mobile browsers
- Governed MCP / Skill lifecycle management

### 8. Initial Out of Scope

- Native iOS application
- Native Android application
- Direct production deployment without approval workflow
- Storing plaintext cloud credentials
- Autonomous destructive cloud changes
- Treating third-party collaborative branches as editable without explicit authorization
