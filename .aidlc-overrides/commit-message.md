# Cloud-360 Commit Message 規範：繁體中文

> 專案 override 規則。與 upstream 任何衝突指示相比，本規則優先。

### 規範

本專案的 commit message **一律使用繁體中文**，包含 type、描述、body 與 PR 標題。詳見 ADR-0010。

格式沿用 conventional commits 的結構，但 type 改為中文：

```
<type>(<scope>)<!>: <描述>

<body（可選，繁體中文）>

<footer（可選）>
```

### Type 對照表

`<type>` 限定為下列中文詞之一。英文對應僅供理解與 branch 命名換算，**不得**直接寫在 commit message 裡：

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

### 維持原文的部分

以下維持英文，不翻譯 — 它們是識別字或被機器解析的 token：

1. **`<scope>`**：對應程式模組、目錄或子系統名稱，例如 `(rbac)`、`(deploy)`、`(ops)`、`(frontend)`。
2. **`BREAKING CHANGE:` footer** 與 breaking 標記 `!`：conventional commits 的機器解析 token。
3. **Trailer**：`Co-Authored-By:`、`Signed-off-by:`、`Refs:` 等。
4. **內文中的程式碼、指令、檔名、專有名詞**：`useEffect`、`git revert`、`docker compose`、`Cloudflare Tunnel`、AWS / GCP / Azure 服務名等。

### 範例

✅ 合規：

```
功能(rbac): 新增角色與故事的權限矩陣
修正(deploy): 讓 cloudflared 以 uid 1000 讀取 0400 憑證
文件(ops): 補上 SLO 與事故處理手冊
整合(ci): 新增 Lint Fixer agentic workflow
還原(deploy): 還原 PR #431，部署至 192.168.10.10 失敗
```

帶 body 與 breaking 標記：

```
功能(api)!: 改用 JWT 取代 session cookie

舊的 session 中介層整個移除，前端需改帶 Authorization header。
`/api/auth/login` 的回應格式同步調整。

BREAKING CHANGE: 既有 session cookie 一律失效，使用者需重新登入。
```

❌ 不合規：

| Commit message | 違規原因 |
|---|---|
| `feat(rbac): 新增權限矩陣` | type 未中文化 |
| `功能(權限): 新增權限矩陣` | scope 應維持英文識別字 |
| `功能: add permission matrix` | 描述未中文化 |
| `新增(rbac): 新增權限矩陣` | `新增` 不在 type 對照表內（應為 `功能`） |
| `功能(rbac) 新增權限矩陣` | 缺少冒號 |

### 與 branch naming 的關係（重要）

`.aidlc-overrides/branch-naming.md` 的 `<type>` **維持英文**，與本規則的中文 type **已解耦**。原因是中文 branch 名稱在 `gh` CLI、URL 與部分 CI 工具需要 percent-encoding，實務上容易出問題。

換算方式：開 branch 時用上表的「英文對應」欄，寫 commit 時用「中文 type」欄。

```
branch：danniel/feat/rbac-permission-matrix
commit：功能(rbac): 新增角色與故事的權限矩陣
```

### 適用範圍

- ✅ 人工 commit 與 PR 標題。
- ✅ AI agent（Claude Code 及其他）產生的 commit 與 PR 標題。
- ✅ CI 自動產生的 commit 與 PR 標題（`deploy.yml` 的 revert PR、gh-aw workflow 的 push）。
- ⏸ 不溯及既往：本規則建立前的既有 commit 歷史保持原狀，不做 rewrite。
- ❌ 不適用：`dependabot/*` 等第三方工具自動產生的 commit；merge commit 的 git 預設訊息（`Merge pull request #N from ...`）。

### 工具相容性

中文 type 無法被 conventional-commits 生態的預設 parser 解析。若未來要接 changelog 產生器或 semantic-release，需自訂 parser preset，可用的 regex：

```
^(功能|修正|文件|格式|重構|效能|測試|建置|整合|雜項|還原)(\([a-zA-Z0-9_,\-\/\.]+\))?!?: .+
```

版本號對應：`功能` → minor、`修正`/`效能` → patch、帶 `!` 或 `BREAKING CHANGE:` → major。

目前專案未使用自動 changelog 工具，此為未來接線時的備註。

### 與 upstream AIDLC rules 的關係

upstream `awslabs/aidlc-workflows` 不規範 commit message 格式，本規則為**純疊加**（無覆蓋對象）。

### 對 AI agent 的指示

- 執行 `git commit` 或 `gh pr create` 前，先確認訊息符合本規則。
- 若使用者下達衝突指令（例如直接給一個英文 commit message），先提醒衝突並請使用者確認。
- 修改 CI workflow 時，若該處會產生 commit 或 PR 標題，一併套用本規則。
