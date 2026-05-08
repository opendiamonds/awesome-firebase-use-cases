# B. Cross-Cloud Component Selection Logic Specification

## 1. Introduction
本文件定義跨雲元件選型的邏輯基準。當使用者需要在不同雲平台間進行選擇時，系統應提供科學且數據化的評估建議。

## 2. Service Equivalency Matrix
系統必須維護一個動態的服務對等表，包含但不限於：
| Category | AWS | GCP | Azure |
| :--- | :--- | :--- | :--- |
| Compute | EC2 | Compute Engine | Virtual Machines |
| Serverless | Lambda | Cloud Functions | Azure Functions |
| Managed SQL | RDS | Cloud SQL | Azure SQL DB |
| Object Storage | S3 | GCS | Blob Storage |

## 3. Decision Matrix Criteria
選型時需考慮以下維度：
- **Performance**: vCPU 類型、IOPS 限制、網路延遲。
- **SLA**: 服務等級協議的百分比與賠償條款。
- **Regional Availability**: 該服務在目標區域 (Region) 是否已上線。
- **Cost Risk**: 是否有潛在的昂貴計費項（如隱藏的 API 調用費）。
- **Vendor Lock-in**: 使用該服務是否會導致遷移困難（e.g., 使用 AWS DynamoDB vs. Managed MongoDB）。

## 4. Recommendation Engine Weights
系統支援三種推薦模式：
1. **Cost Optimized**: 優先選擇 TCO 最低的方案。
2. **Performance Optimized**: 優先選擇效能指標最高的方案。
3. **Balanced**: 在 SLA、效能與成本間取得平衡。

---

# English Version

## 1. Introduction
Defines logic for cross-cloud service comparison and recommendation.

## 2. Equivalency Matrix
Maintain a mapping table for core cloud services across AWS, GCP, and Azure.

## 3. Selection Criteria
Evaluate based on Performance, SLA, Availability, Cost, and Lock-in risk.

## 4. Weights
Support Cost-Optimized, Performance-Optimized, and Balanced recommendation modes.
