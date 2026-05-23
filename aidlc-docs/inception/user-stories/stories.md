# User Stories - Cloud-360

> 本文件列出 Cloud-360 的使用者故事，嚴格依據 `cloud-360-srs.md` 與 `personas.md`，將架構支柱（Pillars A-H）細分為 3~4 個具體情境（共 24 個 User Stories）。每個故事皆包含使用者需求/目標、多角色協作細節 (Multi-Role Collaboration)、詳細列點的驗收標準、首頁登入操作流程、正負向系統回饋、AI 重置/人工微調機制，以及 BDD 劇本。
> This document lists the user stories for Cloud-360, strictly based on `cloud-360-srs.md` and `personas.md`, breaking down architecture pillars (A-H) into 3-4 specific scenarios each (24 User Stories total). Each story includes user goals, multi-role collaboration details, detailed acceptance criteria, homepage login flows, positive/negative feedback, AI reset/manual adjustments, and BDD scenarios.

## 中文版 (Chinese Version)

### A. 架構設計 (AI-Driven Architecture Design)

#### A1. 自然語言轉架構與草圖產出
- **多角色協作 (Multi-Role Collaboration)**:
  - **參與角色**: Alex (雲端架構師, `Project_Architect`), Ian (開發者, `Developer`)
  - **協作細節**: Alex 負責輸入自然語言產出初始高階架構；Ian (開發者) 可以即時檢視生成的草圖，並透過「留言」或「局部重置」提議加入特定的開發元件（如 Redis 快取），AI 會綜合雙方意見更新圖面。
- **使用者需求/目標 (User Goal)**: 希望透過自然語言快速將業務需求轉換為具體的雲端架構藍圖，節省手動繪圖時間。
- **驗收標準 (Acceptance Criteria)**:
  1. 系統能精準識別自然語言中的特定雲端服務 (如 WAF, Aurora) 與高可用性 (HA) 關鍵字。
  2. 產出的圖表必須為相容 `.drawio` 格式，並使用標準雲端服務圖示。
  3. 圖面必須包含清晰的邏輯連線、網路邊界 (VPC/AZ) 與資料流向。
- **操作流程**: 1. 從首頁登入 Desktop Web，進入專案。 2. 在 AI Chat 輸入架構需求。 3. **AI重置/人工微調**: 對產出草圖不滿意可點「全部重置」，或手動在對話框人工修正參數。
- **系統回饋**: 成功：綠燈並將畫布存檔；失敗：紅字提示資源衝突。
- **BDD**: `Given` Alex 在輸入頁面 `When` 提出需求後點擊全部重置並人工加上 "需 WAF" `Then` 系統重新產出包含 WAF 的架構畫布。

#### A2. AI + draw.io 畫布協同編輯
- **多角色協作 (Multi-Role Collaboration)**:
  - **參與角色**: Alex (雲端架構師, `Project_Architect`), Hannah (工程主管, `Project_Editor`)
  - **協作細節**: Alex 在畫布上調整底層網路層時，Hannah 同時在畫布上框選應用程式層請 AI 優化。兩人可即時看到對方的游標與 AI 生成的變更，避免衝突。
- **使用者需求/目標 (User Goal)**: 透過 AI 協作快速微調架構，避免頻繁手動查閱雲端供應商文檔。
- **驗收標準 (Acceptance Criteria)**:
  1. 允許使用者在畫布上框選特定節點群組，並要求 AI 進行針對性修改。
  2. AI 在替換或新增節點時，必須自動保留或重新接上原有的邏輯連線。
  3. 支援追蹤多人的修改歷史，允許一鍵還原 (Undo) 任何變更。
- **操作流程**: 1. 從首頁進入架構畫布。 2. 框選特定區域請 AI 優化。 3. **AI重置/人工微調**: 點「局部重置」要求更換元件型號，隨後人工拖拉連線。
- **系統回饋**: 成功：元件更新且關聯未斷；失敗：提示該元件無法建立連線。
- **BDD**: `Given` 畫布已有基礎架構 `When` 框選 DB 點擊局部重置為 Aurora 並人工接上 API Gateway `Then` 系統僅替換 DB 並保留人工連線。

#### A3. 自動化 Well-Architected 評核與模擬
- **多角色協作 (Multi-Role Collaboration)**:
  - **參與角色**: Hannah (工程主管, `Project_Editor`), Fiona (資安審查員, `Security_Reviewer`)
  - **協作細節**: Hannah 發起可靠性模擬 (HA/DR)；Fiona 在同一個評核報告中關注安全性 (Security) 支柱。當 AI 產出 SPOF 警告時，Hannah 修復架構，Fiona 則確認修復未引入新的資安風險。
- **使用者需求/目標 (User Goal)**: 確保設計出的架構符合雲端最佳實踐，提前發現並規避潛在風險。
- **驗收標準 (Acceptance Criteria)**:
  1. 系統能自動檢測架構圖是否符合可靠性、安全性等五大最佳實踐支柱。
  2. 能模擬單點故障 (SPOF) 或 AZ 級別中斷，並估算 RPO/RTO 達標率。
  3. 產出可下載之詳細健康度評分與改善建議清單 PDF 報告。
- **操作流程**: 1. 從首頁登入評估儀表板。 2. 點擊「執行架構評估」。 3. **AI重置/人工微調**: 若標準過高，可「局部重置」要求放寬 RTO 條件，或人工加上備援節點。
- **系統回饋**: 成功：產出高分健康度報告；失敗：畫面閃爍紅燈警告 SPOF。
- **BDD**: `Given` 掃出資料庫單點故障 `When` Hannah 人工補上備援連線並點擊局部重置評分 `Then` 分數重新計算並達標。

---

### B. 跨雲選型 (Cross-Cloud Component Selection)

#### B1. AI 驅動單一雲端評選決策
- **多角色協作 (Multi-Role Collaboration)**:
  - **參與角色**: Catherine (技術決策者, `Project_Admin`), David (FinOps 分析師, `FinOps_Analyst`)
  - **協作細節**: Catherine 關注效能與 SLA 權重；David 介入並切換為成本優先權重。雙方在同一個矩陣表上進行不同權重的沙盤推演，並將各自的分析結果整合進決策報告。
- **使用者需求/目標 (User Goal)**: 客觀評估不同雲端供應商，以快速找出最適合專案的雲端平台。
- **驗收標準 (Acceptance Criteria)**:
  1. 支援根據使用者設定的偏好權重自動排序雲端供應商推薦。
  2. 比較矩陣表格必須具備至少三個維度：SLA、硬體限制、計費模式。
  3. 能夠一鍵將對比結果與決策矩陣匯出為 PDF 報告。
- **操作流程**: 1. 從首頁進入選型模組。 2. 輸入專案業務特性。 3. **AI重置/人工微調**: 點擊「全部重置」切換權重，或人工點選隱藏 AWS 以專注看 GCP 與 Azure。
- **系統回饋**: 成功：生成詳細決策矩陣表；失敗：API 逾時顯示黃色警告。
- **BDD**: `Given` 跨雲對比表已生成 `When` 點擊局部重置要求更新 SLA，並人工隱藏 AWS `Then` 系統僅產出剩餘廠商的最新數據。

#### B2. 技術生態與相容性掃描
- **多角色協作 (Multi-Role Collaboration)**:
  - **參與角色**: Alex (雲端架構師, `Project_Architect`), George (運維負責人, `Ops_Lead`)
  - **協作細節**: Alex 匯入開發端的 CI/CD 堆疊；George 匯入維運端的監控工具 (如 Prometheus)。AI 綜合兩者的清單產出跨部門的相容性與移轉工時報告。
- **使用者需求/目標 (User Goal)**: 評估現有技術地端棧遷移至雲端的相容性，以準確預估重構成本。
- **驗收標準 (Acceptance Criteria)**:
  1. 能解析現有地端技術棧，並比對至各雲端對應之託管服務。
  2. 為每一項技術遷移提供精確的相容性分數 (0-100%)。
  3. 提供初步預估的遷移與代碼重構工時 (以天或小時為單位)。
- **操作流程**: 1. 從首頁進入相容性分析室。 2. 匯入現有技術棧。 3. **AI重置/人工微調**: 「局部重置」重新評估特定 DB，並人工標註「必定保留的 CI/CD 工具」。
- **系統回饋**: 成功：列出相容性分數與遷移工時；失敗：提示查無對應託管服務。
- **BDD**: `Given` 獲得初始相容報告 `When` 人工標註 Jenkins 必定保留，並局部重置 `Then` AI 重新評估整合風險並更新報告。

#### B3. 地緣合規與存取延遲優化
- **多角色協作 (Multi-Role Collaboration)**:
  - **參與角色**: Fiona (安全性審查員, `Security_Admin`), Catherine (技術決策者, `Project_Admin`)
  - **協作細節**: Catherine 輸入目標客群所在地以追求最低延遲；Fiona 則加入 GDPR 與當地資料落地法規限制。AI 在兩者的需求中找出交集，若有衝突則提示需取捨。
- **使用者需求/目標 (User Goal)**: 確保應用程式部署的區域符合當地法規，且對目標客群的存取延遲最低。
- **驗收標準 (Acceptance Criteria)**:
  1. 系統內建常見法規資料庫 (如 GDPR、HIPAA) 的資料落地要求與邊界。
  2. 根據目標客群位置，在地圖上直觀提供延遲最低的 Top 3 Region 建議。
  3. 若使用者強行選擇違反法規限制的區域，必須以紅字強烈阻擋並給出原因。
- **操作流程**: 1. 從首頁登入地緣合規設定區。 2. 輸入目標客群所在地。 3. **AI重置/人工微調**: 「全部重置」切換法規情境，並人工加入自定義限制。
- **系統回饋**: 成功：地圖顯示最佳推薦 Region；失敗：提示所選區域不符合指定法規。
- **BDD**: `Given` 系統建議美東機房 `When` Fiona 人工勾選 GDPR 並局部重置 `Then` 系統重新推薦歐盟機房。

---

### C. 成本估算與 FinOps (Cost Estimation & FinOps)

#### C1. 專案 TCO 與流量預算預測
- **多角色協作 (Multi-Role Collaboration)**:
  - **參與角色**: David (FinOps 分析師, `FinOps_Analyst`), Hannah (工程主管, `Project_Editor`)
  - **協作細節**: David 設定每月的預算上限；Hannah 在架構圖上新增機器時，系統會即時通知 David 預算變化，若超支則觸發警告給雙方。
- **使用者需求/目標 (User Goal)**: 精準掌握專案每月的總體擁有成本(TCO)與預算走勢，避免費用超支。
- **驗收標準 (Acceptance Criteria)**:
  1. 能根據架構圖自動擷取資源，並查詢最新雲端報價 API。
  2. 產出細至每項資源層級的動態成本拆解圓餅圖。
  3. 允許使用者輸入「每日運作時數」，系統需即時重新計算每月總費用。
- **操作流程**: 1. 從首頁登入 FinOps 看板。 2. 匯入架構執行 TCO 計算。 3. **AI重置/人工微調**: 「全部重置」切換流量模型，並人工修改預設開機時數為 8 小時。
- **系統回饋**: 成功：動態圓餅圖顯示預算；失敗：特定服務報價失敗顯示「價格未知」。
- **BDD**: `Given` 初始 TCO 為 $5000 `When` David 人工修改開機時數為 8 小時並局部重置 `Then` TCO 更新為 $2000，並標記 Manual Override。

#### C2. 專案資源優化與定價模型對比
- **多角色協作 (Multi-Role Collaboration)**:
  - **參與角色**: David (FinOps 分析師, `FinOps_Analyst`), Ben (SRE, `SRE`)
  - **協作細節**: David 提議將一批機器轉為 Spot 實例以省錢；Ben 收到建議後，負責評估該服務是否為無狀態 (Stateless)，並由 Ben 人工決定「鎖定」不可轉換的核心節點。
- **使用者需求/目標 (User Goal)**: 透過轉換計費模型 (Spot/RI) 最大化節省雲端基礎設施開銷。
- **驗收標準 (Acceptance Criteria)**:
  1. 明確標示出架構中哪些無狀態 (Stateless) 資源適合轉為 Spot 實例。
  2. 精確計算轉換為 1-year/3-year RI 的預期節省百分比。
  3. 允許使用者人工排除特定核心機器，系統需動態重新計算剩餘資源的節省效益。
- **操作流程**: 1. 從首頁進入成本優化區。 2. 要求分析 Spot/RI 效益。 3. **AI重置/人工微調**: 「局部重置」僅看 Spot 實例建議，並人工鎖定某台資料庫拒絕修改。
- **系統回饋**: 成功：列出節省金額百分比；失敗：提示該架構無適用之 Spot 機型。
- **BDD**: `Given` AI 建議全上 Spot `When` David 人工鎖定 DB，並對 Web Tier 局部重置 Spot 效益 `Then` 系統重新算出正確的節省金額。

#### C3. Data Egress 隱性成本深度追蹤
- **多角色協作 (Multi-Role Collaboration)**:
  - **參與角色**: David (FinOps 分析師, `FinOps_Analyst`), Alex (雲端架構師, `Project_Architect`)
  - **協作細節**: David 發現跨 AZ 連線產生高昂 Egress 費用，將熱點標記並 tag Alex。Alex 收到通知後調整架構減少跨區流量，David 即時看到費用下降。
- **使用者需求/目標 (User Goal)**: 追蹤與預測最難以察覺的跨區資料傳輸 (Data Egress) 成本。
- **驗收標準 (Acceptance Criteria)**:
  1. 能夠識別並計算跨 AZ 與跨 Region 的潛在網路傳輸費用。
  2. 產出流量熱點圖 (Heat Map)，直觀標示可能導致高昂費用的連線。
  3. 當使用者變更網路拓撲時，即時更新預估的 Egress 總費用。
- **操作流程**: 1. 從首頁登入網路成本追蹤區。 2. 檢視跨區流量預估。 3. **AI重置/人工微調**: 「局部重置」特定 AZ 流量計算，並人工將傳輸量改為 10TB。
- **系統回饋**: 成功：產出流量熱點與成本對應圖；失敗：架構缺乏網路連線無法解析。
- **BDD**: `Given` Egress 預測為 $100 `When` 局部重置並人工修改頻寬至 10TB `Then` Egress 費用飆升，並以紅字強烈標記。

---

### D. 標準化 IaC 生成與安全交付 (IaC Generation)

#### D1. 模板化 Terraform 代碼自動產出
- **多角色協作 (Multi-Role Collaboration)**:
  - **參與角色**: Elena (平台工程師, `Platform_Engineer`), Ian (開發者, `Developer`)
  - **協作細節**: Elena 負責制定變數與模組 (Modules) 規範；Ian 在撰寫特定服務時生成代碼。系統確保 Ian 產出的代碼自動套用 Elena 設定的企業標籤。
- **使用者需求/目標 (User Goal)**: 自動化產生符合企業標準的 IaC 代碼，消除手動撰寫錯誤。
- **驗收標準 (Acceptance Criteria)**:
  1. 代碼目錄必須嚴格區分 `main.tf`, `variables.tf`, `outputs.tf` 等結構。
  2. 生成的代碼必須盡可能引用企業內部的標準 Terraform Modules。
  3. 產出的代碼可直接通過 `terraform init` 與 `terraform validate` 檢查。
- **操作流程**: 1. 從首頁進入 IaC 工作區。 2. 將畫布轉換為代碼。 3. **AI重置/人工微調**: 對 `variables.tf` 點擊「局部重置」加上公司 prefix，並在 IDE 內人工編輯參數。
- **系統回饋**: 成功：生成標準 tf 結構檔；失敗：編譯出錯阻擋下載。
- **BDD**: `Given` AI 初稿生成完畢 `When` Elena 局部重置 prefix 規則並人工改寫 tag `Then` 代碼順利生成並保留人工修改。

#### D2. IaC 安全與合規自動靜態掃描
- **多角色協作 (Multi-Role Collaboration)**:
  - **參與角色**: Elena (平台工程師, `Platform_Engineer`), Fiona (資安審查員, `Security_Reviewer`)
  - **協作細節**: Elena 提交 IaC 代碼觸發掃描；若掃出漏洞，Fiona 會收到通知，她可以選擇批准風險 (Risk Acceptance) 或要求 AI 提供修復建議讓 Elena 套用。
- **使用者需求/目標 (User Goal)**: 在部署前攔截代碼中的資安弱點與合規性問題。
- **驗收標準 (Acceptance Criteria)**:
  1. 內建整合 tfsec 或 Trivy，在匯出前強制進行背景靜態安全掃描。
  2. 發現 High 或 Critical 漏洞時，必須強制阻擋代碼下載與部署。
  3. 系統必須提供至少一個可直接套用的 AI 修復代碼片段。
- **操作流程**: 1. 從首頁登入安全審查區。 2. 觸發 tfsec 掃描。 3. **AI重置/人工微調**: 「局部重置」要求 AI 提供不同修復建議，人工選擇採納並套用。
- **系統回饋**: 成功：顯示全數通過綠標；失敗：發現漏洞閃爍紅燈阻擋部署。
- **BDD**: `Given` 掃描出 High 級別漏洞 `When` AI 產出三個修復方案，Elena 人工選擇其一並套用 `Then` 複掃通過，允許 Git Push。

#### D3. Sensitive Values 與 Secret Manager 整合
- **多角色協作 (Multi-Role Collaboration)**:
  - **參與角色**: Fiona (資安審查員, `Security_Reviewer`), Ian (開發者, `Developer`)
  - **協作細節**: 系統攔截到 Ian 提交的明文密碼；Fiona 接獲警報，強制要求轉為 Secret 引用。Ian 收到修復工單，透過 AI 一鍵替換為安全的 ARN。
- **使用者需求/目標 (User Goal)**: 確保代碼中絕不包含明文密碼，避免金鑰外洩風險。
- **驗收標準 (Acceptance Criteria)**:
  1. 精準掃描並找出代碼中任何 hardcoded 的明文金鑰、密碼。
  2. 自動將明文替換為對應雲端的安全引用格式 (如 AWS Secrets Manager)。
  3. 若無法提供有效的 Secret ARN，禁止將代碼 Push 至遠端存儲庫。
- **操作流程**: 1. 從首頁登入機密檢查區。 2. 掃描 hardcoded secrets。 3. **AI重置/人工微調**: 「全部重置」要求改用 Secrets 引用，人工填寫 Secret ARN。
- **系統回饋**: 成功：明文轉為安全引用格式；失敗：找不到對應的 Secret 變數。
- **BDD**: `Given` 代碼存在明文密碼 `When` 點擊局部重置轉換為 Secret 引用並人工填上 ARN `Then` 代碼變更為安全合規格式。

---

### E. 維運優化審查 (Proactive Operations Optimization)

#### E1. 基於行為的自動規模調整 (Right-sizing)
- **多角色協作 (Multi-Role Collaboration)**:
  - **參與角色**: George (運維負責人, `Ops_Lead`), Hannah (工程主管, `Engineering_Manager`)
  - **協作細節**: George 收到 5 台機器的降級建議並派發給 Hannah。Hannah 審核業務影響，人工剔除 2 台核心服務，最後 George 執行剩下的 3 台降級指令。
- **使用者需求/目標 (User Goal)**: 根據實際系統負載動態縮減閒置資源，降低成本浪費。
- **驗收標準 (Acceptance Criteria)**:
  1. 連續分析過去 14 天的 CPU/Memory 負載，找出平均使用率過低之機器。
  2. 列出具體建議降級的目標實例型號與預估節省金額。
  3. 支援一鍵生成包含目標機器名單與降級腳本的維運變更單。
- **操作流程**: 1. 從首頁登入運維看板。 2. 查閱 Agent 降級清單。 3. **AI重置/人工微調**: 「局部重置」要求保留 50% 餘裕，人工排除核心機器。
- **系統回饋**: 成功：生成正式變更單；失敗：資源具備防刪除保護跳出警告。
- **BDD**: `Given` 降級 5 台機器的建議 `When` 人工剔除 2 台並要求 AI 局部重置剩餘 3 台 `Then` 變更單僅包含 3 台機器的安全降級。

#### E2. 雲端架構演進與現代化引導
- **多角色協作 (Multi-Role Collaboration)**:
  - **參與角色**: Alex (雲端架構師, `Project_Architect`), Catherine (技術決策者, `Project_Admin`)
  - **協作細節**: Alex 透過 AI 產出移轉至 Serverless 的技術分析；Catherine 專注檢視附帶的 ROI 財務報告。兩者在同一計畫案中進行技術與商業的權衡。
- **使用者需求/目標 (User Goal)**: 探索將傳統 Legacy 架構升級為 Serverless 的可行性與效益。
- **驗收標準 (Acceptance Criteria)**:
  1. 自動識別架構中老舊或維運成本過高的 IaaS 資源。
  2. 提供對應的 PaaS 或 Serverless 替代方案。
  3. 估算移轉所需的 ROI 與潛在的效能提升。
- **操作流程**: 1. 從首頁登入現代化評估區。 2. 分析 Legacy 架構。 3. **AI重置/人工微調**: 「全部重置」改以 Serverless 為主，人工勾選必須保留的 VM。
- **系統回饋**: 成功：產出 Serverless 移轉計畫；失敗：提示無合適替代品。
- **BDD**: `Given` 分析報告建議全上 K8s `When` 全部重置要求改看 Serverless 方案 `Then` AI 重新產出以 Lambda 為主的移轉計畫。

#### E3. 自動化維運劇本 (Runbooks) 生成
- **多角色協作 (Multi-Role Collaboration)**:
  - **參與角色**: Ben (SRE, `SRE`), George (運維負責人, `Ops_Lead`)
  - **協作細節**: Ben 透過 AI 生成資料庫重啟劇本並加入人工 Timeout 設定；生成後發送給 George 進行同行審查 (Peer Review)，確認無誤後標記供自動化調用。
- **使用者需求/目標 (User Goal)**: 確保在系統發生常見故障時，能有標準化腳本快速恢復服務。
- **驗收標準 (Acceptance Criteria)**:
  1. 根據目前架構自動產出常見故障 (如 DB 當機) 的應對劇本。
  2. 輸出格式必須為自動化工具 (如 AWS SSM) 可執行的 YAML/JSON。
  3. 劇本需包含明確的重啟指令、Timeout 與恢復驗證步驟。
- **操作流程**: 1. 從首頁進入 Runbook 庫。 2. 要求生成應對劇本。 3. **AI重置/人工微調**: 「局部重置」要求加入快照步驟，並人工修改 Timeout 數值。
- **系統回饋**: 成功：產出可執行腳本；失敗：指令語法錯誤無法解析。
- **BDD**: `Given` 基礎重啟劇本 `When` 局部重置加入快照，並人工延長 Timeout 至 120s `Then` 劇本按新參數安全儲存。

---

### F. AI 多雲維運與審批 (AI Multi-Cloud Operations)

#### F1. 自然語言跨雲健康狀態查詢
- **多角色協作 (Multi-Role Collaboration)**:
  - **參與角色**: Ben (SRE, `SRE`), Hannah (工程主管, `Engineering_Manager`)
  - **協作細節**: Ben 查詢特定異常流量，並將產出的趨勢圖「釘選」分享給 Hannah。Hannah 點擊連結，能直接在圖表上看到 Ben 的標註與對話上下文。
- **使用者需求/目標 (User Goal)**: 透過自然語言快速掌握多雲環境的即時健康狀態與效能瓶頸。
- **驗收標準 (Acceptance Criteria)**:
  1. 正確解析自然語言中提及的特定雲端資源與確切時間範圍。
  2. 透過 MCP 抓取真實監控數據，繪製準確的時間趨勢圖表。
  3. 自動在圖表上標示出超過正常閾值的效能異常點。
- **操作流程**: 1. 從首頁打開 AI Chat。 2. 詢問「昨日跨雲資料庫延遲狀況」。 3. **AI重置/人工微調**: 「全部重置」改變時間範圍，並人工輸入 Tag 過濾。
- **系統回饋**: 成功：畫出走勢圖並標出異常；失敗：MCP 連線超時報錯。
- **BDD**: `Given` 24h 流量圖 `When` 人工加入 `env:prod` tag 並局部重置 `Then` 圖表重新繪製僅顯示生產環境數據。

#### F2. 引導式變更計畫與回滾策略產出
- **多角色協作 (Multi-Role Collaboration)**:
  - **參與角色**: Ben (SRE, `SRE`), Elena (平台工程師, `Platform_Engineer`)
  - **協作細節**: Ben 產生擴容計畫與回滾腳本；Elena 負責檢視該腳本是否會影響底層 K8s 節點狀態。Elena 人工加入檢查點後，腳本才視為 Ready for Review。
- **使用者需求/目標 (User Goal)**: 安全地執行複雜變更，確保每次維運操作都具備完整的回滾機制。
- **驗收標準 (Acceptance Criteria)**:
  1. 針對擴縮容等指令，產出詳細的變更計畫 (Plan)。
  2. 強制作為包裹產出對應的反向回滾腳本 (Rollback script)。
  3. 送審前，介面允許 SRE 人工覆寫指令或新增安全驗證步驟。
- **操作流程**: 1. 從首頁 AI Chat 發起擴容請求。 2. AI 產出 Plan 與 Rollback。 3. **AI重置/人工微調**: 「局部重置」回滾腳本加入安全檢查，並人工修改擴展上限。
- **系統回饋**: 成功：產生變更包裹等待審批；失敗：指令存在邏輯錯誤被系統擋下。
- **BDD**: `Given` 基礎變更 Plan `When` 人工修改實例數至 10 並局部重置回滾邏輯 `Then` 新包裹包含更新的數字與增強的回滾腳本。

#### F3. 行動端高風險操作審批閘門
- **多角色協作 (Multi-Role Collaboration)**:
  - **參與角色**: Ben (SRE, `SRE`), Karen (平台擁有者, `Platform_Owner`)
  - **協作細節**: Ben 在桌面端送出刪除資料庫指令；Karen 隨即在手機端收到推播。Karen 發現影響太大，在手機端 Reject 並寫下「請改用備份替換」，Ben 即時收到退回理由。
- **使用者需求/目標 (User Goal)**: 讓高階主管能隨時隨地安全地審核高風險的基礎設施操作。
- **驗收標準 (Acceptance Criteria)**:
  1. 審批者能透過行動裝置推播於 Mobile Web 檢視變更影響分析。
  2. 強制要求手機端生物辨識 (如 FaceID) 進行二次授權。
  3. 支援 Reject 功能，並要求填寫退回理由以利後續修改。
- **操作流程**: 1. 手機端收到推播登入。 2. 檢視高風險變更內容。 3. **AI重置/人工微調**: Karen 可選擇 Reject，並人工在退回理由中寫下修改要求讓 Agent 重做。
- **系統回饋**: 成功：FaceID 授權通過並寫入 Audit Log；失敗：審核逾時或被拒，操作取消。
- **BDD**: `Given` 變更單 Pending `When` Karen 人工填寫「需補上離峰時段執行」並 Reject `Then` 變更取消，SRE 收到重置要求。

---

### G. 雲端安全態勢 (Cloud Security Posture)

#### G1. IAM 最小權限合規持續掃描
- **多角色協作 (Multi-Role Collaboration)**:
  - **參與角色**: Fiona (安全性審查員, `Security_Admin`), Ian (開發者, `Developer`)
  - **協作細節**: Fiona 掃描出 Ian 的專案中有過度授權的 Role。系統自動指派修復任務給 Ian；Ian 透過 AI 產出權限縮減建議，Fiona 確認後才予以上線。
- **使用者需求/目標 (User Goal)**: 找出環境中過度授權的 IAM 角色，全面落實最小權限原則。
- **驗收標準 (Acceptance Criteria)**:
  1. 產出超過 90 天未使用的 IAM Role 停用建議名單。
  2. 識別活躍狀態但權限過大 (如 `Action: "*"`) 的帳號。
  3. 允許安全管理員快速標記特例 (Exceptions) 或合規排除。
- **操作流程**: 1. 從首頁進入安全看板。 2. 執行過度授權分析。 3. **AI重置/人工微調**: 「局部重置」排除開發環境的 Role，並人工加註安全標籤。
- **系統回饋**: 成功：列出高危險清單；失敗：缺 IAM 讀取權限中斷。
- **BDD**: `Given` 掃出 100 個 Role `When` Fiona 局部重置僅顯示 Prod 且人工排除 3 個特例 `Then` 報告精簡為 15 個處理對象。

#### G2. 自動化策略代碼 (Policy-as-Code) 生成
- **多角色協作 (Multi-Role Collaboration)**:
  - **參與角色**: Fiona (安全性審查員, `Security_Admin`), Elena (平台工程師, `Platform_Engineer`)
  - **協作細節**: Fiona 用自然語言定義安全規則；AI 轉化為 Rego 代碼後，Elena 負責將代碼整合進 CI/CD Pipeline 中。雙方在 IDE 共同確保策略不誤擋發布。
- **使用者需求/目標 (User Goal)**: 將安全規則轉化為程式碼，以利在 CI/CD 流程中自動執行策略攔截。
- **驗收標準 (Acceptance Criteria)**:
  1. 根據自然語言要求產出語法正確的 OPA (Rego) 或 AWS Config 策略代碼。
  2. 系統內建測試沙盒，確保代碼通過基礎邏輯驗證。
  3. 允許在 IDE 介面內由資安人員人工修改條件式與正則表達式。
- **操作流程**: 1. 要求將安全規則轉為代碼。 2. AI 生成 Rego。 3. **AI重置/人工微調**: 「全部重置」改產出 AWS Config 規則，人工修改正則表達式。
- **系統回饋**: 成功：代碼通過測試；失敗：編譯錯誤。
- **BDD**: `Given` 生成 OPA 策略 `When` Fiona 人工修改正則並點擊測試 `Then` 系統回報測試通過。

#### G3. AI 驅動自動化威脅建模 (STRIDE)
- **多角色協作 (Multi-Role Collaboration)**:
  - **參與角色**: Fiona (安全性審查員, `Security_Reviewer`), Alex (雲端架構師, `Project_Architect`)
  - **協作細節**: Fiona 產出威脅報告，標記出「Spoofing」高風險。Alex 收到標記，在架構圖補上 Auth 節點。Fiona 重新整理報告，確認威脅已受控。
- **使用者需求/目標 (User Goal)**: 在架構設計階段及早發現潛在的資安威脅向量，防患未然。
- **驗收標準 (Acceptance Criteria)**:
  1. 掃描架構圖並對應至 STRIDE 模型的六大威脅分類。
  2. 產出包含威脅等級與具體緩解建議的報告。
  3. 允許使用者人工標註防禦措施，動態移出高危險清單。
- **操作流程**: 1. 匯入架構至威脅建模區。 2. 產生 STRIDE 報告。 3. **AI重置/人工微調**: 「局部重置」聚焦 Spoofing，人工標註已防護節點。
- **系統回饋**: 成功：產出威脅分級報告；失敗：架構圖殘缺無法建模。
- **BDD**: `Given` 10 項中度威脅 `When` 人工標記 2 項已由 WAF 防禦並局部重置 `Then` 該 2 項移出高危險名單。

---

### H. MCP 與 Skill 管理 (MCP & Skill Management)

#### H1. 內部自定義 API 工具註冊與解析
- **多角色協作 (Multi-Role Collaboration)**:
  - **參與角色**: Elena (平台工程師, `Platform_Engineer`), Jack (平台管理員, `Platform_Admin`)
  - **協作細節**: Elena 貼上 API Schema 並透過 AI 縮減 Prompt；提交後，Jack 負責審查該 API 的呼叫頻率與資源消耗，確認無安全疑慮後才核准上架。
- **使用者需求/目標 (User Goal)**: 快速將內部自定義的 API 工具註冊為 AI Agent 可呼叫的 Skills。
- **驗收標準 (Acceptance Criteria)**:
  1. 能正確解析 OpenAPI Schema 或內部 API 規格檔案。
  2. 將 API 參數轉譯為 Agent 能準確理解的 System Prompt。
  3. 註冊前進行自動 Health Check，失敗則拒絕上架。
- **操作流程**: 1. 進入 MCP 目錄。 2. 貼上內部 API 端點。 3. **AI重置/人工微調**: 「全部重置」縮短 Prompt，人工編輯必填欄位備註。
- **系統回饋**: 成功：轉為 Active 上架；失敗：Schema 格式不符。
- **BDD**: `Given` 500 字 Prompt `When` 點擊全部重置精簡並人工補上 `region` 限制 `Then` 成功註冊且解析正確。

#### H2. AI Agent 存取邊界與權限審核
- **多角色協作 (Multi-Role Collaboration)**:
  - **參與角色**: Jack (平台管理員, `Platform_Admin`), Ben (SRE, `SRE`)
  - **協作細節**: Jack 在後台將某危險工具強制設為 `Read-only`。當 Ben 的 Agent 試圖執行該工具的 Write 操作時，Agent 會提示 Ben 該操作已被 Jack 封鎖並留下紀錄。
- **使用者需求/目標 (User Goal)**: 嚴格控管 AI Agent 對各項工具的存取權限，避免越權操作。
- **驗收標準 (Acceptance Criteria)**:
  1. 平台管理員可於介面檢視每個工具的風險等級建議。
  2. 支援強制綁定全域最高權限邊界 (如僅限 Read-only)。
  3. 當 Agent 試圖超越權限呼叫工具時，阻擋並在 Audit Log 留下攔截紀錄。
- **操作流程**: 1. 登入後台審查區。 2. 檢視新註冊 MCP。 3. **AI重置/人工微調**: 「局部重置」要求重新判斷風險，或人工設定為 `Read-only`。
- **系統回饋**: 成功：權限邊界全域生效；失敗：全域政策衝突警告。
- **BDD**: `Given` AI 建議給予 Deploy 權限 `When` Jack 人工強制修改為 Read-only `Then` 所有 Agent 呼叫該工具時失去寫入能力。

#### H3. 桌面端深層作業空間整合與審視
- **多角色協作 (Multi-Role Collaboration)**:
  - **參與角色**: Alex (雲端架構師), David (FinOps 分析師), Fiona (安全性審查員)
  - **協作細節**: 三人共享專案工作區但預設視圖不同。Alex 看到架構圖，David 看成本圖表，Fiona 看漏洞清單。他們可將特定的 Widget 分享至對方的作業空間進行討論。
- **使用者需求/目標 (User Goal)**: 提供可高度客製化的中心化視圖，掌控專案架構、成本與安全全貌。
- **驗收標準 (Acceptance Criteria)**:
  1. 桌面端儀表板支援模塊化 (Widgets) 的自由拖拉與排版。
  2. 跨裝置自動記憶使用者的客製化版面配置。
  3. 提供全域「全部重置」按鈕，一鍵恢復預設四格視圖。
- **操作流程**: 1. 登入 Desktop Web 總覽。 2. 檢視各面板。 3. **AI重置/人工微調**: 人工拖拉變更儀表板排版，「全部重置」還原預設版面。
- **系統回饋**: 成功：記憶客製化版面；失敗：載入逾時。
- **BDD**: `Given` 儀表板被拖拉混亂 `When` Alex 點擊全部重置佈局 `Then` 畫面瞬間恢復乾淨的預設四格視圖。

---

## English Version (Translation)

### A. Architecture Design (AI-Driven Architecture Design)

#### A1. Natural Language to Architecture & Draft Generation
- **Multi-Role Collaboration**:
  - **Roles Involved**: Alex (Cloud Architect, `Project_Architect`), Ian (Developer, `Developer`)
  - **Collaboration Details**: Alex inputs requirements to generate the base architecture; Ian views it and uses comments or "Partial Reset" to propose adding Dev components (e.g., Redis). AI merges both inputs.
- **User Goal**: Rapidly convert business requirements into concrete cloud architecture blueprints via natural language to save manual drawing time.
- **Acceptance Criteria**:
  1. Accurately identifies specific cloud services (e.g., WAF, Aurora) and High Availability (HA) keywords from natural language.
  2. Outputs compatible `.drawio` format diagrams using standard cloud service icons.
  3. The canvas must include clear logical connections, network boundaries (VPC/AZ), and data flow directions.
- **Operational Flow**: 1. Log into Desktop Web. 2. Input needs in AI Chat. 3. **AI Reset/Manual Adjust**: Click "Full Reset" if dissatisfied, or manually type corrections in the chat.
- **System Feedback**: Success: Green light, auto-save canvas; Failure: Red text for resource conflict.
- **BDD**: `Given` Alex is typing `When` he requests a canvas, resets it, and manually adds "needs WAF" `Then` AI renders a new architecture including a WAF.

#### A2. AI + draw.io Collaborative Editing
- **Multi-Role Collaboration**:
  - **Roles Involved**: Alex (Cloud Architect, `Project_Architect`), Hannah (Engineering Manager, `Project_Editor`)
  - **Collaboration Details**: While Alex adjusts network layers manually, Hannah selects app tiers for AI optimization. Both see real-time cursor and AI changes to prevent conflicts.
- **User Goal**: Fine-tune architectures rapidly via AI collaboration, avoiding constant manual reference to cloud provider documentation.
- **Acceptance Criteria**:
  1. Allows users to box-select specific node groups on the canvas and request targeted AI modifications.
  2. The AI must preserve or automatically reconnect existing logical links when replacing or adding nodes.
  3. Supports tracking AI modification history, allowing users to 1-click Undo any changes.
- **Operational Flow**: 1. Open canvas from homepage. 2. Box select areas for AI tuning. 3. **AI Reset/Manual Adjust**: "Partial Reset" a node to swap models, then manually drag lines.
- **System Feedback**: Success: Node swapped without breaking links; Failure: Warns if connection is impossible.
- **BDD**: `Given` A base architecture exists `When` DB is partially reset to Aurora and manually linked to Gateway `Then` System only swaps the DB, keeping manual links.

#### A3. Automated Well-Architected Review & Simulation
- **Multi-Role Collaboration**:
  - **Roles Involved**: Hannah (Engineering Manager, `Project_Editor`), Fiona (Security Reviewer, `Security_Reviewer`)
  - **Collaboration Details**: Hannah triggers HA/DR simulations; Fiona monitors the Security pillar in the same report. When SPOFs are flagged, Hannah fixes the design while Fiona ensures no new security flaws emerge.
- **User Goal**: Ensure architectures comply with cloud best practices and preemptively identify potential risks.
- **Acceptance Criteria**:
  1. Automatically assesses if the diagram complies with the 5 pillars of cloud best practices (Reliability, Security, etc.).
  2. Simulates Single Point of Failure (SPOF) or AZ-level outages and estimates RPO/RTO achievement rates.
  3. Outputs a downloadable, detailed health score and remediation checklist PDF report.
- **Operational Flow**: 1. Access Assessment Dashboard. 2. Trigger architecture scan. 3. **AI Reset/Manual Adjust**: "Partial Reset" to relax RTO metrics, or manually drop in a backup node.
- **System Feedback**: Success: High-score health report; Failure: Flashing red SPOF warning.
- **BDD**: `Given` A SPOF is detected `When` Hannah manually adds a backup node and clicks partial reset `Then` The score recalculates and passes.

---

### B. Cross-Cloud Component Selection

#### B1. AI-Driven Single Cloud Selection
- **Multi-Role Collaboration**:
  - **Roles Involved**: Catherine (Tech Decision Maker, `Project_Admin`), David (FinOps Analyst, `FinOps_Analyst`)
  - **Collaboration Details**: Catherine focuses on SLA weights; David steps in to toggle cost-first weights. Both run simulations on the same matrix and combine their findings into one decision report.
- **User Goal**: Objectively evaluate different cloud providers to find the optimal fit for the project.
- **Acceptance Criteria**:
  1. Ranks cloud provider recommendations automatically based on user-defined weights (e.g., cost vs. performance).
  2. The comparison matrix must evaluate at least 3 dimensions: SLAs, hardware limits, and billing models.
  3. Allows 1-click export of the decision matrix into an easily shareable PDF report.
- **Operational Flow**: 1. Access Selection Module. 2. Input workload traits. 3. **AI Reset/Manual Adjust**: "Full Reset" to switch to cost-first weight, or manually hide AWS.
- **System Feedback**: Success: Detailed matrix table; Failure: Yellow API timeout warning.
- **BDD**: `Given` A generated matrix `When` Catherine partially resets to update SLAs and manually hides AWS `Then` The system updates data for remaining vendors.

#### B2. Tech Ecosystem Compatibility Scan
- **Multi-Role Collaboration**:
  - **Roles Involved**: Alex (Cloud Architect, `Project_Architect`), George (Ops Lead, `Ops_Lead`)
  - **Collaboration Details**: Alex imports CI/CD stacks; George imports Ops monitoring tools. AI aggregates both to generate a cross-departmental compatibility and migration hours report.
- **User Goal**: Evaluate the compatibility of existing on-prem tech stacks migrating to the cloud to accurately estimate refactoring costs.
- **Acceptance Criteria**:
  1. Parses the current on-prem tech stack and maps them to managed cloud equivalents.
  2. Provides an exact compatibility score (0-100%) for each technology migration.
  3. Offers preliminary estimates for migration and code-refactoring effort.
- **Operational Flow**: 1. Access Compatibility Room. 2. Import on-prem stack. 3. **AI Reset/Manual Adjust**: "Partial Reset" for a specific DB, manually tag "Must keep CI/CD tools."
- **System Feedback**: Success: Lists migration hours; Failure: No managed service found.
- **BDD**: `Given` An initial report `When` Jenkins is manually tagged as mandatory and reset `Then` AI reassesses integration risks.

#### B3. Latency Optimization & Geo-Compliance
- **Multi-Role Collaboration**:
  - **Roles Involved**: Fiona (Security Admin, `Security_Admin`), Catherine (Tech Decision Maker, `Project_Admin`)
  - **Collaboration Details**: Catherine aims for lowest latency by inputting target locations; Fiona enforces GDPR restrictions. AI finds the optimal overlap and highlights any necessary trade-offs.
- **User Goal**: Ensure app deployment regions comply with local laws while minimizing access latency for the target audience.
- **Acceptance Criteria**:
  1. Built-in database of data residency requirements for common regulations (e.g., GDPR, HIPAA).
  2. Visually recommends the Top 3 lowest-latency Regions on a map.
  3. Strongly blocks users with red text if they select a Region violating chosen regulations.
- **Operational Flow**: 1. Enter Geo-compliance setup. 2. Input target audience location. 3. **AI Reset/Manual Adjust**: "Full Reset" to change regulations, manually inject custom GDPR rules.
- **System Feedback**: Success: Map highlights best Region; Failure: Warns if Region is non-compliant.
- **BDD**: `Given` US-East is recommended `When` Fiona manually checks GDPR and clicks partial reset `Then` System recommends EU data centers.

---

### C. Cost Estimation & FinOps

#### C1. Project TCO & Egress Forecasting
- **Multi-Role Collaboration**:
  - **Roles Involved**: David (FinOps Analyst, `FinOps_Analyst`), Hannah (Engineering Manager, `Project_Editor`)
  - **Collaboration Details**: David sets the monthly budget cap; when Hannah adds VMs to the canvas, the system alerts David of the cost delta, warning both if it exceeds the budget.
- **User Goal**: Accurately track monthly Total Cost of Ownership (TCO) and budget trends to prevent cost overruns.
- **Acceptance Criteria**:
  1. Automatically extracts all compute/storage resources and queries the latest pricing APIs.
  2. Outputs dynamic cost breakdown pie charts detailed to the individual resource level.
  3. Instantly recalculates total monthly cost when the user modifies "daily operational hours".
- **Operational Flow**: 1. Access FinOps Dashboard. 2. Import diagram. 3. **AI Reset/Manual Adjust**: "Full Reset" to high-bandwidth model, manually edit uptime.
- **System Feedback**: Success: Dynamic pie chart; Failure: Unknown prices grayed out.
- **BDD**: `Given` Initial TCO is $5000 `When` David manually edits uptime to 8h and partially resets `Then` TCO drops to $2000, tagged "Manual Override".

#### C2. Resource Optimization & Pricing Model Comparison
- **Multi-Role Collaboration**:
  - **Roles Involved**: David (FinOps Analyst, `FinOps_Analyst`), Ben (SRE, `SRE`)
  - **Collaboration Details**: David proposes converting instances to Spot to save money; Ben evaluates if they are stateless, manually locking core DB nodes to On-Demand before proceeding.
- **User Goal**: Maximize infrastructure savings by transitioning to optimal pricing models (Spot/RI).
- **Acceptance Criteria**:
  1. Clearly flags stateless resources suitable for Spot instances.
  2. Calculates expected savings percentages for converting to 1/3-year RIs.
  3. Allows users to manually exclude core machines, dynamically recalculating savings for the rest.
- **Operational Flow**: 1. Open Cost Optimizer. 2. Request Spot analysis. 3. **AI Reset/Manual Adjust**: "Partial Reset" to view Spot options, manually lock a DB.
- **System Feedback**: Success: Shows savings %; Failure: No applicable Spot instances.
- **BDD**: `Given` AI suggests 100% Spot `When` David manually locks the DB and partially resets `Then` System calculates savings strictly for unlocked tiers.

#### C3. Hidden Cost (Data Egress) Deep Dive
- **Multi-Role Collaboration**:
  - **Roles Involved**: David (FinOps Analyst, `FinOps_Analyst`), Alex (Cloud Architect, `Project_Architect`)
  - **Collaboration Details**: David notices huge egress costs on a cross-AZ link, tagging Alex. Alex adjusts the architecture to localize traffic, and David immediately sees the cost drop.
- **User Goal**: Track and forecast the often-overlooked costs of cross-region Data Egress.
- **Acceptance Criteria**:
  1. Identifies and calculates potential network transfer fees across AZs and Regions.
  2. Outputs traffic heat maps visually flagging expensive connections (e.g., DB syncs).
  3. Instantly updates estimated Egress fees when the topology is altered on the canvas.
- **Operational Flow**: 1. Open Network Tracker. 2. Review egress. 3. **AI Reset/Manual Adjust**: "Partial Reset" an AZ route, manually change volume to 10TB.
- **System Feedback**: Success: Egress heat map; Failure: Cannot parse network without connections.
- **BDD**: `Given` $100 Egress forecast `When` Partially reset and manually bumped to 10TB `Then` Egress costs spike in red.

---

### D. Standardized IaC Generation & Secure Delivery

#### D1. Templated Terraform Generation
- **Multi-Role Collaboration**:
  - **Roles Involved**: Elena (Platform Engineer, `Platform_Engineer`), Ian (Developer, `Developer`)
  - **Collaboration Details**: Elena enforces module/tagging standards; when Ian generates code for his services, the system ensures Elena's enterprise tags are automatically applied.
- **User Goal**: Automate the creation of enterprise-standard IaC code to eliminate manual coding errors.
- **Acceptance Criteria**:
  1. Exported code directories strictly separate `main.tf`, `variables.tf`, `outputs.tf`.
  2. Generated code must maximize reuse of internal standard Terraform Modules.
  3. Output code must pass basic `terraform init/validate` checks out-of-the-box.
- **Operational Flow**: 1. Access IaC Workspace. 2. Convert canvas to code. 3. **AI Reset/Manual Adjust**: "Partial Reset" variables to add prefixes, manually edit tags.
- **System Feedback**: Success: Generates standard `.tf` files; Failure: Syntax compilation block.
- **BDD**: `Given` AI draft generated `When` Elena partially resets prefixes and manually edits tags `Then` Code compiles preserving her changes.

#### D2. Automated Static Security Scan
- **Multi-Role Collaboration**:
  - **Roles Involved**: Elena (Platform Engineer, `Platform_Engineer`), Fiona (Security Reviewer, `Security_Reviewer`)
  - **Collaboration Details**: Elena triggers a scan; Fiona receives a ping for any vulnerabilities. Fiona can accept the risk or ask AI for fix snippets, which Elena then applies.
- **User Goal**: Intercept security vulnerabilities and compliance issues in the code before deployment.
- **Acceptance Criteria**:
  1. Natively integrates tfsec/Trivy to force static scans before export.
  2. Forcibly blocks code download/deployment when High vulnerabilities are detected.
  3. Provides directly applicable AI-remediation code snippets for found vulnerabilities.
- **Operational Flow**: 1. Enter Security Review. 2. Trigger tfsec scan. 3. **AI Reset/Manual Adjust**: "Partial Reset" for alternative fix suggestions, manually apply one.
- **System Feedback**: Success: Green pass mark; Failure: Red flash blocks deployment.
- **BDD**: `Given` High-severity bug found `When` AI suggests fixes and Elena manually applies one `Then` Rescan passes, Git Push unlocked.

#### D3. Sensitive Values & Secret Manager Check
- **Multi-Role Collaboration**:
  - **Roles Involved**: Fiona (Security Reviewer, `Security_Reviewer`), Ian (Developer, `Developer`)
  - **Collaboration Details**: System detects Ian's hardcoded password. Fiona mandates a Secret conversion. Ian uses AI to 1-click replace it with a secure AWS ARN before committing.
- **User Goal**: Ensure code never contains plaintext passwords, preventing credential leaks.
- **Acceptance Criteria**:
  1. Scans and highlights hardcoded plaintext keys/passwords.
  2. Forcibly replaces plaintext with secure references (e.g., AWS Secrets Manager ARNs).
  3. Prohibits pushing code to remote repos without valid Secret ARN mappings.
- **Operational Flow**: 1. Open Secret Scanner. 2. Scan for hardcoded keys. 3. **AI Reset/Manual Adjust**: "Full Reset" to force AWS Secrets format, manually input ARN.
- **System Feedback**: Success: Plaintext securely converted; Failure: Missing secret mapping.
- **BDD**: `Given` Hardcoded password exists `When` Partially reset to Secret Ref and manually filled ARN `Then` Code updates to a secure format.

---

### E. Proactive Operations Optimization

#### E1. Behavior-Based Right-Sizing
- **Multi-Role Collaboration**:
  - **Roles Involved**: George (Ops Lead, `Ops_Lead`), Hannah (Engineering Manager, `Engineering_Manager`)
  - **Collaboration Details**: George receives 5 downsize suggestions and assigns them to Hannah. Hannah evaluates business impact, excludes 2 core DBs, and George executes the remaining 3.
- **User Goal**: Dynamically downsize idle resources based on actual system load to reduce wasteful spending.
- **Acceptance Criteria**:
  1. Analyzes CPU/Memory loads over 14 days to pinpoint machines with sub-10% utilization.
  2. Lists specific target instance types for downgrading and estimates monthly savings.
  3. Supports 1-click generation of formal Change Requests with downsize scripts.
- **Operational Flow**: 1. Open Ops Dashboard. 2. Check downsize lists. 3. **AI Reset/Manual Adjust**: "Partial Reset" to demand 50% buffer, manually exclude core machines.
- **System Feedback**: Success: Change Request created; Failure: Termination protection warning.
- **BDD**: `Given` 5 machines flagged `When` Manually excluding 2 and partially resetting the rest `Then` CR created for 3 machines safely.

#### E2. Architecture Modernization Guidance
- **Multi-Role Collaboration**:
  - **Roles Involved**: Alex (Cloud Architect, `Project_Architect`), Catherine (Tech Decision Maker, `Project_Admin`)
  - **Collaboration Details**: Alex generates a technical Serverless migration plan; Catherine focuses on the attached ROI report. Both weigh technical vs. commercial benefits simultaneously.
- **User Goal**: Explore the feasibility and benefits of upgrading traditional Legacy architectures to Serverless.
- **Acceptance Criteria**:
  1. Flags outdated or high-maintenance IaaS resources (e.g., DB VMs).
  2. Provides managed PaaS or Serverless (e.g., AWS Lambda) technical alternatives.
  3. Estimates the Return on Investment (ROI) and potential performance gains.
- **Operational Flow**: 1. Access Modernization Evaluator. 2. Analyze Legacy setup. 3. **AI Reset/Manual Adjust**: "Full Reset" to prefer Serverless, manually check VMs that must remain.
- **System Feedback**: Success: Serverless ROI plan; Failure: No Serverless alternative available.
- **BDD**: `Given` Plan suggests K8s `When` Fully reset to demand Serverless `Then` AI outputs a Lambda-centric migration plan.

#### E3. Automated Runbooks Generation
- **Multi-Role Collaboration**:
  - **Roles Involved**: Ben (SRE, `SRE`), George (Ops Lead, `Ops_Lead`)
  - **Collaboration Details**: Ben generates a DB restart playbook and edits timeouts; sends it to George for Peer Review. George approves it, marking it Active for automation tools.
- **User Goal**: Ensure standardized scripts are ready to quickly restore service during common system failures.
- **Acceptance Criteria**:
  1. Auto-generates playbooks for common failures based on the current architecture.
  2. Outputs scripts in YAML/JSON directly executable by automation tools.
  3. Includes explicit restart commands, timeout parameters, and health validation steps.
- **Operational Flow**: 1. Open Runbook Library. 2. Generate DB crash playbook. 3. **AI Reset/Manual Adjust**: "Partial Reset" to inject snapshot step, manually adjust Timeouts.
- **System Feedback**: Success: Executable YAML generated; Failure: Parse error on invalid syntax.
- **BDD**: `Given` Basic restart script generated `When` Ben partially resets to add snapshot and manually sets Timeout to 120s `Then` Playbook saved securely.

---

### F. AI Multi-Cloud Operations & Approvals

#### F1. Natural Language Multi-Cloud Health Query
- **Multi-Role Collaboration**:
  - **Roles Involved**: Ben (SRE, `SRE`), Hannah (Engineering Manager, `Engineering_Manager`)
  - **Collaboration Details**: Ben queries anomaly data, pins the trend chart, and shares it with Hannah. Hannah clicks the link to view Ben's annotations and the full chat context instantly.
- **User Goal**: Rapidly grasp real-time health and performance bottlenecks across multi-cloud environments using natural language.
- **Acceptance Criteria**:
  1. Correctly parses natural language for specific cloud resources and exact timeframes.
  2. Fetches real telemetry data via internal MCPs and renders accurate time-trend charts.
  3. Automatically flags anomalous performance spikes directly on the chart.
- **Operational Flow**: 1. Open AI Chat. 2. Ask "Yesterday's cross-cloud DB latency". 3. **AI Reset/Manual Adjust**: "Full Reset" to change timeframe to 1 week, manually append a tag filter.
- **System Feedback**: Success: Trend chart highlights anomalies; Failure: MCP timeout error.
- **BDD**: `Given` 24h chart generated `When` Ben manually adds `env:prod` tag and partially resets `Then` Chart filters to production data only.

#### F2. Guided Change Plan & Rollback Generation
- **Multi-Role Collaboration**:
  - **Roles Involved**: Ben (SRE, `SRE`), Elena (Platform Engineer, `Platform_Engineer`)
  - **Collaboration Details**: Ben creates a scaling plan/rollback. Elena reviews its impact on K8s nodes, manually injecting node-health checks before marking it Ready for Review.
- **User Goal**: Safely execute complex changes by ensuring every operation includes a comprehensive rollback mechanism.
- **Acceptance Criteria**:
  1. Generates detailed Change Plans for commands like scaling or updates.
  2. Mandates the output of a paired reverse Rollback script.
  3. Allows SREs to manually overwrite commands or inject security validation steps.
- **Operational Flow**: 1. Request scaling via AI Chat. 2. AI generates Plan & Rollback. 3. **AI Reset/Manual Adjust**: "Partial Reset" rollback script for safety checks, manually edit max capacity.
- **System Feedback**: Success: Change package ready; Failure: Logic error blocks plan.
- **BDD**: `Given` Base Plan generated `When` Ben manually sets instances to 10 and partially resets rollback logic `Then` New package has updated numbers and safer rollback.

#### F3. Mobile Approval Gate for High-Risk Actions
- **Multi-Role Collaboration**:
  - **Roles Involved**: Ben (SRE, `SRE`), Karen (Platform Owner, `Platform_Owner`)
  - **Collaboration Details**: Ben submits a DB delete command. Karen receives a mobile push, Rejects it, and types "Use a backup swap instead." Ben instantly receives the rejection reason.
- **User Goal**: Enable executives to securely review and authorize high-risk infrastructure changes anytime, anywhere.
- **Acceptance Criteria**:
  1. Sends push notifications to mobile devices displaying clear impact analysis.
  2. Mandates secondary biometric authorization (FaceID/Fingerprint) on mobile to approve.
  3. Supports a Reject function requiring a typed reason to aid subsequent revisions.
- **Operational Flow**: 1. Receives push, logs into Mobile Web. 2. Reviews high-risk change. 3. **AI Reset/Manual Adjust**: Manually Rejects and types a reason, forcing the Agent to redo the plan.
- **System Feedback**: Success: FaceID passes, Audit logged; Failure: Timeout/Rejected cancels action.
- **BDD**: `Given` CR is Pending `When` Karen manually types "Do this off-hours" and Rejects `Then` CR cancels, returning feedback to SRE.

---

### G. Cloud Security Posture

#### G1. IAM Least Privilege Continuous Scan
- **Multi-Role Collaboration**:
  - **Roles Involved**: Fiona (Security Admin, `Security_Admin`), Ian (Developer, `Developer`)
  - **Collaboration Details**: Fiona scans Ian's over-permissive project roles. System assigns a fix task to Ian, who uses AI to suggest reduced scopes. Fiona confirms and deploys the fix.
- **User Goal**: Identify over-permissive IAM roles to enforce the Principle of Least Privilege across the environment.
- **Acceptance Criteria**:
  1. Outputs a definitive list of IAM Roles unused for over 90 days.
  2. Identifies active accounts/services possessing overly broad permissions (e.g., `Action: "*"`).
  3. Allows security admins to quickly flag Exceptions or perform compliance exclusions.
- **Operational Flow**: 1. Open Security Dashboard. 2. Run over-permission analysis. 3. **AI Reset/Manual Adjust**: "Partial Reset" to exclude Dev, manually add security tags.
- **System Feedback**: Success: High-risk list displayed; Failure: Missing IAM read rights.
- **BDD**: `Given` 100 Roles flagged `When` Fiona partially resets to show only Prod and manually excludes 3 `Then` Report shrinks to 15 actionable items.

#### G2. Automated Policy-as-Code Generation
- **Multi-Role Collaboration**:
  - **Roles Involved**: Fiona (Security Admin, `Security_Admin`), Elena (Platform Engineer, `Platform_Engineer`)
  - **Collaboration Details**: Fiona defines rules in natural language; AI converts them to Rego. Elena integrates the Rego into the CI/CD pipeline, collaborating in the IDE to ensure no false blocks.
- **User Goal**: Translate security rules into executable code to automate policy enforcement within the CI/CD pipeline.
- **Acceptance Criteria**:
  1. Translates natural language security requirements into syntactically correct Rego/AWS Config code.
  2. Features a built-in test sandbox ensuring generated code passes basic logic validation.
  3. Integrates an IDE interface allowing manual edits of conditions and regex patterns.
- **Operational Flow**: 1. Ask AI to convert rules to Code. 2. AI generates Rego. 3. **AI Reset/Manual Adjust**: "Full Reset" to request AWS Config, manually edit regex in IDE.
- **System Feedback**: Success: Passes built-in tester; Failure: Syntax compilation errors.
- **BDD**: `Given` AI-generated OPA policy `When` Fiona manually edits the regex condition and tests `Then` Tester reports success.

#### G3. AI-Driven Threat Modeling (STRIDE)
- **Multi-Role Collaboration**:
  - **Roles Involved**: Fiona (Security Reviewer, `Security_Reviewer`), Alex (Cloud Architect, `Project_Architect`)
  - **Collaboration Details**: Fiona's report flags "Spoofing." Alex receives the ping, adds a WAF/Auth node on the canvas. Fiona refreshes the report, confirming the threat is now Mitigated.
- **User Goal**: Preemptively identify potential security threat vectors during the architecture design phase.
- **Acceptance Criteria**:
  1. Scans architecture components mapping them against the 6 threat categories of the STRIDE model.
  2. Outputs a report containing threat tiers (High/Medium/Low) and mitigation suggestions.
  3. Allows users to manually mark nodes as protected, dynamically removing them from the high-risk list.
- **Operational Flow**: 1. Import diagram to Threat Modeler. 2. Generate STRIDE report. 3. **AI Reset/Manual Adjust**: "Partial Reset" to focus on Spoofing, manually mark nodes as protected.
- **System Feedback**: Success: Professional threat tier report; Failure: Incomplete diagram prevents modeling.
- **BDD**: `Given` 10 medium threats found `When` Fiona manually marks 2 as WAF-protected and partially resets `Then` The 2 items drop off the risk list.

---

### H. MCP & Skill Management

#### H1. Internal Custom API Tool Registration
- **Multi-Role Collaboration**:
  - **Roles Involved**: Elena (Platform Engineer, `Platform_Engineer`), Jack (Platform Admin, `Platform_Admin`)
  - **Collaboration Details**: Elena inputs the API schema and shortens the Prompt via AI. Jack reviews the API's rate limits and security scope before officially approving it for Agent use.
- **User Goal**: Rapidly register internal custom API tools as viable Skills callable by the AI Agent.
- **Acceptance Criteria**:
  1. Correctly parses standard OpenAPI Schemas or internal API specification files.
  2. Translates API parameters into a System Prompt that Agents comprehend with 100% accuracy.
  3. Performs automated Health Checks before registration; rejects if connections fail.
- **Operational Flow**: 1. Enter MCP Catalog. 2. Paste API endpoint. 3. **AI Reset/Manual Adjust**: "Full Reset" to shrink verbose Prompt, manually edit required param notes.
- **System Feedback**: Success: Goes Active; Failure: Schema mismatch rejection.
- **BDD**: `Given` 500-word prompt generated `When` Elena fully resets for brevity and manually adds a `region` requirement `Then` Tool goes live successfully.

#### H2. Agent Access Boundaries & Review
- **Multi-Role Collaboration**:
  - **Roles Involved**: Jack (Platform Admin, `Platform_Admin`), Ben (SRE, `SRE`)
  - **Collaboration Details**: Jack forces a dangerous tool to `Read-only`. When Ben attempts to use his Agent for a Write operation on that tool, the Agent blocks Ben and logs the interception.
- **User Goal**: Strictly govern AI Agent access permissions to various tools, preventing unauthorized or destructive actions.
- **Acceptance Criteria**:
  1. Allows Platform Admins to view risk level recommendations (High/Low) for every tool.
  2. Enforces global maximum permission boundaries, ensuring Agents cannot perform high-risk actions.
  3. Intercepts and logs an Audit record whenever an Agent attempts to invoke a tool beyond its boundary.
- **Operational Flow**: 1. Open Admin console. 2. Review new MCP tool. 3. **AI Reset/Manual Adjust**: "Partial Reset" asking AI to re-evaluate risk, or manually force it to `Read-only`.
- **System Feedback**: Success: Boundary enforces globally; Failure: Global policy conflict warning.
- **BDD**: `Given` AI suggests Deploy rights `When` Jack manually forces `Read-only` `Then` All Agents lose write access when calling this tool.

#### H3. Desktop Deep Workspace Experience
- **Multi-Role Collaboration**:
  - **Roles Involved**: Alex (Cloud Architect), David (FinOps Analyst), Fiona (Security Reviewer)
  - **Collaboration Details**: The trio shares a single project workspace but have distinct default widgets. They can seamlessly share specific widgets (like a cost spike chart) to each other's views for discussion.
- **User Goal**: Provide a highly customizable centralized view to command the project's architecture, cost, and security landscape.
- **Acceptance Criteria**:
  1. Desktop dashboard supports free-form drag-and-drop layout structuring of modular widgets.
  2. System automatically remembers and synchronizes customized layout configurations across devices.
  3. Provides a global "Full Reset" button to instantly restore the default 4-grid view.
- **Operational Flow**: 1. Log into Desktop Web overview. 2. View Cost/Sec/Arch panels. 3. **AI Reset/Manual Adjust**: Manually drag to rearrange widgets, "Full Reset" to restore default layout.
- **System Feedback**: Success: Saves custom view; Failure: Layout timeout.
- **BDD**: `Given` A messy dashboard `When` Alex clicks Full Reset layout `Then` Screen instantly snaps back to the clean default 4-grid view.
