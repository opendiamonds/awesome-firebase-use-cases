# Cloud-360

Cloud-360 是面向雲端架構師、SRE、FinOps 與 Security 團隊的 **AI-native multi-cloud architecture and operations platform**。

平台支援 AWS、GCP、Azure 三大公有雲，透過 AI Chat、Agentic AI、MCP、Cloud SDK、Cloud CLI、Terraform / OpenTofu 與可重用 Skills，協助團隊完成架構設計、跨雲選型、成本估算、IaC 產製、安全策略檢視與日常維運最佳化。

## Platform Vision

Cloud-360 的目標是提供一個 Web-first 的多雲管理與設計工作台：

- 將自然語言需求轉成多雲架構方案。
- 使用線上 draw.io / diagrams.net 相容畫布，讓使用者與 AI chatbot 共同編輯架構圖。
- 比較 AWS / GCP / Azure 元件、SLA、限制、相容性與成本。
- 估算多雲 TCO、Data Egress、Spot / Preemptible / Reserved pricing 策略。
- 將確認後的架構轉成 Terraform / OpenTofu 模組草稿。
- 透過 Agentic AI 主動檢查成本、安全、效能、可用性與維運風險。
- 透過 MCP / SDK / CLI / Skills 安全地整合雲平台管理能力。

## Core Modules

1. **Architecture Design**
   - 自然語言轉架構藍圖。
   - 產生 Mermaid / PlantUML / draw.io 圖面。
   - 檢查 Well-Architected Framework 與 HA / DR / Scalability 需求。

2. **Cross-Cloud Component Selection**
   - 比較 AWS、GCP、Azure 同質服務。
   - 依 workload profile 推薦合適雲端元件。
   - 輸出 SLA、限制、相容性、lock-in、維運成本與替代方案。

3. **Cost Estimation & FinOps**
   - 估算 Compute、Database、Storage、Network、CDN、Data Egress 與 Observability 成本。
   - 比較 AWS Spot、Azure Spot、GCP Spot / Preemptible 等計費模式。
   - 產出成本異常與 right-sizing 建議。

4. **Infrastructure as Code - Terraform / OpenTofu**
   - 產生 `aws`、`google`、`azurerm` provider 對應的 Terraform / OpenTofu 模組。
   - 支援 `main.tf`、`variables.tf`、`outputs.tf`、`providers.tf` 與 `modules/` 結構。
   - 整合 tfsec、trivy、Checkov 等靜態掃描工具。

5. **Operations Optimization Review**
   - 分析已部署或設計中的架構。
   - 提供效能、可用性、成本、SLO/SLA 與架構現代化建議。
   - 主動建議 managed service、serverless、container platform 或跨雲遷移方案。

6. **AI Multi-Cloud Operations**
   - 使用 AI Chat 主動查詢、分析與管理 AWS / GCP / Azure。
   - 透過 Agentic AI 被動監控、主動分析與產生維運建議。
   - 透過 MCP servers、Cloud SDKs、Cloud CLIs 與 Skills 執行受控操作。

7. **Cloud Security Posture & Policy Advisory**
   - 檢視 IAM / RBAC、network exposure、storage access、encryption、audit logging、policy guardrails。
   - 產生 least-privilege、Policy-as-Code、IaC patch 與 remediation plan 建議。
   - 高風險修復必須通過 human approval gate。

## Web-Based Desktop and Mobile Experience

Cloud-360 是 Web-first 平台，第一階段不做 native iOS / Android app。

- **Desktop Web**：完整工作台，包含 draw.io co-editing、IaC editor、FinOps dashboard、Security dashboard、Ops dashboard、Agent trace 與 audit log。
- **Mobile Web / Responsive Web / PWA**：維運伴隨介面，聚焦 AI Chat、alerts、approval workflow、cloud health digest、security / cost findings 與 readonly architecture diagram review。

## Architecture Visualization Canvas

Cloud-360 採用線上 **draw.io / diagrams.net-compatible architecture canvas**。使用者可以手動編輯架構圖，也可以透過 AI Chat 以自然語言要求 AI 共同修改圖面。

圖面不只是圖片，而是系統的 shared architecture context：

- source format：`.drawio` / diagrams.net XML
- derived format：Mermaid、PlantUML、SVG、PNG、internal architecture graph JSON
- downstream consumers：Design Agent、FinOps Agent、IaC Agent、Ops Agent、Security Policy Advisor Agent

## Cloud Operation Integration

Cloud-360 透過以下方式整合雲平台：

- MCP servers
- Cloud SDKs
- Cloud CLIs
- Terraform / OpenTofu providers
- AI Skills
- Cloud-native monitoring, billing, IAM, policy and security APIs

Read-only 查詢與分析可直接執行；write / delete / deploy / permission change / production-impacting action 必須先產生 plan、impact、rollback strategy，並通過 human approval gate。

## Documentation

- [System Requirement Specification](docs/srs/cloud-360-srs.md)
- [System Architecture](docs/architecture/system-architecture.md)
- [Core Pillars User Stories](docs/user-stories/core-pillars.md)
- [ADR 0001: Repository Scope](docs/adr/0001-repo-scope.md)
- [ADR 0002: Agent Routing Layer](docs/adr/0002-agent-routing-layer.md)
- [ADR 0003: Web-Based Desktop and Mobile Experience](docs/adr/0003-web-based-experience.md)

## Repository Contract

This repository currently tracks the Cloud-360 SDD baseline:

- platform SRS
- architecture diagrams
- user stories
- ADRs
- repository validation script
- baseline CI

Production credentials, environment-specific secrets, direct production IaC, and destructive cloud operations are explicitly out of scope unless reviewed and approved through future ADRs.

## Validation

```bash
python scripts/validate_repo_contract.py
git diff --check
```
