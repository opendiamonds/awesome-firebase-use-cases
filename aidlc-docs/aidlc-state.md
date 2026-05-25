# AI-DLC State Tracking

> Cloud-360 AIDLC workflow state. Updated automatically by AIDLC stages and manually by maintainers.

## 中文版

### 專案資訊

- **Project Name**: Cloud-360
- **Project Type**: Brownfield（已有 SRS / architecture / user stories / ADR baseline）
- **AIDLC Version**: 0.1.8（見 `.aidlc-rule-details/VERSION`）
- **AIDLC 啟用 PRs**: `Doreen`（目錄重組：.agents/ → AIDLC 三層架構 + docs/ → aidlc-docs/inception/ 完成）
- **Current Stage**: INCEPTION — 已完成 framework adoption + artifact migration，可進入正式 AIDLC stage
- **AIDLC 啟用 PRs**: `feat/aidlc-framework-rules`（PR1：rules + CLAUDE.md）→ `feat/aidlc-docs-migration`（PR2：docs/ → aidlc-docs/inception/ 完成）
- **Current Stage**: INCEPTION — 已完成 framework adoption + artifact migration，可進入正式 AIDLC stage（reverse-engineering / requirements analysis）

### Workspace State

- **Existing Code**: Yes（`firebase_templates/`、`scripts/`、`tools/`、`workflows/`，但主要為 spec / template / validator）
- **Programming Languages**: Python（validate script），Markdown / Mermaid / draw.io（specs）
- **Build System**: 尚無 application build；CI 僅跑 validation。
- **Project Structure**: Spec-Driven repo（尚未產製 application code）
- **Workspace Root**: `/Users/jiangzhengdao/User/Developer/Opendiamonds/cloud-360`

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
  - Reverse Engineering: ⏳
  - Requirements Analysis: ✅（A, B, C 三模組已完成）
  - User Stories: ✅（A, B, C 三模組繁中版已完成）
  - Workflow Planning: ⏳
  - Application Design: 🔄（已有 baseline）
  - Units Generation: ⏳
- 🟢 Construction: ⏳
- 🟡 Operations: ⏳

---

## English Version

### Project Information

- **Project Name**: Cloud-360
- **Project Type**: Brownfield (existing SRS / architecture / user stories / ADR baseline)
- **AIDLC Version**: 0.1.8 (see `.aidlc-rule-details/VERSION`)
- **AIDLC Adoption Branch**: `Doreen` (restructuring: .agents/ → AIDLC three-layer architecture + docs/ → aidlc-docs/inception/ migration completed)
- **Current Stage**: INCEPTION — Framework adoption and artifact migration complete; ready to enter formal AIDLC stages

### Workspace State

- **Existing Code**: Yes (`firebase_templates/`, `scripts/`, `tools/`, `workflows/` — mostly specs / templates / validators)
- **Programming Languages**: Python (validate script), Markdown / Mermaid / draw.io (specs)
- **Build System**: No application build yet; CI only runs validation.
- **Project Structure**: Spec-Driven repo (no application code yet)
- **Workspace Root**: `/Users/houguanyu/Desktop/Work/Cathaybk/Opendiamonds/cloud-360`

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
  - Reverse Engineering: ⏳
  - Requirements Analysis: ✅ (Modules A, B, C completed)
  - User Stories: ✅ (Traditional Chinese A, B, C completed)
  - Workflow Planning: ⏳
  - Application Design: 🔄 (baseline exists)
  - Units Generation: ⏳
- 🟢 Construction: ✅ (A1 Code Generation)
- 🟡 Operations: ⏳
