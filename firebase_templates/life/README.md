# 🏠 生活應用模板（Life）

日常生活所需的 Firebase 模板，讓你用 Firebase + AI 管理生活中的各種大小事。

---

## 📋 收錄範本

| 模板 | 說明 | Firebase 核心 | AI 整合 |
|------|------|--------------|---------|
| expense-tracker | 智能記帳：上傳發票截圖，AI 自動分類記帳 | Storage + Firestore + Functions | Gemini Vision OCR |
| travel-planner | 旅遊行程管家：AI 推薦行程，同步共享行程 | Auth + Firestore + Storage | Gemini 行程建議 |
| ticket-bot | 搶票神器：即時庫存鎖定，搶票通知 | Realtime Database + Functions + FCM | Gemini 搶票時機預測 |
| fitness-tracker | 健身追蹤：記錄運動數據，AI 教練調整課表 | Auth + Firestore + Analytics | Gemini 訓練建議 |
| shared-calendar | 共享行事曆：多人同步，AI 衝突偵測與調度 | Realtime Database + Auth + FCM | Gemini 行程優化 |
| pet-log | 寵物照護日誌：照片記錄，AI 行為異常偵測 | Storage + Firestore + Functions | Gemini Vision |
| reading-tracker | 閱讀追蹤：書單管理，AI 生成閱讀筆記摘要 | Auth + Firestore | Gemini 文件摘要 |
| grocery-list | 共享採購清單：多人即時編輯，AI 推薦常買清單 | Realtime Database + Auth | Gemini 智慧推薦 |

---

## 🚀 貢獻新規模板

新增生活模板的方式：

1. 在本資料夾建立新子資料夾：`[template-name]/`
2. 放入完整的 Firebase 程式碼
3. **必須包含詳細的 `README.md`（見主目錄文件規範）**
4. PR 標題格式：`[life] 新增 [template-name]`

---

## 📖 文件撰寫規範

每個生活模板的 README.md 必須包含：

- [ ] 場景介紹（這個 Template 解決什麼痛點）
- [ ] 前置需求（Firebase 專案、API Key）
- [ ] 安裝步驟（Step-by-step）
- [ ] 功能說明（截圖 + 操作方式）
- [ ] AI 整合方式（Gemini API 設定）
- [ ] 客製化指南（改成自己的樣式）
- [ ] 部署教學（Firebase Hosting / Cloud Run）
