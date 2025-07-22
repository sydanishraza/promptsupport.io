from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from typing import List, Optional
from datetime import datetime

# MongoDB
from motor.motor_asyncio import AsyncIOMotorClient

# Environment variables
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
client = AsyncIOMotorClient(MONGO_URL)
db = client.clean_start

# Pydantic models
class HealthResponse(BaseModel):
    status: str
    message: str

# API Routes
@app.get("/api/health")
async def health_check():
    return HealthResponse(status="healthy", message="Clean slate - ready for fresh development!")

@app.get("/api/status")
async def get_status():
    return {
        "status": "clean",
        "message": "All previous code cleaned up",
        "database": "reset",
        "ready_for": "new dev plan and UI blueprint"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)