from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import test_database_connection
from app.database import create_tables



app = FastAPI(
    title="RailBlock AI Backend",
    version="0.1.0",
    description="Backend API for AI-Powered Railway Maintenance Block Planning"
)
create_tables()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "RailBlock AI Backend"
    }

@app.get("/health/database")
def database_health_check():
    try:
        test_database_connection()
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }