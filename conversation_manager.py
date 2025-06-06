from models import ChatMessage
from typing import Dict, List, Optional
import asyncio

class ConversationManager:
    def __init__(self):
        self.conversations: Dict[str, List[ChatMessage]] = {}
    
    def add_message(self, conv_id: str, message: ChatMessage):
        """Add a message to a conversation"""
        if conv_id not in self.conversations:
            self.conversations[conv_id] = []
        
        self.conversations[conv_id].append(message)
    
    def get_conversation(self, conv_id: str) -> List[ChatMessage]:
        """Get a conversation by ID"""
        return self.conversations.get(conv_id, [])
    
    def delete_conversation(self, conv_id: str) -> bool:
        """Delete a conversation"""
        if conv_id in self.conversations:
            del self.conversations[conv_id]
            return True
        return False

    def create_message(self, role: str, content: str) -> ChatMessage:
        """Create a new chat message"""
        return ChatMessage(
            role=role,
            content=content,
            timestamp=str(asyncio.get_event_loop().time())
        )