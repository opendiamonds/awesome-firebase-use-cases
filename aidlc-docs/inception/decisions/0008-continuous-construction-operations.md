# ADR 0008: Continuous Construction ↔ Operations (deviation from linear AIDLC phasing)

> 本文件必須同時包含中文版與英文版。
> This document must include both Chinese and English versions.

## 中文版

- Status: Accepted
- Date: 2026-07-16
- Amends: 對 upstream AIDLC 三段式（Inception → Construction → Operations）中「Construction → Operations 線性交棒」假設的偏離
- Related: ADR-0007（self-hosted deployment pipeline）、`.aidlc-overrides/continuous-delivery.md`

### Context

Upstream AIDLC（`awslabs/aidlc-workflows`）將開發流程分為三 phase：🔵 Inception、🟢 Construction、🟡 Operations。其規則的預設敘事是依序推進——Construction（code generation、build & test）完成後，才交棒進入 Operations（deployment、observability、incident playbooks）。

Cloud-360 的實際運作方式與此線性模型不符：

1. 我們已建立一條 PR → 合併進 `ut` → 部署到自有 staging 的**連續管線**（ADR-0007）。`ci.yml`（build/test，屬 Construction）與 `deploy.yml`（部署，屬 Operations）之間沒有 phase gate，中間也沒有「Construction 已完成」的交棒點。

2. 我們的 agentic workflows 同時橫跨兩者：UI Regression / Lint Fixer / Contract Guard 屬 build/test 側，Deploy Doctor / deploy rollback 屬運維側，它們在同一個 PR 生命週期內並行運作。

3. `aidlc-docs/aidlc-state.md` 的 Construction 與 Operations 區塊實務上同時處於 🔄，並非一段完成才進下一段。

若繼續沿用「Construction 完成 → 才進 Operations」的線性敘事，會與現況矛盾，也會誘導 AI agent 用錯誤的 phase 語言描述專案、或錯誤地把部署/觀測工作延後到「Operations phase」。

### Decision

1. **採用連續模型取代線性交棒。** 在 Cloud-360，Construction 與 Operations 以連續 DevOps 迴圈運作：build ↔ deploy 之間無 phase gate；Operations（deploy + 觀測 + 應變）是與 Construction 交織的持續循環，而非其後繼階段。

2. **以 override 落地。** 規範寫入 `.aidlc-overrides/continuous-delivery.md`。依 CLAUDE.md 的載入順序，`.aidlc-overrides/` 最後載入且與 upstream 衝突時永遠勝出，因此本決策自動覆蓋 upstream 的線性假設，無需修改 `.aidlc-rule-details/`（升級時會被整批替換）。

3. **不放寬範圍邊界。** 本 ADR 只改「Construction↔Operations 的關係模型」。雲端供應商 production 仍在範圍外（ADR-0001/0002/0007）。observability、incident playbooks、SLO/on-call 等尚未落地的維運能力仍是真實待辦。

4. **狀態描述規範。** 不再以「已進入 Construction / Operations 階段」這類線性 phase 語言描述專案；改為直接陳述能力，細部狀態以 `aidlc-state.md` 為準。CLAUDE.md 第 1 章已據此更新。

### Consequences

**正面**：

- 方法論敘事與實際的 CI/CD 連續交付一致，消除「code 已寫好但還沒『進入 Operations phase』」這種假矛盾。
- AI agent 規劃工作時會把部署、回滾、觀測視為同一條 pipeline 的一部分，而非延後事項。
- override 層承擔偏離，upstream 升級不受影響、也不會把此決策洗掉。

**負面 / 風險**：

- 偏離 upstream 預設流程，未來對照 upstream 文件時需記得本專案的差異（README 與本 ADR 為指引）。
- 「連續」不等於「完成」：仍需留意 observability / incident playbook 這類真維運工作不因模型改變而被視為已達成。

**後續**：

- 落實 Operations 迴圈中尚缺的環節（observability、incident playbooks），並在 `aidlc-state.md` 追蹤。

---

## English Version

- Status: Accepted
- Date: 2026-07-16
- Amends: the "Construction → Operations linear handoff" assumption within upstream AIDLC's three-phase model (Inception → Construction → Operations)
- Related: ADR-0007 (self-hosted deployment pipeline), `.aidlc-overrides/continuous-delivery.md`

### Context

Upstream AIDLC (`awslabs/aidlc-workflows`) divides the lifecycle into three phases: 🔵 Inception, 🟢 Construction, 🟡 Operations. Its default narrative is sequential — Operations (deployment, observability, incident playbooks) is entered only after Construction (code generation, build & test) completes.

Cloud-360 does not operate that way:

1. We already run a **continuous pipeline** — PR → merge into `ut` → deploy to self-hosted staging (ADR-0007). There is no phase gate between `ci.yml` (build/test, a Construction concern) and `deploy.yml` (deployment, an Operations concern), and no "Construction is done" handoff point between them.

2. Our agentic workflows span both at once: UI Regression / Lint Fixer / Contract Guard on the build/test side, Deploy Doctor / deploy rollback on the operations side, all working within the same PR lifecycle.

3. The Construction and Operations sections of `aidlc-docs/aidlc-state.md` are, in practice, both 🔄 simultaneously — not one completed before the next begins.

Keeping the "finish Construction → then Operations" narrative would contradict reality and would lead AI agents to describe the project with the wrong phase language, or to wrongly defer deployment/observability work to a later "Operations phase".

### Decision

1. **Adopt a continuous model in place of a linear handoff.** In Cloud-360, Construction and Operations run as one continuous DevOps loop: no phase gate between build and deploy; Operations (deploy + observe + respond) is a continuous cycle interleaved with Construction, not its successor stage.

2. **Encode it as an override.** The rule lives in `.aidlc-overrides/continuous-delivery.md`. Per CLAUDE.md's load order, `.aidlc-overrides/` loads last and always wins over conflicting upstream rules, so this decision overrides the upstream linear assumption without editing `.aidlc-rule-details/` (which is wholesale-replaced on upgrade).

3. **No scope relaxation.** This ADR changes only the *relationship model* between Construction and Operations. Cloud-provider production remains out of scope (ADR-0001/0002/0007). Operational capabilities not yet built — observability, incident playbooks, SLO/on-call — remain genuine to-dos.

4. **State-description rule.** Stop describing the project with linear phase language ("now in the Construction / Operations stage"); state capabilities directly, with `aidlc-state.md` as the source of detailed status. CLAUDE.md §1 has been updated accordingly.

### Consequences

**Positive**:

- The methodology narrative matches the actual continuous CI/CD delivery, removing the false tension of "code is written but we haven't 'entered the Operations phase' yet".
- AI agents plan deployment, rollback, and observability as part of the same pipeline as code, not as deferred items.
- The override layer carries the deviation; upstream upgrades are unaffected and will not wipe this decision.

**Negative / risks**:

- A deviation from the upstream default flow; when cross-referencing upstream docs, the project's difference must be kept in mind (the README and this ADR are the guides).
- "Continuous" is not "complete": real operational work (observability, incident playbooks) must not be treated as done merely because the model changed.

**Follow-up**:

- Build out the still-missing links in the Operations loop (observability, incident playbooks) and track them in `aidlc-state.md`.
