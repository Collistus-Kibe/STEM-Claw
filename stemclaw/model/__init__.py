"""StemClaw Live Model Adapters for Meta Model API and Llama-4."""

from typing import Optional
from stemclaw.model.adapter import ModelAdapter, ModelResponse, StreamChunk
from stemclaw.model.llama_client import LlamaModelAdapter

__all__ = [
    "ModelAdapter",
    "ModelResponse",
    "StreamChunk",
    "LlamaModelAdapter",
    "get_model_adapter",
]


def get_model_adapter(api_key: Optional[str] = None) -> ModelAdapter:
    """Retrieve the live model adapter connected to Meta Model API / Llama-4."""
    from stemclaw.config import get_settings

    settings = get_settings()
    key = api_key or settings.effective_api_key
    if not key:
        raise ValueError(
            "META_API_KEY is required for live reasoning and synthesis. "
            "Please set META_API_KEY in .stemclaw/.env or acquire a key at https://dev.meta.ai"
        )
    return LlamaModelAdapter(
        api_key=key,
        model=settings.meta_model or settings.llama_model or "muse-wonder",
        fallback_model=settings.llama_fallback_model or "muse-spark",
        base_url=settings.meta_api_base or settings.llama_api_base or "https://api.meta.ai/v1",
    )
