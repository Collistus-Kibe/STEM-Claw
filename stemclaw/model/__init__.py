"""StemClaw Model Adapters for Meta Llama-4 and local testing."""

from stemclaw.model.adapter import ModelAdapter, ModelResponse, StreamChunk
from stemclaw.model.llama_client import LlamaModelAdapter
from stemclaw.model.mock_client import MockModelAdapter

__all__ = [
    "ModelAdapter",
    "ModelResponse",
    "StreamChunk",
    "LlamaModelAdapter",
    "MockModelAdapter",
    "get_model_adapter",
]


def get_model_adapter(force_mock: bool = False) -> ModelAdapter:
    """Retrieve the appropriate model adapter based on configuration and keys."""
    from stemclaw.config import get_settings

    settings = get_settings()
    api_key = settings.effective_api_key
    if force_mock or not api_key:
        return MockModelAdapter()
    return LlamaModelAdapter(
        api_key=api_key,
        model=settings.meta_model or settings.llama_model,
        fallback_model=settings.llama_fallback_model,
        base_url=settings.meta_api_base or settings.llama_api_base,
    )

