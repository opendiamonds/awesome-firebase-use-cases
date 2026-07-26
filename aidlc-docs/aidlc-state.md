# AI-DLC State Tracking

> Cloud-360 AIDLC workflow state. Updated automatically by AIDLC stages and manually by maintainers.

## 中文版

### 專案資訊

- **Project Name**: Cloud-360
- **Project Type**: Brownfield（已有 SRS / architecture / user stories / ADR baseline）
- **AIDLC Version**: 1.0.1（見 `.aidlc/aidlc-rules/VERSION`；最初採用 0.1.8，見 ADR-0006）
- **AIDLC 啟用 PRs**: `feat/aidlc-framework-rules`（PR1）→ `feat/aidlc-docs-migration`（PR2）→ `Doreen`（目錄重組）
- **Current Stage**: **A3 Lens Editor Code Gen 完成** — 待手動驗收（Fiona 編輯／新評核／403）；摘要 `construction/a3/code/lens-editor-summary.md`；Operations PLACEHOLDER

### Workspace State

- **Existing Code**: Yes（`backend/`、`frontend/`、`scripts/`、`tools/`、`workflows/`）
- **Programming Languages**: Python（FastAPI backend）、TypeScript（React frontend）、Markdown / Mermaid / draw.io（specs）
- **Build System**: Frontend Vite build + Backend FastAPI；CI 跑 validation。
- **Project Structure**: Spec-Driven repo + A1/A2 application code（Architecture Design 模組）
- **Workspace Root**: `/Users/luojingting/Documents/opendimand/cloud`

### Extension Configuration

| Extension | Enabled | Decided By | Note |
|---|---|---|---|
| `extensions/security/baseline/` | ✅ | ADR-0006 + user choice | Hard constraint，IAM/encryption/network/audit |
| `extensions/testing/property-based/` | ✅ | ADR-0006 + user choice | Hard constraint，IaC、cost calc、agent routing |
| `extensions/bilingual-docs/` | ✅ | ADR-0005 + ADR-0006 | 永遠強制（無 opt-in） |

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
  - Reverse Engineering: ✅（`inception/reverse-engineering/`：business-overview、architecture、code-structure、api-documentation、component-inventory、technology-stack、dependencies）
  - Requirements Analysis: ✅（A, B, C 三模組已完成）
  - User Stories: ✅（A, B, C 三模組繁中版已完成；含 J 與 A4/A5）
  - Workflow Planning: ✅（`inception/plans/execution-plan.md`）
  - Application Design: ✅（baseline：`system-architecture.md`、`frontend-backend-specification.md`；units：`unit-of-work*.md`）
  - Units Generation: ✅（A1／A2／**A3**／A4／A5／J → U-A1／U-A2／**U-A3**／U-A4／U-A5／U-J；見 `application-design/unit-of-work*.md`；B–H 尚未建 unit）
  - **A3 增量 Inception**: WD ✅ → RA ✅ → US ✅ → WP ✅ → AD ✅ → UG ✅
  - **A3／U-A3 Construction**: FD ✅ → NFR Req ✅ → NFR Design ✅ → Code Generation ✅ → Build&Test 🔄；**增量 Findings←Lens／PDF** Code Gen ✅
  - **A3 Lens Editor 增量 Inception**: RA ✅ → US ✅ → WP ✅ → UG（併 U-A3）✅
  - **A3 Lens Editor Construction**: FD ✅ → Code Gen ✅（待手動驗收）
- 🟢 Construction
  - A1 Code Generation: ✅（舊版 httpx；已由 Agent SDK 路徑取代）
  - A1 Agent SDK Refactor: ✅ Phase 1 + Phase 2 code done — 待手動驗收 Step 6／8（見 `construction/plans/a1-agent-sdk-code-generation-plan.md`、`construction/a1/code/a1-core-gap-summary.md`）
  - A4 Chat Persistence: ✅ Code done — 待手動驗收（見 `construction/plans/a4-chat-persistence-plan.md`、`construction/a4/code/chat-persistence-summary.md`）
  - Role & Permission Redesign: ✅ Core done — A1/A2/A4 語意、Sidebar 隱藏、細項無 J；待 WebSocket JWT／手動 E2E（見 `construction/plans/role-permission-design.md`、`role-permission-construction-plan.md`）
  - A2 Code Generation: 🔄（核心功能已完成，部分 AC 待補 — 見下方驗收對照；summary：`construction/a2/code/canvas-editing-summary.md`）
  - A5 Sharing & Collaboration: ✅ Core done — 待 cursor 廣播／WS JWT（summary：`construction/a5/code/sharing-collab-summary.md`）
  - Pillar J Identity & RBAC: ✅ Core + **J5 done**（註冊 pending、授權申請頁、核准／拒絕、停用刪除；見 `construction/j/`）
  - Build and Test: 🔄（含 A3；backend **61** tests OK；frontend build OK；仍缺 HTTP 整合測／WS JWT／前端 UT）
- 🟡 Operations: 🔄
  - Deployment: ✅ `.github/workflows/deploy.yml` — push 至 `ut` 觸發，於 192.168.10.10 的 self-hosted runner（`cloud360-10-10`）執行 `docker compose up -d --build`；對外經 Cloudflare Tunnel 開放 `cloud360.danniel.cc`（見 ADR-0007）
  - Agentic Automation: ✅ 六支 gh-aw workflow（contract-guard、pr-reviewer、issue-triage、doc-sync、release-watch、daily-digest）
  - Observability / Incident Playbooks: ⏳

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

---

## English Version

### Project Information

- **Project Name**: Cloud-360
- **Project Type**: Brownfield (existing SRS / architecture / user stories / ADR baseline)
- **AIDLC Version**: 1.0.1 (see `.aidlc/aidlc-rules/VERSION`; initially adopted 0.1.8 per ADR-0006)
- **AIDLC Adoption Branch**: `Doreen` (restructuring: .agents/ → AIDLC three-layer architecture + docs/ → aidlc-docs/inception/ migration completed)
- **Current Stage**: **A3 Lens Editor Code Gen done** — awaiting manual acceptance (Fiona edit / new review / 403); summary `construction/a3/code/lens-editor-summary.md`; Operations PLACEHOLDER

### Workspace State

- **Existing Code**: Yes (`backend/`, `frontend/`, `scripts/`, `tools/`, `workflows/`)
- **Programming Languages**: Python (FastAPI backend), TypeScript (React frontend), Markdown / Mermaid / draw.io (specs)
- **Build System**: Frontend Vite build + Backend FastAPI; CI runs validation.
- **Project Structure**: Spec-Driven repo + A1/A2 application code (Architecture Design module)
- **Workspace Root**: `/Users/luojingting/Documents/opendimand/cloud`

### Extension Configuration

| Extension | Enabled | Decided By | Note |
|---|---|---|---|
| `extensions/security/baseline/` | ✅ | ADR-0006 + user choice | Hard constraint: IAM/encryption/network/audit |
| `extensions/testing/property-based/` | ✅ | ADR-0006 + user choice | Hard constraint: IaC, cost calc, agent routing |
| `extensions/bilingual-docs/` | ✅ | ADR-0005 + ADR-0006 | Always enforced (no opt-in) |

> At the requirements analysis stage, `core-workflow.md` need not re-ask about these three extensions; they are enabled by default.

### Existing Inception Artifacts

| Artifact | Location | History |
|---|---|---|
| SRS | `aidlc-docs/inception/requirements/cloud-360-srs.md` | git mv from `docs/srs/cloud-360-srs.md` (includes Doreen enhanced A1/A2, B1/B2, C1/C2 structure) |
| User Stories | `aidlc-docs/inception/user-stories/stories.md` | Split from `core-pillars.md` (26 stories) |
| User Personas | `aidlc-docs/inception/user-stories/personas.md` | Split from `core-pillars.md` (11 rich personas) |
| Application Design | `aidlc-docs/inception/application-design/system-architecture.md` | git mv from `docs/architecture/system-architecture.md` |
| ADR-0001 ~ ADR-0006 | `aidlc-docs/inception/decisions/` | git mv from `docs/adr/` + checkout from main |

### Phase Tracking

- 🔵 Inception
  - Workspace Detection: ✅
  - Reverse Engineering: ✅ (`inception/reverse-engineering/` full as-built set)
  - Requirements Analysis: ✅ (Modules A, B, C completed)
  - User Stories: ✅ (including J and A4/A5)
  - Workflow Planning: ✅ (`inception/plans/execution-plan.md`)
  - Application Design: ✅ (baseline + unit-of-work artifacts)
  - Units Generation: ✅ (A1/A2/**A3**/A4/A5/J → U-A1/U-A2/**U-A3**/U-A4/U-A5/U-J; B–H still unassigned)
  - **A3 incremental Inception**: WD ✅ → RA ✅ → US ✅ → WP ✅ → AD ✅ → UG ✅
  - **A3 / U-A3 Construction**: FD ✅ → NFR Req ✅ → NFR Design ✅ → Code Generation ✅ → Build&Test 🔄; **Findings←Lens amendment** Code Gen ✅
- 🟢 Construction
  - A1 Code Generation: ✅ (legacy httpx superseded by Agent SDK path)
  - A1 Agent SDK Refactor: ✅ Phase 1 + Phase 2 code done — pending manual Steps 6/8 (see `construction/plans/a1-agent-sdk-code-generation-plan.md`, `construction/a1/code/a1-core-gap-summary.md`)
  - A4 Chat Persistence: ✅ Code done — pending manual acceptance (see `construction/plans/a4-chat-persistence-plan.md`, `construction/a4/code/chat-persistence-summary.md`)
  - Role & Permission Redesign: ✅ Core done — A1/A2/A4 semantics, Sidebar hide-when-empty, no Pillar J in matrix UI; pending WebSocket JWT / manual E2E (see `construction/plans/role-permission-design.md`, `role-permission-construction-plan.md`)
  - A2 Code Generation: 🔄 (core features done; partial AC gaps — see acceptance table below; summary: `construction/a2/code/canvas-editing-summary.md`)
  - A5 Sharing & Collaboration: ✅ Core done — pending cursor broadcast / WS JWT (summary: `construction/a5/code/sharing-collab-summary.md`)
  - Pillar J Identity & RBAC: ✅ Core + **J5 done** (pending registration, authorization queue, approve/reject, deactivate-delete; see `construction/j/`)
  - Build and Test: 🔄 (includes A3; backend **61** tests OK; frontend build OK; still missing HTTP integration / WS JWT / frontend UT)
- 🟡 Operations: 🔄
  - Deployment: ✅ `.github/workflows/deploy.yml` — triggered by push to `ut`, runs `docker compose up -d --build` on the self-hosted runner at 192.168.10.10 (`cloud360-10-10`); exposed publicly at `cloud360.danniel.cc` through a Cloudflare Tunnel (see ADR-0007)
  - Agentic Automation: ✅ six gh-aw workflows (contract-guard, pr-reviewer, issue-triage, doc-sync, release-watch, daily-digest)
  - Observability / Incident Playbooks: ⏳

### Construction Unit Acceptance (A2)

| AC / Scenario | Status | Notes |
|---|---|---|
| AI partial edit (based on existing XML) | ✅ | `agent_router.py` Partial Updates + `current_xml` |
| Box-select node group then send to AI | ⚠️ Partial | Relies on manual draw.io selection + text prompt; no selection extraction |
| Preserve connections | ✅ | system prompt + merge logic |
| Modification history + one-click Undo | ❌ | No AI change tracking; draw.io native undo only |
| Save diagram to DB | ✅ | `UserDiagram` + POST/PUT API |
| Multi-file management + dropdown switch | ✅ | `WorkspacePage` diagram selector |
| Share with other users | ✅ | `ShareModal` + `diagram_shares` |
| Multi-user real-time co-edit (XML sync) | ✅ | WebSocket `/api/collab/ws/{diagramId}` |
| Multi-user cursor visibility | ❌ | WebSocket broadcasts XML only; no cursor protocol |
| Auto-load latest draft on workspace entry | ✅ (A4) | Bootstrap restores `last_opened_diagram_id` + that diagram's chat |
