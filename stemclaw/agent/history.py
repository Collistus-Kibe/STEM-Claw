"""Conversation history management with token preservation and smart tool compaction."""

from typing import Any, Dict, List, Optional
from stemclaw.agent.compactor import compact_messages_for_llm
from stemclaw.tools.base import ToolCall, ToolResult


class ConversationHistory:
    """Maintains message sequence for multi-turn agent interaction."""

    def __init__(self, system_prompt: str) -> None:
        self.system_prompt = system_prompt
        self._messages: List[Dict[str, Any]] = [
            {"role": "system", "content": system_prompt}
        ]

    def add_user_message(self, content: str) -> None:
        """Add a user turn."""
        self._messages.append({"role": "user", "content": content})

    def add_assistant_message(
        self,
        content: str,
        tool_calls: Optional[List[ToolCall]] = None,
    ) -> None:
        """Add an assistant turn with optional tool calls."""
        msg: Dict[str, Any] = {"role": "assistant", "content": content or ""}
        if tool_calls:
            msg["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.name,
                        "arguments": tc.raw_arguments
                        or (str(tc.arguments) if tc.arguments else "{}"),
                    },
                }
                for tc in tool_calls
            ]
        self._messages.append(msg)

    def add_tool_result(self, result: ToolResult) -> None:
        """Add tool execution output turn."""
        self._messages.append(result.to_message())

    def get_messages(self, compact: bool = True) -> List[Dict[str, Any]]:
        """Return the current message list for model consumption, with optional tool output compaction."""
        raw = list(self._messages)
        if compact:
            return compact_messages_for_llm(raw)
        return raw

    def count(self) -> int:
        return len(self._messages)

    def clear_messages(self) -> None:
        """Clear all messages except the system prompt."""
        self._messages = [{"role": "system", "content": self.system_prompt}]

    def trim(self, max_turns: int = 40) -> None:
        """Trim oldest user/assistant turns when exceeding limit, preserving system prompt."""
        if len(self._messages) > max_turns:
            system = self._messages[0]
            recent = self._messages[-(max_turns - 1) :]
            self._messages = [system] + recent

    def restore_messages(self, messages: List[Dict[str, Any]]) -> None:
        """Restore message history from a previous session snapshot."""
        if not messages:
            return
        # Ensure system prompt is first message
        if messages[0].get("role") == "system":
            self._messages = list(messages)
            self.system_prompt = messages[0].get("content", self.system_prompt)
        else:
            self._messages = [{"role": "system", "content": self.system_prompt}] + list(messages)

