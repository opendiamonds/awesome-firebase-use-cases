# 🔌 Firebase × n8n Workflows

n8n（開源自動化平台）與 Firebase 結合的 Workflow 範本。

---

## 📋 收錄 Workflows

| Workflow | 觸發條件 | AI Action | 輸出 |
|---------|---------|---------|------|
| new-user-welcome | Firebase Auth 新用戶註冊 | Gemini 生成長文案 | 發送個人化歡迎 Email |
| firestore-sync-notion | Firestore 文件異動 | AI 分類 + 翻譯 | 同步到 Notion/Linear |
| crash-to-issue | Crashlytics Webhook | AI 生成重現步驟 | 自動开 GitHub Issue |
| invoice-ocr-log | Firebase Storage 發票截圖上傳 | Gemini Vision 辨識 + 分類 | 自動寫入記帳 Firestore |
| weekly-report | n8n Scheduler（每週） | Gemini 分析數據 + 摘要 | 發送 Email + 生成圖表 |
| user-segmentation | Firestore 用戶資料更新 | Gemini 行為分析 | 分類到不同受眾群 |
| content-auto-post | Storage 新增內容檔案 | Gemini 生成文案 | 自動發佈到多平台 |
| support-ticket-escalation | Firestore 新增 Support Ticket | Gemini 緊急程度判斷 | 升級到 Slack 頻道 |

---

## ⚙️ n8n + Firebase 設定前置需求

1. **n8n 運行環境**（自架或 n8n.cloud）
2. **Firebase 服務帳號金鑰**（JSON）
3. **Firebase Admin SDK** 在 n8n 中的設定
4. 依據各 Workflow 需要額外 API Key（Gemini、Notion、GitHub 等）

---

## 📚 n8n Workflow 檔案格式

每個 Workflow 資料夾需包含：

```
[workflow-name]/
├── README.md
├── workflow.json        # n8n 可匯入的 JSON 檔
└── screenshots/         # 設定截圖（可選）
```

---

## 🚀 快速上手

```bash
# 1. 安裝 n8n
npm install -g n8n

# 2. 啟動 n8n
n8n start

# 3. 匯入 workflow JSON
# n8n 介面 → Import from File → 選擇 workflow.json

# 4. 設定 Firebase 服務帳號與 API Key
```

---

## 📖 README.md 規範

每個 n8n Workflow 的 README.md 必須包含：

- [ ] 場景介紹
- [ ] Firebase 觸發方式（Auth Trigger / Firestore Trigger / Webhook URL）
- [ ] n8n Node 設定說明
- [ ] Firebase Admin SDK 初始化方式
- [ ] 必要 API Key 清單與取得方式
- [ ] 詳細設定步驟（截圖最佳）
- [ ] 測試方式
- [ ] 常見問題排除
