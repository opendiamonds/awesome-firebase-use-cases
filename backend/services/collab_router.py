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
from models import User, UserDiagram, UserDiagramChat, diagram_shares
from services.auth import get_current_user
from services.rbac import require_arch_action, user_can_arch

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

VIEW_ONLY_WELCOME = (
    "您目前為「僅檢視」權限。\n"
    "可開啟他人分享給您的架構圖，但無法編輯畫布或與 AI 對話。"
)

REVIEW_ONLY_WELCOME = (
    "您目前為「審核」權限（可檢視＋審核，不可編輯）。\n"
    "可開啟他人分享的架構圖進行審核，但無法修改畫布或與 AI 對話。"
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
    """擁有者或被分享者可存取（尚需搭配架構圖 RBAC 語意）。"""
    if diagram.user_id == user.id:
        return True
    return diagram in (user.shared_diagrams or [])


def _arch_can_edit(db: Session, user: User) -> bool:
    return user_can_arch(
        db,
        user.role,
        "edit",
        authorization_status=getattr(user, "authorization_status", "approved"),
    )


def _arch_can_view(db: Session, user: User) -> bool:
    return user_can_arch(
        db,
        user.role,
        "view",
        authorization_status=getattr(user, "authorization_status", "approved"),
    )


def _arch_can_review(db: Session, user: User) -> bool:
    return user_can_arch(
        db,
        user.role,
        "review",
        authorization_status=getattr(user, "authorization_status", "approved"),
    )

def _visible_diagrams(user: User, db: Session) -> List[UserDiagram]:
    """
    架構圖可見範圍：
    - 有編輯：自己的圖 + 被分享的圖
    - 僅檢視／僅審核（無編輯）：只能看別人分享給自己的圖
    """
    if not _arch_can_view(db, user):
        return []
    shared = list(user.shared_diagrams or [])
    if _arch_can_edit(db, user):
        owned = db.query(UserDiagram).filter(UserDiagram.user_id == user.id).all()
        all_diagrams = list({d.id: d for d in (owned + shared)}.values())
    else:
        all_diagrams = shared
    all_diagrams.sort(key=lambda x: x.updated_at, reverse=True)
    return all_diagrams


def _get_accessible_diagram(
    diagram_id: int, user: User, db: Session
) -> UserDiagram:
    if not _arch_can_view(db, user):
        raise HTTPException(status_code=403, detail="權限不足：無法檢視架構圖")
    diagram = db.query(UserDiagram).filter(UserDiagram.id == diagram_id).first()
    if not diagram:
        raise HTTPException(status_code=404, detail="Diagram not found")
    # 無編輯時：僅允許被分享的圖（不可開自己擁有的圖）
    if not _arch_can_edit(db, user):
        shared_ids = {d.id for d in (user.shared_diagrams or [])}
        if diagram.id not in shared_ids:
            raise HTTPException(
                status_code=403,
                detail="僅檢視／審核權限只能開啟他人分享的架構圖",
            )
        return diagram
    if not _user_can_access_diagram(user, diagram):
        raise HTTPException(status_code=403, detail="Access denied")
    return diagram


def _welcome_for_user(db: Session, user: User) -> str:
    if _arch_can_edit(db, user):
        return DEFAULT_WELCOME
    if _arch_can_review(db, user):
        return REVIEW_ONLY_WELCOME
    return VIEW_ONLY_WELCOME


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
    current_user: User = Depends(require_arch_action("edit")),
    db: Session = Depends(get_db),
):
    """分享對象列表：需架構圖編輯權。"""
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
    current_user: User = Depends(require_arch_action("view")),
    db: Session = Depends(get_db),
):
    all_diagrams = _visible_diagrams(current_user, db)
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
    current_user: User = Depends(require_arch_action("view")),
    db: Session = Depends(get_db),
):
    """
    A4：進入工作區時一次取得上次開啟圖 + XML + 聊天。
    僅檢視／審核時只還原「被分享」且仍可見的圖。
    """
    welcome = _welcome_for_user(db, current_user)
    last_id = current_user.last_opened_diagram_id
    diagram_payload = None
    messages: List[dict[str, str]] = [
        {"role": "assistant", "content": welcome}
    ]

    visible_ids = {d.id for d in _visible_diagrams(current_user, db)}
    if last_id and last_id in visible_ids:
        try:
            diagram = _get_accessible_diagram(last_id, current_user, db)
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
            # 僅編輯者還原個人聊天；檢視／審核用說明訊息
            if _arch_can_edit(db, current_user):
                chat = (
                    db.query(UserDiagramChat)
                    .filter(
                        UserDiagramChat.user_id == current_user.id,
                        UserDiagramChat.diagram_id == last_id,
                    )
                    .first()
                )
                parsed = _parse_messages(chat.messages_json) if chat else []
                if parsed:
                    messages = parsed
        except HTTPException:
            diagram_payload = None

    return {
        "diagram": diagram_payload,
        "messages": messages,
        "can_edit": _arch_can_edit(db, current_user),
        "can_review": _arch_can_review(db, current_user),
    }


@router.put("/workspace/last-opened")
def set_last_opened(
    request: LastOpenedRequest,
    current_user: User = Depends(require_arch_action("view")),
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
    current_user: User = Depends(require_arch_action("view")),
    db: Session = Depends(get_db),
):
    _get_accessible_diagram(diagram_id, current_user, db)
    # 無編輯權：不回傳可繼續對話的歷史，改回權限說明
    if not _arch_can_edit(db, current_user):
        return {
            "diagram_id": diagram_id,
            "messages": [
                {"role": "assistant", "content": _welcome_for_user(db, current_user)}
            ],
        }
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
    current_user: User = Depends(require_arch_action("edit")),
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
    current_user: User = Depends(require_arch_action("edit")),
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
    current_user: User = Depends(require_arch_action("view")),
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
        "can_edit": _arch_can_edit(db, current_user),
        "can_review": _arch_can_review(db, current_user),
    }


@router.post("/diagrams")
def create_diagram(
    request: SaveDiagramRequest,
    current_user: User = Depends(require_arch_action("edit")),
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
    current_user: User = Depends(require_arch_action("edit")),
    db: Session = Depends(get_db),
):
    diagram = _get_accessible_diagram(diagram_id, current_user, db)
    # 僅擁有者可改 XML（被分享者若有 edit 仍可協作寫入）
    diagram.xml_data = request.xml_data
    diagram.title = request.title
    current_user.last_opened_diagram_id = diagram_id
    db.commit()
    return {"status": "success", "message": "Diagram updated successfully"}


@router.delete("/diagrams/{diagram_id}")
def delete_diagram(
    diagram_id: int,
    current_user: User = Depends(require_arch_action("edit")),
    db: Session = Depends(get_db),
):
    """刪除架構圖（僅擁有者）。評核／聊天經 CASCADE 一併清除；分享關聯先手動移除。"""
    diagram = db.query(UserDiagram).filter(UserDiagram.id == diagram_id).first()
    if not diagram:
        raise HTTPException(status_code=404, detail="Diagram not found")
    if diagram.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the owner can delete this diagram")

    db.query(User).filter(User.last_opened_diagram_id == diagram_id).update(
        {User.last_opened_diagram_id: None},
        synchronize_session=False,
    )
    db.execute(
        diagram_shares.delete().where(diagram_shares.c.diagram_id == diagram_id)
    )
    db.query(UserDiagramChat).filter(UserDiagramChat.diagram_id == diagram_id).delete(
        synchronize_session=False
    )
    db.delete(diagram)
    db.commit()
    return {"status": "success", "diagram_id": diagram_id, "message": "Diagram deleted"}


@router.post("/diagrams/{diagram_id}/share")
def share_diagram(
    diagram_id: int,
    request: ShareDiagramRequest,
    current_user: User = Depends(require_arch_action("edit")),
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
