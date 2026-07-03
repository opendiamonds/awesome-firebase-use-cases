from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
import logging
from database import get_db
from models import User
import re
import os
from services.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
    require_admin,
    require_any_user
)

logger = logging.getLogger("cloud360.user_router")
router = APIRouter()

# Pydantic Schemas
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

class UpdateRoleRequest(BaseModel):
    role: str

# 1. 註冊新帳號 API
@router.post("/register", response_model=LoginResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    username = request.username.strip().lower()
    password = request.password
    
    # 1. 欄位基礎校驗
    if not username or not password:
        raise HTTPException(status_code=400, detail="帳號與密碼不可為空")
        
    if len(username) < 3 or len(username) > 20:
        raise HTTPException(status_code=400, detail="帳號長度必須在 3 到 20 個字元之間")
        
    if len(password) < 6 or len(password) > 30:
        raise HTTPException(status_code=400, detail="密碼長度必須在 6 到 30 個字元之間")
        
    # 2. 帳號名稱字元過濾 (防範 SQL 注入與字元異常，限英數底線)
    if not re.match("^[a-zA-Z0-9_]+$", username):
        raise HTTPException(status_code=400, detail="帳號只能包含英文、數字與底線")
        
    # 3. 帳號重複性檢測
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="該帳號已被註冊使用")
        
    # 4. 註冊新使用者 (預設分配一般開發者角色)
    hashed_pw = get_password_hash(password)
    new_user = User(
        username=username,
        password_hash=hashed_pw,
        role="Developer",
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # 5. 稽核日誌登記
    audit_msg = f"【新帳號註冊】使用者 '{username}' 成功註冊，預設分配角色為 '{new_user.role}'"
    logger.info(audit_msg)
    
    try:
        audit_path = "/Users/luojingting/Documents/opendimand/cloud/aidlc-docs/audit.md"
        if os.path.exists(audit_path):
            with open(audit_path, "a", encoding="utf-8") as f:
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"\n#### {timestamp} +08:00 — User Registration\n\n")
                f.write(f"**User request (raw)**: \"註冊新帳號 {username}\"\n")
                f.write(f"**Stage**: Operations → Account Creation\n")
                f.write(f"**Outcome**: 使用者 {username} 成功註冊並指派角色為 {new_user.role}，即刻生效。\n")
                f.write(f"**Approver**: System_Auto\n\n---\n")
    except Exception as e:
        logger.error(f"寫入 audit.md 失敗: {e}")
        
    # 6. 自動簽發 JWT Token 登入
    access_token = create_access_token(data={"sub": new_user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": new_user.username,
        "role": new_user.role
    }

# 2. 登入認證 API
@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    # 統一模糊錯誤提示以防止使用者列舉攻擊
    auth_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="帳號或密碼錯誤"
    )
    
    user = db.query(User).filter(User.username == request.username.lower()).first()
    if not user:
        raise auth_exception
        
    if not verify_password(request.password, user.password_hash):
        raise auth_exception
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您的帳號已被停用，請聯絡平台管理員"
        )
        
    # 生成 Token
    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "role": user.role
    }

# 2. 獲取當前登入者資訊 API
@router.get("/me", response_model=UserSchema)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

# 3. 管理員專屬：獲取所有使用者列表 API
@router.get("/list", response_model=List[UserSchema])
def list_users(
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    users = db.query(User).order_by(User.id).all()
    return users

# 4. 管理員專屬：更新使用者角色與權限 API
@router.put("/{user_id}/role", response_model=UserSchema)
def update_user_role(
    user_id: int,
    request: UpdateRoleRequest,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到該使用者"
        )
        
    # 防止將最後一位管理員降級
    if target_user.role in ["Project_Admin", "Platform_Admin"] and request.role not in ["Project_Admin", "Platform_Admin"]:
        admin_count = db.query(User).filter(
            User.role.in_(["Project_Admin", "Platform_Admin"]), 
            User.is_active == True
        ).count()
        if admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="無法更新角色：系統必須保留至少一位啟用狀態的系統管理員"
            )
            
    old_role = target_user.role
    target_user.role = request.role
    db.commit()
    db.refresh(target_user)
    
    # 強制寫入平台日誌
    audit_msg = f"【身分權限變更】管理員 '{admin_user.username}' 將使用者 '{target_user.username}' 的角色從 '{old_role}' 變更為 '{target_user.role}'"
    logger.info(audit_msg)
    
    # 寫入專案稽核日誌紀錄 (可選)
    try:
        audit_path = "/Users/luojingting/Documents/opendimand/cloud/aidlc-docs/audit.md"
        if os.path.exists(audit_path):
            with open(audit_path, "a", encoding="utf-8") as f:
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"\n#### {timestamp} +08:00 — User Privilege Re-assignment\n\n")
                f.write(f"**User request (raw)**: \"變更使用者 {target_user.username} 角色為 {target_user.role}\"\n")
                f.write(f"**Stage**: Operations → Privilege Enforcement\n")
                f.write(f"**Outcome**: 角色成功從 {old_role} 變更為 {target_user.role}，下次重新整理時生效。\n")
                f.write(f"**Approver**: {admin_user.username}\n\n---\n")
    except Exception as e:
        logger.error(f"寫入 audit.md 失敗: {e}")
        
    return target_user
