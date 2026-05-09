# AI-DLC State Tracking

> Cloud-360 AIDLC workflow state. Updated automatically by AIDLC stages and manually by maintainers.

## 中文版

### 專案資訊

- **Project Name**: Cloud-360
- **Project Type**: Brownfield（已有 SRS / architecture / user stories / ADR baseline）
- **AIDLC Version**: 0.1.8（見 `.aidlc-rule-details/VERSION`）
- **AIDLC 啟用 PR**: `feat/aidlc-framework-rules`（PR1：rules + CLAUDE.md，docs/ 不動）
- **Current Stage**: INCEPTION — Adoption / Onboarding（PR1 完成後即進入正式 Inception）

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

### 已存在 Inception Artifacts（PR1 階段尚未遷移）

PR1 維持 `docs/` 結構，PR2 才會搬到 `aidlc-docs/inception/...`：

| Artifact | 目前位置 | PR2 後位置 |
|---|---|---|
| SRS | `docs/srs/cloud-360-srs.md` | `aidlc-docs/inception/requirements/cloud-360-srs.md` |
| User Stories | `docs/user-stories/core-pillars.md` | `aidlc-docs/inception/user-stories/core-pillars.md` |
| Application Design | `docs/architecture/system-architecture.md` | `aidlc-docs/inception/application-design/system-architecture.md` |
| ADR-0001 ~ ADR-0006 | `docs/adr/` | `aidlc-docs/inception/decisions/` |

### Phase Tracking

- 🔵 Inception
  - Workspace Detection: ✅（本檔案即為產出）
  - Reverse Engineering: ⏳（待 PR2 後正式啟動，先反推 SRS / architecture）
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
- **AIDLC Adoption PR**: `feat/aidlc-framework-rules` (PR1: rules + CLAUDE.md, no docs migration)
- **Current Stage**: INCEPTION — Adoption / Onboarding (formal Inception begins after PR1 lands)

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

### Existing Inception Artifacts (not migrated in PR1)

PR1 keeps the `docs/` layout untouched; PR2 will move them under `aidlc-docs/inception/...`:

| Artifact | Current Path | After PR2 |
|---|---|---|
| SRS | `docs/srs/cloud-360-srs.md` | `aidlc-docs/inception/requirements/cloud-360-srs.md` |
| User Stories | `docs/user-stories/core-pillars.md` | `aidlc-docs/inception/user-stories/core-pillars.md` |
| Application Design | `docs/architecture/system-architecture.md` | `aidlc-docs/inception/application-design/system-architecture.md` |
| ADR-0001 ~ ADR-0006 | `docs/adr/` | `aidlc-docs/inception/decisions/` |

### Phase Tracking

- 🔵 Inception
  - Workspace Detection: ✅ (this file is the output)
  - Reverse Engineering: ⏳ (post-PR2, reverse-engineer existing SRS / architecture)
  - Requirements Analysis: ⏳
  - User Stories: 🔄 (baseline exists; to be refined under AIDLC)
  - Workflow Planning: ⏳
  - Application Design: 🔄 (baseline exists; to be refined under AIDLC)
  - Units Generation: ⏳
- 🟢 Construction: ⏳
- 🟡 Operations: ⏳
