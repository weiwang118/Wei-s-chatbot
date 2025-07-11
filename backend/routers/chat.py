from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict
import logging
from datetime import datetime

from app.models import (
    ChatSession,
    CreateChatRequest,
    SendMessageRequest,
    ChatResponse,
    ChatMessage,
    SessionListResponse,
    MessageListResponse,
    Bot,
    CreateBotRequest
)
from app.chai_client import ChaiAPIClient
from app.dependencies import get_chai_client, get_chat_sessions, get_bot_storage

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/create", response_model=ChatSession)
async def create_chat_session(
        request: CreateChatRequest,
        chai_client: ChaiAPIClient = Depends(get_chai_client),
        sessions: Dict = Depends(get_chat_sessions)
):
    """Create a new chat session with a bot"""
    try:
        # Create personality prompt
        prompt = chai_client.create_personality_prompt(
            request.personality,
            request.custom_traits
        )

        # Add custom prompt if provided
        if request.custom_prompt:
            prompt += f"\n\n{request.custom_prompt}"

        # Create session
        session = ChatSession(
            bot_name=request.bot_name,
            user_name=request.user_name,
            prompt=prompt,
            personality=request.personality
        )

        # Store session
        sessions[session.id] = session

        logger.info(f"Created chat session: {session.id}")
        return session

    except Exception as e:
        logger.error(f"Error creating chat session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send", response_model=ChatResponse)
async def send_message(
        request: SendMessageRequest,
        chai_client: ChaiAPIClient = Depends(get_chai_client),
        sessions: Dict = Depends(get_chat_sessions)
):
    """Send a message to the bot and get a response"""
    try:
        # Get session
        if request.session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")

        session = sessions[request.session_id]

        if not session.is_active:
            raise HTTPException(status_code=400, detail="Session is not active")

        # Prepare chat history
        chat_history = [
            {"sender": msg.sender, "message": msg.content}
            for msg in session.messages
        ]

        # Send to CHAI API
        response = await chai_client.send_message({
            "prompt": session.prompt,
            "bot_name": session.bot_name,
            "user_name": session.user_name,
            "chat_history": chat_history,
            "memory": ""
        }, user_message=request.message)

        # Update session with new messages
        user_msg = ChatMessage(
            sender=session.user_name,
            content=request.message
        )

        bot_msg = ChatMessage(
            sender=session.bot_name,
            content=response["response"]
        )

        session.messages.extend([user_msg,bot_msg])
        session.updated_at = datetime.utcnow()

        return ChatResponse(
            response=response["response"],
            bot_name=session.bot_name,
            timestamp=bot_msg.timestamp,
            session_id=request.session_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions(
        active_only: bool = Query(True, description="Only return active sessions"),
        sessions: Dict = Depends(get_chat_sessions)
):
    """List all chat sessions"""
    try:
        all_sessions = list(sessions.values())

        if active_only:
            filtered_sessions = [s for s in all_sessions if s.is_active]
        else:
            filtered_sessions = all_sessions

        # Sort by updated_at descending
        filtered_sessions.sort(key=lambda x: x.updated_at, reverse=True)

        return SessionListResponse(
            sessions=filtered_sessions,
            total=len(filtered_sessions)
        )

    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}", response_model=ChatSession)
async def get_session(
        session_id: str,
        sessions: Dict = Depends(get_chat_sessions)
):
    """Get a specific chat session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    return sessions[session_id]


@router.get("/sessions/{session_id}/messages", response_model=MessageListResponse)
async def get_messages(
        session_id: str,
        limit: int = Query(50, ge=1, le=200),
        offset: int = Query(0, ge=0),
        sessions: Dict = Depends(get_chat_sessions)
):
    """Get messages from a chat session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[session_id]
    messages = session.messages[offset:offset + limit]

    return MessageListResponse(
        messages=messages,
        session_id=session_id,
        total=len(session.messages)
    )


@router.delete("/sessions/{session_id}")
async def delete_session(
        session_id: str,
        sessions: Dict = Depends(get_chat_sessions)
):
    """Delete a chat session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    del sessions[session_id]
    return {"message": "Session deleted successfully"}


@router.post("/sessions/{session_id}/clear")
async def clear_messages(
        session_id: str,
        sessions: Dict = Depends(get_chat_sessions)
):
    """Clear all messages from a session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[session_id]
    session.messages = []
    session.updated_at = datetime.utcnow()

    return {"message": "Messages cleared successfully"}


@router.post("/sessions/{session_id}/deactivate")
async def deactivate_session(
        session_id: str,
        sessions: Dict = Depends(get_chat_sessions)
):
    """Deactivate a chat session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[session_id]
    session.is_active = False
    session.updated_at = datetime.utcnow()

    return {"message": "Session deactivated successfully"}


# Bot management endpoints
@router.post("/bots", response_model=Bot)
async def create_bot(
        request: CreateBotRequest,
        chai_client: ChaiAPIClient = Depends(get_chai_client),
        bots: Dict = Depends(get_bot_storage)
):
    """Create a new bot with custom personality"""
    try:
        # Create personality prompt
        prompt = chai_client.create_personality_prompt(
            request.personality,
            request.custom_traits
        )

        if request.custom_prompt:
            prompt += f"\n\n{request.custom_prompt}"

        # Create bot
        bot = Bot(
            name=request.name,
            personality=request.personality,
            prompt=prompt,
            custom_traits=request.custom_traits
        )

        # Store bot
        bots[bot.id] = bot

        logger.info(f"Created bot: {bot.id} - {bot.name}")
        return bot

    except Exception as e:
        logger.error(f"Error creating bot: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bots", response_model=List[Bot])
async def list_bots(
        bots: Dict = Depends(get_bot_storage)
):
    """List all available bots"""
    return list(bots.values())


@router.get("/bots/{bot_id}", response_model=Bot)
async def get_bot(
        bot_id: str,
        bots: Dict = Depends(get_bot_storage)
):
    """Get a specific bot"""
    if bot_id not in bots:
        raise HTTPException(status_code=404, detail="Bot not found")

    return bots[bot_id]


@router.delete("/bots/{bot_id}")
async def delete_bot(
        bot_id: str,
        bots: Dict = Depends(get_bot_storage)
):
    """Delete a bot"""
    if bot_id not in bots:
        raise HTTPException(status_code=404, detail="Bot not found")

    del bots[bot_id]
    return {"message": "Bot deleted successfully"}