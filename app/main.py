# app/main.py
import logging
import asyncio
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.responses import JSONResponse
from app.core.database import engine, Base
from app.api.routes import lead, auth
from app.websockets import manager
from sqlalchemy.sql import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.logger import logger
from app.middleware import ExceptionLoggingMiddleware, LoggingMiddleware
from fastapi.middleware.cors import CORSMiddleware


uvicorn_logger = logging.getLogger("uvicorn")
uvicorn_logger.handlers = logger.handlers
uvicorn_logger.setLevel(logging.INFO)

# Initialize FastAPI app
app = FastAPI(
    title="Lead Management",
    description="API for managing leads with CRUD operations, JWT authentication, CSV export, and real-time updates via WebSockets.",
    version="1.0.0"
)

# app.add_middleware(LoggingMiddleware)
# app.add_middleware(ExceptionLoggingMiddleware)


logger.info("FastAPI Application is starting...")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL, e.g., ["https://myapp.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler to catch unhandled errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})


app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(lead.router, prefix="/leads", tags=["Leads"])

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Wait for a message from the client
            data = await websocket.receive_text()
            # Broadcast the update to all connected clients (e.g., notify on row update)
            await manager.broadcast(f"Real-time update: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Root endpoint to confirm the API is running
@app.get("/health")
def health_check():
    return {"status": "OK"}


@app.get("/db-check", tags=["Health Check"])
async def db_check(db: AsyncSession = Depends(get_db)):
    """Check database connectivity."""
    try:
        logger.info("Checking database connection...")
        await db.execute(text('SELECT 1'))  # Lightweight query to check DB health
        return {"status": "success", "message": "Database is connected"}
    except Exception as e:
        logger.error(f"Database connection failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Database connection failed")