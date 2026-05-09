# Cloud-360 Branch Naming Convention

> Project override rule. Takes precedence over any conflicting upstream guidance.
> 專案 override 規則。與 upstream 任何衝突指示相比，本規則優先。

## 中文版

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

---

## English Version

### Rule

Every new branch MUST follow this format:

```
<uploader>/<type>/<slug>
```

- `<uploader>`: the contributor's lowercase handle.
  - Danniel always uses `danniel`.
  - Other members use their own consistent lowercase handle (recommended: GitHub username).
- `<type>`: the branch purpose, restricted to one of the following conventional commit types:
  - `feat` — new feature
  - `fix` — bug fix
  - `docs` — documentation change (pure markdown / specification)
  - `chore` — miscellaneous (CI, dependencies, version maintenance)
  - `refactor` — refactoring (behavior unchanged)
  - `test` — adding or fixing tests
- `<slug>`: lowercase English, hyphen-separated, 3–5 words summarizing the change.

### Examples

✅ Compliant:

| Branch | Purpose |
|---|---|
| `danniel/feat/aidlc-docs-migration` | New feature: migrating AIDLC docs |
| `danniel/fix/agent-routing-bug` | Fix incorrect agent routing path |
| `danniel/docs/srs-update` | SRS document update |
| `danniel/chore/dependency-bump` | CI dependency upgrade |
| `danniel/refactor/skill-registry-split` | Refactor MCP skill registry |
| `danniel/test/cost-calculator-property-tests` | Add property-based tests for the cost calculator |

❌ Non-compliant:

| Branch | Violation |
|---|---|
| `feat/aidlc-rules` | Missing `<uploader>/` prefix |
| `Danniel/feat/foo` | Uppercase |
| `danniel/feature/foo` | Type not in the allowed set (use `feat`, not `feature`) |
| `danniel/foo` | Missing `<type>/` segment |
| `danniel/feat/foo_bar` | Slug uses underscores instead of hyphens |

### Scope

- ✅ Applies: every new branch created from `main`.
- ✅ Applies: long-lived feature branches and stacked PR branches (e.g. PR2, PR3).
- ⏸ Not retroactive: branches created before this rule (e.g. `feat/aidlc-framework-rules`, `feat/aidlc-docs-migration`) keep their existing names until merged.
- ❌ Does not apply: auto-generated branches such as `dependabot/*`, `release/*`, or tool-pushed branches.

### Relationship to Upstream AIDLC Rules

Upstream `awslabs/aidlc-workflows` does not specify a git branch naming convention. This rule is a **pure addition** (no upstream rule is overridden). Claude Code must follow this rule whenever it creates a new branch.

### Enforcement

- Human review: PR reviewers check branch names during review.
- Automated check (optional, not yet enforced): a future `.github/workflows/ci.yml` step could validate the head branch with the regex `^[a-z0-9-]+/(feat|fix|docs|chore|refactor|test)/[a-z0-9-]+$`. This override does not require CI integration yet — review + AI agent self-enforcement is enough for now.
- AI agents: Claude Code and other AI agents MUST check that a branch name matches this format before running `git checkout -b` or `git switch -c`. If the user issues a conflicting instruction, surface the conflict and ask for confirmation before proceeding.
