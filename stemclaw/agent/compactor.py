"""Context compactor for scientific literature tool outputs and long dialogues."""

import re
from typing import Any, Dict, List


def compact_literature_text(raw_text: str, max_chars: int = 1200) -> str:
    """Compact verbose tool outputs (e.g. multiple raw abstracts) into dense information cards."""
    if not raw_text or len(raw_text) <= max_chars:
        return raw_text

    # Extract bullet points if already formatted as list
    lines = raw_text.splitlines()
    compacted_lines: List[str] = []
    
    current_entry: List[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(("•", "-", "*", "[PMID", "Title:", "1.", "2.", "3.", "4.", "5.")):
            if current_entry:
                # Keep title and first 120 chars of abstract/snippet
                entry_text = " ".join(current_entry)
                if len(entry_text) > 220:
                    entry_text = entry_text[:220].rstrip() + "..."
                compacted_lines.append(f"• {entry_text}")
                current_entry = []
            current_entry.append(stripped)
        elif current_entry and len(" ".join(current_entry)) < 220:
            current_entry.append(stripped)

    if current_entry:
        entry_text = " ".join(current_entry)
        if len(entry_text) > 220:
            entry_text = entry_text[:220].rstrip() + "..."
        compacted_lines.append(f"• {entry_text}")

    if compacted_lines and len(compacted_lines) >= 2:
        header = f"[Compacted from {len(raw_text)} chars]:"
        result = header + "\n" + "\n".join(compacted_lines[:8])
        return result

    # Fallback smart head+tail truncation with preservation of key identifiers
    head = raw_text[:700].rstrip()
    tail = raw_text[-300:].lstrip()
    return f"{head}\n... [omitted {len(raw_text) - 1000} chars of raw text] ...\n{tail}"


def compact_messages_for_llm(
    messages: List[Dict[str, Any]],
    keep_recent_raw_turns: int = 4,
    max_tool_chars_in_old_turns: int = 1000,
) -> List[Dict[str, Any]]:
    """Return an optimized message list where older tool results are compacted."""
    if len(messages) <= keep_recent_raw_turns:
        return list(messages)

    cutoff_index = max(1, len(messages) - keep_recent_raw_turns)
    optimized: List[Dict[str, Any]] = []

    for idx, msg in enumerate(messages):
        # Never touch system prompt or the most recent raw turns
        if idx == 0 or idx >= cutoff_index:
            optimized.append(msg)
            continue

        # For older tool result messages, apply smart compaction
        if msg.get("role") == "tool" and "content" in msg:
            content = str(msg["content"])
            if len(content) > max_tool_chars_in_old_turns:
                compacted = compact_literature_text(content, max_chars=max_tool_chars_in_old_turns)
                new_msg = dict(msg)
                new_msg["content"] = compacted
                optimized.append(new_msg)
                continue

        optimized.append(msg)

    return optimized
