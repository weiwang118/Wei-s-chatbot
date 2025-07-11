from typing import Dict
import os
from functools import lru_cache

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
    from .main import chai_client
    return chai_client


def get_chat_sessions() -> Dict[str, ChatSession]:
    """Get the chat sessions storage"""
    return chat_sessions


def get_bot_storage() -> Dict[str, Bot]:
    """Get the bot storage"""
    return bot_storage