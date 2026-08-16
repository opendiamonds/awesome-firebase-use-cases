# GitHub 同步實作藍圖 — Cloud-360

- Status: Design（ADR-0012 已 Accepted；實作尚未開始）
- Date: 2026-08-16
- 決策依據：[ADR-0012](../inception/decisions/0012-github-issues-projects-wiki-sync.md)
- 關聯：`.github/workflows/spec-sync.md`、`.github/workflows/issue-triage.md`、`test-case-management-plan.md`

> 本檔是 ADR-0012 的實作細節。ADR 說**為什麼這樣設計**，本檔說**怎麼做**。
> 兩者有出入時以 ADR 為準。

---

## 0. 前置條件（實作前必須先完成）

| # | 項目 | 怎麼做 | 沒做會怎樣 |
|---|---|---|---|
| P1 | **初始化 Wiki** | 在 GitHub UI 建立第一頁（任意內容） | `<repo>.wiki.git` 不存在，階段 4 無法 clone |
| P2 | **Projects v2 token** | 建立 GitHub App 或 classic PAT，scope `project`；存為 secret `GH_PROJECTS_TOKEN` | 階段 3 的 GraphQL 寫入全部 401；`GITHUB_TOKEN` **不涵蓋** Projects v2 |
| P3 | **本機 gh scope** | `gh auth refresh -s read:project,project` | 開發時無法查證看板現況 |
| P4 | **建立 label** | `aidlc`、`intent:<slug>`、`story`、`sync-conflict` | issue 混在 200+ 筆 digest 噪音中無法篩選 |
| P5 | **確認 `issue-triage` 的排除規則** | 讓它跳過帶 `aidlc` 標籤的 issue | 兩個 workflow 互相改標籤，來回震盪 |

---

## 1. 映射細節

### 1.1 intent → Project

| Project 欄位 | 來源 | 方向 |
|---|---|---|
| Project 名稱 | `intents.json` 的 `slug` | repo → GH（建立時） |
| Project 描述 | `<record>/aidlc-state.md` 的 intent 摘要 | repo → GH |
| Status 欄位選項 | AI-DLC 的 phase（ideation／inception／construction／operation） | repo → GH（建立時） |
| Iteration 欄位 | `bolt-plan.md` 的 Bolt 序列 | repo → GH |
| 卡片所在欄位 | — | **GH → repo** |

### 1.2 user story → Issue

`stories.md` 的結構是 `## US-n <標題>`，其下 `### 驗收標準` 為 Given/When/Then 區塊。

| Issue 欄位 | 來源 | 方向 |
|---|---|---|
| 標題 | `US-n <標題>` | repo → GH |
| 內文的受管區塊 | story 敘述 + 驗收標準 + Definition of Done | repo → GH |
| 內文的受管區塊**之外** | 人手寫 | **不同步、永不觸碰** |
| labels `aidlc` / `intent:<slug>` / `story` | 固定 | repo → GH（建立時） |
| 其他 labels | 人／`issue-triage` | **GH → repo** |
| state（open/closed） | — | **GH → repo** |
| assignee | — | **GH → repo** |
| comments | — | 不同步（只在 GitHub） |

### 1.3 unit of work → Issue 的子任務

`unit-of-work.md` 的每個單元渲染成受管區塊內的 task list：

```markdown
- [ ] U-1 後端回應加入 last_activity_at 欄位
- [x] U-2 前端表格新增欄位與空態
```

勾選狀態是 **GH → repo**（人在 issue 上勾）；項目本身的增刪是 **repo → GH**。

> 為什麼不用 GitHub 的 sub-issue：sub-issue 會在 issue 列表產生大量條目，與 story 平級競爭注意力，且 200+ 筆的 issue 池已經夠吵。task list 在 story issue 內部，層級關係自然。

---

## 2. 受管區塊格式

Issue 內文的實際形狀：

```markdown
<!-- aidlc:managed intent=last-login-column story=US-1 hash=a1b2c3d4 -->

## 需求

作為 Security_Reviewer，我需要看到每個帳號的最後活動時間，以便判斷帳號是否仍在使用。

## 驗收標準

**AC-1.1**
- **Given** 一個帳號目前無活動紀錄
- **When** 該帳號以有效憑證發出任一需認證的請求
- **Then** 該帳號的最後活動時間被記錄為該請求發生的時刻

## 實作單元

- [ ] U-1 後端回應加入 last_activity_at 欄位
- [ ] U-2 前端表格新增欄位與空態

---
> 🤖 本區塊由 AI-DLC 自動同步自 `aidlc/spaces/default/intents/260802-last-login-column/inception/user-stories/stories.md`。
> **在此區塊內的修改會被下次同步覆蓋**；要改需求請走 AI-DLC 流程。
> 區塊之外的內容不會被觸碰，歡迎在下方補充討論與脈絡。

<!-- /aidlc:managed -->

（以下由人自由編寫，同步永不觸碰）
```

`hash` 是受管區塊內容的 SHA-256 前 8 碼，用於防迴圈（見第 4 節）。

---

## 3. 同步狀態檔

`<record>/.aidlc-sync-state.json`，**進版控**（不是 gitignored 的 per-clone 檔——跨 runner 比對需要它）：

```json
{
  "version": 1,
  "intent": "last-login-column",
  "project": { "number": 3, "node_id": "PVT_xxx", "last_synced": "2026-08-16T05:00:00Z" },
  "stories": {
    "US-1": {
      "issue": 502,
      "content_hash": "a1b2c3d4",
      "last_pushed": "2026-08-16T05:00:00Z",
      "last_pulled_state": { "state": "open", "assignees": ["danniel"], "labels": ["aidlc", "story"] }
    }
  }
}
```

- `content_hash`：上次推送的受管區塊雜湊。**相同就不推**。
- `last_pulled_state`：上次拉回的狀態快照。與現況相同就不開 PR。

---

## 4. 防迴圈（三道，缺一不可）

1. **內容雜湊**：推送前算受管區塊的 SHA-256，與 `content_hash` 相同就跳過。這擋掉「內容沒變卻反覆寫入」。
2. **commit 標記**：所有同步產生的 commit 訊息前綴 `[aidlc-sync]`。正向同步 workflow 的觸發條件排除這類 commit：
   ```yaml
   if: "!contains(github.event.head_commit.message, '[aidlc-sync]')"
   ```
3. **狀態欄位單向**：狀態只 GH → repo。repo 除了建立 issue 的初始值之外，**不寫**任何狀態欄位。單向的資料流不可能來回震盪。

> 三道防線針對不同的迴圈路徑：雜湊擋內容、commit 標記擋 workflow 觸發、單向性擋語意層的來回。只做其中一道都會留下活路。

---

## 5. 四個階段的 workflow 規格

### 階段 1：`aidlc-sync-push`（repo → Issues）

```yaml
on:
  push:
    branches: [ut]
    paths:
      - "aidlc/spaces/*/intents/*/inception/user-stories/stories.md"
      - "aidlc/spaces/*/intents/*/inception/units-generation/unit-of-work.md"
  workflow_dispatch:
permissions:
  contents: write   # 寫回 .aidlc-sync-state.json
  issues: write     # 建立與更新 issue
```

步驟：解析 `stories.md` 的 `## US-n` → 對每個 story 算受管區塊與雜湊 → 比對 `sync-state` → 不存在則建立 issue、雜湊不同則**只替換受管區塊**（保留區塊外的人寫內容）→ 更新 `sync-state` 並以 `[aidlc-sync]` commit。

**冪等性驗收**：連跑兩次，第二次的建立數與更新數皆為 0。

### 階段 2：`aidlc-sync-pull`（Issues → repo）

```yaml
on:
  schedule: [{ cron: "0 */6 * * *" }]   # 每 6 小時
  workflow_dispatch:
permissions:
  contents: write
  issues: read
  pull-requests: write   # 反向同步一律開 PR
```

步驟：讀 `sync-state` 的 issue 清單 → 抓現況（state／assignees／labels）→ 與 `last_pulled_state` 比對，無差異就結束 → 有差異則更新 `<record>/aidlc-state.md` 的狀態欄與 `sync-state` → **開 PR**（不直接推 `ut`）。

PR 標題：`整合(sync): 從 GitHub 拉回 <intent> 的狀態變更`。

**為什麼一律開 PR**：反向同步是唯一可能繞過 approval gate 的路徑，PR 化讓它必須經過人眼。

### 階段 3：`aidlc-sync-project`（Projects v2）

需 `GH_PROJECTS_TOKEN`。Projects v2 只有 GraphQL API，與 Issues 的 REST 不同，這是它排在第三的原因。雙向：欄位定義與卡片建立為 repo → GH；卡片所在欄位為 GH → repo（併入階段 2 的 PR）。

### 階段 4：`aidlc-sync-wiki`（單向鏡像）

```yaml
on:
  push:
    branches: [ut]
    paths:
      - "aidlc/spaces/*/intents/*/inception/decisions/**"
      - "aidlc/spaces/*/intents/*/inception/user-stories/stories.md"
      - "aidlc/spaces/*/intents/*/inception/requirements-analysis/**"
      - "aidlc/spaces/*/intents/*/inception/application-design/**"
      - "README.md"
      - "DEPLOY.md"
      - "LOCAL-DEV.md"
      - "TESTING.md"
```

clone `<repo>.wiki.git` → 渲染（頁首加來源警語與原始路徑連結）→ commit → push。**不回寫**。

---

## 6. 失敗處理

| 失敗 | 處置 |
|---|---|
| GitHub API 429／5xx | 指數退避重試 3 次；仍失敗則**保持 sync-state 不變**並讓 workflow 紅燈——寧可下次重來，不要留下 state 與現實不符 |
| issue 被人手動刪除 | 從 sync-state 移除該筆並重新建立；在 PR 說明中記載 |
| 受管標記被人刪掉 | **不自動修復**、不覆寫整個內文。開一則帶 `sync-conflict` 標籤的 issue 請人決定——自動重建會吃掉人寫的內容 |
| Wiki push 衝突 | 以 repo 為準強制覆蓋（Wiki 是單向鏡像），並在 workflow log 記載被覆蓋的 commit |

---

## 7. 開放問題（實作前要有答案）

1. **一個 intent 的 stories 改名或刪除時**，對應的 issue 怎麼處理？關閉並加 `wontfix`？還是留著？（傾向：關閉並在受管區塊註記「此 story 已從需求移除」，不刪 issue——issue 編號是外部引用點。）
2. **`daily-digest` 每天產生 issue** 已使 issue 列表達 200+ 筆。是否該讓 digest 改用 discussion 或直接關閉舊的？這會影響同步進來的 issue 的可見度。
3. **多個 in-flight intent 同時同步**時，Project 是每個 intent 一個（可能很多）還是全部共用一個？目前設計是前者，需確認實際使用時的數量是否可接受。
4. **反向同步的 PR 由誰 review**？若無人 review 會堆積，若自動合併則失去它存在的意義。
