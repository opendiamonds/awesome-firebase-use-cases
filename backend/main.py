from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import logging
from services.agent_router import router as agent_router
from services.user_router import router as user_router
from services.collab_router import router as collab_router
from services.design_agent import configure_openrouter_env
from database import init_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cloud360.main")

# Load environment variables
load_dotenv(override=True)

# 將 OPENROUTER_API_KEY 映射為 Agent SDK 所需變數（ANTHROPIC_BASE_URL / AUTH_TOKEN）
configure_openrouter_env()

app = FastAPI(title="Cloud-360 API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event to initialize database
@app.on_event("startup")
def on_startup():
    logger.info("後端服務正在啟動...")
    configure_openrouter_env()
    init_db()

app.include_router(agent_router, prefix="/api/architecture")
app.include_router(user_router, prefix="/api/auth")
app.include_router(collab_router, prefix="/api/collab")

@app.get("/")
def read_root():
    return {"message": "Cloud-360 Backend is running"}
