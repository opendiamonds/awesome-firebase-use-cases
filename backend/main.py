from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from services.agent_router import router as agent_router

# Load environment variables
load_dotenv(override=True)
app = FastAPI(title="Cloud-360 API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agent_router, prefix="/api/architecture")

@app.get("/")
def read_root():
    return {"message": "Cloud-360 Backend is running"}
