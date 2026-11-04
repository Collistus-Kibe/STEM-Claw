"""Meta Llama API adapter supporting Llama-4-Maverick and Scout fallback."""

import json
from typing import Any, Dict, Iterator, List, Optional
import httpx

from stemclaw.model.adapter import ModelAdapter, ModelResponse, StreamChunk
from stemclaw.tools.base import ToolCall


def normalize_model_name(name: str) -> str:
    """Normalize model aliases to exact catalog model IDs."""
    aliases = {
        "muse-wonder": "muse-wonder-1.0",
        "muse-spark": "muse-spark-1.3",
        "muse-spark-contributor": "muse-spark-1.3-contributor",
    }
    cleaned = (name or "").strip()
    return aliases.get(cleaned.lower(), cleaned)


class LlamaModelAdapter(ModelAdapter):
    """Adapter for the hosted Meta Model API (api.meta.ai / api.llama.com)."""

    def __init__(
        self,
        api_key: str,
        model: str = "muse-wonder-1.0",
        fallback_model: str = "muse-spark-1.3",
        base_url: str = "https://api.meta.ai/v1",
        timeout: float = 60.0,
    ) -> None:
        self.api_key = api_key
        self.model_name = normalize_model_name(model)
        self.fallback_model = normalize_model_name(fallback_model) if fallback_model else ""
        clean_url = base_url.rstrip("/")
        if not clean_url.endswith("/v1"):
            clean_url = f"{clean_url}/v1"
        self.endpoint = f"{clean_url}/chat/completions"
        self.timeout = timeout

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        }

    def _send_request(
        self,
        client: httpx.Client,
        payload: Dict[str, Any],
        model: str,
    ) -> httpx.Response:
        payload["model"] = model
        req = client.build_request(
            "POST",
            self.endpoint,
            headers=self._headers(),
            json=payload,
            timeout=self.timeout,
        )
        return client.send(req, stream=True)

    def generate_stream(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Iterator[StreamChunk]:
        """Stream SSE chunks from Meta Llama API, accumulating tool call arguments."""
        payload: Dict[str, Any] = {
            "messages": messages,
            "stream": True,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        accumulated_tool_calls: Dict[int, Dict[str, str]] = {}
        target_model = self.model_name

        with httpx.Client() as client:
            try:
                response = self._send_request(client, payload, target_model)
                if response.status_code in (404, 400) and self.fallback_model:
                    response.close()
                    target_model = self.fallback_model
                    response = self._send_request(client, payload, target_model)

                if response.status_code != 200:
                    err_text = response.read()
                    yield StreamChunk(
                        text_delta=f"\n[Meta API Error {response.status_code}]: {err_text.decode('utf-8', errors='replace')}\n",
                        is_done=True,
                        finish_reason="error",
                    )
                    return

                for line in response.iter_lines():
                    if not line:
                        continue
                    line_str = line.strip()
                    if line_str == "data: [DONE]":
                        break
                    if line_str.startswith("data: "):
                        json_str = line_str[6:]
                        try:
                            chunk_data = json.loads(json_str)
                        except Exception:
                            continue

                        choices = chunk_data.get("choices", [])
                        if not choices:
                            continue

                        delta = choices[0].get("delta", {})
                        finish_reason = choices[0].get("finish_reason")

                        # Text content delta
                        text_delta = delta.get("content") or ""
                        if text_delta:
                            yield StreamChunk(text_delta=text_delta, is_done=False)

                        # Tool calls delta
                        raw_tc_list = delta.get("tool_calls", [])
                        for tc_chunk in raw_tc_list:
                            idx = tc_chunk.get("index", 0)
                            if idx not in accumulated_tool_calls:
                                accumulated_tool_calls[idx] = {
                                    "id": tc_chunk.get("id", f"call_{idx}"),
                                    "name": "",
                                    "arguments": "",
                                }
                            if tc_chunk.get("id"):
                                accumulated_tool_calls[idx]["id"] = tc_chunk["id"]
                            func_chunk = tc_chunk.get("function", {})
                            if func_chunk.get("name"):
                                accumulated_tool_calls[idx]["name"] += func_chunk["name"]
                            if func_chunk.get("arguments"):
                                accumulated_tool_calls[idx]["arguments"] += func_chunk[
                                    "arguments"
                                ]

                        # Package accumulated tool calls
                        if finish_reason in ("tool_calls", "function_call") or (finish_reason and accumulated_tool_calls):
                            completed_calls = []
                            for idx, tc in sorted(accumulated_tool_calls.items()):
                                args_parsed = {}
                                try:
                                    args_parsed = json.loads(tc["arguments"])
                                except Exception:
                                    pass
                                completed_calls.append(
                                    ToolCall(
                                        id=tc["id"],
                                        name=tc["name"],
                                        arguments=args_parsed,
                                        raw_arguments=tc["arguments"],
                                    )
                                )
                            yield StreamChunk(
                                tool_calls=completed_calls,
                                is_done=True,
                                finish_reason="tool_calls",
                            )
                            return

                        if finish_reason:
                            yield StreamChunk(
                                is_done=True, finish_reason=finish_reason
                            )
                            return

            except httpx.HTTPError as e:
                yield StreamChunk(
                    text_delta=f"\n[Network connection error to Meta API: {str(e)}]\n",
                    is_done=True,
                    finish_reason="network_error",
                )
                return

        yield StreamChunk(is_done=True, finish_reason="stop")
