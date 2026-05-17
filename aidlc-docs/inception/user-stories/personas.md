# User Personas - Cloud-360

> This document defines the key user personas for the Cloud-360 platform.
> 本文件定義 Cloud-360 平台的關鍵使用者畫像。

## 中文版

### 1. 雲端架構師 (Cloud Architect)
- **職責**：負責設計高可用、可擴展且安全的跨雲架構。
- **核心目標**：
  - 快速產出符合業務需求的技術架構圖。
  - 確保設計符合雲端服務商的最佳實踐（Well-Architected）。
  - 優化跨雲服務的選擇以降低鎖定風險。
- **核心痛點**：
  - 手動繪製架構圖耗時且難以維護。
  - 難以即時掌握各雲端供應商最新服務的差異。
- **技術背景**：熟悉多種雲端平台（AWS/GCP/Azure），具備 IaC 與網路安全知識。
- **使用場景**：在專案啟動階段使用 AI 轉架構功能，並透過 AI Chat 修改 draw.io 圖表。

### 2. SRE (Site Reliability Engineer)
- **職責**：確保系統的穩定性、可用性與效能。
- **核心目標**：
  - 自動化基礎設施配置與監控。
  - 快速診斷並修復跨雲環境中的故障。
  - 實施自動化的安全與合規性檢查。
- **核心痛點**：
  - 管理分散在不同雲平台的資源非常複雜。
  - 手動處理報警與資源擴展耗費大量精力。
- **技術背景**：精通自動化腳本、監控工具與容器化技術（K8s）。
- **使用場景**：使用 AI Chat 查詢跨雲狀態，審核自動生成的 IaC 安全掃描報告。

### 3. 技術決策者 (Technical Decision Maker)
- **職責**：評估技術方案並決定雲端策略。
- **核心目標**：
  - 根據成本、性能與 SLA 選擇最合適的服務。
  - 降低長期營運成本與技術債。
- **核心痛點**：
  - 缺乏透明的跨雲服務比較數據。
  - 難以評估新技術引入的風險與收益。
- **技術背景**：具備宏觀技術視野，重視商業價值與合規性。
- **使用場景**：參考「服務比較矩陣」進行雲端供應商選型決策。

### 4. FinOps 分析師 (FinOps Analyst)
- **職責**：監控並優化雲端支出。
- **核心目標**：
  - 精確估算架構的每月 TCO。
  - 識別並減少閒置資源與浪費。
- **核心痛點**：
  - 雲端帳單複雜，難以追蹤跨雲流量成本（Egress）。
  - 預算預測與實際支出常有顯著差異。
- **技術背景**：擅長數據分析，熟悉雲端定價模型（Spot、RI、Savings Plans）。
- **使用場景**：在架構設計階段進行成本估算，審核跨雲流量成本分析。

### 5. 平台工程師 (Platform Engineer)
- **職責**：建構與維護內部開發者平台（IDP），提供標準化工具。
- **核心目標**：
  - 提供自助式的 IaC 模板與 MCP 工具。
  - 維護 AI Skill 目錄以標準化作業流程。
- **核心痛點**：
  - 頻繁處理重複的基礎設施請求。
  - 難以管理眾多自定義腳本與自動化工具的安全性。
- **技術背景**：深厚、 IaC、API 設計與 AI 整合經驗。
- **使用場景**：註冊新的 MCP Server，管理 AI Skill 目錄與工具權限。

### 6. 安全性審查員 (Security Reviewer)
- **職責**：確保雲端環境符合安全標準與合規要求。
- **核心目標**：
  - 檢測權限過大的身分（Least Privilege）。
  - 自動化安全性掃描與漏洞發現。
- **核心痛點**：
  - 多雲環境下的安全性原則不一致，難以統一稽核。
  - 安全警告過多，難以識別真正的威脅。
- **技術背景**：具備網路安全、身分驗證（IAM/RBAC）與合規性經驗。
- **使用場景**：審查 IaC 安全掃描結果，分析權限過大的 IAM 角色。

### 7. 運維負責人 (Operations Lead)
- **職責**：領導維運團隊，制定應對與恢復策略。
- **核心目標**：
  - 提升團隊的 MTTR（平均修復時間）。
  - 實施主動式維運，防範未然。
- **核心痛點**：
  - 團隊成員對不同雲平台的熟悉度參差不齊。
  - 缺乏跨平台的統一操作視圖。
- **技術背景**：具備豐富的事件管理與團隊管理經驗。
- **使用場景**：檢視 Agentic AI 產出的主動式維運建議。

### 8. 工程主管 (Engineering Manager)
- **職責**：管理開發進度，平衡開發速度與產品質量。
- **核心目標**：
  - 縮短從設計到部署的週期（Time-to-Market）。
  - 提升團隊開發效率，減少手動繁瑣工作。
- **核心痛點**：
  - 團隊在雲端架構設計上耗時過長。
  - 難以平衡技術創新與穩定性要求。
- **技術背景**：具備軟體開發管理與敏捷開發經驗。
- **使用場景**：檢視專案架構進度與成本預算報告。

### 9. 一般使用者 (End User)
- **職責**：最終應用程式的使用者或 API 消費者。
- **核心目標**：
  - 獲得穩定且快速的應用程式體驗。
  - 確保其數據安全與隱私。
- **核心痛點**：
  - 系統延遲或服務中斷。
- **技術背景**：不一定具備雲端技術背景。
- **使用場景**：間接受益於 AI 驅動的自動修復與擴展。

### 10. 平台管理員 (Platform Admin)
- **職責**：管理 Cloud-360 平台本身的配置與使用者權限。
- **核心目標**：
  - 確保 Cloud-360 平台的安全與高效運行。
- **核心痛點**：
  - 需要管理複雜的 MCP 權限模型。
- **技術背景**：具備系統管理與權限管理經驗。
- **使用場景**：分析權限過大的身分，管理平台操作政策。

### 11. 平台擁有者 (Platform Owner)
- **職責**：對 Cloud-360 平台的產品方向與決策負責。
- **核心目標**：
  - 審核高風險的雲端操作與變更。
  - 確保平台發展符合企業戰略。
- **核心痛點**：
  - 高風險變更可能導致嚴重的生產事故。
- **技術背景**：具備決策權，了解業務影響。
- **使用場景**：透過行動裝置審核高風險的操作請求。

---

## English Version

### 1. Cloud Architect
- **Responsibility**: Designs high-availability, scalable, and secure cross-cloud architectures.
- **Core Goals**:
  - Quickly generate architectural blueprints that meet business requirements.
  - Ensure designs comply with cloud provider Well-Architected best practices.
  - Optimize cross-cloud component selection to reduce vendor lock-in.
- **Core Pain Points**:
  - Manual drawing of architecture diagrams is time-consuming and hard to maintain.
  - Difficulty staying updated on service differences across multiple cloud providers.
- **Technical Background**: Familiar with multiple cloud platforms (AWS/GCP/Azure); knowledgeable in IaC and network security.
- **Usage Scenario**: Uses NL-to-Architecture during project initiation; edits draw.io charts via AI Chat.

### 2. SRE (Site Reliability Engineer)
- **Responsibility**: Ensures system stability, availability, and performance.
- **Core Goals**:
  - Automate infrastructure provisioning and monitoring.
  - Rapidly diagnose and remediate failures in cross-cloud environments.
  - Implement automated security and compliance checks.
- **Core Pain Points**:
  - Managing resources scattered across different cloud platforms is complex.
  - Manual handling of alerts and scaling consumes excessive effort.
- **Technical Background**: Expert in automation scripting, monitoring tools, and containerization (K8s).
- **Usage Scenario**: Queries cross-cloud status via AI Chat; reviews automated IaC security scan reports.

### 3. Technical Decision Maker
- **Responsibility**: Evaluates technical solutions and decides on cloud strategies.
- **Core Goals**:
  - Select the most suitable services based on cost, performance, and SLA.
  - Reduce long-term operational costs and technical debt.
- **Core Pain Points**:
  - Lack of transparent cross-cloud service comparison data.
  - Difficulty assessing the risks and benefits of introducing new technologies.
- **Technical Background**: Broad technical vision; focuses on business value and compliance.
- **Usage Scenario**: References the "Service Comparison Matrix" for provider selection decisions.

### 4. FinOps Analyst
- **Responsibility**: Monitors and optimizes cloud spending.
- **Core Goals**:
  - Accurately estimate monthly TCO for proposed architectures.
  - Identify and reduce idle resources and waste.
- **Core Pain Points**:
  - Complex cloud billing; difficulty tracking cross-cloud data transfer costs (Egress).
  - Significant variances between budget forecasts and actual spending.
- **Technical Background**: Skilled in data analysis; familiar with cloud pricing models (Spot, RI, Savings Plans).
- **Usage Scenario**: Estimates costs during the architecture design phase; reviews cross-cloud egress analysis.

### 5. Platform Engineer
- **Responsibility**: Builds and maintains Internal Developer Platforms (IDP).
- **Core Goals**:
  - Provide self-service IaC templates and MCP tools.
  - Maintain the AI Skill catalog to standardize workflows.
- **Core Pain Points**:
  - Frequently handles repetitive infrastructure requests.
  - Hard to manage the security of numerous custom scripts and automation tools.
- **Technical Background**: Deep experience in DevOps, IaC, API design, and AI integration.
- **Usage Scenario**: Registers new MCP Servers; manages AI Skill catalogs and tool permissions.

### 6. Security Reviewer
- **Responsibility**: Ensures cloud environments meet security standards and compliance requirements.
- **Core Goals**:
  - Detect over-permissive identities (Least Privilege).
  - Automate security scanning and vulnerability discovery.
- **Core Pain Points**:
  - Inconsistent security policies across multi-cloud environments make auditing difficult.
  - Alert fatigue makes it hard to identify real threats.
- **Technical Background**: Experienced in network security, identity management (IAM/RBAC), and compliance.
- **Usage Scenario**: Reviews IaC security scan results; analyzes over-permissive IAM roles.

### 7. Operations Lead
- **Responsibility**: Leads the operations team and defines response and recovery strategies.
- **Core Goals**:
  - Improve the team's MTTR (Mean Time To Recovery).
  - Implement proactive operations to prevent issues.
- **Core Pain Points**:
  - Team members have varying levels of familiarity with different cloud platforms.
  - Lack of a unified operational view across platforms.
- **Technical Background**: Extensive experience in incident management and team leadership.
- **Usage Scenario**: Reviews proactive operational recommendations generated by Agentic AI.

### 8. Engineering Manager
- **Responsibility**: Manages development progress; balances development speed with product quality.
- **Core Goals**:
  - Shorten the design-to-deployment cycle (Time-to-Market).
  - Increase team productivity by reducing manual toil.
- **Core Pain Points**:
  - Team spends too much time on cloud architecture design.
  - Difficulty balancing technical innovation with stability requirements.
- **Technical Background**: Experienced in software development management and Agile methodologies.
- **Usage Scenario**: Reviews project architecture progress and cost budget reports.

### 9. End User
- **Responsibility**: The user of the final application or consumer of APIs.
- **Core Goals**:
  - Experience a stable and fast application.
  - Ensure data security and privacy.
- **Core Pain Points**:
  - System latency or service interruptions.
- **Technical Background**: Does not necessarily have a cloud technology background.
- **Usage Scenario**: Indirectly benefits from AI-driven automated remediation and scaling.

### 10. Platform Admin
- **Responsibility**: Manages the configuration and user permissions of the Cloud-360 platform itself.
- **Core Goals**:
  - Ensure the secure and efficient operation of the Cloud-360 platform.
- **Core Pain Points**:
  - Needs to manage a complex MCP permission model.
- **Technical Background**: Experienced in system administration and access control.
- **Usage Scenario**: Analyzes over-permissive identities and manages platform operation policies.

### 11. Platform Owner
- **Responsibility**: Accountable for the product direction and decisions of the Cloud-360 platform.
- **Core Goals**:
  - Review high-risk cloud operations and changes.
  - Ensure platform development aligns with corporate strategy.
- **Core Pain Points**:
  - High-risk changes can lead to serious production incidents.
- **Technical Background**: Decision-making authority; understands business impact.
- **Usage Scenario**: Approves high-risk operation requests via mobile web.
