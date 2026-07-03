import os
import logging
import bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User

logger = logging.getLogger("cloud360.database")

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
    
    db = SessionLocal()
    try:
        # 檢查是否已存在使用者
        user_count = db.query(User).count()
        if user_count == 0:
            logger.info("資料庫為空，開始從 personas.md 初始化 11 位預設使用者...")
            
            # 定義 11 位 Persona 的資料
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
                    is_active=True
                )
                db.add(db_user)

            
            db.commit()
            logger.info("預設使用者初始化完成！")
        else:
            logger.info(f"資料庫已存在 {user_count} 位使用者，跳過初始化。")
    except Exception as e:
        logger.error(f"初始化資料庫時發生錯誤: {e}")
        db.rollback()
    finally:
        db.close()
