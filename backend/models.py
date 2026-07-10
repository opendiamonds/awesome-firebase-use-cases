"""
models.py — Cloud-360 ORM 模型

含使用者、架構圖、分享關聯，以及 A4 聊天持久化（user × diagram）。
"""

from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

diagram_shares = Table(
    "diagram_shares",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("diagram_id", Integer, ForeignKey("user_diagrams.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # Role handle, e.g., Project_Admin, Developer, SRE
    is_active = Column(Boolean, default=True)
    # A4：上次開啟的架構圖（重整後自動還原）
    last_opened_diagram_id = Column(
        Integer, ForeignKey("user_diagrams.id", ondelete="SET NULL"), nullable=True
    )

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
            "is_active": self.is_active,
            "last_opened_diagram_id": self.last_opened_diagram_id,
        }


class UserDiagram(Base):
    __tablename__ = "user_diagrams"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False, default="未命名架構圖")
    xml_data = Column(Text, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    owner = relationship("User", foreign_keys=[user_id])
    shared_users = relationship(
        "User", secondary=diagram_shares, backref="shared_diagrams"
    )


class UserDiagramChat(Base):
    """
    A4：每位使用者在每張架構圖上的獨立聊天紀錄。
    複合主鍵 (user_id, diagram_id)；messages_json 存 [{role, content}, ...]。
    """

    __tablename__ = "user_diagram_chats"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    diagram_id = Column(Integer, ForeignKey("user_diagrams.id"), primary_key=True)
    messages_json = Column(Text, nullable=False, default="[]")
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class RolePermission(Base):
    """
    RBAC：角色 × User Story 細項權限（檢視／編輯／審核）。
    預設資料見 schema_rbac.sql；可由 Admin 頁②調整。
    """

    __tablename__ = "role_permissions"

    role = Column(String(64), primary_key=True)
    story_id = Column(String(16), primary_key=True)
    can_view = Column(Boolean, nullable=False, default=False)
    can_edit = Column(Boolean, nullable=False, default=False)
    can_review = Column(Boolean, nullable=False, default=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    updated_by = Column(String(128), nullable=True)
