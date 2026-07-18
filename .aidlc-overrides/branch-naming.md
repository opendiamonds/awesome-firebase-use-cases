# Cloud-360 Branch Naming Convention

> Project override rule. Takes precedence over any conflicting upstream guidance.
> 專案 override 規則。與 upstream 任何衝突指示相比，本規則優先。

### 規範

所有新建分支必須遵循下列格式：

```
<uploader>/<type>/<slug>
```

- `<uploader>`：開分支的人慣用的英文小寫 handle。
  - Danniel 一律使用 `danniel`。
  - 其他成員使用各自一致的英文小寫 handle（建議與 GitHub username 一致）。
- `<type>`：分支用途，限定為下列 conventional commit 類型之一：
  - `feat` — 新功能
  - `fix` — bug 修復
  - `docs` — 文件變更（純 markdown / spec）
  - `chore` — 雜項（CI、依賴、版本維護）
  - `refactor` — 重構（行為不變）
  - `test` — 測試補強或修正
- `<slug>`：英文小寫，連字號分隔，3–5 個詞概述變更目的。

### 範例

✅ 合規：

| Branch | 用途 |
|---|---|
| `danniel/feat/aidlc-docs-migration` | 新功能：搬遷 AIDLC docs |
| `danniel/fix/agent-routing-bug` | 修復 agent routing 路徑判斷錯誤 |
| `danniel/docs/srs-update` | SRS 文件更新 |
| `danniel/chore/dependency-bump` | CI 依賴升級 |
| `danniel/refactor/skill-registry-split` | 重構 MCP skill registry |
| `danniel/test/cost-calculator-property-tests` | 補 cost calculator property-based 測試 |

❌ 不合規：

| Branch | 違規原因 |
|---|---|
| `feat/aidlc-rules` | 缺少 `<uploader>/` 前綴 |
| `Danniel/feat/foo` | 大寫 |
| `danniel/feature/foo` | type 不在限定清單（要 `feat` 不是 `feature`） |
| `danniel/foo` | 缺少 `<type>/` 段 |
| `danniel/feat/foo_bar` | slug 用底線而非連字號 |

### 套用範圍

- ✅ 適用：所有從 `main` 建立的新分支。
- ✅ 適用：long-lived feature branch、stacked PR branch（如 PR2、PR3）。
- ⏸ 不溯及：在本規則建立前已存在的分支（例如 `feat/aidlc-framework-rules`、`feat/aidlc-docs-migration`）保留原名直到合併。
- ❌ 不適用：自動產生的分支，例如 `dependabot/*`、`release/*`、tooling 自動 push 的 branch。

### 與 upstream AIDLC rules 的關係

upstream `awslabs/aidlc-workflows` 不規範 git branch 命名，本規則為**純疊加**（無覆蓋對象）。Claude Code 開分支前必須遵循此規則。

### Enforcement

- 人類審查：PR reviewer 在 review 時檢查 branch 名稱。
- 自動檢查（可選，未強制）：未來可在 `.github/workflows/ci.yml` 加 step，使用 regex `^[a-z0-9-]+/(feat|fix|docs|chore|refactor|test)/[a-z0-9-]+$` 檢查 head branch；本 override 暫不強制 CI 整合，先以 review + Claude Code 自動套用為主。
- AI agent：Claude Code 與其他 AI agent 在執行 `git checkout -b` / `git switch -c` 之前，必須先確認 branch name 符合此格式。若使用者下達衝突指令，先提醒並請使用者確認。
