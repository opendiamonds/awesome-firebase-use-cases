# 🔌 Firebase × Zapier Workflows

Zapier 與 Firebase 結合的 Workflow 範本（Zap）。

---

## 📋 收錄 Workflows（Zaps）

| Zap | 觸發條件 | AI Action | 輸出 |
|-----|---------|---------|------|
| new-user-crm | Firebase Auth 新用戶 | — | 新增到 HubSpot/Salesforce CRM |
| firestore-to-sheet | Firestore 文件新增/更新 | — | 同步到 Google Sheets |
| crash-pagerduty | Crashlytics 新 Crash | AI 分析嚴重度 | 觸發 PagerDuty Alert |
| analytics-to-slack | Analytics 事件觸發 | Gemini 摘要 | 發送 Slack 訊息 |
| storage-new-file-email | Storage 新檔案上傳 | Gemini Vision 描述 | 發送 Email 通知 |

---

## ⚙️ Zapier + Firebase 設定前置需求

1. **Zapier 帳號**
2. **Firebase Realtime Database Web 勾選**（Zapier 主要支援 Realtime DB）
3. **Firebase Admin SDK** 用於 Webhook 觸發
4. 依據各 Zap 需要額外 API Key

> ⚠️ **注意**：Zapier 對 Firestore 原生支援較少，建議使用 Realtime Database 或透過 Firebase Functions Webhook 轉接。

---

## 📚 Zap 檔案格式

每個 Workflow 資料夾需包含：

```
[workflow-name]/
├── README.md
├── zapier-zap.json    # Zap 設定截圖或 JSON
└── screenshots/       # 設定截圖（可選）
```

---

## 📖 README.md 規範

每個 Zapier Workflow 的 README.md 必須包含：

- [ ] 場景介紹
- [ ] Firebase 觸發設定（Realtime DB / Webhook）
- [ ] Zapier Trigger/Action 模組設定說明
- [ ] 必要 API Key 清單與取得方式
- [ ] 詳細設定步驟（截圖最佳）
- [ ] 測試方式
- [ ] 常見問題排除
