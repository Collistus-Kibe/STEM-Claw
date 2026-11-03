"""Clean offline fallback adapter when META_API_KEY is not yet configured."""

from typing import Any, Dict, Iterator, List, Optional
from stemclaw.model.adapter import ModelAdapter, ModelResponse, StreamChunk
from stemclaw.tools.base import ToolCall


class OfflineModelAdapter(ModelAdapter):
    """Graceful offline adapter that informs user live key is required for synthesis."""

    def __init__(self, model_name: str = "offline-mode") -> None:
        self.model_name = model_name

    def generate_stream(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Iterator[StreamChunk]:
        last_user = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user = m.get("content", "")
                break

        response = (
            f"[Offline Mode] Received query: '{last_user}'.\n\n"
            "To perform live scientific synthesis and literature search with muse-wonder,\n"
            "please configure your live Meta Model API Key:\n"
            "  1. Acquire a free key at: https://dev.meta.ai\n"
            "  2. In StemClaw, type: /keys set META_API_KEY\n"
            "  3. Or add to .stemclaw/.env: META_API_KEY=your_key\n"
        )

        for word in response.split(" "):
            yield StreamChunk(text_delta=word + " ")
        yield StreamChunk(is_done=True, finish_reason="stop")

    def generate(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> ModelResponse:
        chunks = list(self.generate_stream(messages, tools))
        text = "".join(c.text_delta for c in chunks)
        return ModelResponse(content=text, finish_reason="stop", model_name=self.model_name)
