"""StemClaw Model Adapters for Meta Model API and Llama-4."""

from typing import Optional
from stemclaw.model.adapter import ModelAdapter, ModelResponse, StreamChunk
from stemclaw.model.llama_client import LlamaModelAdapter
from stemclaw.model.offline_client import OfflineModelAdapter

__all__ = [
    "ModelAdapter",
    "ModelResponse",
    "StreamChunk",
    "LlamaModelAdapter",
    "OfflineModelAdapter",
    "get_model_adapter",
]


def get_model_adapter(
    api_key: Optional[str] = None, force_mock: bool = False
) -> ModelAdapter:
    """Retrieve the model adapter (live Meta API if key present, else graceful offline fallback)."""
    from stemclaw.config import get_settings

    settings = get_settings()
    key = api_key or settings.effective_api_key
    if force_mock or not key:
        return OfflineModelAdapter()
    return LlamaModelAdapter(
        api_key=key,
        model=settings.meta_model or settings.llama_model or "muse-wonder",
        fallback_model=settings.llama_fallback_model or "muse-spark",
        base_url=settings.meta_api_base or settings.llama_api_base or "https://api.meta.ai/v1",
    )
