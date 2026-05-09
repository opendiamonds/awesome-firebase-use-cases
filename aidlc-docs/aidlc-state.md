# AI-DLC State Tracking

> Cloud-360 AIDLC workflow state. Updated automatically by AIDLC stages and manually by maintainers.

## 中文版

### 專案資訊

- **Project Name**: Cloud-360
- **Project Type**: Brownfield（已有 SRS / architecture / user stories / ADR baseline）
- **AIDLC Version**: 0.1.8（見 `.aidlc-rule-details/VERSION`）
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

### 已存在 Inception Artifacts（PR2 完成後）

| Artifact | 位置 | History 來源 |
|---|---|---|
| SRS | `aidlc-docs/inception/requirements/cloud-360-srs.md` | git mv from `docs/srs/cloud-360-srs.md` |
| User Stories | `aidlc-docs/inception/user-stories/core-pillars.md` | git mv from `docs/user-stories/core-pillars.md` |
| Application Design | `aidlc-docs/inception/application-design/system-architecture.md` | git mv from `docs/architecture/system-architecture.md` |
| ADR-0001 ~ ADR-0006 | `aidlc-docs/inception/decisions/` | git mv from `docs/adr/` |

### Phase Tracking

- 🔵 Inception
  - Workspace Detection: ✅（本檔案即為產出）
  - Reverse Engineering: ⏳（PR2 已完成 artifact migration，可正式啟動以反推 SRS / architecture 與既有程式碼一致性）
  - Requirements Analysis: ⏳
  - User Stories: 🔄（已有 baseline，待 AIDLC stage 補強）
  - Workflow Planning: ⏳
  - Application Design: 🔄（已有 baseline，待 AIDLC stage 補強）
  - Units Generation: ⏳
- 🟢 Construction: ⏳
- 🟡 Operations: ⏳

---

## English Version

### Project Information

- **Project Name**: Cloud-360
- **Project Type**: Brownfield (existing SRS / architecture / user stories / ADR baseline)
- **AIDLC Version**: 0.1.8 (see `.aidlc-rule-details/VERSION`)
- **AIDLC Adoption PRs**: `feat/aidlc-framework-rules` (PR1: rules + CLAUDE.md) → `feat/aidlc-docs-migration` (PR2: docs/ → aidlc-docs/inception/ migration completed)
- **Current Stage**: INCEPTION — Framework adoption and artifact migration complete; ready to enter formal AIDLC stages (reverse-engineering / requirements analysis)

### Workspace State

- **Existing Code**: Yes (`firebase_templates/`, `scripts/`, `tools/`, `workflows/` — mostly specs / templates / validators)
- **Programming Languages**: Python (validate script), Markdown / Mermaid / draw.io (specs)
- **Build System**: No application build yet; CI only runs validation.
- **Project Structure**: Spec-Driven repo (no application code yet)
- **Workspace Root**: `/Users/jiangzhengdao/User/Developer/Opendiamonds/cloud-360`

### Extension Configuration

| Extension | Enabled | Decided By | Note |
|---|---|---|---|
| `extensions/security/baseline/` | ✅ | ADR-0006 + user choice | Hard constraint: IAM/encryption/network/audit |
| `extensions/testing/property-based/` | ✅ | ADR-0006 + user choice | Hard constraint: IaC, cost calc, agent routing |
| `extensions/bilingual-docs/` | ✅ | ADR-0005 + ADR-0006 | Always enforced (no opt-in) |

> The Requirements Analysis stage in `core-workflow.md` does not need to re-prompt the user about these three extensions — they are enabled by default.

### Existing Inception Artifacts (post-PR2)

| Artifact | Path | History Source |
|---|---|---|
| SRS | `aidlc-docs/inception/requirements/cloud-360-srs.md` | git mv from `docs/srs/cloud-360-srs.md` |
| User Stories | `aidlc-docs/inception/user-stories/core-pillars.md` | git mv from `docs/user-stories/core-pillars.md` |
| Application Design | `aidlc-docs/inception/application-design/system-architecture.md` | git mv from `docs/architecture/system-architecture.md` |
| ADR-0001 ~ ADR-0006 | `aidlc-docs/inception/decisions/` | git mv from `docs/adr/` |

### Phase Tracking

- 🔵 Inception
  - Workspace Detection: ✅ (this file is the output)
  - Reverse Engineering: ⏳ (PR2 artifact migration complete; can now reverse-engineer the existing SRS / architecture against the codebase)
  - Requirements Analysis: ⏳
  - User Stories: 🔄 (baseline exists; to be refined under AIDLC)
  - Workflow Planning: ⏳
  - Application Design: 🔄 (baseline exists; to be refined under AIDLC)
  - Units Generation: ⏳
- 🟢 Construction: ⏳
- 🟡 Operations: ⏳
