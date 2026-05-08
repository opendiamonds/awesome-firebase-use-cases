# C. Cost Estimation & FinOps Rules Specification

## 1. Introduction
本文件定義成本估算與 FinOps 的計算規則，確保平台產出的 TCO 報告具有參考價值與準確性。

## 2. Pricing Data Sources
系統必須從以下來源獲取即時價格：
- **AWS**: Price List Query API.
- **GCP**: Cloud Billing Catalog API.
- **Azure**: Retail Prices API.
- **Fall-back**: 如果 API 無法存取，使用本地緩存的價格數據並註明。

## 3. Calculation Rules
### 3.1 Compute Cost
- 計算公式: `Rate * Quantity * Usage_Hours`.
- 考慮 Spot/Preemptible 的折扣率（取最近 30 天平均值）。

### 3.2 Data Egress (Traffic Cost)
這是最容易被忽視的成本。系統必須區分：
- **Intra-Region**: 免費或低價。
- **Inter-Region**: 跨區流量費。
- **Internet Egress**: 傳出到公網的流量費。
- **Cross-Cloud**: 當數據從 AWS 流向 GCP 時的累積費用。

### 3.3 Storage Cost
- 包含預留容量 (Provisioned Capacity) 與實際使用量。
- 包含請求費 (PUT/GET requests).

## 4. Right-sizing Analysis
- 推薦邏輯: 如果 CPU 平均利用率 < 10% 且峰值 < 30% 持續超過 7 天，建議調降實例規格 (Downsize).

---

# English Version

## 1. Introduction
Defines rules for cost estimation and FinOps analysis.

## 2. Data Sources
Integrate with official Pricing APIs for AWS, GCP, and Azure.

## 3. Calculation Rules
Detailed logic for Compute, Storage, and Egress (Intra-Region, Inter-Region, Internet, Cross-Cloud).

## 4. Right-sizing
Logic for resource optimization recommendations based on utilization.
