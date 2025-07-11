from typing import Dict
import os
from functools import lru_cache
import backend.app.main as main_module
from fastapi import HTTPException

from .models import ChatSession, Bot

chat_sessions: Dict[str, ChatSession] = {}
bot_storage: Dict[str, Bot] = {}


@lru_cache()
def get_settings():
    """Get application settings"""
    return {
        "api_key": os.getenv("CHAI_API_KEY", "CR_14d43f2bf78b4b0590c2a8b87f354746")
    }


def get_chai_client():
    """Get the global CHAI client instance"""
    if main_module.chai_client is None:
        raise HTTPException(status_code=503, detail="CHAI client not initialized")
    return main_module.chai_client


def get_chat_sessions() -> Dict[str, ChatSession]:
    """Get the chat sessions storage"""
    return chat_sessions


def get_bot_storage() -> Dict[str, Bot]:
    """Get the bot storage"""
    return bot_storage