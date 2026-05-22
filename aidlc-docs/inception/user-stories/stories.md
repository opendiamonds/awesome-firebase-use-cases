# User Stories - Cloud-360

> 本文件列出 Cloud-360 的使用者故事，按架構支柱（Pillars A-H）分類，深度結合 Persona 操作場景，並包含 BDD（行為驅動開發）劇本以及 AI 重置與人工調整機制。
> This document lists the user stories for Cloud-360, organized by architecture pillars (A-H), deeply integrated with Persona scenarios, and includes BDD scenarios alongside AI reset and manual adjustment mechanisms.

## 中文版

### A. 架構設計 (AI-Driven Architecture Design)
- **Story**: 透過自然語言快速產出並驗證多雲架構藍圖
- **Persona**: Alex (雲端架構師)
- **權限控管機制 (RBAC)**：
  - 需要 `Project_Architect` 或 `Project_Editor` 權限才能發起架構生成與修改。
  - `Viewer` 權限登入後僅能檢視架構圖。
- **登入與操作流程**：
  1. Alex 從首頁登入 Cloud-360 桌面版，進入「專案工作區」。
  2. 點擊「新增架構」，在 AI Chat 輸入需求：「需要 AWS 電商架構，支援 Multi-AZ，Aurora 資料庫與 WAF」。
  3. AI 分析後在 draw.io 畫布上生成完整架構草圖。
  4. **AI 重置與人工調整機制**：若 Alex 對整體架構方向不滿意，可點擊「全部重置 (Full Reset)」請 AI 重新評估；若僅對網路層不滿意，可框選網路區塊點選「局部重置 (Partial Reset)」。所有 AI 產出後，Alex 皆可隨時「人工介入」拖拉節點與連線。
  5. 畫布定案後，系統背景自動執行 Well-Architected 驗證。
- **系統回饋**：
  - **成功**：彈出綠色提示「架構生成完畢，通過檢測」，並存入版本紀錄。
  - **失敗**：若局部重置引發架構衝突，AI 標示錯誤節點並給出紅色警告。
- **行為驅動開發 (BDD Scenarios)**：
  - **Scenario 1: AI 局部重置與人工微調**
    - **Given** Alex 已登入且位於架構畫布，畫面上已有 AI 生成的初始架構。
    - **When** Alex 發現資料庫層設計不佳，框選該區並點擊「局部重置」，輸入「改用 DynamoDB」，隨後人工將新產生的節點連線至 API Gateway。
    - **Then** 系統保留其餘架構不變，僅抽換資料庫區塊，並重新進行合規檢測。

### B. 跨雲選型 (Cross-Cloud Component Selection)
- **Story**: 產出客觀透明的跨雲服務比較決策矩陣
- **Persona**: Catherine (技術決策者)
- **權限控管機制 (RBAC)**：
  - 僅 `Project_Admin` 與 `Technical_Lead` 權限可調整選型權重。
- **登入與操作流程**：
  1. Catherine 登入後導覽至「跨雲選型」模組。
  2. 輸入「高併發 NoSQL 資料庫」場景與偏好權重。
  3. AI 即時生成包含 AWS、GCP、Azure 的決策矩陣報告。
  4. **AI 重置與人工調整機制**：Catherine 檢視矩陣後，若發現缺少特定的衡量指標，可點擊「局部重置」要求 AI「加入 Data Egress 比較」。她也能人工勾選或隱藏特定雲端廠商，進行「人工調整」來客製化報告。
- **系統回饋**：
  - **成功**：生成動態對比圖表與可下載的 PDF 報告。
  - **失敗**：API 數據過期時顯示黃色警告，提示手動同步。
- **行為驅動開發 (BDD Scenarios)**：
  - **Scenario 1: 決策矩陣的人工介入與重置**
    - **Given** Catherine 正在查閱剛生成的 NoSQL 決策矩陣。
    - **When** 她對 GCP Firestore 的評價不認同，點選該欄位執行「局部重置」要求「更新至 2026 年最新 SLA」，並人工加上一條內部團隊的註解。
    - **Then** 系統僅重新生成 Firestore 的評估數據，並保留她的人工註解，最後匯出報告。

### C. 成本估算與 FinOps (Cost Estimation & FinOps)
- **Story**: 專案層級的 TCO 精算與 Data Egress 追蹤
- **Persona**: David (FinOps 分析師)
- **權限控管機制 (RBAC)**：
  - 需 `FinOps_Analyst` 才能檢視詳細定價協議與成本，預設對開發者遮蔽。
- **登入與操作流程**：
  1. David 登入進入「FinOps 儀表板」，匯入 Alex 畫好的架構。
  2. 系統 AI 精算 TCO 並模擬 Data Egress 流量成本。
  3. **AI 重置與人工調整機制**：若 AI 推測的每月流量模型不符預期，David 可點擊「全部重置」讓 AI 改以「影音串流高頻寬模型」重新推算。同時，他可以「人工修改」EC2 的預設開機時數（例如調整為一天只開 8 小時）。
- **系統回饋**：
  - **成功**：圓餅圖即時刷新，顯示採用新模型與人工調整後的節省比例。
  - **失敗**：若無法取得定價，標記為「價格未知」。
- **行為驅動開發 (BDD Scenarios)**：
  - **Scenario 1: 成本模型的重置與微調**
    - **Given** David 獲得了一份預估為每月 $5000 的基礎成本報告。
    - **When** 他點選「局部重置」要求 AI 重新評估資料庫層的流量成本，並人工將網路傳輸量從 5TB 修改為 10TB。
    - **Then** 系統即時重新計算，總金額更新，並將人工修改過的參數標註為「Manual Override」。

### D. IaC 產出與安全掃描 (IaC - Terraform / OpenTofu)
- **Story**: 將畫布架構無縫轉化為安全的 IaC 模組
- **Persona**: Elena (平台工程師), Fiona (安全性審查員)
- **權限控管機制 (RBAC)**：
  - `Platform_Engineer` 可產出代碼，部署需經 `Security_Reviewer` 審核與掃描。
- **登入與操作流程**：
  1. Elena 登入「IaC 工作區」，點選「轉換為 Terraform 模組」。
  2. AI 生成結構化的 `main.tf`、`variables.tf` 等代碼。
  3. **AI 重置與人工調整機制**：若 Elena 發現 AI 生成的 Naming Convention 不符公司規定，可選取 `variables.tf` 點擊「局部重置」，指示 AI「依照公司標準加上 pre-fix」。她也可以在內建 IDE 中進行「人工編寫」來修改特定參數。
  4. 儲存後觸發 tfsec 背景安全掃描。
- **系統回饋**：
  - **成功**：掃描通過，允許下載或 Push 至 Git。
  - **失敗**：掃描到高危漏洞，紅色阻擋導出並給出 AI 修復建議。
- **行為驅動開發 (BDD Scenarios)**：
  - **Scenario 1: IaC 代碼生成與局部覆寫**
    - **Given** Elena 在 IaC 工作區看到 AI 初步生成的 Terraform 代碼。
    - **When** 她不滿意 S3 Bucket 的模組引用方式，框選該段代碼點選「局部重置」要求改用「內部公用 Module」，隨後人工補上 `tags` 參數。
    - **Then** 系統重新生成 S3 區塊代碼，保留她手打的 `tags`，並順利通過後續的靜態安全掃描。

### E. 維運優化審查 (Operations Optimization Review)
- **Story**: 基於背景 Agent 分析的架構 Right-sizing
- **Persona**: George (運維負責人)
- **權限控管機制 (RBAC)**：
  - `Ops_Lead` 可查看全局效能並套用優化，變更會通知 `Project_Owner`。
- **登入與操作流程**：
  1. George 登入「Operations Dashboard」，查看 AI Agent 的降級 (Down-size) 建議。
  2. **AI 重置與人工調整機制**：如果 AI 的建議太過激進，George 可對特定建議點擊「局部重置」，輸入「我們即將有行銷活動，請保留至少 50% 餘裕」讓 AI 重新建議實例型號。他也能「人工調整」目標實例等級（例如手動選定 `t3.medium`）。
  3. 勾選最終建議並產生優化變更單。
- **系統回饋**：
  - **成功**：建立變更單，狀態改為「Pending Scheduled Execution」。
  - **失敗**：若資源被鎖定 (Termination Protection)，彈出保護警告。
- **行為驅動開發 (BDD Scenarios)**：
  - **Scenario 1: 維運建議的人工校正**
    - **Given** George 收到一份將 5 台機器降級的 AI 建議。
    - **When** 他認為其中 2 台是核心服務不能動，於是對那兩台進行「人工剔除」，並要求 AI 對剩下 3 台「局部重置」降級策略。
    - **Then** 系統產生新的變更單，僅包含 3 台機器的安全降級計畫。

### F. AI 多雲維運與審批 (AI Multi-Cloud Operations)
- **Story**: 高風險操作的 Human Approval Gate 機制
- **Persona**: Ben (SRE), Karen (平台擁有者)
- **權限控管機制 (RBAC)**：
  - 涉及高風險指令強制進入 Human Approval Gate，僅 `Platform_Owner` 可核准。
- **登入與操作流程**：
  1. Ben 在 AI Chat 輸入：「幫我把 Prod Web ASG 實例數改為 10」。
  2. AI 產出變更計畫 (Plan) 與回滾策略 (Rollback) 的執行腳本。
  3. **AI 重置與人工調整機制**：送出審批前，Ben 若發現回滾腳本寫得不夠安全，可點擊「局部重置」要求 AI「加入資料庫快照步驟」，或切換到「人工編輯模式」親自修改腳本。
  4. 確認無誤後送出，Karen 在手機端審核並透過 FaceID 批准。
- **系統回饋**：
  - **成功**：手機端顯示授權成功，自動執行並寫入 Audit Log。
  - **失敗**：Karen 拒絕或超時，自動取消變更。
- **行為驅動開發 (BDD Scenarios)**：
  - **Scenario 1: 變更腳本的局部重置與高層審批**
    - **Given** Ben 透過 AI 產生了一份包含擴容與回滾的自動化腳本。
    - **When** Ben 覺得回滾的 Timeout 設得太短，人工將它從 30s 改為 120s，並送出給 Karen 審批。Karen 登入後按下同意。
    - **Then** 系統依照 Ben 人工調整過的安全時間執行擴容腳本，並留下不可篡改的紀錄。

### G. 雲端安全態勢 (Cloud Security Posture)
- **Story**: 全局 IAM 最小權限原則掃描與策略代碼化
- **Persona**: Fiona (安全性審查員)
- **權限控管機制 (RBAC)**：
  - 僅 `Security_Admin` 或合規稽核員可發起全局安全掃描。
- **登入與操作流程**：
  1. Fiona 登入「Security Dashboard」，執行 IAM Least Privilege 分析。
  2. 系統列出未使用的 Role，Fiona 要求 AI 產出對應的 OPA (Rego) 策略代碼。
  3. **AI 重置與人工調整機制**：若 AI 生成的 Rego 代碼過於嚴格，Fiona 可點擊「局部重置」要求 AI「排除開發環境的 Role」，或者直接進入編輯器「人工修改」正則表達式。
- **系統回饋**：
  - **成功**：產出精確的 Rego 代碼並提供測試驗證通過。
  - **失敗**：若缺 MCP 授權，彈出紅字錯誤要求更新憑證。
- **行為驅動開發 (BDD Scenarios)**：
  - **Scenario 1: 安全策略的生成與客製化**
    - **Given** Fiona 在畫面上看到 AI 初步生成的 20 行 Rego 策略代碼。
    - **When** 她發現某個允許條件寫反了，便框選該段點擊「局部重置」並給予提示，接著人工加入了公司特定的標籤檢查邏輯。
    - **Then** OPA 策略測試器成功運行通過，確保既攔截危險權限又允許正常開發。

### H. MCP 與 Skill 管理 (MCP & Skill Management)
- **Story**: 註冊並管控內部自定義工具的存取邊界
- **Persona**: Elena (平台工程師), Jack (平台管理員)
- **權限控管機制 (RBAC)**：
  - `Platform_Engineer` 可申請註冊，`Platform_Admin` 審核與標記風險等級。
- **登入與操作流程**：
  1. Elena 登入「MCP & Skill 目錄」，填寫內部 CMDB API 端點。
  2. AI 自動解析 API Schema 並生成工具的系統提示詞 (System Prompt) 描述。
  3. **AI 重置與人工調整機制**：若 AI 生成的 Prompt 描述不夠精確，Elena 可點擊「全部重置」讓 AI 重新解析，或「人工編輯」Prompt 來明確告訴未來的 Agent 該如何正確傳入參數。
  4. Jack 登入後台審查並標記為 `Read-only`。
- **系統回饋**：
  - **成功**：工具狀態轉為 `Active`，SRE 可在 AI Chat 呼叫。
  - **失敗**：Health Check 逾時或 Schema 錯誤，拒絕上架。
- **行為驅動開發 (BDD Scenarios)**：
  - **Scenario 1: AI 工具描述的優化與上架**
    - **Given** Elena 剛輸入 API URL，AI 為其生成了很長的參數說明。
    - **When** Elena 覺得過於冗長，點擊「全部重置」要求「精簡至 50 字以內」，並人工微調了必填參數的備註。提交後 Jack 進行了審批。
    - **Then** 該 MCP 工具成功上架，且後續的 AI Agent 在呼叫時能根據精簡的描述，達到 100% 的參數傳遞正確率。

---

## English Version

### A. Architecture Design (AI-Driven Architecture Design)
- **Story**: Rapidly generate and validate multi-cloud blueprints via natural language.
- **Persona**: Alex (Cloud Architect)
- **RBAC**: 
  - `Project_Architect` or `Project_Editor` is required to trigger generation and edits.
  - `Viewer` can only view the diagrams.
- **Operational Flow**:
  1. Alex logs into the desktop workspace.
  2. Clicks "New Architecture" and prompts the AI: "Need an AWS e-commerce architecture, Multi-AZ, Aurora, and WAF."
  3. The AI generates a complete draft on the draw.io canvas.
  4. **AI Reset & Manual Adjustment**: If unsatisfied with the overall direction, Alex can click **"Full Reset"** for a complete regeneration. If only the network tier is flawed, he can select the network block and click **"Partial Reset"**. Post-generation, Alex retains the ability to make **manual adjustments** (drag and drop nodes/connections).
  5. The background Agent triggers a Well-Architected validation.
- **System Feedback**:
  - **Success**: A green toast reads "Architecture generated and validated," saving to version control.
  - **Failure**: Conflicting constraints during partial resets trigger red highlights on conflicting nodes.
- **BDD Scenarios**:
  - **Scenario 1: Partial Reset and Manual Tweaking**
    - **Given** Alex is logged in with an AI-generated architecture on the canvas.
    - **When** He dislikes the database design, selects it, clicks "Partial Reset" saying "Use DynamoDB", and manually connects the new node to the API Gateway.
    - **Then** The system keeps the rest of the architecture intact, swaps the DB tier, and successfully re-runs compliance checks.

### B. Cross-Cloud Component Selection
- **Story**: Generate objective and transparent cross-cloud decision matrices.
- **Persona**: Catherine (Technical Decision Maker)
- **RBAC**: 
  - Only `Project_Admin` and `Technical_Lead` can adjust selection weights.
- **Operational Flow**:
  1. Catherine logs into the "Component Selection" module.
  2. Inputs a "High-concurrency NoSQL Database" scenario with SLA-first weights.
  3. AI instantly generates a comparison matrix for AWS, GCP, and Azure.
  4. **AI Reset & Manual Adjustment**: If a metric is missing, she clicks **"Partial Reset"** to "Add Data Egress comparison." She can also **manually toggle** specific cloud providers on or off to customize the report.
- **System Feedback**:
  - **Success**: Interactive charts and a PDF report are generated.
  - **Failure**: Stale API data shows a yellow warning for manual sync.
- **BDD Scenarios**:
  - **Scenario 1: Matrix Manual Override and Reset**
    - **Given** Catherine is reviewing the generated NoSQL matrix.
    - **When** She disagrees with the Firestore data, triggers a "Partial Reset" for that column stating "Update to 2026 SLAs", and manually adds a team-specific annotation.
    - **Then** The system regenerates only the Firestore data, retains her manual note, and exports the final report.

### C. Cost Estimation & FinOps
- **Story**: Calculate precise project-level TCO and track Data Egress.
- **Persona**: David (FinOps Analyst)
- **RBAC**: 
  - Requires `FinOps_Analyst` to view detailed budgets.
- **Operational Flow**:
  1. David imports an architecture into the "FinOps Dashboard."
  2. The AI calculates TCO and simulates Data Egress.
  3. **AI Reset & Manual Adjustment**: If the traffic model is inaccurate, David hits **"Full Reset"** and tells the AI to use a "High-bandwidth streaming model." He also makes a **manual adjustment** to EC2 uptime (e.g., setting it to 8 hours/day).
- **System Feedback**:
  - **Success**: Pie charts refresh dynamically reflecting the savings.
  - **Failure**: Missing pricing APIs are flagged as "Price Unknown."
- **BDD Scenarios**:
  - **Scenario 1: Cost Model Reset and Refinement**
    - **Given** David receives a $5000/month baseline estimate.
    - **When** He uses "Partial Reset" on the database tier's traffic logic and manually overrides network egress from 5TB to 10TB.
    - **Then** The system instantly recalculates the total, tagging his changes as "Manual Override."

### D. IaC Generation & Security Scan (Terraform / OpenTofu)
- **Story**: Seamlessly convert canvas architectures into secure IaC modules.
- **Persona**: Elena (Platform Engineer), Fiona (Security Reviewer)
- **RBAC**: 
  - `Platform_Engineer` generates code; deployment blocked by `Security_Reviewer` checks.
- **Operational Flow**:
  1. Elena clicks "Convert to Terraform Module" in the IaC workspace.
  2. AI generates structured `.tf` files.
  3. **AI Reset & Manual Adjustment**: Unhappy with the naming convention, she selects `variables.tf`, clicks **"Partial Reset"**, and requests "Add corporate prefixes." She then performs **manual code edits** within the IDE.
  4. Saving triggers a background tfsec scan.
- **System Feedback**:
  - **Success**: Scan passes, allowing ZIP download/Git push.
  - **Failure**: High-severity vulnerabilities block export and highlight the code.
- **BDD Scenarios**:
  - **Scenario 1: IaC Code Partial Reset**
    - **Given** Elena reviews the AI-generated Terraform code.
    - **When** She dislikes the S3 module reference, highlights it, clicks "Partial Reset" to "Use internal public module," and manually types in the `tags`.
    - **Then** The system regenerates the S3 block, preserves her tags, and passes the static security scan.

### E. Operations Optimization Review
- **Story**: Apply architecture right-sizing based on background Agent analysis.
- **Persona**: George (Operations Lead)
- **RBAC**: 
  - `Ops_Lead` views and applies optimizations.
- **Operational Flow**:
  1. George reviews Agentic AI right-sizing suggestions in the Dashboard.
  2. **AI Reset & Manual Adjustment**: Finding a suggestion too aggressive, he clicks **"Partial Reset"** instructing the AI to "Leave a 50% buffer for an upcoming campaign." He can also **manually select** the target instance type (e.g., `t3.medium`).
  3. Approves final suggestions to create a Change Request.
- **System Feedback**:
  - **Success**: Change request enters "Pending Scheduled Execution."
  - **Failure**: Termination Protected resources block automated plans.
- **BDD Scenarios**:
  - **Scenario 1: Correcting Ops Recommendations**
    - **Given** George sees an AI recommendation to downsize 5 machines.
    - **When** He manually excludes 2 core-service machines, and requests a "Partial Reset" of the strategy for the remaining 3.
    - **Then** A new change request is generated containing a safe downgrade plan for only the 3 selected machines.

### F. AI Multi-Cloud Operations & Approvals
- **Story**: Manage the Human Approval Gate for high-risk operations.
- **Persona**: Ben (SRE), Karen (Platform Owner)
- **RBAC**: 
  - High-risk actions from `SRE` require `Platform_Owner` approval.
- **Operational Flow**:
  1. Ben uses AI Chat: "Change Prod Web ASG instances to 10."
  2. AI generates the execution Plan and Rollback script.
  3. **AI Reset & Manual Adjustment**: Before submitting, Ben notices the rollback script lacks safety checks. He clicks **"Partial Reset"** to "Add a DB snapshot step," and switches to **manual edit mode** to refine the timeout logic.
  4. Karen reviews and approves via FaceID on her phone.
- **System Feedback**:
  - **Success**: Executed successfully; Audit Logs written.
  - **Failure**: Karen rejects or times out, canceling the operation.
- **BDD Scenarios**:
  - **Scenario 1: High-Risk Script Reset and Approval**
    - **Given** Ben has an AI-generated scaling and rollback script.
    - **When** He manually increases the timeout from 30s to 120s, then submits it. Karen logs in and approves.
    - **Then** The system executes the script using Ben's manually adjusted safety timeout, leaving an immutable audit trail.

### G. Cloud Security Posture
- **Story**: Scan for Least Privilege IAM violations and generate Policy-as-Code.
- **Persona**: Fiona (Security Reviewer)
- **RBAC**: 
  - Only `Security_Admin` initiates global scans.
- **Operational Flow**:
  1. Fiona runs an IAM Least Privilege Analysis.
  2. System lists unused Roles; Fiona asks AI to generate OPA (Rego) policy code.
  3. **AI Reset & Manual Adjustment**: If the policy is too strict, she hits **"Partial Reset"** to "Exclude the Dev environment," or **manually edits** the regex in the code editor.
- **System Feedback**:
  - **Success**: Rego code passes test-validation.
  - **Failure**: Missing MCP auth prompts a red credential error.
- **BDD Scenarios**:
  - **Scenario 1: Policy Code Customization**
    - **Given** Fiona sees 20 lines of AI-generated Rego policy.
    - **When** She notices a flawed condition, highlights it for a "Partial Reset" with specific hints, and manually adds a corporate tag-checking logic.
    - **Then** The OPA tester runs successfully, ensuring both security and developer flexibility.

### H. MCP & Skill Management
- **Story**: Register and enforce access boundaries for internal custom tools.
- **Persona**: Elena (Platform Engineer), Jack (Platform Admin)
- **RBAC**: 
  - `Platform_Engineer` submits requests; `Platform_Admin` audits and approves.
- **Operational Flow**:
  1. Elena registers an internal CMDB API.
  2. AI parses the schema and generates a System Prompt description.
  3. **AI Reset & Manual Adjustment**: If the prompt is inaccurate, Elena clicks **"Full Reset"** for a re-parse, or **manually edits** the text to explicitly instruct future Agents on parameter usage.
  4. Jack reviews and marks it `Read-only`.
- **System Feedback**:
  - **Success**: Tool becomes `Active` for SRE use.
  - **Failure**: Schema errors reject the registration.
- **BDD Scenarios**:
  - **Scenario 1: Refining AI Tool Prompts**
    - **Given** Elena inputs an API URL and AI generates a verbose parameter description.
    - **When** She clicks "Full Reset" asking to "Keep under 50 words," and manually tweaks the notes for required parameters. Jack approves it.
    - **Then** The MCP tool goes live, and subsequent Agents achieve 100% parameter accuracy using the refined description.
