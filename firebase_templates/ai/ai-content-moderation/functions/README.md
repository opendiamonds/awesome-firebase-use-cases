# 🤖 AI Content Moderation — Firebase Cloud Functions + Gemini

## 場景介紹

**實際可部署**的內容審核系統。當使用者在 App 發布內容時，自動觸發 Firebase Function，將內容送至 Gemini AI 分析，並根據結果自動標記或通知管理員。

適合：社群平台、論壇、評論系統、即時通訊 App

## 系統架構

```
使用者發布內容 → Firestore onCreate Trigger → Cloud Functions → Gemini API
                                                         ↓
                                        結果寫回 Firestore + 通知管理員
```

## 前置需求

1. Firebase 專案（Blaze Plan）
2. Gemini API Key：https://aistudio.google.com/apikey
3. Node.js 20+
4. Firebase CLI

## 安裝

```bash
# 複製到你的專案
cp -r firebase_templates/ai/ai-content-moderation/functions /path/to/your/project/

cd functions
npm install
```

## 設定環境變數

在 Firebase Console → Functions → 環境變數，新增：

```
GEMINI_API_KEY=your_api_key_here
```

## 部署

```bash
npm run build
firebase deploy --only functions
```

## Firestore 文件結構

### 輸入（Trigger）
```json
{ "text": "使用者發布的內容", "authorId": "user123" }
```

### 輸出（更新後）
```json
{
  "text": "使用者發布的內容",
  "moderation": {
    "safe": false,
    "categories": ["仇恨言論"],
    "confidence": 0.92,
    "flaggedAt": "timestamp"
  },
  "moderatedAt": "timestamp"
}
```

## 審核的 7 大類別

| 類別 | 說明 |
|------|------|
| 仇恨言論或歧視 | 種族、性別、宗教等歧視 |
| 暴力或血腥 | 暴力描述、武器、血腥場面 |
| 色情或成人內容 | 性暗示、裸露內容 |
| 騷擾或霸凌 | 人身攻擊、網路霸凌 |
| 危險或非法活動 | 毒品、自殺指導、犯罪教學 |
| 誤導或假訊息 | 謠言、偽科學陰謀論 |
| 個人隱私洩露 | 電話、地址、身份證號等個資 |

## 成本估算

以 100萬 DAU 社群 App 為例（每人每天 5 篇）：

- Firestore：~$1.8/天
- Gemini 1.5 Flash：~$0.18/天
- Cloud Functions：~$0.5/天
- **總計：約 $2.5/天（~$75/月）**

---

*此模板為 cloud-360 實用化項目，PR 歡迎。*
