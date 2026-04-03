# 🤖 Firebase × AI 整合模板（AI）

Firebase 生態系與 AI 平台（Gemini、Vertex AI、OpenAI）深度整合的模板集合。

---

## 📋 收錄範本

| 模板 | 說明 | Firebase 核心 | AI 整合 |
|------|------|--------------|---------|
| gen2-functions-gemini | Cloud Functions Gen2 + Gemini API 快速上手 | Functions Gen2 + Firestore | Gemini API |
| vertex-ai-rag | Firestore + Vertex AI RAG 檢索增強生成 | Firestore + Functions + Vertex AI | Vertex AI Search + PaLM |
| assistant-framework | 多輪對話 + Tool Use + 上下文記憶 | Functions + Firestore + Auth | Gemini + Tool Use |
| agentic-workflow | Firebase Functions 驅動的 Agentic Workflow | Functions + Firestore + Scheduler | Gemini Agentic |
| multimodal-pipeline | Storage trigger → Gemini Vision → Firestore | Storage + Functions + Firestore | Gemini Vision |
| ai-chatbot-firebase | 即時 AI 客服機器人：多輪對話 + 知識庫 | Functions + Firestore + FCM | Gemini + RAG |
| summarization-pipeline | 文件/音訊自動摘要 pipeline | Functions + Storage + Firestore | Gemini Pro |
| intent-classifier | 使用者意圖分類：常見問題自動分流 | Functions + Firestore + Analytics | Gemini Classification |

---

## 🔑 AI 整合的核心概念

Firebase × AI 的整合方式：

```
┌─────────────┐      ┌──────────────────┐      ┌──────────────┐
│  Firebase   │ ───→ │  Cloud Functions  │ ───→ │  AI API     │
│  Trigger    │      │  (中介處理)       │      │ (Gemini/    │
│             │      │                  │      │  Vertex AI)  │
└─────────────┘      └──────────────────┘      └──────────────┘
       ↑                     ↓
       └────────── Firebase ─┘
              (讀寫資料)
```

---

## 🚀 貢獻新規模板

新增 AI 模板的方式：

1. 在本資料夾建立新子資料夾：`[template-name]/`
2. 放入完整的 Firebase 程式碼
3. **必須包含詳細的 `README.md`（見主目錄文件規範）**
4. PR 標題格式：`[ai] 新增 [template-name]`

---

## 📖 文件撰寫規範

每個 AI 模板的 README.md 必須包含：

- [ ] 場景介紹（這個 Template 解決什麼痛點）
- [ ] AI 模型說明（Gemini / Vertex AI / GPT）
- [ ] API Key 取得方式與設定
- [ ] 安裝步驟（Step-by-step）
- [ ] AI Prompt 設計說明
- [ ] Tool Use / Function Calling 設定（如有）
- [ ] Context Window 管理策略
- [ ] 部署教學
