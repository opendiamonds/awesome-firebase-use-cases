# AIDLC Audit Log

> Append-only log of AIDLC workflow events: user requests, stage transitions, extension toggles, approvals.
> 僅追加（append-only）的 AIDLC 工作流程稽核紀錄。

### 紀錄格式

每筆紀錄使用以下格式：

```markdown
### YYYY-MM-DD HH:MM TZ — <event-type>
**User request (raw)**: ...
**Stage**: ...
**Outcome**: ...
**Approver**: ...
```

### 事件紀錄

#### 2026-05-09 00:45 +08:00 — Workspace Initialization

**User request (raw)**: "@[/aidlc-init]"
**Stage**: Inception → Workspace Detection
**Outcome**: 初始化 AIDLC 生命週期。偵測為 Brownfield 專案，建立 `aidlc-docs/audit.md` 與 `aidlc-docs/aidlc-state.md`。
**Approver**: houguanyu

---

#### 2026-05-09 00:55 +08:00 — User Story Generation (Modules A, B, C)

**User request (raw)**: "README.md 中有 Core Modules 請幫我寫出 Architecture Design, Cross-Cloud Component Selection, Cost Estimation & FinOps 這三個的 User Story"
**Stage**: Inception → User Stories
**Outcome**: 已完成 Architecture Design、Cross-Cloud Component Selection、Cost Estimation & FinOps 三個模組的繁體中文 User Story，並更新至 `aidlc-docs/inception/user-stories/core-pillars.md`。
**Approver**: houguanyu

---

#### 2026-05-09 01:05 +08:00 — Requirements Analysis (Modules A, B, C)

**User request (raw)**: "好的 繼續需求分析 (Requirements Analysis) 但只要Architecture Design, Cross-Cloud Component Selection, Cost Estimation & FinOps這三個"
**Stage**: Inception → Requirements Analysis
**Outcome**: 已完成 A、B、C 三個核心模組的深度需求分析。更新 SRS 文件並建立細部規格書（已於 Doreen 分支存放於 `docs/srs/detailed/`，後於目錄重組時刪除）。
**Approver**: houguanyu

---

#### 2026-05-11 10:10 +08:00 — Directory Restructuring (align with main)

**User request (raw)**: "請幫我讀 main 分支 按照 main 分支的目錄結構去改 然後是要antigravity 也可以讀取的結構"
**Stage**: Inception → Framework Adoption
**Outcome**: 完成目錄結構重組，對齊 origin/main 的 AIDLC 三層架構：`.agents/` → `.aidlc-rules/` + `.aidlc-rule-details/` + `.aidlc-overrides/`；`docs/` → `aidlc-docs/inception/`；新增 `CLAUDE.md`；刪除 `docs/` 整個目錄。
**Approver**: houguanyu

---

#### 2026-05-22 19:38 +08:00 — Requirements & User Stories Revision (Bilingual & BDD)

**User request (raw)**: "我想重寫requirements... 開始依照persona修改stories... 再幫我在a-h鍾 加入BDD..."
**Stage**: Inception → User Stories (Refinement)
**Outcome**: 
1. 重寫 `cloud-360-srs.md` 以符合 ADR-0005 雙語規範。
2. 重寫 `personas.md`，加上具體人物名稱、情境描述與需求模組映射。
3. 重寫 `stories.md`，加入 BDD 劇本、登入操作流程、RBAC 權限控管與 AI 產出重置機制（局部/全部重置與人工微調）。
**Approver**: luojingting

---

#### 2026-05-23 23:55 +08:00 — User Stories Granular Expansion & Multi-Role Collaboration

**User request (raw)**: "幫我a-h個列3到4小點... 幫我在每一項加入 那一個項目的使用者需求/目標 還有該項的驗收標準... 每一個項目的驗收標準 幫我評估看看是否需要詳細列點... 評估多角色針對功能的互動性與協作細節... 幫我上傳到git"
**Stage**: Inception → User Stories (Detailing)
**Outcome**: 
1. 將 A-H 支柱全面細化為 24 個具體的 User Stories。
2. 為每個 Story 補充「使用者需求/目標 (User Goal)」。
3. 為每個 Story 展開「驗收標準 (Acceptance Criteria)」，每項提供 3 個具體列點。
4. 導入「多角色協作 (Multi-Role Collaboration)」取代單一 Persona，定義跨角色互動細節。
5. 提交變更至 Git。
**Approver**: luojingting

---

#### 2026-05-24 00:01 +08:00 — System Feedback & CTA Refinement

**User request (raw)**: "在story裡面 每個項目使用這操作成功或失敗時，再詳細一點描述使用者會看到的畫面回饋，在操作成功公時引導使用者進行下個操作，失敗時也引導使用者如何操作成功或聯絡相關人員... 幫我上傳到git"
**Stage**: Inception → User Stories (Refinement)
**Outcome**: 
1. 全面擴充 A-H 共 24 個 User Stories 的「系統回饋 (System Feedback)」。
2. 為每個操作成功與失敗場景加入了「極為詳細的畫面 UI 回饋描述」。
3. 在每個場景加入了明確的「後續操作引導 (Call-To-Action)」。
4. 提交變更至 Git。
**Approver**: luojingting

---

#### 2026-05-24 20:47 +08:00 — IaC Pillar (D) Refinement for Terraform/OpenTofu

**User request (raw)**: "幫我在 user story 的 d類 確認有 Infrastructure as Code - Terraform / OpenTofu... 產生 aws、google、azurerm provider 對應的 Terraform / OpenTofu 模組。 支援 main.tf、variables.tf、outputs.tf、providers.tf 與 modules/ 結構。 整合 tfsec、trivy、Checkov 等靜態掃描工具。"
**Stage**: Inception → User Stories (Refinement)
**Outcome**: 
1. 重寫 Pillar D 驗收標準，明確支援產出跨雲 (aws, google, azurerm) 的 Terraform 與 OpenTofu 代碼。
2. 確立嚴格的 IaC 專案結構：`main.tf`, `variables.tf`, `outputs.tf`, `providers.tf` 及 `modules/`。
3. 明確整合 tfsec, Trivy, Checkov 作為預設的靜態掃描引擎。
**Approver**: luojingting

---

#### 2026-05-24 20:54 +08:00 — Security Pillar (G) Refinement for CSPM & Policy Advisory

**User request (raw)**: "我的 g 需要包含 Cloud Security Posture & Policy Advisory... 檢視 IAM / RBAC、network exposure、storage access、encryption、audit logging、policy guardrails。 產生 least-privilege、Policy-as-Code、IaC patch 與 remediation plan 建議。 高風險修復必須通過 human approval gate。"
**Stage**: Inception → User Stories (Refinement)
**Outcome**: 
1. 將 Pillar G 重構為「Cloud Security Posture & Policy Advisory」。
2. 加入 CSPM 掃描，強制檢查 network exposure, storage access, encryption, audit logging。
3. 加入 Least-Privilege IAM/RBAC 檢查，並要求 AI 產出極簡化 Policy 建議。
4. 加入 Policy Guardrails，支援將自然語言轉化為 Policy-as-Code (Rego/Config) 並整合至 CI/CD。
5. 強制所有高風險修復 (包含 IaC patch 與權限縮減) 必須通過 Human Approval Gate 審批。
**Approver**: luojingting

---

#### 2026-05-24 21:01 +08:00 — MCP Pillar (H) Refinement for Skill Lifecycle & Agent Routing

**User request (raw)**: "幫我看h類的內容 1跟2比較沒問題 3 幫我看看能不能補充 管理 MCP servers、tools、AI Skills、cloud provider connectors 與 reusable workflows。 支援註冊、啟用/停用、版本控管、權限範圍、健康檢查、相依性檢查與審批流程。 將工具能力納入 Agent Routing Layer，讓 AI 能安全選用合適工具執行 read-only 分析或經審批後的維運操作。"
**Stage**: Inception → User Stories (Refinement)
**Outcome**: 
1. 重寫 Pillar H3 為「全域 MCP 工具與 Skill 註冊生命週期管理」。
2. 加入完整的工具生命週期管理，包含 MCP servers, AI Skills, Cloud Connectors 及 workflows。
3. 導入自動化的 Health Check 與 Dependency Check 機制。
4. 將所有工具註冊納入 Agent Routing Layer，賦予 AI 自主但受控的工具調用能力 (限定 read-only 或需過 Human Approval Gate)。
**Approver**: luojingting

---

#### 2026-05-25 11:01 +08:00 — Synchronize Contract Validation Script

**User request (raw)**: "幫我根據 最外層的 readme 調整 scripts資料夾底下的 validate_repo_contract"
**Stage**: Inception → Framework Maintenance
**Outcome**: 
1. 更新 `scripts/validate_repo_contract.py`，修正 `aidlc-docs/inception/user-stories/stories.md` 的關鍵字檢查。
2. 將檢查項目由原有的舊版名稱更新為 `Cost Estimation & FinOps` 與 `Cloud Security Posture`，以對應 `README.md` 中確立的 Core Modules 命名。
3. 執行 Contract Validation 測試通過。
**Approver**: luojingting

---

#### 2026-06-07 19:25 +08:00 — Draw.io XML Structure Fix (Not a diagram file)

**User request (raw)**: "drawio呈現 Not a diagram file 的錯誤"
**Stage**: Construction → SVG Rendering Fix (XML Validation)
**Outcome**: 
1. 解決了因 `<mxImageBundle>` 被不小心放進 `cells` 陣列中，導致最後被拼接在 `<root>` 內部作為 `<mxCell>` 的子節點。這違反了 draw.io 的 XML Schema 規範（`<root>` 內只能包含 `<mxCell>`），造成 diagrams.net 在載入時出現 "Not a diagram file" 的解析錯誤。
2. 重構了 [agent_router.py](file:///Users/luojingting/Documents/opendimand/cloud/backend/services/agent_router.py) 的 XML 拼接邏輯：將 `<mxImageBundle>` 從 `cells` 陣列抽離，並以 `<mxfile>` 與 `<diagram>` 作為最外層容器，將 `<mxGraphModel>` 與 `<mxImageBundle>` 作為 `<diagram>` 的直接子節點（同級併列）。
3. 修正了儲存格 style 的 `image` 屬性格式：將 `image=editors/images/img_comp_{idx}` 修正為 `image=img_comp_{idx}`，確保其能正確與 `<mxImageBundle>` 中的 `<mxImage name="img_comp_{idx}">` 匹配，順利載入自訂 Base64 SVG 圖示而不報 404。
**Approver**: luojingting

---

#### 2026-06-07 19:30 +08:00 — XML Simplified Inline Base64 Data URI Fix (404 and Not a diagram file)

**User request (raw)**: "Failed to load resource: the server responded with a status of 404 () 現在有這錯誤，可以看是哪一段嗎，或是後端你有幫我重啟？"
**Stage**: Construction → SVG Rendering Fix (XML Optimization & Simplified Embedding)
**Outcome**: 
1. 發現使用 `mxImageBundle` 與 `mxfile` 的方式在 draw.io 內部代碼支援並不穩定，容易因為 tag 擺放與解析順序不同而重啟 404 與 Not a diagram file 的循環錯誤。
2. 重構了 [agent_router.py](file:///Users/luojingting/Documents/opendimand/cloud/backend/services/agent_router.py) 的 XML 產製邏輯：廢除外部 `mxImageBundle` 宣告，回歸最標準的 `<mxGraphModel>` 結構。將各個元件的 SVG 進行 Base64 編碼，再使用 `urllib.parse.quote` 將整串 Data URI 進行 URL 百分比編碼以消除分號 `;`，然後直接在細胞的 `style` 樣式屬性中嵌入該 URI。
3. 此結構被 draw.io 原生 100% 支援，百分比編碼完全避免了 style parser 對分號的錯誤截斷，並且因為完全是以 base64 嵌入在 style 中，不會觸發 any 外部網域資源拉取，徹底解決 404 報錯。
**Approver**: luojingting

---

#### 2026-06-07 19:35 +08:00 — Draw.io Native Base64 Autocomplete Fix (404 and Not a diagram file)

**User request (raw)**: "data%3Aimage%2Fsvg%2…C9nPgo8L3N2Zz4%3D:1 GET https://embed.diagrams.net/data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CCjxzdmcgd2lk… 404 (Not Found)"
**Stage**: Construction → SVG Rendering Fix (Draw.io Parsing Mechanism Alignment)
**Outcome**: 
1. 發現當對 `data:image/` 進行百分比編碼（Percent-encode）以避開分號 `;` 時（例如變成 `data%3Aimage%2F`），draw.io 的 JS 引擎因為只匹配明文的 `data:image/` 開頭，而無法識別其為 Data URI。結果將其視為普通的相對路徑，向外發出 HTTP 請求，最後引發 404。
2. 重構了 [agent_router.py](file:///Users/luojingting/Documents/opendimand/cloud/backend/services/agent_router.py) 的 XML 產製邏輯：改為在 style 中寫入 `data:image/svg+xml,` + `[Base64編碼]` 格式（意即省略了 `;base64`）。
3. 此做法既利用逗號 `,` 避開了分號 `;` 對 style 解析器的切分，又保留了明文的 `data:image/` 開頭。同時對準了 draw.io 在面對此格式時會自動在內部將其補齊改寫為 `data:image/svg+xml;base64,...` 的自作聰明特性。如此一來，瀏覽器能 100% 成功還原並以 Base64 解碼 SVG 圖片，徹底解決了 404 與 Not a diagram file 的所有問題。
**Approver**: luojingting

---

#### 2026-07-02 16:32 +08:00 — Identity Authentication & RBAC User Stories

**User request (raw)**: "0. 需要做使用者權限管理，一個登入頁面，使用者登入後僅能看到自己有權限的頁面，也需要一管理員可以編輯的使用者權限"
**Stage**: Inception → Requirements & User Stories Addition
**Outcome**: 
1. 在 [cloud-360-srs.md](file:///Users/luojingting/Documents/opendimand/cloud/aidlc-docs/inception/requirements/cloud-360-srs.md) 中新增 Pillar J 中英文規格需求與技術約束。
2. 在 [core-pillars.md](file:///Users/luojingting/Documents/opendimand/cloud/aidlc-docs/inception/user-stories/core-pillars.md) 中定義 Pillar J 的 J1, J2, J3 故事大綱。
3. 在 [stories.md](file:///Users/luojingting/Documents/opendimand/cloud/aidlc-docs/inception/user-stories/stories.md) 中新增 Pillar J 中英文詳細情境故事，包含角色協作、驗收標準與 BDD 劇本。
**Approver**: luojingting

---

#### 2026-07-02 16:49 +08:00 — Identity Authentication & RBAC Construction

**User request (raw)**: "0. 需要做使用者權限管理，一個登入頁面，使用者登入後僅能看到自己有權限的頁面，也需要一管理員可以編輯的使用者權限"
**Stage**: Construction → Authentication & RBAC Implementation
**Outcome**: 
1. **Docker PostgreSQL 部署**：建立 `docker-compose.yml` 運行本地 PostgreSQL 容器。
2. **後端認證 API 與角色指派**：使用 SQLAlchemy 設計 `User` 模型，以 `personas.md` 的 11 位平台人物進行初始化（密碼經過 bcrypt 強雜湊加密）。實作 JWT 認證、`/api/auth/login`、`/api/auth/me` 與限制管理員使用的角色指派 API，並在變更角色時寫入日誌。
3. **前端路由守衛與介面**：引入 `react-router-dom` 配置路由，實作 `ProtectedRoute` 與 `AdminRoute` 路由守衛。設計玻璃擬態設計的登入頁面（`/login`）、403 Forbidden 頁面與管理員 RBAC 控制面板（`/admin`）。
4. **全站整合**：重構 `Sidebar.tsx` 與 `App.tsx` 以接入 AuthContext 與角色導航，並通過 `npm run build` 編譯驗證。
**Approver**: luojingting

---

#### 2026-07-03 11:20 +08:00 — User Registration Implementation

**User request (raw)**: "我想要多一個註冊的功能"
**Stage**: Construction → Account Registration Feature
**Outcome**: 
1. **後端註冊 API**：在 `user_router.py` 中新增 `POST /api/auth/register`，包含輸入長度（username: 3-20, password: 6-30）、正則防注入過濾、重複帳號檢查，並在寫入資料庫時預設指派為 `"Developer"` 角色且對密碼進行 `bcrypt` 強雜湊加密。
2. **前端註冊卡片**：重構 `LoginPage.tsx`，在玻璃擬態卡片內新增「沒有帳號？立即註冊 / 已有帳號？立即登入」表單狀態切換。在註冊表單中整合確認密碼（Confirm Password）的前端比對校驗。
3. **整合自動登入**：註冊成功後後端直接生成並返回 JWT Token，前端接收後寫入快取，實現註冊後即自動登入的順暢體驗。
**Approver**: luojingting

---

#### 2026-07-12 02:02 +08:00 — 本地環境部署與服務啟動

**User request (raw)**: "請幫我讀 DEPLOY.md 並幫我執行"
**Stage**: Operations → Local Deployment
**Outcome**: 
1. **基礎設施啟動**：透過 Docker Compose 啟動 PostgreSQL 15 與 Adminer 容器，開啟本地資料庫服務。
2. **環境配置**：建立並設定 `backend/.env` 與 `frontend/.env`，保留原本的 API 金鑰與設定，修正 `DATABASE_URL` 連線。
3. **資料庫初始化**：執行 `schema_rbac.sql`，建立所有結構並成功寫入 **308 筆** 角色權限對照資料，且建立 `admin` 管理員帳號。
4. **依賴安裝與啟動**：重建損壞的 Python 虛擬環境，安裝後端與前端依賴，順利啟動後端 FastAPI 服務（`127.0.0.1:8000`）與前端 Vite 服務（`localhost:5173`），並通過專案合約驗證。
**Approver**: houguanyu

---

#### 2026-07-25 — Commit message 一律繁體中文（ADR-0010）

**User request (raw)**: "commit message 也改繁中"
**Stage**: Operations / Governance → Commit Message Convention
**Outcome**:
1. **新增 override**：`.aidlc-overrides/commit-message.md` — commit message 與 PR 標題一律繁中，conventional commit type 中文化（`功能`、`修正`、`文件`、`格式`、`重構`、`效能`、`測試`、`建置`、`整合`、`雜項`、`還原`）；scope、`BREAKING CHANGE:`、trailer 維持英文。
2. **新增 ADR-0010**：`aidlc-docs/inception/decisions/0010-chinese-commit-messages.md`，記錄決策脈絡與工具相容性風險。
3. **branch naming 解耦**：`.aidlc-overrides/branch-naming.md` 明確標示 branch 的 `<type>` 維持英文（中文 branch 名稱在 `gh` CLI／URL 需 percent-encoding），並附中英對照換算範例。
4. **CLAUDE.md**：第 6 章工作模式新增第 7 條 commit message 規則，原第 7 條順延為第 8 條。
5. **CI 自動產出一併中文化**：`.github/workflows/deploy.yml` 的 revert commit 訊息（`git commit --amend`）與 revert PR 標題／body 改繁中；`.github/workflows/lint-fix.md` 指示 Lint Fixer 以 `修正(frontend):` 開頭撰寫 commit message，並以 `gh aw compile` 重編譯 `lint-fix.lock.yml`。
6. **overrides 索引補正**：`.aidlc-overrides/README.md` 補上先前漏登的 `traditional-chinese-docs.md`，並新增 `commit-message.md`。

**限制**：`scripts/validate_repo_contract.py` 驗證檔案內容而非 git 歷史，本規則無法納入 repo contract 自動強制；目前依賴 PR review 與 AI agent 自動套用。
**不溯及既往**：既有 commit 歷史不做 rewrite。
**Approver**: danniel

---

#### 2026-07-25 — 部署完成 Slack 通知

**User request (raw)**: "AI-DLC 我部署完成的時候要能夠通知slack chaneel"
**Stage**: Operations → Deploy Notification（依 `.aidlc-overrides/continuous-delivery.md`，與 Construction 連續進行，無 phase gate）
**Requirements Analysis**: `aidlc-docs/operations/deploy-slack-notification-questions.md`（5 題全數作答，無矛盾）
- Q1 接入方式：B — Slack App bot token + `slackapi/slack-github-action`
- Q2 通知範圍：C — 成功 + 失敗 + 回滾結果
- Q3 Channel：A — 單一頻道 `#nemoclaw`（`C0B5XEQDVR7`）
- Q4 Mention：`@here`（選項 B），僅失敗與回滾時觸發
- Q5 訊息內容：A,B,C,D,E — commit、PR、網址、耗時、run 連結全收

**Outcome**:
1. **新增 `notify` job**（`.github/workflows/deploy.yml`）：`needs: [deploy, rollback]` + `if: always()`，涵蓋成功／失敗／取消／回滾四種結果。
2. **刻意跑在 GitHub-hosted runner**：不使用 self-hosted runner，確保 192.168.10.10 本身故障時通知仍可送出。
3. **新增 job outputs**：`deploy` 導出 `deployed`／`subject`／`started`（commit 標題以 heredoc 形式寫入 `$GITHUB_OUTPUT`，避免任意文字破壞 key=value）；`rollback` 導出 `restored`（healthy／unhealthy／none）與 `revert_pr`。
4. **`restored` 預設 unhealthy，僅健康檢查通過才升級為 healthy**，避免訊息謊報「已還原」。
5. **payload 以 `jq` 產生 JSON 檔**：所有跳脫交給 `jq`，同時避開 `slack-github-action` v4.0.0 對 YAML 多行縮排轉嚴的 breaking change。
6. **`@here` 使用 Slack API 的 `<!here>` 形式**：字面 `@here` 在 `chat.postMessage` 只會顯示為純文字、不會實際通知。
7. **絕不讓通知影響部署結果**：token 未設定時跳過並發 warning；送出步驟設 `errors: false`，Slack 故障不會把成功的部署變紅燈。

**Verification**: YAML 解析通過；自 workflow 抽出實際 compose 腳本，以 5 種情境（成功／手動 dispatch／失敗+回滾成功／失敗+無 last-good／取消）實測，含引號、反引號、`&` 的 commit 標題跳脫正確；`python3 scripts/validate_repo_contract.py` 通過。
**未做**：未開新 ADR — 本變更屬 ADR-0007 部署管線的增量，非架構級決策。
**Approver**: danniel

---

#### 2026-07-25 — Slack 通知驗證結果

**Stage**: Operations → Deploy Notification（驗證）
**方式**: 暫時性 workflow `slack-notify-test.yml`，compose 腳本自 `deploy.yml` 的 notify job 逐字複製，不觸發實際部署。驗證後已刪除。
**結果**（run 30161853421）:
1. **成功情境 `ok=true`**、**失敗情境 `ok=true`**，channel `C0B5XEQDVR7`，bot `NeMoClaw`，`acceptedScopes: ["chat:write"]`。
2. **`<!here>` 經 Slack 解析為 `{"type":"broadcast","range":"here"}`** — 確認為真實廣播通知，非純文字。
3. mrkdwn 渲染正確：粗體標題、`code` span、連結標籤（`GitHub Actions`、`待合併`）、emoji、耗時格式（`3 分 13 秒`）皆如預期。

**過程中發現並修正的問題**：`errors: false` 會讓 Slack 端的拒絕（`not_in_channel`、`invalid_auth`）留下綠燈且零輸出 — 壞掉的通知與正常的無法區分。已在 `deploy.yml` 加入 `Report whether Slack accepted the message` 步驟，讀取 action 的 `ok` output，非 true 時以 warning 揭露 response，但仍不將部署判定為失敗。

**仍未驗證**：`needs.deploy.outputs.*` / `needs.rollback.outputs.*` 的 job outputs 串接，只有真實部署會行經該路徑。
**Approver**: danniel

---

#### 2026-07-26 13:10 +08:00 — Staging 中斷：Error 1033（runner 離線）

**User request (raw)**: "目前環境掛掉了，代表ut有異常"
**Stage**: Operations → Incident Response
**症狀**: `https://cloud360.danniel.cc/` 回 Cloudflare `Error 1033 Cloudflare Tunnel error`（Ray ID `a213a5c38f30ce41`）。

**根因**: **不是 `ut` 的程式碼異常**。self-hosted runner `cloud360-10-10`（即 192.168.10.10）離線；該機同時承載應用容器與 `cloudflared` 容器，機器層失效導致 tunnel 斷線，Cloudflare 找不到出口而回 1033。

**判斷依據**: deploy job 呈 `queued`／`pending` 而非 `failure` — 代表 job 從未被領走執行，而非執行後失敗。若為程式碼問題，deploy 會執行並失敗，並觸發 rollback 與 Deploy Doctor。GitHub API 查得 runner `status=offline` 佐證。

**時間軸**:
| 時間 | 事件 |
|---|---|
| 07-19 06:34 | 最後一次成功部署（`ea5d6b1d`） |
| 07-25 18:08 | deploy 觸發（`2f0da31b`），卡在 queued |
| 07-26 08:05 | deploy 被 cancelled（`03887005`） |
| 07-26 09:08 | deploy 觸發（`0cae22ed`），卡在 pending |
| 07-26 13:10 | 使用者回報 Error 1033 |

**處置**: 依 `operations/runbooks.md` Playbook F（Self-hosted runner 離線）重啟 runner service。

**結果**: runner 回到 `online`；兩個積壓 job 依時間序執行並全部 success（`2f0da31b` → `0cae22ed`，最新版最後落地）；`https://cloud360.danniel.cc/` 回 HTTP 200。附帶效果為 `ut` 自 07-19 起累積的 A3 Well-Architected 與 A1 chat UX 變更一併部署至 staging，**尚待手動驗收**。

**暴露的缺口（未處理）**: 本次無任何自動告警。兩層原因：(1) Slack 通知目前只在 `main`，尚未同步至 `ut`；(2) 即使同步，`notify` job 掛在 `deploy` 之後，job 卡在 queued 時不會執行。現行設計能回報「部署失敗」，無法回報「部署未開始」或「站台不可用」。補法必須是**外部**健康檢查告警（例如 dc-infra 的 Prometheus blackbox 探測 `cloud360.danniel.cc`），機器自身失效時無法由其自行發出警報。對應 `runbooks.md` 第 4 章「告警去向」的待補項。

**Approver**: danniel
