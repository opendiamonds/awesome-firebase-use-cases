# awesome-firebase-use-cases

> Firebase 模板 × AI 加速器 — 用詳細文件，讓你在自己的 Firebase 環境快速落地。

---

## 🎯 這個專案在做什麼？

你是不是曾經看過 Firebase 的功能，卻不知道從哪裡開始？或是架好 Firebase 之後，不知道怎麼接 AI、怎麼做自動化？

**awesome-firebase-use-cases** 收集並實作了大量 Firebase 模板，每個模板都有：

- ✅ **詳細使用者手冊**（Step-by-step 文件）
- ✅ **完整程式碼範例**（可直接複製使用）
- ✅ **AI 整合指南**（Gemini / Vertex AI / n8n）
- ✅ **快速上手腳本**（自己的 Firebase 專案直接啟動）

---

## 📂 專案結構

```
awesome-firebase-use-cases/
├── firebase_templates/          # Firebase 應用模板
│   ├── life/                   # 生活應用
│   ├── work/                   # 工作應用
│   ├── dev/                    # 開發者 SDLC
│   ├── ai/                     # Firebase × AI 整合
│   └── social/                 # 社群/內容創作
│
├── workflows/                  # 自動化 Workflows
│   └── n8n/                    # Firebase × n8n
│
└── tools/                      # 開發者工具
    ├── skills/                 # OpenClaw Skills
    └── mcp/                    # MCP Servers
```

---

## 🚀 快速開始

```bash
# 1. 挑選你想要的 Template
# 2. 詳見各資料夾的 README.md
# 3. 跟著文件一步步建立自己的 Firebase 專案
```

---

## 📚 文件目標

這個專案的核心特色是**文件品質**。

每個 Template 的 README.md 都包含：

| 區塊 | 內容 |
|------|------|
| 場景介紹 | 這個 Template 解決什麼問題 |
| 前置需求 | 需要哪些 Firebase 服務與 API Key |
| 安裝步驟 | 在自己的 Firebase 專案中如何設定 |
| 功能說明 | 各功能的操作方式 |
| AI 整合 | 怎麼接 Gemini / Vertex AI |
| 客製化指南 | 怎麼改成自己的品牌 |
| 部署方式 | Firebase Hosting / Cloud Run 部署 |

---

## 🤝 貢獻方式

歡迎提交 Issue 回報問題，或 Pull Request 貢獻新的 Template！

1. Fork 此專案
2. 建立新資料夾（格式：`firebase_templates/[分類]/[template-name]`）
3. 包含完整 README.md（依上方文件模板）
4. Pull Request → 我們會 Review 文件與程式碼

---

## 📄 License

MIT License
