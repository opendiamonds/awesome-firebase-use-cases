/**
 * Firebase Cloud Functions + Gemini AI 內容審核
 *
 * 觸發：Firestore `users/{userId}/posts/{postId}` 新增文件
 * 功能：
 *   1. 讀取文件內容
 *   2. 送至 Gemini API 進行內容審核
 *   3. 回寫審核結果（safe: boolean, categories: string[], confidence: number）
 *   4. 若判定為不安全，自動標記並通知管理員
 */

import * as functions from "firebase-functions";
import * as admin from "firebase-admin";

admin.initializeApp();

const db = admin.firestore();

interface ModerationResult {
  safe: boolean;
  categories: string[];
  confidence: number;
  flaggedAt: FirebaseFirestore.FieldValue;
}

/**
 * 內容審核核心函數
 * 觸發於：`users/{userId}/posts/{postId}`
 */
export const moderateContent = functions.firestore
  .document("users/{userId}/posts/{postId}")
  .onCreate(async (snap, context) => {
    const { userId, postId } = context.params;
    const data = snap.data();
    const content = data.text || data.content || data.message || "";

    if (!content) {
      functions.logger.warn("Empty content, skipping moderation");
      return null;
    }

    functions.logger.info(`Moderating post ${postId} from user ${userId}`);

    try {
      const result = await callGeminiModeration(content);

      await snap.ref.update({
        moderation: result,
        moderatedAt: admin.firestore.FieldValue.serverTimestamp(),
      } as Record<string, unknown>);

      if (!result.safe) {
        await notifyAdmin(userId, postId, result.categories);
      }

      functions.logger.info(`Moderation complete: safe=${result.safe}`);
      return result;
    } catch (error) {
      functions.logger.error("Moderation failed:", error);
      await snap.ref.update({
        moderation: {
          safe: null,
          error: (error as Error).message,
          flaggedAt: admin.firestore.FieldValue.serverTimestamp(),
        },
        moderatedAt: admin.firestore.FieldValue.serverTimestamp(),
      });
      return null;
    }
  });

async function callGeminiModeration(content: string): Promise<ModerationResult> {
  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) throw new Error("GEMINI_API_KEY not configured");

  const prompt = `你是內容審核系統。請分析以下使用者生成內容（UGC），判斷是否包含以下任何一種不當內容：
1. 仇恨言論或歧視
2. 暴力或血腥內容
3. 色腥或成人內容
4. 騷擾或霸凌
5. 危險或非法活動
6. 誤導或假訊息
7. 個人隱私洩露

請以 JSON 格式回覆（只回覆 JSON，不要有其他文字）：
{"safe": true或false, "categories": ["偵測到的類別陣列，如果安全則為空"], "confidence": 0.0到1.0}

內容：${content}`;

  const response = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contents: [{ parts: [{ text: prompt }] }],
        generationConfig: { responseMimeType: "application/json", temperature: 0.1 },
      }),
    }
  );

  if (!response.ok) throw new Error(`Gemini API error: ${response.status}`);

  const result = await response.json();
  const text = result.candidates?.[0]?.content?.parts?.[0]?.text;
  if (!text) throw new Error("Empty response from Gemini");

  const parsed = JSON.parse(text);
  return {
    safe: parsed.safe ?? true,
    categories: parsed.categories ?? [],
    confidence: parsed.confidence ?? 0.5,
    flaggedAt: admin.firestore.FieldValue.serverTimestamp(),
  } as ModerationResult;
}

async function notifyAdmin(
  userId: string,
  postId: string,
  categories: string[]
): Promise<void> {
  await db.collection("admin").add({
    type: "content_flagged",
    userId,
    postId,
    categories,
    createdAt: admin.firestore.FieldValue.serverTimestamp(),
    read: false,
  });
  functions.logger.warn(`Content flagged: user=${userId}, post=${postId}, categories=${categories.join(", ")}`);
}
