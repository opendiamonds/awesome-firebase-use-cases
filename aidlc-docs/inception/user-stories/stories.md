# User Stories - Cloud-360

> 本文件列出 Cloud-360 的使用者故事，嚴格依據 `cloud-360-srs.md` 與 `personas.md`，將架構支柱（Pillars A-H）細分為 3~4 個具體情境（共 24 個 User Stories）。每個故事皆包含使用者需求/目標、多角色協作細節、詳細列點的驗收標準、首頁登入操作流程、正負向系統畫面回饋與引導、AI 重置/人工微調機制，以及 BDD 劇本。
> This document lists the user stories for Cloud-360, strictly based on `cloud-360-srs.md` and `personas.md`, breaking down architecture pillars (A-H) into 3-4 specific scenarios each (24 User Stories total). Each story includes user goals, multi-role collaboration details, detailed acceptance criteria, homepage login flows, highly detailed positive/negative UI feedback with Call-To-Actions, AI reset mechanisms, and BDD scenarios.

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
- **系統回饋 (System Feedback)**:
  - **成功 (Success)**: 畫面中央浮現綠色 Toast 提示「✔ 架構草圖已生成」，並自動存檔。**後續引導**：彈出按鈕引導點擊「前往 IaC 工作區生成代碼」或「進行 Well-Architected 評估」。
  - **失敗 (Failure)**: 畫面頂部跳出紅色警告框「資源衝突：所選區域不支援該服務」。**後續引導**：提示「請於對話框修改參數後重試」，或提供「聯絡平台架構師 (Alex) 尋求協助」的快捷按鈕。
- **BDD**: `Given` Alex 在輸入頁面 `When` 提出需求後點擊全部重置並人工加上 "需 WAF" `Then` 系統重新產出包含 WAF 的架構畫布。

#### A2. AI + draw.io 畫布協同編輯
- **多角色協作 (Multi-Role Collaboration)**:
  - **參與角色**: Alex (雲端架構師, `Project_Architect`), Hannah (工程主管, `Project_Editor`)
  - **協作細節**: Alex 在畫布上調整底層網路層時，Hannah 同時在畫布上框選應用程式層請 AI 優化。兩人可即時看到對方的游標與 AI 生成的變更，避免衝突。
- **使用者需求/目標 (User Goal)**: 透過 AI 協作快速微調架構，避免頻繁手動查閱雲端供應商文檔，並將編輯結果與個人帳號綁定，確保下次登入時能無縫接續編輯。
- **驗收標準 (Acceptance Criteria)**:
  1. 允許使用者在畫布上框選特定節點群組，並要求 AI 進行針對性修改。
  2. AI 在替換或新增節點時，必須自動保留或重新接上原有的邏輯連線。
  3. 支援追蹤多人的修改歷史，允許一鍵還原 (Undo) 任何變更。
  4. 提供「儲存架構圖」功能，將畫布 XML 寫入資料庫，並於下次進入工作區時自動載入最新草稿。
- **操作流程**: 1. 從首頁進入架構畫布（系統自動載入歷史草稿）。 2. 框選特定區域請 AI 優化。 3. 點擊右上角「儲存架構圖」將結果同步至資料庫。
- **系統回饋 (System Feedback)**:
  - **成功 (Success)**: 點擊儲存後出現綠色 Toast 提示「架構圖儲存成功」。**後續引導**：出現懸浮按鈕引導「匯出架構圖」或「查看預估成本」。
  - **失敗 (Failure)**: 儲存失敗或節點元件不相容時出現錯誤提示。**後續引導**：提示「請檢查網路連線後重試」或「點擊查閱雲端相容性官方文件」。
- **BDD**: `Given` 畫布已有基礎架構並存檔 `When` 使用者重新登入並進入工作區 `Then` 系統自動從資料庫載入該使用者最後一次儲存的畫布 XML 狀態。

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
- **系統回饋 (System Feedback)**:
  - **成功 (Success)**: 彈出綠色滿分徽章與撒花特效，顯示「符合最佳實踐」。**後續引導**：引導點選「下載 PDF 報告」並「發送給主管審閱」。
  - **失敗 (Failure)**: SPOF 節點標示為跳動的紅色驚嘆號，並顯示扣分項目。**後續引導**：提示「請點擊 AI 自動加入備援節點」，或點選「聯絡 SRE 團隊討論」。
- **BDD**: `Given` 掃出資料庫單點故障 `When` Hannah 人工補上備援連線並點擊局部重置評分 `Then` 分數重新計算並達標。

#### A4. 重整後仍記得對話與上次開啟的架構圖
- **多角色協作 (Multi-Role Collaboration)**:
  - **參與角色**: Alex (雲端架構師, `Project_Architect`), Hannah (工程主管, `Project_Editor`)
  - **協作細節**: Alex 與 Hannah 各自在不同架構圖上與 AI 對話；重整瀏覽器或重新登入後，每人回到自己上次開啟的圖，並看到該圖對應的完整聊天紀錄，互不混淆。
- **使用者需求/目標 (User Goal)**: 重整重整或短暫離開後，仍能接續與 AI 的多輪對話，並自動回到上次編輯的架構圖，無需重述需求。
- **驗收標準 (Acceptance Criteria)**:
  1. 聊天紀錄必須持久化於後端資料庫，鍵值為 **使用者 × 架構圖 (`user_id` + `diagram_id`)**；不同圖表的對話互相隔離。
  2. 進入工作區（或重整頁面）時，系統必須自動選回該使用者**上次開啟的架構圖**，並載入其 XML 與對應聊天 `messages[]`。
  3. 每次使用者送出訊息或收到助理回覆後，聊天紀錄須寫回資料庫（至少在一輪對話結束後成功持久化）；切換 `diagramId` 時載入該圖的對話（無紀錄則顯示預設歡迎訊息）。
  4. 僅圖表擁有者與被分享且有權開啟該圖的使用者可讀寫對應聊天；未授權回傳 403。
  5. 工作區須提供「清空對話」按鈕：點擊並確認後，刪除**目前架構圖**對應的 `user × diagram` 聊天紀錄，畫布 XML 不變；清空後聊天區回到預設歡迎訊息。
- **操作流程**: 1. 登入並開啟某架構圖，與 AI 多輪對話。 2. 重整瀏覽器或重新登入進入工作區。 3. 系統自動選回上次圖表並還原聊天；可繼續追問（例如「再加上 WAF」）。 4. 若要重開話題，點「清空對話」→ 確認 → 僅該圖聊天被清除。
- **系統回饋 (System Feedback)**:
  - **成功 (Success)**: 進入工作區後聊天區顯示歷史訊息，畫布為上次圖表；可選 Toast「已還原上次對話」。清空成功時 Toast「✔ 已清空此架構圖的對話」。
  - **失敗 (Failure)**: 無法載入歷史時顯示預設歡迎訊息與提示「無法還原對話，請重新描述需求」；不阻擋產圖。清空失敗時紅色提示「無法清空對話，請重試」。
- **BDD**: `Given` Alex 在 diagram#12 已與 AI 對話三輪並重整頁面 `When` 再次進入工作區 `Then` 系統自動開啟 diagram#12 且聊天區顯示原先三輪訊息。  
  `Given` Alex 在 diagram#12 有歷史對話 `When` 點擊清空對話並確認 `Then` 該圖聊天被刪除、顯示歡迎訊息，且 diagram#12 的 XML 仍在。

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
- **系統回饋 (System Feedback)**:
  - **成功 (Success)**: 產出帶有各雲端商 Logo 的動態對比圖表，最優選將高亮顯示。**後續引導**：引導點擊「套用此雲端商並開始架構設計」。
  - **失敗 (Failure)**: 儀表板顯示黃色「API 逾時」警示條，數據呈現灰色。**後續引導**：提示「請點擊重新整理按鈕」，若持續失敗則引導「提交工單聯絡平台維護團隊」。
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
- **系統回饋 (System Feedback)**:
  - **成功 (Success)**: 顯示環狀進度條 (如 85% 相容)，下方展開綠色的無縫轉移清單。**後續引導**：引導點擊「查看需要人工重構的代碼清單」。
  - **失敗 (Failure)**: 圖表卡在 0% 並彈出紅字「查無雲端替代方案」。**後續引導**：提示「請調整為 IaaS 虛擬機評估方案」，或「聯絡平台管理員新增支援服務」。
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
- **系統回饋 (System Feedback)**:
  - **成功 (Success)**: 世界地圖上出現綠色光點標示最佳 Region，並附上法規核准打勾。**後續引導**：引導點擊「確認區域並鎖定專案設定」。
  - **失敗 (Failure)**: 地圖上的所選區域覆蓋紅色斜線，彈出「違反 GDPR」警告。**後續引導**：提示「請點擊系統推薦的替代 Region」，或「聯絡法務/資安團隊評估例外豁免」。
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
- **系統回饋 (System Feedback)**:
  - **成功 (Success)**: 中心出現動態更新的圓餅圖，綠色字體顯示總預算範圍內。**後續引導**：引導點擊「設定預算超支警報 (Billing Alarm)」。
  - **失敗 (Failure)**: 部分區塊顯示灰色並標示「定價無法獲取」。**後續引導**：提示「請手動輸入預估金額」，或引導「點擊聯絡 FinOps 分析師 (David) 確認合約價格」。
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
- **系統回饋 (System Feedback)**:
  - **成功 (Success)**: 畫面浮出金幣動畫，並以大字體顯示「預估節省 30%」。**後續引導**：引導點擊「一鍵套用轉換變更單」。
  - **失敗 (Failure)**: 畫面提示「該架構不適用 Spot 實例」，建議清單為空。**後續引導**：提示「請嘗試解鎖核心機器再試一次」，或「聯絡維運團隊確認架構彈性」。
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
- **系統回饋 (System Feedback)**:
  - **成功 (Success)**: 架構圖上的連線轉為粗細不同的藍色流向圖，標明費用。**後續引導**：引導點擊「匯出網路流量熱點分析報告」。
  - **失敗 (Failure)**: 無法解析網路路徑，彈出黃字「請確認網路設定」。**後續引導**：提示「請點擊 AI 檢查網路連線完整性」，或「聯絡網路工程師修復拓撲」。
- **BDD**: `Given` Egress 預測為 $100 `When` 局部重置並人工修改頻寬至 10TB `Then` Egress 費用飆升，並以紅字強烈標記。

---

### D. 標準化 IaC 生成與安全交付 (IaC Generation)

#### D1. 模板化 Terraform / OpenTofu 代碼自動產出
- **多角色協作 (Multi-Role Collaboration)**:
  - **參與角色**: Elena (平台工程師, `Platform_Engineer`), Ian (開發者, `Developer`)
  - **協作細節**: Elena 負責制定變數與模組 (Modules) 規範；Ian 在撰寫特定服務時生成代碼。系統確保 Ian 產出的代碼自動套用 Elena 設定的企業標籤。
- **使用者需求/目標 (User Goal)**: 自動化產生符合企業標準的 IaC 代碼，支援多雲架構並消除手動撰寫錯誤。
- **驗收標準 (Acceptance Criteria)**:
  1. 能根據畫布架構自動產出支援 `aws`, `google`, `azurerm` provider 對應的 Terraform / OpenTofu 模組代碼。
  2. 代碼目錄必須嚴格遵循企業標準，包含 `main.tf`, `variables.tf`, `outputs.tf`, `providers.tf` 與 `modules/` 結構。
  3. 產出的代碼可直接通過 `terraform init` / `tofu init` 與 `validate` 語法檢查。
- **操作流程**: 1. 從首頁進入 IaC 工作區。 2. 將畫布轉換為代碼。 3. **AI重置/人工微調**: 對 `variables.tf` 點擊「局部重置」加上公司 prefix，並在 IDE 內人工編輯參數。
- **系統回饋 (System Feedback)**:
  - **成功 (Success)**: 編輯器右下角彈出綠色「✔ 轉換成功」，顯示完整 `.tf` 檔案樹。**後續引導**：引導點擊「進入安全靜態掃描」或「一鍵推送到 Git」。
  - **失敗 (Failure)**: 編輯器跳出紅色編譯錯誤提示，問題行數高亮標記。**後續引導**：提示「請點選 AI 自動修復錯誤語法」，若無法解決則「聯絡平台工程師 (Elena)」。
- **BDD**: `Given` AI 初稿生成完畢 `When` Elena 局部重置 prefix 規則並人工改寫 tag `Then` 代碼順利生成並保留人工修改。

#### D2. IaC 安全與合規自動靜態掃描
- **多角色協作 (Multi-Role Collaboration)**:
  - **參與角色**: Elena (平台工程師, `Platform_Engineer`), Fiona (資安審查員, `Security_Reviewer`)
  - **協作細節**: Elena 提交 IaC 代碼觸發掃描；若掃出漏洞，Fiona 會收到通知，她可以選擇批准風險 (Risk Acceptance) 或要求 AI 提供修復建議讓 Elena 套用。
- **使用者需求/目標 (User Goal)**: 在部署前透過多重掃描引擎攔截代碼中的資安弱點與合規性問題。
- **驗收標準 (Acceptance Criteria)**:
  1. 內建整合 tfsec、Trivy 與 Checkov，在匯出前強制進行深度靜態安全掃描。
  2. 發現 High 或 Critical 漏洞時，必須強制阻擋代碼下載與部署。
  3. 系統必須提供至少一個可直接套用的 AI 修復代碼片段。
- **操作流程**: 1. 從首頁登入安全審查區。 2. 觸發 tfsec/Checkov 綜合掃描。 3. **AI重置/人工微調**: 「局部重置」要求 AI 提供不同修復建議，人工選擇採納並套用。
- **系統回饋 (System Feedback)**:
  - **成功 (Success)**: 畫面中央出現滿版綠色的安全盾牌打勾動畫，標示「0 漏洞」。**後續引導**：引導點擊「核准並開始自動化部署」。
  - **失敗 (Failure)**: 畫面紅光閃爍，阻擋按鈕變灰，列出高危 CVE 漏洞清單。**後續引導**：提示「請點擊 AI 提供的安全修復代碼」，或點選「聯絡資安審查員 (Fiona) 申請特例豁免」。
- **BDD**: `Given` Checkov 掃描出 High 級別漏洞 `When` AI 產出三個修復方案，Elena 人工選擇其一並套用 `Then` 複掃通過，允許 Git Push。

#### D3. Sensitive Values 與 Secret Manager 整合
- **多角色協作 (Multi-Role Collaboration)**:
  - **參與角色**: Fiona (資安審查員, `Security_Reviewer`), Ian (開發者, `Developer`)
  - **協作細節**: 系統攔截到 Ian 提交的明文密碼；Fiona 接獲警報，強制要求轉為 Secret 引用。Ian 收到修復工單，透過 AI 一鍵替換為安全的 ARN。
- **使用者需求/目標 (User Goal)**: 確保 IaC 代碼中絕不包含明文密碼，避免金鑰外洩風險。
- **驗收標準 (Acceptance Criteria)**:
  1. 精準掃描並找出代碼中任何 hardcoded 的明文金鑰、密碼。
  2. 自動將明文替換為對應雲端 (如 AWS Secrets Manager / Azure Key Vault) 的安全引用格式。
  3. 若無法提供有效的 Secret ARN，禁止將代碼 Push 至遠端存儲庫。
- **操作流程**: 1. 從首頁登入機密檢查區。 2. 掃描 hardcoded secrets。 3. **AI重置/人工微調**: 「全部重置」要求改用 Secrets 引用，人工填寫 Secret ARN。
- **系統回饋 (System Feedback)**:
  - **成功 (Success)**: 密碼明文以打字機特效安全轉換為 Provider 原生 Secret 變數。**後續引導**：引導點擊「儲存代碼並進入下一步」。
  - **失敗 (Failure)**: 跳出紅字「找不到對應的 Secret ARN，替換失敗」。**後續引導**：提示「請前往 Secrets Manager 創建新金鑰」，或「聯絡資安團隊尋求授權」。
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
- **系統回饋 (System Feedback)**:
  - **成功 (Success)**: 建議清單旁出現綠色的「建議採納」標章，並動態累加節省總額。**後續引導**：引導點擊「創建降級維運變更單 (CR)」。
  - **失敗 (Failure)**: 目標清單反灰並標示橘色的「受終止保護」。**後續引導**：提示「請前往雲端控制台解除保護狀態」，或「聯絡系統擁有者授權解鎖」。
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
- **系統回饋 (System Feedback)**:
  - **成功 (Success)**: 畫面左右並排顯示「Legacy」與「Serverless」的綠色對比雷達圖，展示 ROI 提升。**後續引導**：引導點擊「匯出高階主管評估簡報」。
  - **失敗 (Failure)**: 畫面提示「技術棧過於老舊，無法自動轉換」。**後續引導**：提示「請嘗試使用 K8s 容器化作為過渡方案」，或「聯絡資深架構師進行人工專案評估」。
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
- **系統回饋 (System Feedback)**:
  - **成功 (Success)**: 畫面以打字機特效生成完整的 YAML 腳本，右側出現「✔ 驗證通過」綠牌。**後續引導**：引導點擊「註冊腳本至自動化 Runbook 庫」。
  - **失敗 (Failure)**: 指令編輯區塊亮紅燈，顯示「解析錯誤：缺乏必要變數」。**後續引導**：提示「請點擊局部重置讓 AI 重新填寫變數」，或「聯絡 SRE (Ben) 協助編寫腳本」。
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
- **系統回饋 (System Feedback)**:
  - **成功 (Success)**: 聊天視窗內平滑渲染出綠色時間趨勢圖，異常峰值以紅點醒目提示。**後續引導**：引導點擊「將圖表釘選至個人桌面」或「產生分享連結發送給主管」。
  - **失敗 (Failure)**: 圖表轉為雜訊狀態，彈出紅色「MCP 連線超時」。**後續引導**：提示「請點擊重試重新連線」，或「聯絡平台管理員 (Jack) 檢查 Agent 狀態」。
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
- **系統回饋 (System Feedback)**:
  - **成功 (Success)**: 產生左右分欄的變更計畫 (Plan) 與帶有綠色防護盾的回滾腳本。**後續引導**：引導點擊「送出審批 (Submit for Approval)」。
  - **失敗 (Failure)**: 送出按鈕反灰鎖死，提示「回滾腳本邏輯有誤，無法保證系統安全」。**後續引導**：提示「請點擊局部重置要求 AI 重寫回滾邏輯」，或「邀請平台工程師同行審閱」。
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
- **系統回饋 (System Feedback)**:
  - **成功 (Success)**: 手機畫面顯示綠色大勾勾「授權成功」並伴隨短暫震動。**後續引導**：提示「點擊查看變更單即時執行進度」。
  - **失敗 (Failure)**: 手機畫面顯示紅叉「授權被拒」或「操作逾時失效」。**後續引導**：提示「請在意見框內填寫退回理由讓 SRE 重新調整」，或「致電 SRE 負責人說明原因」。
- **BDD**: `Given` 變更單 Pending `When` Karen 人工填寫「需補上離峰時段執行」並 Reject `Then` 變更取消，SRE 收到重置要求。

---

### G. 雲端安全態勢與策略顧問 (Cloud Security Posture & Policy Advisory)

#### G1. 全局安全態勢與合規持續檢視 (CSPM & Continuous Compliance)
- **多角色協作 (Multi-Role Collaboration)**:
  - **參與角色**: Fiona (資安審查員, `Security_Reviewer`), Alex (雲端架構師, `Project_Architect`)
  - **協作細節**: Fiona 觸發全域掃描，涵蓋 Network exposure、Storage access、Encryption 與 Audit logging 配置。系統產出 Remediation Plan 與 IaC patch，Alex 套用代碼後，由於涉及高風險修復，強制進入 Human Approval Gate 由 Fiona 審批。
- **使用者需求/目標 (User Goal)**: 持續監控雲端資源設定是否符合資安合規標準，並快速產出自動化修復計畫與代碼。
- **驗收標準 (Acceptance Criteria)**:
  1. 系統必須能深度檢視並報告 Network exposure (如 Public SG)、Storage access、Encryption (at rest/transit) 以及 Audit logging 是否正確啟用。
  2. 針對掃出的弱點，必須產出對應的 Remediation Plan 與具體可執行的 IaC Patch。
  3. 任何被標記為高風險 (High-Risk) 的修復執行前，強制必須通過 Human Approval Gate 審批機制。
- **操作流程**: 1. 登入全域安全看板。 2. 啟動合規性深度掃描。 3. **AI重置/人工微調**: 人工修改 IaC patch 的參數，重置修復計畫。
- **系統回饋 (System Feedback)**:
  - **成功 (Success)**: 顯示滿版綠盾牌與高分評分，產出防護清單。**後續引導**: 引導點擊「一鍵套用 IaC Patch 並送出高風險修復審批 (Human Approval Gate)」。
  - **失敗 (Failure)**: 亮紅燈警示掃描受阻或權限不足。**後續引導**: 提示「請點擊重新綁定 IAM Scanner Role」。
- **BDD**: `Given` 掃描發現 S3 bucket 缺乏加密 `When` AI 產生 IaC Patch 並由 SRE 點擊套用 `Then` 系統攔截部署，觸發 Human Approval Gate 等待 Fiona 審批。

#### G2. IAM / RBAC 與最小權限策略 (Least-Privilege & Identity Security)
- **多角色協作 (Multi-Role Collaboration)**:
  - **參與角色**: Fiona (資安審查員, `Security_Reviewer`), Ian (開發者, `Developer`)
  - **協作細節**: Fiona 掃描出 Ian 的專案中有過度授權的帳號。系統自動指派修復任務給 Ian；Ian 透過 AI 產出 Least-privilege 建議，修復單送交 Fiona 的 Approval Gate 確認。
- **使用者需求/目標 (User Goal)**: 嚴格審視 IAM 與 RBAC，找出過度授權的角色並落實最小權限原則。
- **驗收標準 (Acceptance Criteria)**:
  1. 深度檢視現有 IAM / RBAC 權限，找出過度授權 (Over-permissive) 的帳號或角色。
  2. 基於歷史存取紀錄自動產出極簡化的 Least-privilege Policy 建議。
  3. 若建議縮減的權限涉及核心運算資源存取，強制進入 Human Approval Gate 審核。
- **操作流程**: 1. 進入 IAM 審查區。 2. 執行過度授權分析。 3. **AI重置/人工微調**: 「局部重置」排除特定開發人員，人工加註安全標籤。
- **系統回饋 (System Feedback)**:
  - **成功 (Success)**: 清單過濾動畫完成，顯示綠色標語「已精簡為安全權限範圍」。**後續引導**: 引導點擊「生成 Least-Privilege Policy 並送出審批」。
  - **失敗 (Failure)**: 畫面跳出紅色對話框「讀取歷史存取紀錄權限不足」。**後續引導**: 提示「請點擊授權請求按鈕申請跨帳號權限」。
- **BDD**: `Given` 掃出 Action 為 "*" 的權限 `When` AI 產出 Least-privilege 建議並人工選擇套用 `Then` 修復行為被鎖定，等待 Fiona 透過 Human Approval Gate 核准。

#### G3. 自動化策略防護網 (Policy Guardrails & Policy-as-Code)
- **多角色協作 (Multi-Role Collaboration)**:
  - **參與角色**: Fiona (資安審查員, `Security_Reviewer`), Elena (平台工程師, `Platform_Engineer`)
  - **協作細節**: Fiona 用自然語言定義 Policy guardrails；AI 轉化為 Policy-as-Code (如 Rego)。Elena 負責將代碼整合進 CI/CD 中，雙方在 IDE 共同確保策略不會誤擋正常發布。
- **使用者需求/目標 (User Goal)**: 建立自動化的 Policy Guardrails 以防止違規部署，將資安規範代碼化。
- **驗收標準 (Acceptance Criteria)**:
  1. 支援將自然語言的合規要求轉化為 Policy-as-Code (OPA Rego 或 AWS Config)。
  2. 建立防禦性的 Policy Guardrails，在部署階段主動攔截不合規的 IaC 操作。
  3. 允許在 IDE 介面內由資安人員人工修改條件式與正則表達式。
- **操作流程**: 1. 進入 Guardrail 設定區。 2. 輸入防禦規則要求。 3. **AI重置/人工微調**: 「全部重置」改產出 AWS Config 規則，人工修改正則表達式。
- **系統回饋 (System Feedback)**:
  - **成功 (Success)**: 代碼編輯區塊右上角亮起綠燈，模擬終端機顯示 `PASS`。**後續引導**: 引導點擊「將此策略合併至防護網生效」。
  - **失敗 (Failure)**: 終端機報出紅色編譯錯誤，高亮提示語法不符之處。**後續引導**: 提示「請在 IDE 內人工修復語法」，或「點擊 AI 智能除錯」。
- **BDD**: `Given` AI 生成 OPA Policy `When` Fiona 人工修改正則並點擊測試 `Then` 系統回報防護策略測試通過。

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
- **系統回饋 (System Feedback)**:
  - **成功 (Success)**: 工具卡片轉為鮮豔的 `ACTIVE` 狀態，並打上綠色勾勾。**後續引導**：引導點擊「立即在 AI Chat 中進行測試呼叫」。
  - **失敗 (Failure)**: 卡片劇烈震動並顯示紅字「Schema 格式解析失敗」。**後續引導**：提示「請檢查 YAML/JSON 語法是否合規」，或「聯絡 API 開發者確認文件規格」。
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
- **系統回饋 (System Feedback)**:
  - **成功 (Success)**: 畫面頂端彈出綠色橫幅「權限邊界已成功鎖定為全域生效」。**後續引導**：引導點擊「返回 MCP 目錄檢視其他工具」。
  - **失敗 (Failure)**: 跳出黃色警示框「該設定與現有全域安全策略衝突」。**後續引導**：提示「請檢視現有全域策略清單」，或「聯絡資安主管 (Fiona) 確認例外豁免條款」。
- **BDD**: `Given` AI 建議給予 Deploy 權限 `When` Jack 人工強制修改為 Read-only `Then` 所有 Agent 呼叫該工具時失去寫入能力。

#### H3. 全域 MCP 工具與 Skill 註冊生命週期管理 (MCP & Skill Lifecycle)
- **多角色協作 (Multi-Role Collaboration)**:
  - **參與角色**: Elena (平台工程師, `Platform_Engineer`), Jack (平台管理員, `Platform_Admin`)
  - **協作細節**: Elena 註冊新的 MCP server 與雲端連接器 (Connectors)，並設定其讀寫權限範圍。系統進行依賴性與健康檢查後，交由 Jack 進行啟用審批。審批通過後，該工具正式納入 Agent Routing Layer 供 AI 選用。
- **使用者需求/目標 (User Goal)**: 統一管理與配置 AI 依賴的所有外部工具與工作流，確保 Agent 只能在安全審批後的邊界內自動調用工具。
- **驗收標準 (Acceptance Criteria)**:
  1. 支援管理包含 MCP servers, Tools, AI Skills, Cloud provider connectors 以及 Reusable workflows 的完整生命週期 (註冊、啟用/停用、版本控管)。
  2. 內建自動化的相依性檢查 (Dependency Check) 與定期的健康檢查 (Health Check)，失效的工具將被標記並停用。
  3. 將所有合規工具納入 **Agent Routing Layer**，使 AI 能根據意圖自動且安全地選用合適工具，執行 read-only 分析或觸發經審批 (Human Approval Gate) 的維運操作。
- **操作流程**: 1. 進入 MCP 與 Skill 管理中心。 2. 新增或更新 MCP Server。 3. **AI重置/人工微調**: 人工調整工具權限邊界，限制其僅能執行 Read-only 動作。
- **系統回饋 (System Feedback)**:
  - **成功 (Success)**: 新工具卡片亮起綠燈顯示「ACTIVE」，並標示「Routing Layer 已接入」。**後續引導**: 引導點擊「在 Sandbox 測試 Agent 工具調用」。
  - **失敗 (Failure)**: 卡片亮紅燈顯示「Health Check 失敗」或「相依性缺失」。**後續引導**: 提示「請點擊檢視錯誤日誌」或「重新配置雲端連接器憑證」。
- **BDD**: `Given` Elena 註冊了一個具備修改權限的 Cloud Connector `When` AI 自動測試連線成功，但 Jack 人工在審批階段將其降級為 Read-only `Then` Agent 在 Routing Layer 呼叫該工具時僅能執行查詢動作。

### J. 身分認證與基於角色的權限管理 (Identity Authentication & Role-Based Access Control)

#### J1. 統一登入入口與安全憑證驗證
- **多角色協作 (Multi-Role Collaboration)**:
  - **參與角色**: 平台內所有使用者 (如 Alex, Fiona, Ian 等), Jack (平台管理員, `Platform_Admin`)
  - **協作細節**: 所有使用者必須通過統一登入入口完成身分認證以獲取 Session Token。Jack 負責設定密碼複雜度策略與 MFA 規則。
- **使用者需求/目標 (User Goal)**: 擁有一個安全的登入頁面，驗證身分並開始系統工作，保障帳戶與系統資料的安全。
- **驗收標準 (Acceptance Criteria)**:
  1. 提供獨立的 Desktop / Mobile Web 登入頁面，支援帳號與密碼欄位輸入。
  2. 驗證失敗時必須回傳模糊之錯誤提示（如「帳號或密碼錯誤」），以防止暴力破解與使用者列舉攻擊。
  3. 驗證成功後，在瀏覽器安全儲存加密的 Token，並隨附時效控制（Token Expiration），逾時自動登出。
- **操作流程**: 1. 訪問平台首頁網址。 2. 輸入帳號密碼並點擊「登入」。 3. **AI重置/人工微調**: 登入失敗可點擊「重設密碼」，或手動修正輸入之憑證。
- **系統回饋 (System Feedback)**:
  - **成功 (Success)**: 綠色 Toast 提示「✔ 登入成功，正在跳轉...」，隨後頁面跳轉至該角色對應之預設工作面板。**後續引導**：引導進入首頁控制台。
  - **失敗 (Failure)**: 紅色警告「✘ 登入失敗：帳號或密碼錯誤」。**後續引導**：提示「請確認您的憑證後重試」，或提供「聯絡管理員」按鈕。
- **BDD**: `Given` 使用者未登入 `When` 輸入正確憑證點擊登入 `Then` 派發 Token 並導向對應角色頁面。

#### J2. 基於角色的權限頁面可見性控制
- **多角色協作 (Multi-Role Collaboration)**:
  - **參與角色**: Ian (開發者, `Developer`), David (FinOps 分析師, `FinOps_Analyst`), Fiona (資安審查員, `Security_Reviewer`)
  - **協作細節**: 開發者 Ian 與 FinOps 分析師 David 在登入後，各自只能看到符合自己工作範疇的頁面。當 Ian 企圖越權查看 David 的成本面板時，系統將主動阻擋。
- **使用者需求/目標 (User Goal)**: 確保平台內不同使用者僅能訪問與其職責相關的選單與工作區，落實職責分離 (SoD) 與最小權限原則。
- **驗收標準 (Acceptance Criteria)**:
  1. 側邊導航欄與系統選單必須根據當前使用者的 Role 屬性動態隱藏或顯示對應的工作區連結。
  2. 當使用者企圖手動修改瀏覽器 URL 路由（Bypass）訪問未授權頁面（如 `Developer` 訪問 `/admin`）時，前端路由守衛必須立刻攔截並將其導向 403 Forbidden 頁面。
  3. 後端 API 接收請求時，必須同步比對 Token 中的 Role 範圍，確認無權限時回傳 403 HTTP code。
- **操作流程**: 1. 使用者登入並進入主畫面。 2. 檢視左側選單，訪問授權模組。 3. **AI重置/人工微調**: 系統選單動態更新，若發生誤判，管理員可「局部重置」清除當前 Session 快取要求重配。
- **系統回饋 (System Feedback)**:
  - **成功 (Success)**: 介面順暢渲染授權的面板選單。**後續引導**：引導點擊進入相關分析工作區。
  - **失敗 (Failure)**: 畫面轉為「403 拒絕存取」錯誤警告。**後續引導**：提示「您無此頁面的存取權限」，並提供「返回首頁」或「申請權限」按鈕。
- **BDD**: `Given` Ian 的角色為 Developer `When` 嘗試修改瀏覽器 URL 訪問 `/admin` `Then` 路由守衛攔截並顯示 403 拒絕訪問。

#### J3. 管理員專屬的權限編輯與指派面板
- **多角色協作 (Multi-Role Collaboration)**:
  - **參與角色**: Catherine (管理員, `Project_Admin`), Ian (開發者, `Developer`)
  - **協作細節**: Catherine 進入權限面板，編輯 Ian 的角色。變更後，Ian 的系統權限將動態更新，且此動作將自動記錄至稽核日誌供 Fiona 審查。
- **使用者需求/目標 (User Goal)**: 讓管理員可以方便地檢視所有帳戶，並根據項目職責即時調配或收回使用者權限。
- **驗收標準 (Acceptance Criteria)**:
  1. 提供管理員專屬的 RBAC 管理面板，能完整列出系統內所有使用者名稱、角色與權限範圍。
  2. 允許管理員點擊編輯並動態變更任一使用者的角色，變更必須存入後端資料庫且在目標使用者下次重新整理時立即生效。
  3. 每次權限的變更（升級或降級）必須被強制記錄至平台稽核日誌 (Audit Log)，內容需包含執行管理員、受影響帳戶、以及權限異動詳情。
- **操作流程**: 1. 管理員進入「權限管理面板」。 2. 選擇使用者並修改其角色屬性後存檔。 3. **AI重置/人工微調**: 點擊「重置此使用者」可還原至系統預設權限。
- **系統回饋 (System Feedback)**:
  - **成功 (Success)**: 綠色彈窗提示「✔ 使用者角色已更新為 SRE」，該行狀態更新為最新角色。**後續引導**：引導「檢視稽核日誌確認變更已記錄」。
  - **失敗 (Failure)**: 紅色提示「✘ 更新失敗：不能將最後一位管理員降級」。**後續引導**：提示「請先指派其他管理員後重試」。
- **BDD**: `Given` 管理員 Catherine 登入權限管理面板 `When` 將 Ian 的角色改為 SRE 並點擊儲存 `Then` 使用者狀態更新，且 Audit Log 生成對應變更紀錄。

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
- **System Feedback**:
  - **Success**: A green toast "✔ Architecture draft generated" appears in the center, autosaving the canvas. **Next Step**: A button prompts "Proceed to IaC generation" or "Start Well-Architected review".
  - **Failure**: A red warning box pops up at the top: "Resource Conflict: Service not supported in selected Region." **Next Step**: Prompts "Please adjust parameters in the chat and retry" or offers a shortcut to "Contact Lead Architect (Alex) for help".
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
- **System Feedback**:
  - **Success**: The modified node flashes a green border for 2 seconds with "Changes synced." **Next Step**: A floating button prompts "Export architecture diagram" or "View estimated costs."
  - **Failure**: The node turns red, links break, and a prompt says "Component does not support this protocol." **Next Step**: Prompts "Please manually drag lines to reconnect" or "Click to read cloud compatibility documentation."
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
- **System Feedback**:
  - **Success**: Pops up a green perfect-score badge with confetti, showing "Compliant with Best Practices." **Next Step**: Prompts to "Download PDF Report" and "Send to management for review."
  - **Failure**: SPOF nodes are marked with a bouncing red exclamation mark detailing the penalty. **Next Step**: Prompts "Click to let AI auto-add backup nodes" or "Contact SRE team to discuss."
- **BDD**: `Given` A SPOF is detected `When` Hannah manually adds a backup node and clicks partial reset `Then` The score recalculates and passes.

#### A4. Persist Chat and Last-Opened Diagram Across Refresh
- **Multi-Role Collaboration**:
  - **Roles Involved**: Alex (Cloud Architect, `Project_Architect`), Hannah (Engineering Manager, `Project_Editor`)
  - **Collaboration Details**: Alex and Hannah each chat with AI on different diagrams; after refresh or re-login, each returns to their last-opened diagram with that diagram's full chat history, without cross-talk.
- **User Goal**: After a browser refresh or short leave, continue the multi-turn AI conversation and land on the last edited diagram without restating requirements.
- **Acceptance Criteria**:
  1. Chat history MUST be persisted in the backend DB keyed by **user × diagram (`user_id` + `diagram_id`)**; conversations for different diagrams are isolated.
  2. On entering the workspace (or refreshing), the system MUST auto-select the user's **last-opened diagram** and load its XML plus the corresponding chat `messages[]`.
  3. After each user message / assistant reply (at least once per completed turn), chat MUST be written back to the DB; switching `diagramId` loads that diagram's chat (or the default welcome message if empty).
  4. Only the diagram owner and users with share access may read/write that chat; unauthorized access returns 403.
  5. The workspace MUST provide a **Clear chat** button: after confirmation, delete the chat for the **current diagram** (`user × diagram`) only; canvas XML is unchanged; the chat UI returns to the default welcome message.
- **Operational Flow**: 1. Open a diagram and chat with AI for multiple turns. 2. Refresh or re-login into the workspace. 3. System restores last diagram and chat; user can continue (e.g., "add a WAF"). 4. To start fresh, click Clear chat → confirm → only that diagram's chat is cleared.
- **System Feedback**:
  - **Success**: Chat shows prior messages and canvas shows last diagram; optional toast "Previous conversation restored." On clear: toast "✔ Chat cleared for this diagram."
  - **Failure**: Falls back to welcome message with "Could not restore chat; please restate your needs" without blocking diagram generation. Clear failure: red "Could not clear chat; please retry."
- **BDD**: `Given` Alex chatted three turns on diagram#12 and refreshed `When` he re-enters the workspace `Then` diagram#12 opens and the chat shows the original three turns.  
  `Given` Alex has chat history on diagram#12 `When` he clears chat and confirms `Then` that diagram's chat is deleted, welcome message shows, and diagram#12 XML remains.

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
- **System Feedback**:
  - **Success**: Outputs a dynamic comparison chart with provider logos, highlighting the optimal choice. **Next Step**: Prompts "Apply this provider and begin architecture design."
  - **Failure**: Dashboard shows a yellow "API Timeout" banner; data turns gray. **Next Step**: Prompts "Please click refresh" or "Submit ticket to platform maintenance team if it persists."
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
- **System Feedback**:
  - **Success**: Displays a circular progress bar (e.g., 85% compatible) expanding into a green list of seamless migrations. **Next Step**: Prompts "View list of codes requiring manual refactoring."
  - **Failure**: Chart stuck at 0% with red text "No cloud alternative found." **Next Step**: Prompts "Please adjust to IaaS VM evaluation" or "Contact platform admin to add support."
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
- **System Feedback**:
  - **Success**: Map displays green glowing dots on the best Regions with a compliance checkmark. **Next Step**: Prompts "Confirm Region and lock project settings."
  - **Failure**: Selected Region is covered in red slashes with a "GDPR Violation" warning. **Next Step**: Prompts "Please click system recommended alternatives" or "Contact legal/security for exception review."
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
- **System Feedback**:
  - **Success**: Center displays a dynamic pie chart with the total budget in green text indicating it's within limits. **Next Step**: Prompts "Set up Billing Alarm."
  - **Failure**: Certain wedges turn gray labeled "Price Unavailable." **Next Step**: Prompts "Please manually input estimates" or "Contact FinOps (David) to verify contract pricing."
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
- **System Feedback**:
  - **Success**: A coin animation floats up, showing "Est. 30% Savings" in large text. **Next Step**: Prompts "Apply 1-click conversion Change Request."
  - **Failure**: Screen prompts "Architecture not suitable for Spot instances"; list remains empty. **Next Step**: Prompts "Try unlocking core machines" or "Contact Ops to verify architecture elasticity."
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
- **System Feedback**:
  - **Success**: Canvas connections morph into blue flow lines of varying thickness with cost tags. **Next Step**: Prompts "Export network egress heatmap report."
  - **Failure**: Cannot parse routing, showing yellow text "Please verify network config." **Next Step**: Prompts "Ask AI to check network topology integrity" or "Contact Network Engineer."
- **BDD**: `Given` $100 Egress forecast `When` Partially reset and manually bumped to 10TB `Then` Egress costs spike in red.

---

### D. Standardized IaC Generation & Secure Delivery

#### D1. Templated Terraform / OpenTofu Generation
- **Multi-Role Collaboration**:
  - **Roles Involved**: Elena (Platform Engineer, `Platform_Engineer`), Ian (Developer, `Developer`)
  - **Collaboration Details**: Elena enforces module/tagging standards; when Ian generates code for his services, the system ensures Elena's enterprise tags are automatically applied.
- **User Goal**: Automate the creation of enterprise-standard IaC code that supports multi-cloud providers, eliminating manual coding errors.
- **Acceptance Criteria**:
  1. Automatically generates Terraform / OpenTofu module code supporting `aws`, `google`, and `azurerm` providers based on the canvas.
  2. The code directory must strictly follow enterprise standards, including `main.tf`, `variables.tf`, `outputs.tf`, `providers.tf`, and `modules/` structure.
  3. Output code must pass basic `terraform init` / `tofu init` and `validate` checks out-of-the-box.
- **Operational Flow**: 1. Access IaC Workspace. 2. Convert canvas to code. 3. **AI Reset/Manual Adjust**: "Partial Reset" variables to add prefixes, manually edit tags.
- **System Feedback**:
  - **Success**: The editor pops up a green "✔ Conversion Successful" and displays the `.tf` file tree. **Next Step**: Prompts "Proceed to static security scan" or "1-click Git Push."
  - **Failure**: Red compilation errors flash in the editor, highlighting problematic lines. **Next Step**: Prompts "Click for AI to auto-fix syntax" or "Contact Platform Engineer (Elena)."
- **BDD**: `Given` AI draft generated `When` Elena partially resets prefixes and manually edits tags `Then` Code compiles preserving her changes.

#### D2. Automated Static Security Scan
- **Multi-Role Collaboration**:
  - **Roles Involved**: Elena (Platform Engineer, `Platform_Engineer`), Fiona (Security Reviewer, `Security_Reviewer`)
  - **Collaboration Details**: Elena triggers a scan; Fiona receives a ping for any vulnerabilities. Fiona can accept the risk or ask AI for fix snippets, which Elena then applies.
- **User Goal**: Intercept security vulnerabilities and compliance issues in the code before deployment using multiple scanning engines.
- **Acceptance Criteria**:
  1. Natively integrates tfsec, Trivy, and Checkov to force deep static scans before export.
  2. Forcibly blocks code download/deployment when High vulnerabilities are detected.
  3. Provides directly applicable AI-remediation code snippets for found vulnerabilities.
- **Operational Flow**: 1. Enter Security Review. 2. Trigger combined tfsec/Checkov scan. 3. **AI Reset/Manual Adjust**: "Partial Reset" for alternative fix suggestions, manually apply one.
- **System Feedback**:
  - **Success**: A full-screen green security shield checks off, indicating "0 Vulnerabilities." **Next Step**: Prompts "Approve and begin automated deployment."
  - **Failure**: Screen flashes red, blocks deployment buttons, and lists Critical CVEs. **Next Step**: Prompts "Click to apply AI security fixes" or "Contact Security (Fiona) for Risk Acceptance."
- **BDD**: `Given` Checkov flagged a High-severity bug `When` AI suggests fixes and Elena manually applies one `Then` Rescan passes, Git Push unlocked.

#### D3. Sensitive Values & Secret Manager Check
- **Multi-Role Collaboration**:
  - **Roles Involved**: Fiona (Security Reviewer, `Security_Reviewer`), Ian (Developer, `Developer`)
  - **Collaboration Details**: System detects Ian's hardcoded password. Fiona mandates a Secret conversion. Ian uses AI to 1-click replace it with a secure AWS/Azure ARN before committing.
- **User Goal**: Ensure IaC code never contains plaintext passwords, preventing credential leaks.
- **Acceptance Criteria**:
  1. Scans and highlights hardcoded plaintext keys/passwords.
  2. Forcibly replaces plaintext with secure references to native cloud providers (e.g., AWS Secrets Manager, Azure Key Vault).
  3. Prohibits pushing code to remote repos without valid Secret ARN mappings.
- **Operational Flow**: 1. Open Secret Scanner. 2. Scan for hardcoded keys. 3. **AI Reset/Manual Adjust**: "Full Reset" to force native Secrets format, manually input ARN.
- **System Feedback**:
  - **Success**: Plaintext transforms into native Provider Secret variables via typewriter effect. **Next Step**: Prompts "Save code and proceed to next step."
  - **Failure**: Pops up red text "Matching Secret ARN not found, conversion failed." **Next Step**: Prompts "Go to Secrets Manager to create a new key" or "Contact Security for permissions."
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
- **System Feedback**:
  - **Success**: A green "Adoption Recommended" badge appears next to the list, dynamically tallying savings. **Next Step**: Prompts "Create downsize Change Request (CR)."
  - **Failure**: List greys out with an orange "Termination Protection Active" label. **Next Step**: Prompts "Go to cloud console to disable protection" or "Contact system owner for authorization."
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
- **System Feedback**:
  - **Success**: Side-by-side green radar charts comparing Legacy vs. Serverless appear, highlighting ROI gains. **Next Step**: Prompts "Export executive summary presentation."
  - **Failure**: Prompts "Tech stack too legacy for automated Serverless conversion." **Next Step**: Prompts "Try using containerization (K8s) as a transitional step" or "Contact Lead Architect for manual review."
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
- **System Feedback**:
  - **Success**: YAML script generates via typewriter effect, with a green "✔ Validation Passed" badge. **Next Step**: Prompts "Register script into automated Runbook Library."
  - **Failure**: Editor flashes red stating "Parse Error: Missing required variables." **Next Step**: Prompts "Click partial reset to let AI refill variables" or "Contact SRE (Ben) to code it."
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
- **System Feedback**:
  - **Success**: Smoothly renders a green trend chart in chat, with anomalies tagged via red dots. **Next Step**: Prompts "Pin chart to personal dashboard" or "Generate shareable link for manager."
  - **Failure**: Chart dissolves into static, popping a red "MCP Connection Timeout." **Next Step**: Prompts "Click to retry connection" or "Contact Platform Admin (Jack) to verify Agent."
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
- **System Feedback**:
  - **Success**: Generates split-pane views of the Plan and a green shield-tagged Rollback script. **Next Step**: Prompts "Submit package for Approval."
  - **Failure**: Submit button greyed out with "Rollback logic flawed; system safety unverified." **Next Step**: Prompts "Ask AI to rewrite rollback logic" or "Invite Platform Engineer for peer review."
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
- **System Feedback**:
  - **Success**: Mobile screen shows a large green checkmark "Authorization Successful" with a short vibration. **Next Step**: Prompts "Tap to view real-time execution progress."
  - **Failure**: Mobile shows a red cross "Authorization Denied" or "Session Timeout." **Next Step**: Prompts "Type rejection reason for SRE to rework" or "Call SRE Lead to explain."
- **BDD**: `Given` CR is Pending `When` Karen manually types "Do this off-hours" and Rejects `Then` CR cancels, returning feedback to SRE.

---

### G. Cloud Security Posture & Policy Advisory

#### G1. CSPM & Continuous Compliance Review
- **Multi-Role Collaboration**:
  - **Roles Involved**: Fiona (Security Reviewer, `Security_Reviewer`), Alex (Cloud Architect, `Project_Architect`)
  - **Collaboration Details**: Fiona triggers a global scan covering network exposure, storage access, encryption, and audit logging. The system generates a Remediation Plan and an IaC patch. When Alex applies the patch, the high-risk nature of the fix forces it into a Human Approval Gate for Fiona to authorize.
- **User Goal**: Continuously monitor cloud resources for security compliance and rapidly generate automated remediation plans and code.
- **Acceptance Criteria**:
  1. Deeply inspects and reports on Network exposure (e.g., Public SGs), Storage access, Encryption (at rest/transit), and Audit logging configurations.
  2. Generates a specific Remediation Plan and directly executable IaC Patch for all discovered vulnerabilities.
  3. Mandates that any fix flagged as High-Risk must pass through a Human Approval Gate before execution.
- **Operational Flow**: 1. Access Global Security Dashboard. 2. Start deep compliance scan. 3. **AI Reset/Manual Adjust**: Manually modify IaC patch parameters, resetting the remediation plan.
- **System Feedback**:
  - **Success**: Displays a full green shield and high score, outputting a protected checklist. **Next Step**: Prompts "1-click apply IaC Patch and submit for Human Approval Gate."
  - **Failure**: Flashes a red light warning of blocked scans or insufficient permissions. **Next Step**: Prompts "Click to rebind IAM Scanner Role."
- **BDD**: `Given` A scan finds an unencrypted S3 bucket `When` AI generates an IaC Patch and SRE applies it `Then` The system intercepts deployment, triggering a Human Approval Gate for Fiona's review.

#### G2. Least-Privilege & Identity Security (IAM / RBAC)
- **Multi-Role Collaboration**:
  - **Roles Involved**: Fiona (Security Reviewer, `Security_Reviewer`), Ian (Developer, `Developer`)
  - **Collaboration Details**: Fiona scans Ian's over-permissive project roles. The system assigns a fix task to Ian, who uses AI to generate least-privilege suggestions. The fix ticket is routed to Fiona's Approval Gate.
- **User Goal**: Rigorously audit IAM and RBAC to identify over-permissive roles and enforce the Principle of Least Privilege.
- **Acceptance Criteria**:
  1. Deeply inspects existing IAM / RBAC permissions to identify over-permissive accounts or roles.
  2. Automatically generates minimized Least-Privilege Policy recommendations based on historical access records.
  3. Forces any permission reductions affecting core compute resources into a Human Approval Gate.
- **Operational Flow**: 1. Enter IAM Review area. 2. Run over-permission analysis. 3. **AI Reset/Manual Adjust**: "Partial Reset" to exclude specific developers, manually add security tags.
- **System Feedback**:
  - **Success**: List filtering animation completes, showing green text "Refined to secure privilege scope." **Next Step**: Prompts "Generate Least-Privilege Policy and submit for approval."
  - **Failure**: Pops a red dialog "Insufficient permissions to read access history." **Next Step**: Prompts "Click to request cross-account access."
- **BDD**: `Given` An Action of "*" is flagged `When` AI suggests a Least-privilege policy and user applies it `Then` The fix is locked pending Human Approval Gate authorization from Fiona.

#### G3. Policy Guardrails & Policy-as-Code Automation
- **Multi-Role Collaboration**:
  - **Roles Involved**: Fiona (Security Reviewer, `Security_Reviewer`), Elena (Platform Engineer, `Platform_Engineer`)
  - **Collaboration Details**: Fiona defines policy guardrails in natural language; AI converts them into Policy-as-Code (e.g., Rego). Elena integrates it into CI/CD, collaborating in the IDE to ensure valid deployments aren't blocked.
- **User Goal**: Establish automated Policy Guardrails to prevent non-compliant deployments by encoding security rules.
- **Acceptance Criteria**:
  1. Translates natural language compliance requirements into Policy-as-Code (OPA Rego or AWS Config).
  2. Establishes defensive Policy Guardrails to proactively intercept non-compliant IaC operations during deployment.
  3. Features an IDE interface allowing manual edits of conditions and regex patterns by security personnel.
- **Operational Flow**: 1. Enter Guardrail configuration. 2. Input defensive rule requests. 3. **AI Reset/Manual Adjust**: "Full Reset" to request AWS Config rules, manually edit regex.
- **System Feedback**:
  - **Success**: Code block corner lights up green, mock terminal displays `PASS`. **Next Step**: Prompts "Merge this policy to enforce the guardrail."
  - **Failure**: Terminal throws red compilation errors, highlighting syntax mismatches. **Next Step**: Prompts "Manually fix syntax in IDE" or "Click AI Smart Debug for assistance."
- **BDD**: `Given` AI-generated OPA Policy `When` Fiona manually edits the regex and tests `Then` System reports guardrail policy validation success.

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
- **System Feedback**:
  - **Success**: Tool card flips to a vibrant `ACTIVE` state with a green check. **Next Step**: Prompts "Test call this tool immediately in AI Chat."
  - **Failure**: Card shakes violently displaying red text "Schema parse failed." **Next Step**: Prompts "Check YAML/JSON formatting compliance" or "Contact API developer to verify spec."
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
- **System Feedback**:
  - **Success**: Top banner flashes green: "Permission boundaries successfully enforced globally." **Next Step**: Prompts "Return to MCP Catalog to review other tools."
  - **Failure**: Yellow warning box: "Settings conflict with existing global security policies." **Next Step**: Prompts "Review global policy list" or "Contact Security Lead (Fiona) for exemptions."
- **BDD**: `Given` AI suggests Deploy rights `When` Jack manually forces `Read-only` `Then` All Agents lose write access when calling this tool.

#### H3. Global MCP Tool & Skill Lifecycle Management
- **Multi-Role Collaboration**:
  - **Roles Involved**: Elena (Platform Engineer, `Platform_Engineer`), Jack (Platform Admin, `Platform_Admin`)
  - **Collaboration Details**: Elena registers a new MCP server and cloud provider connectors, defining their permission scopes. Following automated dependency and health checks, the tool is routed to Jack for approval. Once approved, it is integrated into the Agent Routing Layer for AI usage.
- **User Goal**: Centrally manage and configure all external tools and workflows the AI relies on, ensuring Agents only invoke tools within safe, pre-approved boundaries.
- **Acceptance Criteria**:
  1. Supports full lifecycle management (Registration, Enable/Disable, Version Control) for MCP servers, Tools, AI Skills, Cloud Provider Connectors, and Reusable Workflows.
  2. Features built-in automated Dependency Checks and recurring Health Checks, automatically flagging and disabling failing tools.
  3. Integrates all compliant tools into an **Agent Routing Layer**, empowering the AI to safely and autonomously select appropriate tools for read-only analysis or human-approved operational actions.
- **Operational Flow**: 1. Access MCP & Skill Management Center. 2. Register or update an MCP Server. 3. **AI Reset/Manual Adjust**: Manually adjust tool boundaries to strictly enforce Read-only limits.
- **System Feedback**:
  - **Success**: Tool card turns green displaying "ACTIVE" with a "Routing Layer Connected" badge. **Next Step**: Prompts "Test Agent tool invocation in Sandbox."
  - **Failure**: Card turns red displaying "Health Check Failed" or "Missing Dependencies." **Next Step**: Prompts "Click to view error logs" or "Reconfigure connector credentials."
- **BDD**: `Given` Elena registers a Cloud Connector with write permissions `When` AI successfully tests the connection, but Jack manually downgrades it to Read-only during approval `Then` Agents using the Routing Layer can only perform read actions via this tool.

### J. Identity Authentication & Role-Based Access Control (RBAC)

#### J1. Unified Login Portal & Secure Credentials Validation
- **Multi-Role Collaboration**:
  - **Roles Involved**: All platform users (e.g., Alex, Fiona, Ian), Jack (Platform Admin, `Platform_Admin`)
  - **Collaboration Details**: All users must verify their identities through the unified login portal to obtain a Session Token. Jack configures password complexity policies and MFA rules.
- **User Goal**: Securely log into the platform, validating credentials to start a session and protecting accounts and system data.
- **Acceptance Criteria**:
  1. Provides a dedicated Desktop / Mobile Web login page with username and password input fields.
  2. Returns a generic, obfuscated error message on verification failure (e.g., "Invalid username or password") to prevent brute-force and user enumeration attacks.
  3. Securely stores the encrypted token in the browser upon successful validation, carrying a token expiration time to auto-logout on timeout.
- **Operational Flow**: 1. Access the platform login URL. 2. Enter credentials and click "Login". 3. **AI Reset/Manual Adjust**: Reset password if failed, or manually correct the input credentials.
- **System Feedback**:
  - **Success**: A green toast shows "✔ Login successful, redirecting...", and the page redirects to the user role's default dashboard. **Next Step**: Enters dashboard homepage.
  - **Failure**: A red warning shows "✘ Login failed: Invalid username or password." **Next Step**: Prompts "Please check your credentials and retry" or offers a "Contact Admin" button.
- **BDD**: `Given` A user is unauthenticated `When` they enter valid credentials and click login `Then` A token is issued and they are redirected to their role's page.

#### J2. Role-Based Page Visibility Control
- **Multi-Role Collaboration**:
  - **Roles Involved**: Ian (Developer, `Developer`), David (FinOps Analyst, `FinOps_Analyst`), Fiona (Security Reviewer, `Security_Reviewer`)
  - **Collaboration Details**: Developer Ian and FinOps Analyst David each only see pages relevant to their duties post-login. When Ian attempts to access David's cost console, the system blocks him.
- **User Goal**: Ensure users only access menus and workspaces relevant to their roles, enforcing Separation of Duties (SoD) and least privilege.
- **Acceptance Criteria**:
  1. The sidebar navigation and system menus dynamically show or hide workspace links based on the user's role.
  2. When a user manually modifies the browser URL to bypass restrictions (e.g., a Developer visiting `/admin`), the route guards intercept and redirect them to a 403 Forbidden page.
  3. The back-end APIs must simultaneously validate the user's role in the token, returning a 403 HTTP code on unauthorized requests.
- **Operational Flow**: 1. User logs in and enters dashboard. 2. Views the sidebar and accesses authorized modules. 3. **AI Reset/Manual Adjust**: Menus auto-update; if a misconfiguration occurs, administrators can "Partial Reset" the session cache.
- **System Feedback**:
  - **Success**: Smoothly renders authorized menus and widgets. **Next Step**: Click to enter the workspace.
  - **Failure**: Redirects to a "403 Access Denied" page. **Next Step**: Prompts "You do not have permission to view this page" and provides "Return to Home" or "Request Access" buttons.
- **BDD**: `Given` Ian's role is Developer `When` he manually alters the URL path to `/admin` `Then` The route guard intercepts and renders a 403 Access Denied page.

#### J3. Administrator's Permission Management & Assignment Panel
- **Multi-Role Collaboration**:
  - **Roles Involved**: Catherine (Admin, `Project_Admin`), Ian (Developer, `Developer`)
  - **Collaboration Details**: Catherine enters the permission console to edit Ian's role. Upon saving, Ian's privileges update instantly, and the action is logged to the Audit Log for Fiona to review.
- **User Goal**: Enable administrators to inspect all accounts and dynamically assign or revoke user privileges based on project duties.
- **Acceptance Criteria**:
  1. Provides an administrator-only RBAC panel listing all users, their assigned roles, and permission scopes.
  2. Allows administrators to edit and save role changes, updating database states and applying new privileges to the target user upon their next refresh.
  3. Enforces mandatory audit logging for role updates, specifying the administrator, the target user, and change details.
- **Operational Flow**: 1. Admin accesses "User Management Panel". 2. Selects a user, modifies their role, and saves. 3. **AI Reset/Manual Adjust**: Click "Reset User" to restore platform default privileges.
- **System Feedback**:
  - **Success**: A green toast prompts "✔ User role updated to SRE," updating the table state. **Next Step**: Prompts "Check audit log to confirm changes."
  - **Failure**: A red alert prompts "✘ Update failed: Cannot downgrade the last administrator." **Next Step**: Prompts "Assign another admin first."
- **BDD**: `Given` Administrator Catherine is logged into the console `When` she changes Ian's role to SRE and saves `Then` The user state updates, and a corresponding audit entry is logged.

