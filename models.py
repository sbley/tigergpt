from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class ChatMessage(BaseModel):
    role: str = Field(..., description="Message role (user/assistant)")
    content: str = Field(..., description="Message content")
    timestamp: str = Field(..., description="Message timestamp")


class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID")


class MCPServerRequest(BaseModel):
    name: str = Field(..., description="Server name")
    command: str = Field(..., description="Command to start server")
    args: List[str] = Field(default_factory=list, description="Command arguments")
    env: Dict[str, str] = Field(default_factory=dict, description="Environment variables")
    enabled: bool = Field(True, description="Whether the server is enabled")
