"""
user_router — 登入／註冊／使用者角色／角色權限矩陣 API
"""

from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import logging
import re
import os
from database import get_db
from models import User, RolePermission
from services.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
)
from services.rbac import (
    CANONICAL_ROLES,
    STORY_IDS,
    ARCH_DIAGRAM_STORIES,
    is_canonical_role,
    normalize_role,
    permissions_map_for_role,
    list_all_permissions,
    require_story_action,
    user_can,
    ensure_role_permissions_seeded,
    sync_arch_permission_flags,
)

logger = logging.getLogger("cloud360.user_router")
router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str


class UserSchema(BaseModel):
    id: int
    username: str
    role: str
    is_active: bool

    class Config:
        orm_mode = True


class MeResponse(BaseModel):
    id: int
    username: str
    role: str
    is_active: bool
    permissions: Dict[str, dict]


class UpdateRoleRequest(BaseModel):
    role: str


class RolePermissionRow(BaseModel):
    role: str
    story_id: str
    can_view: bool
    can_edit: bool
    can_review: bool
    updated_by: Optional[str] = None


class RolePermissionUpdate(BaseModel):
    role: str
    story_id: str
    can_view: bool
    can_edit: bool
    can_review: bool


class BulkRolePermissionUpdate(BaseModel):
    rows: List[RolePermissionUpdate] = Field(min_length=1)


class ResetDefaultsResponse(BaseModel):
    seeded: int
    message: str


def _audit_append(title: str, request_raw: str, outcome: str, approver: str) -> None:
    try:
        audit_path = "/Users/luojingting/Documents/opendimand/cloud/aidlc-docs/audit.md"
        if os.path.exists(audit_path):
            with open(audit_path, "a", encoding="utf-8") as f:
                import datetime

                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"\n#### {timestamp} +08:00 — {title}\n\n")
                f.write(f"**User request (raw)**: \"{request_raw}\"\n")
                f.write(f"**Stage**: Operations → Privilege Enforcement\n")
                f.write(f"**Outcome**: {outcome}\n")
                f.write(f"**Approver**: {approver}\n\n---\n")
    except Exception as e:
        logger.error("寫入 audit.md 失敗: %s", e)


@router.post("/register", response_model=LoginResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    username = request.username.strip().lower()
    password = request.password

    if not username or not password:
        raise HTTPException(status_code=400, detail="帳號與密碼不可為空")

    if len(username) < 3 or len(username) > 20:
        raise HTTPException(status_code=400, detail="帳號長度必須在 3 到 20 個字元之間")

    if len(password) < 6 or len(password) > 30:
        raise HTTPException(status_code=400, detail="密碼長度必須在 6 到 30 個字元之間")

    if not re.match("^[a-zA-Z0-9_]+$", username):
        raise HTTPException(status_code=400, detail="帳號只能包含英文、數字與底線")

    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="該帳號已被註冊使用")

    hashed_pw = get_password_hash(password)
    new_user = User(
        username=username,
        password_hash=hashed_pw,
        role="Developer",
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info(
        "【新帳號註冊】使用者 '%s' 成功註冊，預設角色 '%s'",
        username,
        new_user.role,
    )
    _audit_append(
        "User Registration",
        f"註冊新帳號 {username}",
        f"使用者 {username} 成功註冊並指派角色為 {new_user.role}，即刻生效。",
        "System_Auto",
    )

    access_token = create_access_token(data={"sub": new_user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": new_user.username,
        "role": new_user.role,
    }


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    auth_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="帳號或密碼錯誤",
    )

    user = db.query(User).filter(User.username == request.username.lower()).first()
    if not user:
        raise auth_exception

    if not verify_password(request.password, user.password_hash):
        raise auth_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您的帳號已被停用，請聯絡平台管理員",
        )

    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "role": user.role,
    }


@router.get("/me", response_model=MeResponse)
def get_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "permissions": permissions_map_for_role(db, current_user.role),
    }


@router.get("/roles")
def list_canonical_roles(
    _: User = Depends(get_current_user),
):
    """回傳正式角色 allowlist（供 Admin 下拉）。"""
    return {"roles": CANONICAL_ROLES, "stories": STORY_IDS}


@router.get("/list", response_model=List[UserSchema])
def list_users(
    admin_user: User = Depends(require_story_action("J3a", "view")),
    db: Session = Depends(get_db),
):
    return db.query(User).order_by(User.id).all()


@router.put("/{user_id}/role", response_model=UserSchema)
def update_user_role(
    user_id: int,
    request: UpdateRoleRequest,
    admin_user: User = Depends(require_story_action("J3a", "edit")),
    db: Session = Depends(get_db),
):
    new_role = normalize_role(request.role.strip())
    if not is_canonical_role(new_role):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"無效角色：必須為 {CANONICAL_ROLES} 之一",
        )

    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到該使用者",
        )

    # 不可移除最後一位具 J3a.edit 的管理員
    if target_user.role != new_role:
        had_admin_edit = user_can(db, target_user.role, "J3a", "edit")
        will_have = user_can(db, new_role, "J3a", "edit")
        if had_admin_edit and not will_have:
            admin_edit_count = 0
            for u in db.query(User).filter(User.is_active == True).all():  # noqa: E712
                if user_can(db, u.role, "J3a", "edit"):
                    admin_edit_count += 1
            if admin_edit_count <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="無法更新角色：系統必須保留至少一位可編輯使用者角色的管理員",
                )

    old_role = target_user.role
    target_user.role = new_role
    db.commit()
    db.refresh(target_user)

    logger.info(
        "【身分權限變更】管理員 '%s' 將 '%s' 從 '%s' 改為 '%s'",
        admin_user.username,
        target_user.username,
        old_role,
        target_user.role,
    )
    _audit_append(
        "User Privilege Re-assignment",
        f"變更使用者 {target_user.username} 角色為 {target_user.role}",
        f"角色成功從 {old_role} 變更為 {target_user.role}，下次重新整理時生效。",
        admin_user.username,
    )
    return target_user


@router.get("/role-permissions", response_model=List[RolePermissionRow])
def get_role_permissions(
    _: User = Depends(require_story_action("J3b", "view")),
    db: Session = Depends(get_db),
):
    rows = list_all_permissions(db)
    return [
        RolePermissionRow(
            role=r.role,
            story_id=r.story_id,
            can_view=r.can_view,
            can_edit=r.can_edit,
            can_review=r.can_review,
            updated_by=r.updated_by,
        )
        for r in rows
    ]


@router.put("/role-permissions", response_model=List[RolePermissionRow])
def put_role_permissions(
    body: BulkRolePermissionUpdate,
    admin_user: User = Depends(require_story_action("J3b", "edit")),
    db: Session = Depends(get_db),
):
    # 展開：任一 A1／A2／A4 變更 → 三者同步同一組旗標
    expanded: List[RolePermissionUpdate] = []
    seen_arch_roles: set[str] = set()
    for item in body.rows:
        role = normalize_role(item.role)
        if item.story_id in ARCH_DIAGRAM_STORIES:
            if role in seen_arch_roles:
                continue
            seen_arch_roles.add(role)
            v, e, r = sync_arch_permission_flags(
                item.can_view, item.can_edit, item.can_review
            )
            for sid in ARCH_DIAGRAM_STORIES:
                expanded.append(
                    RolePermissionUpdate(
                        role=role,
                        story_id=sid,
                        can_view=v,
                        can_edit=e,
                        can_review=r,
                    )
                )
        else:
            expanded.append(item)

    updated: List[RolePermission] = []
    for item in expanded:
        role = normalize_role(item.role)
        if not is_canonical_role(role):
            raise HTTPException(400, detail=f"無效角色：{item.role}")
        if item.story_id not in STORY_IDS:
            raise HTTPException(400, detail=f"無效 story_id：{item.story_id}")

        row = (
            db.query(RolePermission)
            .filter(
                RolePermission.role == role,
                RolePermission.story_id == item.story_id,
            )
            .first()
        )
        old = None
        if row is None:
            row = RolePermission(
                role=role,
                story_id=item.story_id,
                can_view=item.can_view,
                can_edit=item.can_edit,
                can_review=item.can_review,
                updated_by=admin_user.username,
            )
            db.add(row)
        else:
            old = (row.can_view, row.can_edit, row.can_review)
            row.can_view = item.can_view
            row.can_edit = item.can_edit
            row.can_review = item.can_review
            row.updated_by = admin_user.username
        updated.append(row)
        if old and old != (item.can_view, item.can_edit, item.can_review):
            logger.info(
                "【角色矩陣變更】%s: %s/%s %s → (%s,%s,%s)",
                admin_user.username,
                role,
                item.story_id,
                old,
                item.can_view,
                item.can_edit,
                item.can_review,
            )

    db.commit()
    for row in updated:
        db.refresh(row)

    _audit_append(
        "Role Permission Matrix Update",
        f"更新 {len(expanded)} 列 role_permissions",
        f"管理員 {admin_user.username} 已更新角色細項權限矩陣。",
        admin_user.username,
    )
    return [
        RolePermissionRow(
            role=r.role,
            story_id=r.story_id,
            can_view=r.can_view,
            can_edit=r.can_edit,
            can_review=r.can_review,
            updated_by=r.updated_by,
        )
        for r in updated
    ]


@router.post("/role-permissions/reset-defaults", response_model=ResetDefaultsResponse)
def reset_role_permissions_defaults(
    admin_user: User = Depends(require_story_action("J3b", "review")),
    db: Session = Depends(get_db),
):
    """還原為設計預設矩陣（需 J3b.review）。"""
    n = ensure_role_permissions_seeded(db, force=True)
    _audit_append(
        "Role Permission Matrix Reset",
        "還原 role_permissions 為設計預設",
        f"已重播 {n} 列預設矩陣。",
        admin_user.username,
    )
    return ResetDefaultsResponse(seeded=n, message=f"已還原 {n} 列預設權限")
