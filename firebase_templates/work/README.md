# 💼 工作應用模板（Work）

提升工作效率的 Firebase 模板，適用於職場、個人工作者、小型團隊。

---

## 📋 收錄範本

| 模板 | 說明 | Firebase 核心 | AI 整合 |
|------|------|--------------|---------|
| project-board | 專案管理看板：Kanban 多人協作，AI 生成 WBS | Firestore + Realtime + Auth | Gemini WBS 自動生成 |
| smart-meeting | 會議智慧助理：會前自動整理議程，會後生成紀錄 | Functions + Gemini + Calendar API | Gemini 會議摘要 + Action Items |
| ai-secretary | AI 文書助理：文件摘要、翻譯、潤稿 | Functions + Vertex AI + Storage | Gemini 文件處理 |
| knowledge-base | 內部知識庫：自然語言查詢，RAG 架構 | Firestore + Vertex AI Search | RAG 檢索 + 生成 |
| customer-feedback | 客戶回饋系統：情感分析，分類 Priority | Functions + Firestore + Analytics | Gemini 情感分析 |
| shift-scheduler | 排班/資源調度：AI 優化排班，平衡人力 | Realtime Database + Functions | Gemini 排班優化 |
| employee-onboarding | 新人入職助手：文件簽核、任務指引、進度追蹤 | Auth + Firestore + FCM | Gemini 入職指引 |
| goal-tracker | 團隊目標追蹤：OKR 管理，AI 進度預測 | Firestore + Functions + Analytics | Gemini 進度分析 |

---

## 🚀 貢獻新規模板

新增工作模板的方式：

1. 在本資料夾建立新子資料夾：`[template-name]/`
2. 放入完整的 Firebase 程式碼
3. **必須包含詳細的 `README.md`（見主目錄文件規範）**
4. PR 標題格式：`[work] 新增 [template-name]`

---

## 📖 文件撰寫規範

每個工作模板的 README.md 必須包含：

- [ ] 場景介紹（這個 Template 解決什麼痛點）
- [ ] 前置需求（Firebase 專案、API Key、權限設定）
- [ ] 安裝步驟（Step-by-step）
- [ ] 功能說明（截圖 + 操作方式）
- [ ] AI 整合方式（Gemini API / Vertex AI 設定）
- [ ] 團隊協作設定（分享權限、邀請成員）
- [ ] 客製化指南（改成自己的品牌與流程）
- [ ] 部署教學（Firebase Hosting / Cloud Run）
