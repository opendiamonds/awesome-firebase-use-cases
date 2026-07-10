"""
collab_router.py — 架構圖 CRUD、分享、WebSocket 共編，以及 A4 聊天持久化 API

A4 端點：
  GET  /workspace/bootstrap     — 還原 last_opened + 該圖聊天
  GET  /diagrams/{id}/chat      — 讀取聊天
  PUT  /diagrams/{id}/chat      — 儲存聊天
  DELETE /diagrams/{id}/chat     — 清空該圖聊天（不刪圖）
  PUT  /workspace/last-opened   — 更新上次開啟圖
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db
from models import User, UserDiagram, UserDiagramChat
from services.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

# 限制持久化輪數，避免 messages_json 過大
MAX_CHAT_MESSAGES = 100

DEFAULT_WELCOME = (
    "嗨！我是您的 AI 雲端架構助理 👋\n"
    "請描述您想建立的雲端架構，例如：\n"
    "✨ 我要做一個電商網站\n"
    "✨ 我要一個包含 WAF 與 Aurora 的高可用架構"
)


class ConnectionManager:
    def __init__(self):
        # workspace_id -> list of WebSockets
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, workspace_id: str):
        await websocket.accept()
        if workspace_id not in self.active_connections:
            self.active_connections[workspace_id] = []
        self.active_connections[workspace_id].append(websocket)
        logger.info(
            "WebSocket connected to workspace %s. Total: %s",
            workspace_id,
            len(self.active_connections[workspace_id]),
        )

    def disconnect(self, websocket: WebSocket, workspace_id: str):
        if workspace_id in self.active_connections:
            if websocket in self.active_connections[workspace_id]:
                self.active_connections[workspace_id].remove(websocket)
            if not self.active_connections[workspace_id]:
                del self.active_connections[workspace_id]
        logger.info("WebSocket disconnected from workspace %s.", workspace_id)

    async def broadcast(
        self, message: str, workspace_id: str, exclude: WebSocket = None
    ):
        if workspace_id in self.active_connections:
            for connection in self.active_connections[workspace_id]:
                if connection != exclude:
                    try:
                        await connection.send_text(message)
                    except Exception as e:
                        logger.error(
                            "Error broadcasting to a client in %s: %s", workspace_id, e
                        )


manager = ConnectionManager()


def _user_can_access_diagram(user: User, diagram: UserDiagram) -> bool:
    """擁有者或被分享者可存取。"""
    if diagram.user_id == user.id:
        return True
    return diagram in (user.shared_diagrams or [])


def _get_accessible_diagram(
    diagram_id: int, user: User, db: Session
) -> UserDiagram:
    diagram = db.query(UserDiagram).filter(UserDiagram.id == diagram_id).first()
    if not diagram:
        raise HTTPException(status_code=404, detail="Diagram not found")
    if not _user_can_access_diagram(user, diagram):
        raise HTTPException(status_code=403, detail="Access denied")
    return diagram


def _parse_messages(raw: str) -> List[dict[str, str]]:
    try:
        data = json.loads(raw or "[]")
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        logger.warning("messages_json 解析失敗，回傳空陣列")
    return []


def _serialize_messages(messages: List[Any]) -> str:
    cleaned: List[dict[str, str]] = []
    for m in messages[-MAX_CHAT_MESSAGES:]:
        if isinstance(m, dict):
            role = m.get("role", "user")
            content = m.get("content", "")
        else:
            continue
        if role not in ("user", "assistant"):
            continue
        cleaned.append({"role": role, "content": str(content)})
    return json.dumps(cleaned, ensure_ascii=False)


def _get_or_create_chat(
    user_id: int, diagram_id: int, db: Session
) -> UserDiagramChat:
    chat = (
        db.query(UserDiagramChat)
        .filter(
            UserDiagramChat.user_id == user_id,
            UserDiagramChat.diagram_id == diagram_id,
        )
        .first()
    )
    if not chat:
        chat = UserDiagramChat(
            user_id=user_id,
            diagram_id=diagram_id,
            messages_json="[]",
        )
        db.add(chat)
        db.commit()
        db.refresh(chat)
    return chat


@router.websocket("/ws/{workspace_id}")
async def websocket_endpoint(websocket: WebSocket, workspace_id: str):
    await manager.connect(websocket, workspace_id)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                await manager.broadcast(data, workspace_id, exclude=websocket)
            except Exception as e:
                logger.error("Error processing message: %s", e)
    except WebSocketDisconnect:
        manager.disconnect(websocket, workspace_id)


@router.get("/users")
def get_users(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    users = db.query(User).filter(User.id != current_user.id).all()
    return [{"id": u.id, "username": u.username, "role": u.role} for u in users]


class SaveDiagramRequest(BaseModel):
    xml_data: str
    title: str = "未命名架構圖"


class ShareDiagramRequest(BaseModel):
    user_ids: List[int]


class SaveChatRequest(BaseModel):
    messages: List[dict[str, str]] = Field(default_factory=list)


class LastOpenedRequest(BaseModel):
    diagram_id: Optional[int] = None


@router.get("/diagrams")
def list_my_diagrams(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    owned = db.query(UserDiagram).filter(UserDiagram.user_id == current_user.id).all()
    shared = current_user.shared_diagrams
    all_diagrams = list(set(owned + shared))
    all_diagrams.sort(key=lambda x: x.updated_at, reverse=True)

    return [
        {
            "id": d.id,
            "title": d.title,
            "updated_at": d.updated_at,
            "is_owner": d.user_id == current_user.id,
        }
        for d in all_diagrams
    ]


@router.get("/workspace/bootstrap")
def workspace_bootstrap(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    A4：進入工作區時一次取得上次開啟圖 + XML + 聊天。
    若 last_opened 無效或無權限，回傳 null diagram 與預設歡迎訊息。
    """
    last_id = current_user.last_opened_diagram_id
    diagram_payload = None
    messages: List[dict[str, str]] = [
        {"role": "assistant", "content": DEFAULT_WELCOME}
    ]

    if last_id:
        diagram = db.query(UserDiagram).filter(UserDiagram.id == last_id).first()
        if diagram and _user_can_access_diagram(current_user, diagram):
            chat = (
                db.query(UserDiagramChat)
                .filter(
                    UserDiagramChat.user_id == current_user.id,
                    UserDiagramChat.diagram_id == diagram.id,
                )
                .first()
            )
            stored = _parse_messages(chat.messages_json) if chat else []
            if stored:
                messages = stored
            diagram_payload = {
                "id": diagram.id,
                "title": diagram.title,
                "xml_data": diagram.xml_data,
                "updated_at": diagram.updated_at,
                "is_owner": diagram.user_id == current_user.id,
                "shared_user_ids": (
                    [u.id for u in diagram.shared_users]
                    if diagram.user_id == current_user.id
                    else []
                ),
            }
        else:
            # 無效指標：清掉，避免下次再踩
            current_user.last_opened_diagram_id = None
            db.commit()
            last_id = None

    return {
        "last_opened_diagram_id": last_id,
        "diagram": diagram_payload,
        "messages": messages,
    }


@router.put("/workspace/last-opened")
def set_last_opened(
    request: LastOpenedRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新使用者上次開啟的架構圖。"""
    if request.diagram_id is None:
        current_user.last_opened_diagram_id = None
        db.commit()
        return {"status": "success", "last_opened_diagram_id": None}

    _get_accessible_diagram(request.diagram_id, current_user, db)
    current_user.last_opened_diagram_id = request.diagram_id
    db.commit()
    return {"status": "success", "last_opened_diagram_id": request.diagram_id}


@router.get("/diagrams/{diagram_id}/chat")
def get_diagram_chat(
    diagram_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_accessible_diagram(diagram_id, current_user, db)
    chat = (
        db.query(UserDiagramChat)
        .filter(
            UserDiagramChat.user_id == current_user.id,
            UserDiagramChat.diagram_id == diagram_id,
        )
        .first()
    )
    messages = _parse_messages(chat.messages_json) if chat else []
    if not messages:
        messages = [{"role": "assistant", "content": DEFAULT_WELCOME}]
    return {"diagram_id": diagram_id, "messages": messages}


@router.put("/diagrams/{diagram_id}/chat")
def save_diagram_chat(
    diagram_id: int,
    request: SaveChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_accessible_diagram(diagram_id, current_user, db)
    chat = _get_or_create_chat(current_user.id, diagram_id, db)
    chat.messages_json = _serialize_messages(request.messages)
    current_user.last_opened_diagram_id = diagram_id
    db.commit()
    return {"status": "success", "message": "Chat saved"}


@router.delete("/diagrams/{diagram_id}/chat")
def clear_diagram_chat(
    diagram_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """清空該使用者在此架構圖的對話；不刪除圖表 XML。"""
    _get_accessible_diagram(diagram_id, current_user, db)
    chat = (
        db.query(UserDiagramChat)
        .filter(
            UserDiagramChat.user_id == current_user.id,
            UserDiagramChat.diagram_id == diagram_id,
        )
        .first()
    )
    if chat:
        db.delete(chat)
        db.commit()
    return {
        "status": "success",
        "message": "Chat cleared",
        "messages": [{"role": "assistant", "content": DEFAULT_WELCOME}],
    }


@router.get("/diagrams/{diagram_id}")
def get_diagram(
    diagram_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    diagram = _get_accessible_diagram(diagram_id, current_user, db)
    return {
        "id": diagram.id,
        "title": diagram.title,
        "xml_data": diagram.xml_data,
        "updated_at": diagram.updated_at,
        "is_owner": diagram.user_id == current_user.id,
        "shared_user_ids": (
            [u.id for u in diagram.shared_users]
            if diagram.user_id == current_user.id
            else []
        ),
    }


@router.post("/diagrams")
def create_diagram(
    request: SaveDiagramRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    diagram = UserDiagram(
        user_id=current_user.id, title=request.title, xml_data=request.xml_data
    )
    db.add(diagram)
    db.commit()
    db.refresh(diagram)
    current_user.last_opened_diagram_id = diagram.id
    db.commit()
    return {
        "id": diagram.id,
        "status": "success",
        "message": "Diagram created successfully",
    }


@router.put("/diagrams/{diagram_id}")
def update_diagram(
    diagram_id: int,
    request: SaveDiagramRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    diagram = _get_accessible_diagram(diagram_id, current_user, db)
    diagram.xml_data = request.xml_data
    diagram.title = request.title
    current_user.last_opened_diagram_id = diagram_id
    db.commit()
    return {"status": "success", "message": "Diagram updated successfully"}


@router.post("/diagrams/{diagram_id}/share")
def share_diagram(
    diagram_id: int,
    request: ShareDiagramRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    diagram = db.query(UserDiagram).filter(UserDiagram.id == diagram_id).first()
    if not diagram:
        raise HTTPException(status_code=404, detail="Diagram not found")
    if diagram.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the owner can share this diagram")

    users = db.query(User).filter(User.id.in_(request.user_ids)).all()
    diagram.shared_users = users
    db.commit()
    return {"status": "success", "message": "Share settings updated"}
