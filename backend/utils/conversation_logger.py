"""Conversation logging utility for tracking chat history."""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from agents import Message


class ConversationLogger:
    """Logger for conversation history to files."""

    def __init__(self, logs_dir: str = "logs"):
        """
        Initialize the conversation logger.

        Args:
            logs_dir: Directory to store conversation logs
        """
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(exist_ok=True)
        self.active_conversations: Dict[str, Dict[str, Any]] = {}

    def start_conversation(self, conversation_id: str, agent_type: str) -> None:
        """
        Start tracking a new conversation.

        Args:
            conversation_id: Unique identifier for the conversation
            agent_type: Type of agent being used (llm, react, multi)
        """
        self.active_conversations[conversation_id] = {
            "conversation_id": conversation_id,
            "agent_type": agent_type,
            "started_at": datetime.now().isoformat(),
            "messages": []
        }

    def log_message(self, conversation_id: str, message: Message) -> None:
        """
        Log a message to a conversation.

        Args:
            conversation_id: Unique identifier for the conversation
            message: Message to log
        """
        if conversation_id not in self.active_conversations:
            # If conversation doesn't exist, create it with unknown agent type
            self.start_conversation(conversation_id, "unknown")

        message_dict = {
            "role": message.role,
            "content": message.content,
            "timestamp": message.timestamp or datetime.now().isoformat()
        }

        self.active_conversations[conversation_id]["messages"].append(message_dict)

    def log_conversation(self, conversation_id: str, messages: List[Message], agent_type: str) -> None:
        """
        Log an entire conversation to file.

        Args:
            conversation_id: Unique identifier for the conversation
            messages: List of messages in the conversation
            agent_type: Type of agent being used
        """
        # Update active conversation
        if conversation_id not in self.active_conversations:
            self.start_conversation(conversation_id, agent_type)

        # Log all messages
        for message in messages:
            if message not in [m for m in self.active_conversations[conversation_id]["messages"]]:
                self.log_message(conversation_id, message)

        # Write to file
        self._write_conversation_log(conversation_id)

    def end_conversation(self, conversation_id: str) -> None:
        """
        Mark a conversation as ended and write final log.

        Args:
            conversation_id: Unique identifier for the conversation
        """
        if conversation_id in self.active_conversations:
            self.active_conversations[conversation_id]["ended_at"] = datetime.now().isoformat()
            self._write_conversation_log(conversation_id)
            del self.active_conversations[conversation_id]

    def _write_conversation_log(self, conversation_id: str) -> None:
        """
        Write conversation log to file.

        Args:
            conversation_id: Unique identifier for the conversation
        """
        if conversation_id not in self.active_conversations:
            return

        conversation_data = self.active_conversations[conversation_id]

        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_{conversation_id}_{timestamp}.json"
        filepath = self.logs_dir / filename

        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(conversation_data, f, indent=2, ensure_ascii=False)

    def update_conversation(self, conversation_id: str, messages: List[Message], agent_type: str) -> None:
        """
        Update an active conversation with new messages.

        Args:
            conversation_id: Unique identifier for the conversation
            messages: Current list of all messages in the conversation
            agent_type: Type of agent being used
        """
        if conversation_id not in self.active_conversations:
            self.start_conversation(conversation_id, agent_type)

        # Clear existing messages and add all current messages
        self.active_conversations[conversation_id]["messages"] = [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp or datetime.now().isoformat()
            }
            for msg in messages
        ]

        # Update agent type
        self.active_conversations[conversation_id]["agent_type"] = agent_type

        # Write to file
        self._write_conversation_log(conversation_id)


# Global conversation logger instance
conversation_logger = ConversationLogger()
