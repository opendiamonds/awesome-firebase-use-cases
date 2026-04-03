# 🔄 自動化 Workflows

Firebase 事件驅動的自動化 Workflows，透過 n8n、Make、Zapier 等平台串接各種服務。

---

## 📂 目錄結構

```
workflows/
├── n8n/       # Firebase × n8n Workflows
├── make/      # Firebase × Make (Integromat) Workflows
└── zapier/    # Firebase × Zapier Workflows
```

---

## 🔗 Workflow 整合架構

```
Firebase Event          Workflow Platform         輸出/Action
─────────────────       ───────────────────       ──────────────
Auth (新用戶註冊)    →   n8n / Make / Zapier   →   發送歡迎 Email
Firestore 文件異動   →   Workflow             →   同步到 Notion
Storage 檔案上傳     →   Workflow            →   觸發 AI 處理
Functions Error       →   Workflow            →   通知 Slack/Discord
Scheduler 排程       →   Workflow            →   自動生成報表
```

---

## 🤝 貢獻新 Workflow

新增 Workflow 的方式：

1. 在對應子資料夾建立新資料夾：`[workflow-name]/`
2. 放入 Workflow JSON/設定檔
3. **必須包含詳細的 `README.md`（見規範）**
4. PR 標題格式：`[n8n] 新增 [workflow-name]`

---

## 📖 文件撰寫規範

每個 Workflow 的 README.md 必須包含：

- [ ] 場景介紹
- [ ] Firebase 觸發條件（Auth / Firestore / Functions / Storage）
- [ ] 前置需求（n8n/Make/Zapier 帳號、相關 API Key）
- [ ] 詳細設定步驟（截圖說明）
- [ ] 資料流向說明
- [ ] 測試方式
- [ ] 客製化參數說明
