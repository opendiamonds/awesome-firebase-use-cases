# Test Case Management Plan — Cloud-360

> 本文件必須同時包含中文版與英文版。
> This document must include both Chinese and English versions.

## 中文版

- Status: Draft（規劃中，待選定工具後定案）
- Date: 2026-07-13
- 關聯：[[ui-regression]] workflow、`frontend/tests/e2e/regression.spec.ts`、user stories（A1/A2/A4/Pillar J）

### 1. 目標與現況

目標：建立一套能同時管理**自動化測案**與**未來手動測案**的測案管理機制，並提供跨時間的**通過率趨勢儀表板**與**需求↔測案的追溯**。

現況（已具備）：
- 自動化測案 = 程式碼：`frontend/tests/e2e/regression.spec.ts`（6 個核心免-LLM 案例）。
- 執行：每個 PR 由 `.github/workflows/ui-regression.md` 起臨時 stack 跑 Playwright，agent 在 PR 留言失敗案例。
- 結果：GitHub Checks（單次 pass/fail）+ `pw-report.json` artifact。

缺口：
- 沒有跨 run 的**歷史通過率趨勢 / 儀表板**。
- 沒有**手動測案**的登錄、執行與紀錄能力（未來需求）。
- 沒有**需求↔測案↔結果**的追溯矩陣。

### 2. 核心原則：每種測案有單一真實來源

| 測案類型 | 真實來源 | 執行 | 結果去向 |
|---|---|---|---|
| 自動化 | Playwright spec（repo code） | GitHub Actions（PR 觸發） | Checks + TCM 儀表板 |
| 手動（未來） | TCM 平台 | TCM 的 test run（人工執行） | TCM 儀表板 |

自動化測案**不搬進** TCM 當主檔（會造成雙份維護）；TCM 只保存自動化案例的**中繼資料與歷史結果**，本體仍是 code。手動測案則以 TCM 為主檔。兩者在同一個儀表板匯總。

### 3. 工具選型（關鍵決策）

需要一個能容納「手動 + 自動 + 儀表板 + 追溯」的 TCM。兩條路：

**方案 A — Kiwi TCMS（自架，建議）**
- 開源、可 Docker 自架，與現有 192.168.10.10 基礎設施一致（可用剛建好的部署管線 + Cloudflare Tunnel 上線）。
- 支援手動測案、測試計畫、test run、需求追溯、API 匯入自動化結果。
- 資料留在自有主機，符合本專案「不外送、避免外部 SaaS 依賴」的範圍紀律（ADR-0001）。
- 代價：需自行維運（多一個服務）；自動化整合走 API，較 Qase 的原生 reporter 費工。

**方案 B — Qase（SaaS 免費方案）**
- 上手最快、`qase-playwright` reporter 自動回寫每次 run、儀表板與趨勢開箱即用。
- 代價：資料進外部 SaaS、免費方案有額度上限、多一個外部帳號與 API token。

**建議**：方案 A（Kiwi TCMS 自架）。理由：你已自架整套服務並重視資料自主，Kiwi 可用同一條部署管線上線；手動測案量還小，維運負擔可控。若後續發現維運成本過高、或需要更順的自動化整合，再評估切換 Qase。

⚠️ 選定後需一筆記錄：自架走 ADR（新服務納入 scope）；選 Qase 則因引入外部 SaaS，建議開新 ADR 評估資料外送。

### 4. 整合架構

```text
自動化：PR → ui-regression → Playwright → pw-report.json
                                   │
                                   └── (reporter/API) ──► TCM test run（自動）
手動：  release 前 → TCM 手動 test run（人工執行）
                                   │
              兩者匯入同一 TCM 專案 ──► 儀表板（通過率趨勢、flaky）
                                   └► 追溯：TCM case ⇄ user story（A1/A2/A4/J…）
```

- 追溯：TCM 每個 case 加一個「story_id」欄位，對應 `aidlc-docs/inception/user-stories/stories.md`。
- 自動化回寫：在 Playwright 每個 test 加註 case 對應 id（annotation），run 後把結果推到 TCM。

### 5. 分階段落地

- **Phase 0（現在）**：維持 Playwright + Checks 現狀；定案工具（方案 A/B）。
- **Phase 1**：建 TCM 專案，測試套件結構鏡射 AIDLC pillar（A1/A2/A4/J）；把現有 6 個自動化案例登錄為 TCM case，接上自動回寫（API token 存為 GitHub secret）。
- **Phase 2**：為未自動化的流程撰寫**手動測案**（例如 A1 自然語言生成架構圖 —— 這條在 CI 刻意跳過，因為會呼叫 OpenRouter 產生費用），建立每次 release 的手動 test cycle。
- **Phase 3**：儀表板 + 追溯矩陣（story ⇄ case ⇄ result）；可選加一支 gh-aw agent，在 release 時彙整測試覆蓋摘要。

### 6. GitHub 與 TCM 的分工

- **GitHub**：自動化測試 code、CI 執行、PR gating（自動化在 PR 上的 pass/fail 真實來源）。
- **TCM**：測案目錄（手動 + 自動中繼資料）、測試計畫、手動執行、跨 run 趨勢儀表板、追溯矩陣。

### 7. 待決事項

1. 工具：方案 A（Kiwi 自架）或 B（Qase SaaS）？
2. 是否為此開新 ADR（自架納 scope／SaaS 資料外送）？
3. 追溯粒度：case 對應到 story（A1）即可，或需細到 acceptance criteria？

---

## English Version

- Status: Draft (planning; finalised once the tool is chosen)
- Date: 2026-07-13
- Related: the [[ui-regression]] workflow, `frontend/tests/e2e/regression.spec.ts`, user stories (A1/A2/A4/Pillar J)

### 1. Goal and Current State

Goal: a test-case management practice that covers **automated** cases and **future manual** cases, with a cross-time **pass-rate trend dashboard** and **requirement ↔ test-case traceability**.

Already in place:
- Automated cases = code: `frontend/tests/e2e/regression.spec.ts` (6 core LLM-free cases).
- Execution: every PR, `.github/workflows/ui-regression.md` spins up an ephemeral stack, runs Playwright, and the agent comments failing cases on the PR.
- Results: GitHub Checks (per-run pass/fail) + the `pw-report.json` artifact.

Gaps:
- No cross-run **pass-rate trend / dashboard**.
- No ability to author, execute, and record **manual test cases** (a future need).
- No **requirement ↔ case ↔ result** traceability matrix.

### 2. Core Principle: One Source of Truth per Case Type

| Case type | Source of truth | Execution | Results land in |
|---|---|---|---|
| Automated | Playwright specs (repo code) | GitHub Actions (PR-triggered) | Checks + TCM dashboard |
| Manual (future) | The TCM platform | TCM test runs (by hand) | TCM dashboard |

Automated cases are **not** migrated into the TCM as their master copy (that would mean double maintenance); the TCM holds only their **metadata and historical results**, while the code stays the source of truth. Manual cases are mastered in the TCM. Both roll up to one dashboard.

### 3. Tool Selection (the key decision)

We need a TCM that holds manual + automated cases, dashboards, and traceability. Two paths:

**Option A — Kiwi TCMS (self-hosted, recommended)**
- Open-source, Docker-self-hostable, consistent with the existing 192.168.10.10 infrastructure (it can go live through the deploy pipeline and Cloudflare Tunnel we just built).
- Supports manual cases, test plans, test runs, requirement traceability, and API import of automated results.
- Data stays on an owned host, honouring this project's "no external SaaS, keep data in-house" scope discipline (ADR-0001).
- Cost: you operate one more service; automated integration goes through its API, more work than Qase's native reporter.

**Option B — Qase (SaaS, free tier)**
- Fastest to adopt; the `qase-playwright` reporter auto-pushes every run; dashboards and trends out of the box.
- Cost: data goes to an external SaaS, the free tier has quotas, and it adds an external account and API token.

**Recommendation**: Option A (self-hosted Kiwi TCMS). You already self-host the whole stack and value data ownership; Kiwi can go live on the same pipeline, and the manual-case volume is small enough to keep operations manageable. If operating it proves costly, or smoother automated integration is needed, reassess Qase.

⚠️ Either way, record the decision: self-hosting warrants an ADR (a new service enters scope); choosing Qase warrants an ADR to weigh sending data to an external SaaS.

### 4. Integration Architecture

```text
Automated: PR → ui-regression → Playwright → pw-report.json
                                     │
                                     └── (reporter/API) ──► TCM test run (auto)
Manual:    pre-release → TCM manual test run (by hand)
                                     │
              both feed one TCM project ──► dashboard (pass-rate trend, flaky)
                                     └► traceability: TCM case ⇄ user story (A1/A2/A4/J…)
```

- Traceability: each TCM case carries a `story_id` field mapping to `aidlc-docs/inception/user-stories/stories.md`.
- Auto write-back: annotate each Playwright test with its case id and push results to the TCM after the run.

### 5. Phased Rollout

- **Phase 0 (now)**: keep Playwright + Checks as-is; decide the tool (Option A/B).
- **Phase 1**: stand up the TCM project with suites mirroring the AIDLC pillars (A1/A2/A4/J); register the 6 existing automated cases and wire auto write-back (API token as a GitHub secret).
- **Phase 2**: author **manual cases** for flows not automated (e.g. A1 natural-language architecture generation, deliberately skipped in CI because it calls OpenRouter and costs credits); run a manual test cycle each release.
- **Phase 3**: dashboards + traceability matrix (story ⇄ case ⇄ result); optionally a gh-aw agent that summarises test coverage at release time.

### 6. Division of Labour: GitHub vs TCM

- **GitHub**: automated test code, CI execution, PR gating (the source of truth for automated pass/fail on a PR).
- **TCM**: the case catalogue (manual + automated metadata), test plans, manual execution, cross-run trend dashboards, the traceability matrix.

### 7. Open Decisions

1. Tool: Option A (self-hosted Kiwi) or B (Qase SaaS)?
2. Open a new ADR for this (self-hosting into scope / SaaS data egress)?
3. Traceability granularity: case-to-story (A1) enough, or down to individual acceptance criteria?
