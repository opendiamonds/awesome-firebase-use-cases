<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). -->
> Orchestrator-maintained stage diary.

## Interpretations
- 2026-08-20T02:12:00Z — embedded monolith：無新容器／無新雲資源；OQ-3 以 repo 內 YAML allowlist 定案，不新增查價 credential env。
- 2026-08-20T02:12:00Z — MVP coverage：AWS `official_list`；GCP／Azure `manual_override_only`（對齊 mockups M2）。
- 2026-08-23T02:32:00Z — **ADR-C1-09 覆寫**：三雲皆 `official_list`；allowlist 含 AWS／GCP Catalog／Azure Retail；可選 `GCP_BILLING_API_KEY`；區域依 `diagram_cloud` 過濾。歷史 Q&A／上兩則日記保留，以本則與 living docs 為準。

## Deviations

## Tradeoffs

## Open questions

- 2026-08-20T02:18:00Z — OQ-3 定案：AWS Price List 公開 JSON；GCP/Azure manual_override_only；五 unit 產物齊，gate awaiting-approval。
- 2026-08-23T02:32:00Z — OQ-3 後續：見 ADR-C1-09（三雲官方價）；上則為歷史定案紀錄。
