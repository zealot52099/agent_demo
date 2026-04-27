"""对话记忆管理。"""
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from agent_system.config import settings
from agent_system.logging_config import logger


@dataclass
class Message:
    role: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


class ConversationMemory:
    def __init__(self, max_turns: Optional[int] = None):
        self.max_turns = max_turns or settings.max_history_turns
        self.messages: List[Message] = []
        self.session_id: Optional[str] = None

    def add_user_message(self, content: str, metadata: Optional[Dict] = None):
        msg = Message(role="user", content=content, metadata=metadata or {})
        self.messages.append(msg)
        self._trim()
        logger.debug(f"Added user message, total turns: {len(self.messages)}")

    def add_assistant_message(self, content: str, metadata: Optional[Dict] = None):
        msg = Message(role="assistant", content=content, metadata=metadata or {})
        self.messages.append(msg)
        self._trim()
        logger.debug(f"Added assistant message, total turns: {len(self.messages)}")

    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        if role not in ("user", "assistant", "system"):
            raise ValueError(f"Invalid role: {role}")
        msg = Message(role=role, content=content, metadata=metadata or {})
        self.messages.append(msg)
        self._trim()

    def get_messages(self) -> List[Message]:
        return self.messages.copy()

    def get_history_for_inference(self) -> List[Dict[str, str]]:
        return [{"role": m.role, "content": m.content} for m in self.messages]

    def _trim(self):
        if len(self.messages) > self.max_turns * 2:
            self.messages = self.messages[-(self.max_turns * 2):]
            logger.debug(f"Trimmed messages, keeping last {self.max_turns * 2}")

    def clear(self):
        self.messages.clear()
        logger.info("Memory cleared")

    def get_turn_count(self) -> int:
        return len([m for m in self.messages if m.role == "user"])

    def get_last_user_message(self) -> Optional[str]:
        for msg in reversed(self.messages):
            if msg.role == "user":
                return msg.content
        return None

    def get_last_n_turns(self, n: int) -> List[Message]:
        user_msgs = [m for m in self.messages if m.role == "user"]
        if not user_msgs:
            return []
        start_idx = max(0, len(user_msgs) - n)
        start_msg = user_msgs[start_idx]
        start_time = start_msg.timestamp
        return [m for m in self.messages if m.timestamp >= start_time]


class MemoryManager:
    _instances: Dict[str, ConversationMemory] = {}

    @classmethod
    def get_memory(cls, session_id: str) -> ConversationMemory:
        if session_id not in cls._instances:
            cls._instances[session_id] = ConversationMemory()
            logger.info(f"Created new memory for session: {session_id}")
        return cls._instances[session_id]

    @classmethod
    def clear_memory(cls, session_id: str):
        if session_id in cls._instances:
            cls._instances[session_id].clear()
            del cls._instances[session_id]
            logger.info(f"Cleared memory for session: {session_id}")

    @classmethod
    def list_sessions(cls) -> List[str]:
        return list(cls._instances.keys())