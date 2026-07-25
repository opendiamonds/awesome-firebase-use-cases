# NFR Requirements - Unit A1 (Architecture Design Agent)

## 中文版

## 1. 性能與響應時間 (Performance)
* **LLM 回應處理**：所有對話與畫圖請求使用 SSE (Server-Sent Events) 進行串流傳輸，確保使用者能即時看見進度與代理思考過程，首字延遲 (TTFT) 應小於 3 秒。
* **Webhook 外部請求**：向 n8n 查詢服務圖示 SVG 的請求必須設定明確的超時時間（上限 5.0 秒），以防止因 n8n 服務無響應導致整個繪圖 API 掛起。
* **圖示 Fallback**：若圖示取得超時或失敗，必須於 0.5 秒內切換至灰底 fallback 圖示，保證產圖流程不因圖示缺失中斷。

## 2. 安全性與合規性 (Security & Compliance)
* **RBAC 權限管控**：繪圖工具 (`draw_architecture_diagram`) 與對話產生端點均必須受 JWT 機制保護，且發起帳號必須擁有 `A1.edit`（寫入/畫圖）或 `A1.view`（檢視/對話）權限。
* **金鑰安全性**：API 金鑰（如 OpenRouter Key）嚴禁明文寫入程式碼或提交至 git，必須一律通過 `backend/.env` 環境變數注入。

## 3. 可用性與彈性 (Availability & Resiliency)
* **故障降級**：在 OpenRouter 連線失效時，應能回報明確的「外部 AI 服務無法連線」錯誤，而非引發系統崩潰，不影響其他本地資料庫與共編模組的運作。

---

## English Version

## 1. Performance & Response Time
* **LLM Response Handling**: All conversation and diagram-generation requests use SSE (Server-Sent Events) for streaming, ensuring users can see progress and the agent's reasoning in real time. Time-To-First-Token (TTFT) must be less than 3 seconds.
* **Webhook External Requests**: Requests to n8n for cloud-service-icon SVGs must have an explicit timeout (maximum 5.0 seconds) to prevent the entire diagram API from hanging when the n8n service is unresponsive.
* **Icon Fallback**: If icon retrieval times out or fails, the system must switch to a grey-background fallback icon within 0.5 seconds, guaranteeing the diagram-generation flow is not interrupted by a missing icon.

## 2. Security & Compliance
* **RBAC Permission Control**: The diagram tool (`draw_architecture_diagram`) and the conversation-generation endpoint must both be protected by the JWT mechanism. The initiating account must hold `A1.edit` (write/draw) or `A1.view` (view/converse) permissions.
* **Key Security**: API keys (e.g., the OpenRouter Key) must never be written in plaintext in the codebase or committed to git. They must always be injected via `backend/.env` environment variables.

## 3. Availability & Resiliency
* **Graceful Degradation**: When the OpenRouter connection fails, the system must report a clear "External AI service unavailable" error rather than causing a system crash, without affecting the operation of other local database and collaborative-editing modules.
