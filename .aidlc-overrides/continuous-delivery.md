# Cloud-360 Continuous Construction ↔ Operations

> Project override rule. Takes precedence over any conflicting upstream guidance.
> 專案 override 規則。與 upstream 任何衝突指示相比，本規則優先。

### 規範

Upstream AIDLC 將 🟢 **Construction**（NFR、functional design、code generation、build & test）與 🟡 **Operations**（deployment、observability、incident playbooks）描述為依序的兩個 phase，帶有「Construction 完成後才交棒到 Operations」的隱含線性假設。

**在 Cloud-360，這個線性交棒模型不適用，一律以下列連續模型取代：**

1. **build ↔ deploy 之間沒有 phase gate。** 從 PR → 合併進 `ut` → 部署到自有 staging（見 ADR-0007）是單一連續管線。「寫 code / build / test」與「部署 / 運行」屬於同一條流程，不是先後兩段。

2. **Operations 是持續的迴圈，不是一次性階段。** Operations 的內涵是「deploy + 觀測 + 應變」的持續循環，與 Construction 交織並行，而非跟在 Construction 之後。任何 code 變更都同時是一次潛在的維運事件（部署、回滾、觀測）。

3. **不得以「Construction 尚未完成」為由延後 Operations 工作，反之亦然。** 兩者並行推進；`aidlc-docs/aidlc-state.md` 的 Construction 與 Operations 區塊同時維護、可同時處於 🔄。

4. **保留的邊界。** 本 override 只改「Construction↔Operations 的關係模型」，不改**範圍邊界**：雲端供應商 production 仍在範圍外（見 CLAUDE.md 第 5 章、ADR-0007）。Operations 中尚未落地的維運學科（observability、incident playbooks、SLO/on-call）仍是真實待辦，連續模型不等於它們已完成。

### 對 AI agent 的實務指示

- 規劃工作時，把部署、回滾、觀測、告警視為與 code 實作同一條 pipeline 的環節，而非「之後才做的 Operations phase」。
- 描述專案狀態時，不要宣告「已進入 Construction / Operations 階段」這類線性 phase 語言；直接陳述具備哪些能力，並以 `aidlc-state.md` 為細部狀態來源。
- 完整脈絡與決策理由見 ADR-0008。
