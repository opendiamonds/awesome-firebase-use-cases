from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from pydantic import BaseModel
from database import get_db
from models import User, UserDiagram
from services.auth import get_current_user
from typing import Dict, List
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        # workspace_id -> list of WebSockets
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, workspace_id: str):
        await websocket.accept()
        if workspace_id not in self.active_connections:
            self.active_connections[workspace_id] = []
        self.active_connections[workspace_id].append(websocket)
        logger.info(f"WebSocket connected to workspace {workspace_id}. Total: {len(self.active_connections[workspace_id])}")

    def disconnect(self, websocket: WebSocket, workspace_id: str):
        if workspace_id in self.active_connections:
            if websocket in self.active_connections[workspace_id]:
                self.active_connections[workspace_id].remove(websocket)
            if not self.active_connections[workspace_id]:
                del self.active_connections[workspace_id]
        logger.info(f"WebSocket disconnected from workspace {workspace_id}.")

    async def broadcast(self, message: str, workspace_id: str, exclude: WebSocket = None):
        if workspace_id in self.active_connections:
            for connection in self.active_connections[workspace_id]:
                if connection != exclude:
                    try:
                        await connection.send_text(message)
                    except Exception as e:
                        logger.error(f"Error broadcasting to a client in {workspace_id}: {e}")

manager = ConnectionManager()

@router.websocket("/ws/{workspace_id}")
async def websocket_endpoint(websocket: WebSocket, workspace_id: str):
    await manager.connect(websocket, workspace_id)
    try:
        while True:
            # Receive XML or cursor data from client
            data = await websocket.receive_text()
            
            try:
                # Optionally parse to check message type (e.g., {"type": "xml", "xml": "..."})
                # For now, just blindly broadcast the raw payload to other clients
                await manager.broadcast(data, workspace_id, exclude=websocket)
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, workspace_id)

@router.get("/users")
def get_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    users = db.query(User).filter(User.id != current_user.id).all()
    return [{"id": u.id, "username": u.username, "role": u.role} for u in users]

class SaveDiagramRequest(BaseModel):
    xml_data: str
    title: str = "未命名架構圖"

class ShareDiagramRequest(BaseModel):
    user_ids: List[int]

@router.get("/diagrams")
def list_my_diagrams(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Diagrams owned by the user or shared with the user
    owned = db.query(UserDiagram).filter(UserDiagram.user_id == current_user.id).all()
    shared = current_user.shared_diagrams
    all_diagrams = list(set(owned + shared))
    all_diagrams.sort(key=lambda x: x.updated_at, reverse=True)
    
    return [
        {
            "id": d.id, 
            "title": d.title, 
            "updated_at": d.updated_at,
            "is_owner": d.user_id == current_user.id
        } for d in all_diagrams
    ]

@router.get("/diagrams/{diagram_id}")
def get_diagram(diagram_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    diagram = db.query(UserDiagram).filter(UserDiagram.id == diagram_id).first()
    if not diagram:
        raise HTTPException(status_code=404, detail="Diagram not found")
        
    if diagram.user_id != current_user.id and diagram not in current_user.shared_diagrams:
        raise HTTPException(status_code=403, detail="Access denied")
        
    return {
        "id": diagram.id, 
        "title": diagram.title, 
        "xml_data": diagram.xml_data, 
        "updated_at": diagram.updated_at,
        "is_owner": diagram.user_id == current_user.id,
        "shared_user_ids": [u.id for u in diagram.shared_users] if diagram.user_id == current_user.id else []
    }

@router.post("/diagrams")
def create_diagram(request: SaveDiagramRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    diagram = UserDiagram(user_id=current_user.id, title=request.title, xml_data=request.xml_data)
    db.add(diagram)
    db.commit()
    db.refresh(diagram)
    return {"id": diagram.id, "status": "success", "message": "Diagram created successfully"}

@router.put("/diagrams/{diagram_id}")
def update_diagram(diagram_id: int, request: SaveDiagramRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    diagram = db.query(UserDiagram).filter(UserDiagram.id == diagram_id).first()
    if not diagram:
        raise HTTPException(status_code=404, detail="Diagram not found")
        
    if diagram.user_id != current_user.id and diagram not in current_user.shared_diagrams:
        raise HTTPException(status_code=403, detail="Access denied")
    
    diagram.xml_data = request.xml_data
    diagram.title = request.title
    db.commit()
    return {"status": "success", "message": "Diagram updated successfully"}

@router.post("/diagrams/{diagram_id}/share")
def share_diagram(diagram_id: int, request: ShareDiagramRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    diagram = db.query(UserDiagram).filter(UserDiagram.id == diagram_id).first()
    if not diagram:
        raise HTTPException(status_code=404, detail="Diagram not found")
        
    # Only owner can share
    if diagram.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the owner can share this diagram")
        
    users = db.query(User).filter(User.id.in_(request.user_ids)).all()
    diagram.shared_users = users
    db.commit()
    
    return {"status": "success", "message": "Share settings updated"}

