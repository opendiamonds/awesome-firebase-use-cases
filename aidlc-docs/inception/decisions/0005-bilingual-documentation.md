# ADR 0005: Bilingual Documentation

> 本文件必須同時包含中文版與英文版。
> This document must include both Chinese and English versions.

## 中文版

- Status: Accepted
- Date: 2026-05-02

## Context

Cloud-360 會由中文使用者、國際協作者、AI agent、dev-agent 與不同技術角色共同閱讀與維護。為避免規格理解落差，`docs/` 文件必須同時提供中文版與英文版。

## Decision

所有 `docs/**/*.md` 文件必須包含：

- `## 中文版`
- `## English Version`

文件可以採同檔雙語模式，不必拆成兩個檔案。第一階段採同檔雙語，降低文件同步成本。

## Requirements

- 新增或修改 docs 文件時，必須同步更新中文與英文內容。
- README 可以保持產品入口，但需連到雙語 docs。
- SRS、Architecture、User Stories、ADR 都必須雙語。
- CI 的 repository contract validation 必須檢查 docs 文件是否包含雙語章節。

## Consequences

- 中文團隊可以快速討論產品與架構。
- 英文 reviewer、外部 contributor 與 AI agent 可以理解規格。
- 文件變更成本略增，但能降低跨語言誤解風險。

## English Version

- Status: Accepted
- Date: 2026-05-02

## Context

Cloud-360 documentation will be read and maintained by Chinese-speaking users, international collaborators, AI agents, dev-agents, and different technical roles. To avoid requirement and architecture misunderstandings, all documentation under `docs/` must provide both Chinese and English versions.

## Decision

Every `docs/**/*.md` document must include:

- `## 中文版`
- `## English Version`

The documentation may use a single-file bilingual format. The initial phase uses the single-file bilingual format to reduce synchronization overhead.

## Requirements

- When adding or modifying docs, both Chinese and English content must be updated together.
- README may remain the product entry point, but it should link to bilingual docs.
- SRS, Architecture, User Stories, and ADRs must all be bilingual.
- CI repository contract validation must check whether docs files contain bilingual sections.

## Consequences

- Chinese-speaking teams can discuss product and architecture quickly.
- English reviewers, external contributors, and AI agents can understand the specification.
- Documentation changes become slightly more expensive, but cross-language misunderstanding risk is reduced.
