"""Abstract base class and data structures for model adapters."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Optional
from stemclaw.tools.base import ToolCall


@dataclass
class StreamChunk:
    """Incremental chunk emitted during response streaming."""

    text_delta: str = ""
    tool_calls: List[ToolCall] = field(default_factory=list)
    is_done: bool = False
    finish_reason: Optional[str] = None


@dataclass
class ModelResponse:
    """Completed response from a model generation turn."""

    content: str
    tool_calls: List[ToolCall] = field(default_factory=list)
    model_name: str = ""
    finish_reason: str = "stop"

    def has_tool_calls(self) -> bool:
        return len(self.tool_calls) > 0


class ModelAdapter(ABC):
    """Protocol for unified LLM interactions (streaming & tool calls)."""

    model_name: str

    @abstractmethod
    def generate_stream(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Iterator[StreamChunk]:
        """Stream generation chunks with tool call accumulation."""
        pass

    def generate(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> ModelResponse:
        """Generate a complete response turn."""
        content_acc = []
        tool_calls_acc = []
        finish_reason = "stop"

        for chunk in self.generate_stream(messages, tools=tools):
            if chunk.text_delta:
                content_acc.append(chunk.text_delta)
            if chunk.tool_calls:
                tool_calls_acc.extend(chunk.tool_calls)
            if chunk.finish_reason:
                finish_reason = chunk.finish_reason

        return ModelResponse(
            content="".join(content_acc),
            tool_calls=tool_calls_acc,
            model_name=self.model_name,
            finish_reason=finish_reason,
        )
