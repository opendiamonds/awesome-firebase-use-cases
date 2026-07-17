import os
import logging
import bcrypt
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User

logger = logging.getLogger("cloud360.database")

# 自動判斷環境：如果有設定 APP_ENV，或是預設為 local，就去抓對應的 .env 檔案
app_env = os.environ.get("APP_ENV", "local")
if app_env == "local":
    # 這裡確保只在 local 開發時強制讀取 .env
    # 部署到正式環境 (如 production) 時，通常由平台 (AWS/Vercel) 直接注入環境變數
    load_dotenv()

# Database configuration
DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/cloud360"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def hash_password(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    logger.info("正在初始化資料庫與資料表...")
    Base.metadata.create_all(bind=engine)
    # A4／J5：既有 DB 補欄位／新表（create_all 不會 ALTER 舊表）
    _ensure_a4_schema()
    _ensure_j5_schema()

    db = SessionLocal()
    try:
        # 檢查是否已存在使用者
        user_count = db.query(User).count()
        if user_count == 0:
            logger.info("資料庫為空，開始從 personas.md 初始化 11 位預設使用者...")

            default_personas = [
                {"username": "catherine", "role": "Project_Admin", "password": "catherine123"},
                {"username": "jack", "role": "Platform_Admin", "password": "jack123"},
                {"username": "alex", "role": "Project_Architect", "password": "alex123"},
                {"username": "ben", "role": "SRE", "password": "ben123"},
                {"username": "david", "role": "FinOps_Analyst", "password": "david123"},
                {"username": "elena", "role": "Platform_Engineer", "password": "elena123"},
                {"username": "fiona", "role": "Security_Reviewer", "password": "fiona123"},
                {"username": "george", "role": "Ops_Lead", "password": "george123"},
                {"username": "hannah", "role": "Project_Editor", "password": "hannah123"},
                {"username": "ian", "role": "Developer", "password": "ian123"},
                {"username": "karen", "role": "Platform_Owner", "password": "karen123"},
            ]

            for persona in default_personas:
                hashed_pw = hash_password(persona["password"])
                db_user = User(
                    username=persona["username"],
                    password_hash=hashed_pw,
                    role=persona["role"],
                    is_active=True,
                    authorization_status="approved",
                )
                db.add(db_user)

            db.commit()
            logger.info("預設使用者初始化完成！")
        else:
            logger.info(f"資料庫已存在 {user_count} 位使用者，跳過初始化。")

        # 確保預設 admin 帳號存在（與 schema_rbac.sql 對齊）
        admin = db.query(User).filter(User.username == "admin").first()
        if admin is None:
            db.add(
                User(
                    username="admin",
                    password_hash=hash_password("admin123"),
                    role="Platform_Admin",
                    is_active=True,
                    authorization_status="approved",
                )
            )
            db.commit()
            logger.info("已建立預設帳號 admin / Platform_Admin")
        elif getattr(admin, "authorization_status", None) != "approved":
            admin.authorization_status = "approved"
            if not admin.role:
                admin.role = "Platform_Admin"
            db.commit()

        # RBAC 矩陣：空表時 seed（不覆寫 Admin UI 已調過的資料）
        from services.rbac import ensure_role_permissions_seeded

        seeded = ensure_role_permissions_seeded(db, force=False)
        if seeded:
            logger.info("role_permissions 已 seed %d 列", seeded)
        else:
            from models import RolePermission

            logger.info(
                "role_permissions 已有 %d 列，略過 seed",
                db.query(RolePermission).count(),
            )
    except Exception as e:
        logger.error(f"初始化資料庫時發生錯誤: {e}")
        db.rollback()
    finally:
        db.close()


def _ensure_a4_schema():
    """為既有資料庫補上 A4 欄位與 user_diagram_chats 表。"""
    from sqlalchemy import text

    statements = [
        """
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS last_opened_diagram_id INTEGER
        """,
        """
        CREATE TABLE IF NOT EXISTS user_diagram_chats (
            user_id INTEGER NOT NULL REFERENCES users(id),
            diagram_id INTEGER NOT NULL REFERENCES user_diagrams(id) ON DELETE CASCADE,
            messages_json TEXT NOT NULL DEFAULT '[]',
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            PRIMARY KEY (user_id, diagram_id)
        )
        """,
    ]
    with engine.begin() as conn:
        for sql in statements:
            try:
                conn.execute(text(sql))
            except Exception as e:
                logger.warning("A4 schema 補丁略過/失敗: %s — %s", sql[:60], e)
    logger.info("A4 schema 檢查完成")


def _ensure_j5_schema():
    """為既有資料庫補上 J5 authorization_status 與 role_authorization_requests。"""
    from sqlalchemy import text

    statements = [
        """
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS authorization_status VARCHAR(32) DEFAULT 'approved'
        """,
        """
        UPDATE users SET authorization_status = 'approved'
        WHERE authorization_status IS NULL OR authorization_status = ''
        """,
        """
        ALTER TABLE users ALTER COLUMN role DROP NOT NULL
        """,
        """
        CREATE TABLE IF NOT EXISTS role_authorization_requests (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            requested_role VARCHAR(64) NOT NULL,
            status VARCHAR(32) NOT NULL DEFAULT 'pending',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            decided_by VARCHAR(128),
            decided_at TIMESTAMP WITH TIME ZONE,
            note TEXT
        )
        """,
        """
        CREATE INDEX IF NOT EXISTS ix_role_auth_req_user_id
        ON role_authorization_requests (user_id)
        """,
        """
        CREATE INDEX IF NOT EXISTS ix_role_auth_req_status
        ON role_authorization_requests (status)
        """,
    ]
    with engine.begin() as conn:
        for sql in statements:
            try:
                conn.execute(text(sql))
            except Exception as e:
                logger.warning("J5 schema 補丁略過/失敗: %s — %s", sql[:60], e)
    logger.info("J5 schema 檢查完成")
