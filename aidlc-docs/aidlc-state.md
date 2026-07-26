# AI-DLC State Tracking

> Cloud-360 AIDLC workflow state. Updated automatically by AIDLC stages and manually by maintainers.

### 專案資訊

- **Project Name**: Cloud-360
- **Project Type**: Brownfield（已有 SRS / architecture / user stories / ADR baseline）
- **AIDLC Version**: 0.1.8（見 `.aidlc-rule-details/VERSION`）
- **AIDLC 啟用 PRs**: `feat/aidlc-framework-rules`（PR1）→ `feat/aidlc-docs-migration`（PR2）→ `Doreen`（目錄重組）
- **Current Stage**: CONSTRUCTION — A1/A4 待手動 E2E；**RBAC 角色權限重設計實作中**（見 `construction/plans/role-permission-construction-plan.md`）

### Workspace State

- **Existing Code**: Yes（`backend/`、`frontend/`、`firebase_templates/`、`scripts/`、`tools/`、`workflows/`）
- **Programming Languages**: Python（FastAPI backend）、TypeScript（React frontend）、Markdown / Mermaid / draw.io（specs）
- **Build System**: Frontend Vite build + Backend FastAPI；CI 跑 validation。
- **Project Structure**: Spec-Driven repo + A1/A2 application code（Architecture Design 模組）
- **Workspace Root**: `/Users/luojingting/Documents/opendimand/cloud`

### Extension Configuration

| Extension | Enabled | Decided By | Note |
|---|---|---|---|
| `extensions/security/baseline/` | ✅ | ADR-0006 + user choice | Hard constraint，IAM/encryption/network/audit |
| `extensions/testing/property-based/` | ✅ | ADR-0006 + user choice | Hard constraint，IaC、cost calc、agent routing |
| （文件語言：繁體中文）| ✅ | ADR-0009 | 取代 bilingual-docs/ADR-0005；所有文件一律繁中 |

> `core-workflow.md` requirements analysis 階段不需再次詢問三項 extensions 是否啟用，預設皆為 enabled。

### 已存在 Inception Artifacts

| Artifact | 位置 | History 來源 |
|---|---|---|
| SRS | `aidlc-docs/inception/requirements/cloud-360-srs.md` | git mv from `docs/srs/cloud-360-srs.md`（含 Doreen 強化版 A1/A2, B1/B2, C1/C2） |
| User Stories | `aidlc-docs/inception/user-stories/stories.md` | 由 `core-pillars.md` 拆分產出（含 26 個 stories） |
| User Personas | `aidlc-docs/inception/user-stories/personas.md` | 由 `core-pillars.md` 拆分產出（含 11 個 rich personas） |
| Application Design | `aidlc-docs/inception/application-design/system-architecture.md` | git mv from `docs/architecture/system-architecture.md` |
| ADR-0001 ~ ADR-0006 | `aidlc-docs/inception/decisions/` | git mv from `docs/adr/` + checkout from main |

### Phase Tracking

- 🔵 Inception
  - Workspace Detection: ✅
  - Reverse Engineering: ⏳
  - Requirements Analysis: ✅（A, B, C 三模組已完成）
  - User Stories: ✅（A, B, C 三模組繁中版已完成）
  - Workflow Planning: ⏳
  - Application Design: 🔄（已有 baseline）
  - Units Generation: ⏳
- 🟢 Construction
  - A1 Code Generation: ✅（舊版 httpx；已由 Agent SDK 路徑取代）
  - A1 Agent SDK Refactor: ✅ Phase 1 + Phase 2 code done — 待手動驗收 Step 6／8（見 `construction/plans/a1-agent-sdk-code-generation-plan.md`、`construction/a1/code/a1-core-gap-summary.md`）
  - A4 Chat Persistence: ✅ Code done — 待手動驗收（見 `construction/plans/a4-chat-persistence-plan.md`、`construction/a4/code/chat-persistence-summary.md`）
  - Role & Permission Redesign: ✅ Core done — A1/A2/A4 語意、Sidebar 隱藏、細項無 J；待 WebSocket JWT／手動 E2E（見 `construction/plans/role-permission-design.md`、`role-permission-construction-plan.md`）
  - A2 Code Generation: 🔄（核心功能已完成，部分 AC 待補 — 見下方驗收對照）
  - Build and Test: 🔄（`.github/workflows/ci.yml`：repo contract、frontend lint/typecheck/build、backend import check、Docker build。**尚無測試套件** — backend job 只做 import check）
- 🟡 Operations: 🔄
  - Deployment: ✅ `.github/workflows/deploy.yml` — push 至 `ut` 觸發，於 192.168.10.10 的 self-hosted runner（`cloud360-10-10`）執行 `docker compose up -d --build`；對外經 Cloudflare Tunnel 開放 `cloud360.danniel.cc`（見 ADR-0007）
  - Agentic Automation: ✅ 十支 gh-aw workflow（contract-guard、pr-reviewer、issue-triage、spec-sync、code-drift-alert、release-watch、daily-digest、lint-fix、deploy-doctor、ui-regression）
  - Incident Playbooks: ✅ `aidlc-docs/operations/runbooks.md`（SLO + 7 則 playbook）
  - Observability: 🔄 Prometheus + Grafana + blackbox 已建（`grafana.danniel.cc`，於 dc-infra 維運）；主動告警待 Telegram bot token
  - Deploy Notification: ✅ `deploy.yml` 的 `notify` job 以 Slack bot token（`SLACK_BOT_TOKEN`）發送成功／失敗／回滾結果至 `#nemoclaw`（`C0B5XEQDVR7`）；失敗與回滾帶 `<!here>`。跑在 GitHub-hosted runner，故 192.168.10.10 本身故障時仍可送達（需求釐清見 `operations/deploy-slack-notification-questions.md`）

### Construction Unit 驗收（A2）

| AC / 場景 | 狀態 | 備註 |
|---|---|---|
| AI 局部編輯（基於現有 XML） | ✅ | `agent_router.py` Partial Updates + `current_xml` |
| 框選節點群組後送 AI | ⚠️ 部分 | 依賴 draw.io 手動框選 + 文字描述，未抽取 selection |
| 連線保留 | ✅ | system prompt + merge 邏輯 |
| 修改歷史 + 一鍵 Undo | ❌ | 未實作 AI 變更追蹤；僅 draw.io 內建 undo |
| 儲存架構圖至 DB | ✅ | `UserDiagram` + POST/PUT API |
| 多檔案管理 + 下拉切換 | ✅ | `WorkspacePage` diagram selector |
| 分享給其他使用者 | ✅ | `ShareModal` + `diagram_shares` |
| 多人即時共編（XML 同步） | ✅ | WebSocket `/api/collab/ws/{diagramId}` |
| 多人游標可見 | ❌ | WebSocket 僅廣播 XML，未實作 cursor |
| 進入工作區自動載入最新草稿 | ✅（A4） | bootstrap 還原 `last_opened_diagram_id` + 該圖聊天 |
