"""Conversation history management with token preservation, API sanitization, and smart compaction."""

from typing import Any, Dict, List, Optional
from stemclaw.agent.compactor import compact_messages_for_llm
from stemclaw.tools.base import ToolCall, ToolResult


def sanitize_messages_for_api(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Sanitize message sequence for strict OpenAI / Meta API compliance.

    Rules enforced:
    1. System prompt (if any) is preserved at index 0.
    2. Every message with role='tool' must have a preceding assistant message in the same
       context declaring a tool_call with the exact matching id. Orphaned tool messages are dropped.
    3. Any assistant message with tool_calls must be followed by matching role='tool' messages.
       If any tool call id lacks a result, it is stripped from tool_calls. If all are missing,
       tool_calls is removed completely to avoid unfulfilled call errors.
    """
    if not messages:
        return []

    system_msg = None
    other_msgs: List[Dict[str, Any]] = []
    for m in messages:
        if m.get("role") == "system":
            if system_msg is None:
                system_msg = m
        else:
            other_msgs.append(m)

    sanitized: List[Dict[str, Any]] = []
    i = 0
    n = len(other_msgs)
    while i < n:
        m = other_msgs[i]
        role = m.get("role")

        if role == "user":
            sanitized.append(m)
            i += 1
        elif role == "assistant":
            tool_calls = m.get("tool_calls")
            if not tool_calls:
                sanitized.append(m)
                i += 1
            else:
                expected_ids = {
                    tc.get("id")
                    for tc in tool_calls
                    if isinstance(tc, dict) and tc.get("id")
                }
                found_tool_msgs: List[Dict[str, Any]] = []
                j = i + 1
                while j < n and other_msgs[j].get("role") == "tool":
                    t_msg = other_msgs[j]
                    t_id = t_msg.get("tool_call_id")
                    if t_id in expected_ids:
                        found_tool_msgs.append(t_msg)
                    j += 1

                matched_ids = {t.get("tool_call_id") for t in found_tool_msgs}
                if matched_ids:
                    filtered_tcs = [
                        tc for tc in tool_calls
                        if isinstance(tc, dict) and tc.get("id") in matched_ids
                    ]
                    clean_assistant = dict(m)
                    clean_assistant["tool_calls"] = filtered_tcs
                    sanitized.append(clean_assistant)
                    sanitized.extend(found_tool_msgs)
                else:
                    clean_assistant = dict(m)
                    clean_assistant.pop("tool_calls", None)
                    if clean_assistant.get("content"):
                        sanitized.append(clean_assistant)

                i = j
        elif role == "tool":
            # Orphaned tool message with no preceding assistant tool_calls — drop it
            i += 1
        else:
            sanitized.append(m)
            i += 1

    return [system_msg] + sanitized if system_msg else sanitized


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
        """Return the current message list for model consumption, sanitized and compacted."""
        sanitized = sanitize_messages_for_api(self._messages)
        if compact:
            return compact_messages_for_llm(sanitized)
        return sanitized

    def count(self) -> int:
        return len(self._messages)

    def clear_messages(self) -> None:
        """Clear all messages except the system prompt."""
        self._messages = [{"role": "system", "content": self.system_prompt}]

    def trim(self, max_turns: int = 40) -> None:
        """Trim oldest turns when exceeding limit, preserving system prompt and turn atomicity."""
        if len(self._messages) <= max_turns:
            return

        system = self._messages[0] if self._messages and self._messages[0].get("role") == "system" else None
        non_system = self._messages[1:] if system else self._messages

        target_start = max(0, len(non_system) - (max_turns - 1))
        user_idx = None
        for i in range(target_start, len(non_system)):
            if non_system[i].get("role") == "user":
                user_idx = i
                break

        if user_idx is not None:
            kept = non_system[user_idx:]
        else:
            kept = non_system[target_start:]

        candidate = [system] + kept if system else kept
        self._messages = sanitize_messages_for_api(candidate)

    def restore_messages(self, messages: List[Dict[str, Any]]) -> None:
        """Restore message history from a previous session snapshot."""
        if not messages:
            return
        if messages[0].get("role") == "system":
            self._messages = sanitize_messages_for_api(messages)
            self.system_prompt = messages[0].get("content", self.system_prompt)
        else:
            restored = [{"role": "system", "content": self.system_prompt}] + list(messages)
            self._messages = sanitize_messages_for_api(restored)


