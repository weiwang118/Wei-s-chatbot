from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class PersonalityType(str, Enum):
    FRIENDLY = "friendly"
    PROFESSIONAL = "professional"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"
    EMPATHETIC = "empathetic"
    HUMOROUS = "humorous"
    ADVENTUROUS = "adventurous"
    INTELLECTUAL = "intellectual"
    CUSTOM = "custom"


class ChatMessage(BaseModel):
    sender: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = {}


class ChatHistory(BaseModel):
    sender: str
    message: str


class ChatSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    bot_name: str = "Assistant"
    user_name: str = "User"
    prompt: str
    personality: PersonalityType = PersonalityType.FRIENDLY
    messages: List[ChatMessage] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    metadata: Optional[Dict[str, Any]] = {}


class CreateChatRequest(BaseModel):
    bot_name: str = "Assistant"
    user_name: str = "User"
    personality: PersonalityType = PersonalityType.FRIENDLY
    custom_prompt: Optional[str] = None
    custom_traits: Optional[List[str]] = None

    @validator('bot_name', 'user_name')
    def validate_names(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Name cannot be empty")
        if len(v) > 50:
            raise ValueError("Name cannot exceed 50 characters")
        return v.strip()


class SendMessageRequest(BaseModel):
    session_id: str
    message: str

    @validator('message')
    def validate_message(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Message cannot be empty")
        if len(v) > 2000:
            raise ValueError("Message cannot exceed 2000 characters")
        return v.strip()


class ChatResponse(BaseModel):
    response: str
    bot_name: str
    timestamp: datetime
    session_id: str


class Bot(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    personality: PersonalityType
    prompt: str
    custom_traits: Optional[List[str]] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True


class CreateBotRequest(BaseModel):
    name: str
    personality: PersonalityType
    custom_prompt: Optional[str] = None
    custom_traits: Optional[List[str]] = []

    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Bot name cannot be empty")
        if len(v) > 50:
            raise ValueError("Bot name cannot exceed 50 characters")
        return v.strip()


class SessionListResponse(BaseModel):
    sessions: List[ChatSession]
    total: int


class MessageListResponse(BaseModel):
    messages: List[ChatMessage]
    session_id: str
    total: int


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)