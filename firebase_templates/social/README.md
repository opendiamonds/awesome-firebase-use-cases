# 🌐 社群/內容創作模板（Social）

內容創作者、社群經營者適用的 Firebase 模板，用 AI 加速內容產出與互動。

---

## 📋 收錄範本

| 模板 | 說明 | Firebase 核心 | AI 整合 |
|------|------|--------------|---------|
| content-calendar | AI 內容行事曆：排程管理 + 靈感建議 | Auth + Firestore + FCM | Gemini 靈感生成 |
| social-inbox | 社群訊息收件匣：多平台統一管理回覆 | Functions + Firestore + Auth | Gemini 自動回覆建議 |
| analytics-dashboard | 社群數據儀表板：多平台數據彙整 | Analytics + Firestore + Functions | Gemini 數據解讀 |
| newsletter-generator | 電子報自動生成：根據文章產出精美 Newsletter | Functions + Storage + Firestore | Gemini 文章摘要 + 排版 |
| hashtag-suggester | AI Hashtag 建議：分析內文，推薦最佳標籤 | Functions + Firestore | Gemini Hashtag 分析 |
| comment-moderator | AI 留言審核：自動標記不當留言 | Functions + Firestore + Auth | Gemini 內容審核 |
| content-translator | 內容多語翻譯：一鍵翻譯成多語版本 | Functions + Storage + Firestore | Gemini 翻譯 |
| creator-monetization | 創作者變現追蹤：收入統計 + AI 建議 | Firestore + Functions + Analytics | Gemini 收益分析 |

---

## 🚀 貢獻新規模板

新增社群模板的方式：

1. 在本資料夾建立新子資料夾：`[template-name]/`
2. 放入完整的 Firebase 程式碼
3. **必須包含詳細的 `README.md`（見主目錄文件規範）**
4. PR 標題格式：`[social] 新增 [template-name]`

---

## 📖 文件撰寫規範

每個社群模板的 README.md 必須包含：

- [ ] 場景介紹（這個 Template 解決什麼痛點）
- [ ] 前置需求（Firebase 專案、第三方 API Key）
- [ ] 安裝步驟（Step-by-step）
- [ ] 功能說明（截圖 + 操作方式）
- [ ] AI 整合方式
- [ ] 多平台串接設定（如 LINE、Instagram 等）
- [ ] 客製化指南
- [ ] 部署教學
