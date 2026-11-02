"""Mock model adapter for testing and offline development."""

import json
from typing import Any, Dict, Iterator, List, Optional
from stemclaw.model.adapter import ModelAdapter, ModelResponse, StreamChunk
from stemclaw.tools.base import ToolCall


class MockModelAdapter(ModelAdapter):
    """Simulates Meta Llama-4 Maverick streaming and tool calling offline."""

    def __init__(
        self,
        model_name: str = "mock-llama-4-maverick",
    ) -> None:
        self.model_name = model_name
        self._queued_chunks: List[List[StreamChunk]] = []

    def queue_response(self, text: str) -> None:
        """Queue a specific text response for the next turn."""
        chunks = [
            StreamChunk(text_delta=text, is_done=False),
            StreamChunk(is_done=True, finish_reason="stop"),
        ]
        self._queued_chunks.append(chunks)

    def queue_tool_call(
        self,
        name: str,
        arguments: Dict[str, Any],
        call_id: str = "call_mock_001",
    ) -> None:
        """Queue a tool call emission for the next turn."""
        tc = ToolCall(
            id=call_id,
            name=name,
            arguments=arguments,
            raw_arguments=json.dumps(arguments),
        )
        chunks = [
            StreamChunk(
                text_delta="",
                tool_calls=[tc],
                is_done=True,
                finish_reason="tool_calls",
            )
        ]
        self._queued_chunks.append(chunks)

    def generate_stream(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Iterator[StreamChunk]:
        """Stream chunks with simulated tool calling and content."""
        if self._queued_chunks:
            chunks = self._queued_chunks.pop(0)
            for c in chunks:
                yield c
            return

        last_msg = messages[-1] if messages else {}
        last_role = last_msg.get("role", "")
        last_content = str(last_msg.get("content", ""))

        # Check if the last turn was a tool execution output
        if last_role == "tool":
            tool_name = last_msg.get("name", "tool")
            response_text = (
                f"I processed the data from external tool `{tool_name}`: "
                f"'{last_content}'. Based on this scientific observation, "
                "the parameters are verified and consistent with the active research loadout."
            )
            words = response_text.split(" ")
            for i, word in enumerate(words):
                yield StreamChunk(
                    text_delta=word + (" " if i < len(words) - 1 else ""),
                    is_done=False,
                )
            yield StreamChunk(is_done=True, finish_reason="stop")
            return

        # Check if user query should trigger the dummy diagnostic tool
        should_call_tool = (
            tools
            and any(t.get("function", {}).get("name") == "echo_tool" for t in tools)
            and any(
                trigger in last_content.lower()
                for trigger in ["echo", "test tool", "dummy", "diagnostic", "ping"]
            )
        )

        if should_call_tool:
            # Emit a tool call request
            tool_call = ToolCall(
                id="mock_call_echo_001",
                name="echo_tool",
                arguments={"message": f"Diagnostic ping from user: '{last_content}'"},
                raw_arguments=f'{{"message": "Diagnostic ping from user: \'{last_content}\'"}}',
            )
            yield StreamChunk(
                text_delta="",
                tool_calls=[tool_call],
                is_done=True,
                finish_reason="tool_calls",
            )
            return

        # Regular conversational response
        canned_response = (
            f"[StemClaw {self.model_name}] Received research query: \"{last_content}\". "
            "Standing by to query endpoints, inspect curated datasets, or execute analysis scripts."
        )
        words = canned_response.split(" ")
        for i, word in enumerate(words):
            yield StreamChunk(
                text_delta=word + (" " if i < len(words) - 1 else ""),
                is_done=False,
            )

        yield StreamChunk(is_done=True, finish_reason="stop")
