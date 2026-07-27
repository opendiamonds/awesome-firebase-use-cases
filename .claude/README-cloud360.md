# Cloud-360 對 AI-DLC v2 安裝的調整

本目錄由 upstream [`awslabs/aidlc-workflows`](https://github.com/awslabs/aidlc-workflows) 的 `v2` 分支產出（版本 **2.5.11**，commit `257b43a`）複製而來。除下列一處外，內容與 upstream 一致。

## 唯一的調整：`settings.json` 移除環境相依設定

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

## 需要這些設定的人怎麼做

複製範本到 gitignored 的個人設定檔，各自填寫：

```bash
cp .claude/settings.local.json.example .claude/settings.local.json
```

`settings.local.json` 已列入 `.gitignore`，優先權高於 `settings.json`，不會影響他人。

> ⚠️ upstream README 指出 v2 在 **Claude Opus 4.8** 上表現最佳；較弱的模型可能讓 conductor 跳過 reviewer pass 或 learnings ritual、草率通過 approval gate。若要固定模型，請寫在自己的 `settings.local.json`。

## 重新安裝或升級時

從 upstream 重新複製 `dist/claude/` 會**覆蓋**上述調整。覆蓋後請重新移除那幾項，或改以 `settings.local.json` 覆寫。

## 現況

本次為**並行安裝**：v2 已裝，但 v1.0.1（`.aidlc/aidlc-rules/`）仍在，`scripts/validate_repo_contract.py` 與 `CLAUDE.md` 尚未切換。移除 v1 與搬遷 `aidlc-docs/` 屬後續 PR。
