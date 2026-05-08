# A. Architecture Design Module Specification

## 1. Introduction
本文件詳細定義 Cloud-360 的架構設計模組需求。該模組負責將使用者的自然語言輸入轉化為結構化的雲端架構設計。

## 2. Natural Language Processing (NLP) Requirements
### 2.1 Keyword Identification
系統必須能識別並提取以下關鍵要素：
- **Workload Type**: `web-app`, `data-pipeline`, `batch-job`, `ecommerce`, `saas`.
- **High Availability (HA)**: `multi-az`, `multi-region`, `active-active`, `active-passive`.
- **Target Provider**: `aws`, `gcp`, `azure`, `multi-cloud`.
- **Security & Compliance**: `pci-dss`, `hipaa`, `iso27001`, `public-facing`, `private-only`.

### 2.2 Intent Parsing
- 識別使用者是在「建立新架構」還是「修改現有架構」。
- 如果需求不明確，系統必須主動提出澄清問題。

## 3. Diagram Generation Logic
### 3.1 Draw.io XML Integration
- 系統必須生成符合 diagrams.net (draw.io) XML Schema 的文件。
- 元件必須使用官方對應的樣式標籤 (e.g., `mxgraph.aws3.ec2`).
- 支援自動佈局 (Auto-layout) 算法，確保圖面整潔。

### 3.2 Mermaid Support
- 生成 `flowchart TD` 或 `C4Context` 格式。
- 支援在 AI Chat 中即時渲染預覽。

## 4. Architectural Validation Rules
- **HA Check**: 如果使用者要求高可用，但設計中缺少 Multi-AZ 或 Load Balancer，必須提出警告。
- **DR Check**: 檢查備援區域的數據同步機制 (e.g., RDS Cross-Region Read Replica).
- **Security Check**: 檢查是否有未受保護的公網入口。

---

# English Version

## 1. Introduction
This document defines the detailed requirements for the Architecture Design module.

## 2. NLP Requirements
- **Keyword Identification**: Extract workload, HA, provider, and security tags.
- **Intent Parsing**: Distinguish between creation and modification.

## 3. Diagram Generation
- **Draw.io**: Generate XML compatible with diagrams.net using official icon sets.
- **Mermaid**: Support for chat preview rendering.

## 4. Validation Rules
- Enforce HA and DR best practices based on user intent.
