"""
agent_router.py — A1 架構對話／產圖 API（SSE 適配層）

職責：
  - 驗證 JWT 與請求 body
  - 將 design_agent 事件轉成 SSE（message / progress / xml / error）
  - 不直接呼叫 OpenRouter；LLM 迴圈由 design_agent（Agent SDK）負責

契約（前端依賴，請勿變更）：
  POST /api/architecture/generate
  body: { messages: [{role, content}], current_xml?: string }
  response: text/event-stream，data 為 JSON {type, content}
"""

from __future__ import annotations

import json
import logging
import os
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from models import User
from services.design_agent import configure_openrouter_env, run_design_agent
from services.rbac import require_arch_action

logger = logging.getLogger(__name__)

router = APIRouter()


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    current_xml: Optional[str] = None


@router.post("/generate")
async def chat_and_generate(
    request: ChatRequest,
    current_user: User = Depends(require_arch_action("edit")),
):
    """
    A1 入口：轉發至 Design Agent，以 SSE 串流回傳。
    需具備架構圖生成編輯權（A1／A2／A4）。
    """
    messages = request.messages
    if not messages:
        raise HTTPException(status_code=400, detail="對話不可為空")

    # 啟動前確保 OpenRouter env 已映射（亦會在 design_agent 內再呼叫一次）
    configure_openrouter_env()

    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    auth_token = os.environ.get("ANTHROPIC_AUTH_TOKEN")

    logger.info("========================================")
    logger.info("收到畫圖/對話請求（Agent SDK 路徑），user=%s", current_user.username)
    logger.info("OPENROUTER_API_KEY 狀態: %s", "已設定" if openrouter_key else "未設定")
    logger.info("ANTHROPIC_AUTH_TOKEN 狀態: %s", "已設定" if auth_token else "未設定")

    if not openrouter_key and not auth_token:
        logger.error("錯誤: 未設定 OpenRouter / Agent SDK 認證")
        raise HTTPException(
            status_code=500,
            detail="尚未設定 OPENROUTER_API_KEY（Agent SDK 經 OpenRouter 需要此金鑰）",
        )

    payload = [{"role": m.role, "content": m.content} for m in messages]

    async def event_generator():
        # 將 design_agent 的 dict 事件包裝成 SSE data 行
        async for event in run_design_agent(payload, request.current_xml):
            chunk = json.dumps(event, ensure_ascii=False)
            yield f"data: {chunk}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
