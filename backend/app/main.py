from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from app.database import test_database_connection
from app.database import create_tables
from app.routes.blocks import router as blocks_router
from app.routes.passenger import router as passenger_router
from app.routes.trains import router as trains_router
from app.routes.maintenance import router as maintenance_router
from app.routes.risk import router as risk_router
from app.routes.assets import router as assets_router
from app.routes.optimizer_routes import router as optimizer_router
from app.routes.level_crossing import router as level_crossing_router
from app.services.alert_manager import alert_manager
from app.routes.level_crossing import router as level_crossing_router
from app.routes.rolling_stock import router as rolling_stock_router
from app.routes.dashboard import router as dashboard_router
from app.routes.coplan import router as coplan_router

from app.services.alert_manager import alert_manager

app = FastAPI(
    title="RailBlock AI Backend",
    version="0.1.0",
    description="Backend API for AI-Powered Railway Maintenance Block Planning"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

create_tables()

app.include_router(blocks_router)
app.include_router(passenger_router)
app.include_router(trains_router)
app.include_router(maintenance_router)
app.include_router(risk_router)
app.include_router(assets_router)
app.include_router(optimizer_router)
app.include_router(level_crossing_router)
app.include_router(level_crossing_router)
app.include_router(rolling_stock_router)
app.include_router(dashboard_router)
app.include_router(coplan_router)


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
@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    await alert_manager.connect(websocket)

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        alert_manager.disconnect(websocket)