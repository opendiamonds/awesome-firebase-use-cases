# Inception Plans

> AIDLC inception-phase planning artifacts for Cloud-360.
> Cloud-360 inception 階段的規劃產出。

## 中文版

### 目錄內容

`aidlc-docs/inception/plans/` 存放 AIDLC inception 階段（workflow planning / unit planning / cross-pillar 排程）的規劃產出。

| 檔案 | 說明 |
|---|---|
| [`development-plan.html`](development-plan.html) | 9 pillar / 26 user story 的 wave-based 開發計劃；含 Kanban 看板、相依圖、story table、pillar 細節、NFR 與風險。**建議用瀏覽器開啟**：`open aidlc-docs/inception/plans/development-plan.html`。 |
| [GitHub Project (live)](https://github.com/users/Dannielchung/projects/1) | live kanban，26 個 draft items，欄位：Wave / Pillar / Story ID。可直接拖卡片改 status |

### 與其他 inception 子目錄的關係

- `requirements/` — SRS（需求規格）來源。
- `user-stories/` — pillar 與 user stories 來源。
- `application-design/` — system architecture（agent routing、integration layer 等）。
- `decisions/` — ADRs（架構級決策）。
- `plans/`（**本目錄**） — 把上述輸入整理成可執行的 wave 與 sprint。

### 維護準則

- 計劃檔案（HTML / md）更新時要記錄到 `aidlc-docs/audit.md`。
- 涉及範圍變動（例如新增 pillar、wave 重切）需另開 ADR。
- markdown 檔案（例如本 README）必須雙語（per ADR-0005）；HTML 內也建議含中英對照區塊。

---

## English Version

### Contents

`aidlc-docs/inception/plans/` holds AIDLC inception-phase planning artifacts: workflow planning, unit planning, cross-pillar scheduling.

| File | Purpose |
|---|---|
| [`development-plan.html`](development-plan.html) | Wave-based development plan covering all 9 pillars and 26 user stories; includes Kanban board, dependency graph, story table, pillar details, NFRs, and known risks. **Open in a browser**: `open aidlc-docs/inception/plans/development-plan.html`. |
| [GitHub Project (live)](https://github.com/users/Dannielchung/projects/1) | Live kanban with 26 draft items; custom fields Wave / Pillar / Story ID. Drag cards to update status. |

### Relationship to other inception subdirectories

- `requirements/` — SRS source.
- `user-stories/` — pillars and user stories source.
- `application-design/` — system architecture (agent routing, integration layer, etc.).
- `decisions/` — ADRs (architecture decisions).
- `plans/` (**this directory**) — turns the above into executable waves and sprints.

### Maintenance rules

- Updates to plan files (HTML or md) are recorded in `aidlc-docs/audit.md`.
- Scope changes (new pillar, wave restructure) require a new ADR.
- Markdown files (this README included) must be bilingual per ADR-0005; HTML files are encouraged to include side-by-side Chinese/English sections.
