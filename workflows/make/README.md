# 🔌 Firebase × Make (Integromat) Workflows

Make（原 Integromat）與 Firebase 結合的 Workflow 範本。

---

## 📋 收錄 Workflows

| Workflow | 觸發條件 | AI Action | 輸出 |
|---------|---------|---------|------|
| firestore-backup-drive | Firestore 資料變動 | — | 自動備份到 Google Drive |
| new-signup-slack | Firebase Auth 新用戶 | — | 通知 Slack 頻道 |
| storage-resize-optimize | Storage 圖片上傳 | — | 自動生成縮圖 + 優化 |
| analytics-weekly-email | Analytics 每週彙整 | AI 數據解讀 | 發送摘要 Email |
| user-behavior-segment | Firestore 用戶行為更新 | Gemini 分類 | 寫入Segment |
| content-moderation | Storage 檔案上傳 | Gemini Vision 審核 | 標記/刪除不當內容 |

---

## ⚙️ Make + Firebase 設定前置需求

1. **Make 帳號**（make.com）
2. **Firebase 服務帳號金鑰**（JSON）
3. 依據各 Workflow 需要額外 API Key

---

## 📚 Make Scenario 檔案格式

每個 Workflow 資料夾需包含：

```
[workflow-name]/
├── README.md
├── scenario.json          # Make 可匯入的 Scenario
└── screenshots/           # 設定截圖（可選）
```

---

## 📖 README.md 規範

每個 Make Workflow 的 README.md 必須包含：

- [ ] 場景介紹
- [ ] Firebase 觸發模組設定方式
- [ ] Make Module 設定說明
- [ ] 必要 API Key 清單與取得方式
- [ ] 詳細設定步驟（截圖最佳）
- [ ] 測試方式
- [ ] 常見問題排除
