# Team-Level Rules

> This team's affirmed practices and corrections. Loaded after `org.md` as
> strict-additive guidance; contradictions with broader policy are rejected.
> Populated by the practices-discovery affirmation gate. Edit at the gate,
> not directly.
>
> Cloud-360 note: 本層為本專案自有規則（見 ADR-0011），以繁體中文撰寫；
> `org.md` 為 upstream 框架預設層，維持英文。識別字、路徑、指令維持原文。
> 下文的 `<record>/` 是作用中 intent 的 record 目錄簡寫，即
> `aidlc/spaces/<active-space>/intents/<slug>/`。

## Way of Working

### Branch 命名

所有新建分支必須遵循 `<uploader>/<type>/<slug>`：

- `<uploader>`：開分支者慣用的英文小寫 handle（建議與 GitHub username 一致）。Danniel 一律用 `danniel`。
- `<type>`：**一律英文小寫**，限定 `feat`（新功能）、`fix`（bug 修復）、`docs`（純文件／spec）、`chore`（CI、依賴、版本維護）、`refactor`（行為不變的重構）、`test`（測試補強）。
- `<slug>`：英文小寫、連字號分隔、3–5 個詞概述變更目的。

合規範例：`danniel/feat/rbac-permission-matrix`、`danniel/fix/agent-routing-bug`、`danniel/chore/dependency-bump`。
不合規：`feat/aidlc-rules`（缺 uploader）、`Danniel/feat/foo`（大寫）、`danniel/feature/foo`（type 不在清單）、`danniel/feat/foo_bar`（底線非連字號）。

不溯及既往：本規則建立前的既有分支保留原名直到合併。不適用於 `dependabot/*`、`release/*` 等自動產生的分支。

執行 `git checkout -b` / `git switch -c` 前必須先確認 branch name 合規；使用者若下達衝突指令，先提醒衝突並請使用者確認。

### Commit message 與 PR 標題

一律使用**繁體中文**，包含 type、描述、body 與 PR 標題（ADR-0010）。格式沿用 conventional commits，但 type 改為中文：

```
<type>(<scope>)<!>: <描述>

<body（可選，繁體中文）>

<footer（可選）>
```

`<type>` 限定下列中文詞，英文對應僅供理解與 branch 命名換算，**不得**寫進 commit message：

| 中文 type | 英文對應 | 用途 |
|---|---|---|
| `功能` | feat | 新功能 |
| `修正` | fix | bug 修復 |
| `文件` | docs | 文件變更（純 markdown / spec） |
| `格式` | style | 純格式調整，不影響行為 |
| `重構` | refactor | 重構，行為不變 |
| `效能` | perf | 效能改善 |
| `測試` | test | 測試補強或修正 |
| `建置` | build | 建置系統、依賴升級 |
| `整合` | ci | CI / CD 設定與 workflow |
| `雜項` | chore | 其他雜項維護 |
| `還原` | revert | 還原先前的 commit |

維持英文不翻譯的部分（識別字或被機器解析的 token）：`<scope>`（如 `(rbac)`、`(deploy)`、`(frontend)`）、`BREAKING CHANGE:` footer 與 breaking 標記 `!`、trailer（`Co-Authored-By:`、`Signed-off-by:`、`Refs:`）、內文中的程式碼／指令／檔名／專有名詞。

範例：

```
功能(rbac): 新增角色與故事的權限矩陣
修正(deploy): 讓 cloudflared 以 uid 1000 讀取 0400 憑證
整合(ci): 新增 Lint Fixer agentic workflow
```

**Branch type 與 commit type 已解耦**：branch 名稱維持英文 type（中文在 `gh` CLI、URL 與部分 CI 工具需 percent-encoding），commit 用中文 type，兩者以上表換算。

```
branch：danniel/feat/rbac-permission-matrix
commit：功能(rbac): 新增角色與故事的權限矩陣
```

適用於人工 commit、AI agent 產生的 commit／PR 標題、CI 自動產生的 commit（`deploy.yml` 的 revert PR、gh-aw workflow 的 push）。不溯及既往；不適用 `dependabot/*` 等第三方工具與 git 預設的 merge commit 訊息。

中文 type 無法被 conventional-commits 生態的預設 parser 解析；未來若接 changelog 產生器需自訂 preset，可用 regex：

```
^(功能|修正|文件|格式|重構|效能|測試|建置|整合|雜項|還原)(\([a-zA-Z0-9_,\-\/\.]+\))?!?: .+
```

## Walking Skeleton

<!-- Affirmed during practices-discovery. Example: -->
<!-- We don't run a walking skeleton — our deployment pipeline is mature -->
<!-- and the slice cost outweighs the value at our maturity stage. -->

## Testing Posture

<!-- Affirmed during practices-discovery. Example: -->
<!-- We use BDD. Specifications drive scenarios; scenarios drive code. -->
<!-- Each Unit ships with feature files in /features/. -->

## Deployment

<!-- Affirmed during practices-discovery. -->

## Code Style

<!-- Team-specific conventions beyond the linter. Example: -->
<!-- - Prefer named exports over default exports -->
<!-- - All async functions return Result<T, E>, never throw -->

## Forbidden

- ❌ **不得產生雙語分段**：文件不得保留或新增 `## 中文版` / `## English Version` 標題；文件為單一語言（繁體中文）。`scripts/validate_repo_contract.py` 會擋下 record 內殘留的 `## English Version`（CI 紅燈）。
- ❌ **不得自動寫 decisions log**：使用者沒有明確要求時，不要寫 `<record>/decisions-log.md`。AIDLC 階段事件由引擎寫進 `<record>/audit/` 的 per-clone shard，不要手動編輯；架構級決策開 ADR。舊的 per-turn `.ailog/` 機制已於 PR #17 整體移除，不得重建。
- ❌ **不得把敏感資料寫進任何 log 或決議紀錄**：token、API key、production credential 一律遮罩為 `[REDACTED]` 並提醒使用者。

## Mandated

- ✅ **文件語言：繁體中文**（ADR-0009，取代 upstream 的 bilingual-docs 與 ADR-0005）。AI-DLC 工作產出（`aidlc/spaces/*/intents/**/*.md`）、`CLAUDE.md`、`aidlc/spaces/*/memory/team.md`、`aidlc/spaces/*/memory/project.md` 一律繁體中文。例外：程式碼、指令、識別字、專有名詞維持原文；upstream 框架自身的英文檔（`.claude/**`、`aidlc/spaces/*/memory/org.md`、`phases/*.md`）不在此限。修改既有文件時，若見殘留英文版分段一併清除。
- ✅ **決議紀錄（on-demand）**：當使用者**明確要求**記錄當下對話的決議時（「記錄這個決議」、「把這個決定記下來」、「log this decision」等；以判斷而非死記字串，不確定就先反問），把決議追加到 `<record>/decisions-log.md`，append-only、繁體中文，每筆為 H3：

  ```markdown
  ### YYYY-MM-DD HH:MM:SS +TZ — <短標題（5–10 字）>

  **Decision / 決議**: <1–3 句獨立可懂的決議內容>
  **Context / 背景**: <為何有這個決議；簡短背景>
  **Trigger / 觸發語**: <使用者要求記錄時的原文>
  **Related / 相關**: <PR、ADR、branch、commit、issue 連結；無則 N/A>
  ```

  短標題概述決策本身，不要寫成「使用者問 X」。Decision 區塊要能脫離對話上下文獨立理解。
- ✅ **小步前進**：每個 stage 完成後產出 stage-completion summary，附 extension compliance（compliant / non-compliant / N/A 與理由），等使用者確認再進下一階段。
- ✅ **問題格式**：向使用者提問時使用 A/B/C/D/E 多選題與 `[Answer]:` tag。
- ✅ **內容驗證**：建檔前驗證 Mermaid 語法、ASCII 圖與特殊字元跳脫；Mermaid 一律附文字 fallback。

## Corrections

<!-- Self-learning loop appends here. -->
