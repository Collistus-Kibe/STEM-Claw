"""Base classes for all StemClaw tools and schemas."""

import inspect
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Type
from pydantic import BaseModel


@dataclass
class ToolCall:
    """A tool call requested by the LLM."""

    id: str
    name: str
    arguments: Dict[str, Any] = field(default_factory=dict)
    raw_arguments: str = ""


@dataclass
class ToolResult:
    """The result of executing a tool call."""

    call_id: str
    name: str
    output: str
    is_error: bool = False

    def to_message(self) -> Dict[str, Any]:
        """Convert to standard OpenAI/Llama tool response message format."""
        return {
            "role": "tool",
            "tool_call_id": self.call_id,
            "name": self.name,
            "content": self.output,
        }


class BaseTool(ABC):
    """Abstract base class for all StemClaw endpoint and builtin tools."""

    name: str
    description: str
    input_model: Optional[Type[BaseModel]] = None

    def get_parameters_schema(self) -> Dict[str, Any]:
        """Derive JSON schema from Pydantic model or default object."""
        if self.input_model is not None:
            schema = self.input_model.model_json_schema()
            # Clean schema for strict LLM tool calling
            schema.pop("title", None)
            return schema
        return {
            "type": "object",
            "properties": {},
            "required": [],
        }

    def to_schema(self) -> Dict[str, Any]:
        """Format as Meta Llama / OpenAI compatible function tool schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.get_parameters_schema(),
            },
        }

    @abstractmethod
    def run(self, **kwargs) -> str:
        """Execute the tool synchronously."""
        pass

    async def run_async(self, **kwargs) -> str:
        """Execute the tool asynchronously (default delegates to run)."""
        return self.run(**kwargs)

    def execute(self, **kwargs) -> ToolResult:
        """Execute with error boundary and validation."""
        try:
            if self.input_model is not None:
                validated = self.input_model(**kwargs)
                kwargs = validated.model_dump()
            result_str = self.run(**kwargs)
            return ToolResult(
                call_id="",
                name=self.name,
                output=str(result_str),
                is_error=False,
            )
        except Exception as e:
            return ToolResult(
                call_id="",
                name=self.name,
                output=f"Error executing {self.name}: {str(e)}",
                is_error=True,
            )

