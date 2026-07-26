# A3 Offline Custom Lens POC Summary

## 中文版

### 決策對齊

| 決策 | 實作 |
|---|---|
| Q0=A 完全離線 | 不呼叫 boto3／WA Tool API |
| Q1=D Lens 為準 | `scores_json.source_of_truth=offline_lens`；總分／支柱分來自 lens |
| Findings←Lens | `findings_json`＝Lens HIGH＋MEDIUM；severity high／warn；code `LENS-*` |
| Q4=A | 啟發式不寫入權威 findings（僅失敗備援） |
| Q3=A | ReviewAgent 輸入＝Lens findings |
| Q5=B | Lens 失敗時 findings 回退啟發式並標 `source=heuristic` |
| Q7=B／Q8=B | 自製 `cloud360-core-mvp-lens.json` |

### 新增／關鍵 API

- `backend/lenses/cloud360-core-mvp-lens.json`
- `backend/services/wa_lens_engine.py`（含 `findings_from_lens_score`）
- `backend/tests/test_wa_lens_engine.py`

### 流程

1. `WaRuleEngine` → `rules_done`（啟發式分數；findings 暫空）
2. 填答 → `riskRules` → `lens_done`（權威分數＋Lens findings）
3. `ReviewAgent`（依 Lens findings）→ `complete`

---

## English Version

### Decision alignment

| Decision | Implementation |
|---|---|
| Q0=A fully offline | No boto3 / WA Tool API |
| Q1=D lens authority | Overall / pillar scores from lens |
| Findings←Lens | `findings_json` = HIGH+MEDIUM; severity high/warn; codes `LENS-*` |
| Q4=A | Heuristic findings not authoritative (fallback only) |
| Q3=A | ReviewAgent input = Lens findings |
| Q5=B | On lens failure, heuristic findings with `source=heuristic` |
| Q7=B / Q8=B | Homemade `cloud360-core-mvp-lens.json` |

### Pipeline

1. `WaRuleEngine` → `rules_done` (heuristic scores; empty findings)
2. Answers → `riskRules` → `lens_done` (authoritative scores + Lens findings)
3. `ReviewAgent` (Lens findings) → `complete`
