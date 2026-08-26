from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import test_database_connection
from app.database import create_tables
from app.routes.blocks import router as blocks_router
from app.routes.passenger import router as passenger_router
from app.routes.trains import router as trains_router
from app.routes.maintenance import router as maintenance_router
from app.routes.risk import router as risk_router
from app.routes.assets import router as assets_router
from app.routes.optimizer_routes import router as optimizer_router



app = FastAPI(
    title="RailBlock AI Backend",
    version="0.1.0",
    description="Backend API for AI-Powered Railway Maintenance Block Planning"
)
create_tables()

app.include_router(blocks_router)
app.include_router(passenger_router)
app.include_router(trains_router)
app.include_router(maintenance_router)
app.include_router(risk_router)
app.include_router(assets_router)
app.include_router(optimizer_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "https://rail-block-ai-wine.vercel.app",
        "https://rail-block-ai-passenger.vercel.app",
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