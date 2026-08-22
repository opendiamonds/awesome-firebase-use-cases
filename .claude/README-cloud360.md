# Cloud-360 對 AI-DLC v2 安裝的調整

本目錄由 upstream [`awslabs/aidlc-workflows`](https://github.com/awslabs/aidlc-workflows) 的 `v2` 分支產出複製而來。除下列**兩處**外，內容與 upstream 一致。

版本的單一事實來源是 `.claude/tools/aidlc-version.ts` 的 `AIDLC_VERSION`（跑 `/aidlc --version` 可查），目前為 **2.5.33**。初次並行安裝為 2.5.11（upstream commit `257b43a`，見 commit `4f2b626`）。

## 調整 1：`settings.json` 移除環境相依設定

upstream 的 `settings.json` 是**進版控**的共享檔案，預設帶著 AWS workshop 情境的設定。原樣 commit 會強制本 repo 的每位開發者走 Bedrock，沒有 AWS 憑證者會直接失敗。

已移除下列項目：

| 項目 | upstream 預設 | 移除原因 |
|---|---|---|
| `CLAUDE_CODE_USE_BEDROCK` | `1` | 強制走 Bedrock；本團隊未必都使用 |
| `AWS_REGION` | `us-east-1` | 環境相依 |
| `ANTHROPIC_DEFAULT_*_MODEL` | `global.anthropic.*` | Bedrock 專用 model ID，非 Bedrock 環境無效 |
| `AWS_AIDLC_DEFAULT_SCOPE` | `workshop` | 教學用 scope，不適合真實功能開發；改為由 `/aidlc` 依描述自動偵測 |
| `model` | `opus[1m]` | 個人偏好 |
| `effortLevel` | `xhigh` | 個人偏好 |

`permissions`、`statusLine`、`hooks`、`companyAnnouncements` 均維持 upstream 原樣。

> ⚠️ 因此 upstream 的 `.claude/CLAUDE.md` 中「shipped `settings.json` 預設走 AWS Bedrock / Opus 4.8 / `AWS_REGION=us-east-1`」那段敘述**不適用於本 repo** — 那些鍵已被移除，`env` 為空物件。需要 Bedrock 的人請寫進自己的 `settings.local.json`。

## 調整 2：`knowledge/aidlc-shared/ai-dlc-principles.md` 的 artifacts 路徑

upstream 該檔第 3 條原則寫「Every stage produces versioned markdown documents in `aidlc-docs/`」—— 這是 v1 的扁平佈局，與 v2 自身的 per-intent record 設計矛盾（`aidlc-state.ts` 的註解明寫 `flat aidlc-docs/ root is gone`）。屬 upstream 未清乾淨的殘留。

已改為指向 `aidlc/spaces/<space>/intents/<record>/`。這是**純文件敘述**的修正，不影響任何程式行為。

> upstream 其他仍提及 `aidlc-docs` 的地方是**刻意**的，不要改：
> - `.claude/tools/aidlc-lib.ts` 的 `FLAT_MIGRATION_ROOT` — v1→v2 一次性搬遷的偵測常數
> - `.claude/sensors/*.md` 的 `matches: "**/{aidlc-docs,intents}/**"` — 同時匹配新舊佈局，讓 sensor 對兩種 repo 都會觸發
> - `.claude/knowledge/aidlc-shared/worktree-info-schema.md` — 描述 per-Bolt worktree 的 forked state 路徑

## 需要這些設定的人怎麼做

複製範本到 gitignored 的個人設定檔，各自填寫：

```bash
cp .claude/settings.local.json.example .claude/settings.local.json
```

`settings.local.json` 已列入 `.gitignore`，優先權高於 `settings.json`，不會影響他人。

> ⚠️ upstream README 指出 v2 在 **Claude Opus 4.8** 上表現最佳；較弱的模型可能讓 conductor 跳過 reviewer pass 或 learnings ritual、草率通過 approval gate。若要固定模型，請寫在自己的 `settings.local.json`。

## 調整 3：新增 `tcms` plugin 的 `tcms-test-cases` stage

**這是新增檔案，不是修改 upstream 檔**，但它位於 `.claude/` 之下，因此同樣會被升級時的整批複製波及。

| 項目 | 路徑 | 性質 |
|---|---|---|
| Stage 檔（**手寫，需備份**） | `.claude/aidlc-common/stages/construction/tcms-test-cases.md` | 手寫來源 |
| 驗證 skill（**手寫，需備份**） | `.claude/skills/tcms-verify/SKILL.md` | 手寫來源，`/tcms-verify` |
| Runner skill | `.claude/skills/tcms-test-cases/` | 由 `aidlc-runner-gen.ts write` 產生 |
| 編譯產物 | `.claude/tools/data/stage-graph.json`、`scope-grid.json` | 由 `aidlc-graph.ts compile` 產生 |

兩個手寫檔需要保存；runner skill 與編譯產物都能從 stage 檔重新產生。

`aidlc-runner-gen.ts check` 只管它自己產生的 runner 集合，多一個手寫的
`tcms-verify` skill 不會讓 drift guard 紅燈（已實測）。

**不在 `.claude/` 之下、因此不受升級影響**（不需備份）：

- 撰寫標準：`aidlc/spaces/default/knowledge/aidlc-quality-agent/test-case-authoring.md`
- Blocking 規則：`aidlc/spaces/default/memory/project.md` 的 `## Mandated`
- 同步工具：`scripts/tcms_sync.py`

之所以把 stage 檔放在 upstream 目錄，是因為 stage graph 的編譯器**只掃描** `.claude/aidlc-common/stages/<phase>/`（`aidlc-graph.ts` 的 `stagesDir()`；`AIDLC_STAGES_DIR` 是測試用的 seam，不是安裝點）。沒有第二個位置可放。

## 重新安裝或升級時

從 upstream 重新複製 `dist/claude/` 會**覆蓋**上述調整。覆蓋後請：

1. 重新移除 `settings.json` 的環境相依鍵（或改以 `settings.local.json` 覆寫）。
2. 重新套用 `ai-dlc-principles.md` 第 3 條的 artifacts 路徑修正 —— 先確認 upstream 是否已自行修好，若已修好則此項可刪。
3. 放回 `tcms-test-cases.md` stage 檔，然後重新產生它的衍生物：
   ```bash
   bun .claude/tools/aidlc-graph.ts compile
   bun .claude/tools/aidlc-runner-gen.ts write
   ```
   驗證兩道 drift guard 皆為 exit 0：
   ```bash
   bun .claude/tools/aidlc-graph.ts compile --check
   bun .claude/tools/aidlc-runner-gen.ts check
   ```
   並確認 stage 有進 graph（`/aidlc --doctor` 應列出 33 個 stage，其中 `tcms-test-cases` 的 `plugin` 為 `tcms`）。

   兩種漏做各有守門機制，不必靠記憶：

   | 漏掉什麼 | 誰會抓到 |
   |---|---|
   | stage 檔沒放回 | `scripts/validate_repo_contract.py`（已列入 `REQUIRED_FILES`）→ CI 紅燈 |
   | 放回了但沒重新編譯 | `/aidlc --doctor` 的 `Uncompiled stage files` 檢查 |

接著跑 `/aidlc --doctor` 與 `python3 scripts/validate_repo_contract.py` 驗證。

## 現況

**已完整切換到 v2**（ADR-0011）：

- 專案規則位於 `aidlc/spaces/default/memory/`：`team.md`（團隊實踐）、`project.md`（專案特化）；`org.md` 僅校正整合主幹為 `ut` 與部署段落。
- AI 入口（`CLAUDE.md`、`AGENTS.md`、`.cursor/rules/`、`.agents/`）與 `scripts/validate_repo_contract.py` 均已指向 v2。
- 舊的扁平 `aidlc-docs/` 已由引擎的 flat-layout migration 整棵搬進 baseline record `aidlc/spaces/default/intents/260802-default/`；`audit.md` 轉為 `audit/<host>-<clone>.md` per-clone shard，`aidlc/.migrated` 為冪等標記。

驗證方式：`/aidlc --doctor` 與 `python3 scripts/validate_repo_contract.py` 皆須通過。
