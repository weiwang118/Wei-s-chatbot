from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Dict
import os
import logging
from datetime import datetime

from .chai_client import ChaiAPIClient
from .models import (
    ChatMessage,
    ChatSession
)
from routers import chat

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Global CHAI client instance
chai_client = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global chai_client
    api_key = os.getenv("CHAI_API_KEY", "CR_14d43f2bf78b4b0590c2a8b87f354746")
    chai_client = ChaiAPIClient(api_key)
    await chai_client.initialize()
    logger.info("CHAI API client initialized")
    yield
    # Shutdown
    await chai_client.close()
    logger.info("CHAI API client closed")


# Create FastAPI app
app = FastAPI(
    title="CHAI Chat Interface",
    description="Web interface for CHAI's AI chat models",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://localhost:3000"],  # Streamlit and other frontends
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for sessions (replace with Redis in production)
chat_sessions: Dict[str, ChatSession] = {}
active_connections: Dict[str, WebSocket] = {}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "CHAI Chat Interface API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/api/chat",
            "chatroom": "/api/chatroom",
            "debate": "/api/debate",
            "docs": "/docs"
        }
    }


# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}


# Include routers
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])


# WebSocket endpoint for real-time chat
@app.websocket("/ws/chat/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    await websocket.accept()
    active_connections[session_id] = websocket

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()

            # Get session
            if session_id not in chat_sessions:
                await websocket.send_json({
                    "error": "Session not found"
                })
                continue

            session = chat_sessions[session_id]

            # Send to CHAI API
            chai_response = await chai_client.send_message({
                "prompt": session.prompt,
                "bot_name": session.bot_name,
                "user_name": session.user_name,
                "chat_history": [
                    {"sender": msg.sender, "message": msg.content}
                    for msg in session.messages
                ],
                "memory": ""
            }, user_message=data["message"])

            # Update session history
            session.messages.append(ChatMessage(
                sender=session.user_name,
                content=data["message"],
                timestamp=datetime.utcnow()
            ))
            session.messages.append(ChatMessage(
                sender=session.bot_name,
                content=chai_response["response"],
                timestamp=datetime.utcnow()
            ))

            # Send response back
            await websocket.send_json({
                "sender": session.bot_name,
                "message": chai_response["response"],
                "timestamp": datetime.utcnow().isoformat()
            })

    except WebSocketDisconnect:
        del active_connections[session_id]
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()
        if session_id in active_connections:
            del active_connections[session_id]


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "error": exc.detail,
        "status_code": exc.status_code
    }


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return {
        "error": "Internal server error",
        "status_code": 500
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)