"""Papers With Code search tool for ML benchmarks, tasks, and implementations."""

from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel, Field
from stemclaw.tools.base import BaseTool


class PapersWithCodeInput(BaseModel):
    query: str = Field(..., description="Machine learning topic, task name, dataset, or paper title")
    limit: int = Field(default=5, ge=1, le=15, description="Max papers to return")


class PapersWithCodeTool(BaseTool):
    name = "papers_with_code"
    description = (
        "Search Papers with Code for machine learning papers with linked code repositories, "
        "benchmark evaluation leaderboards, tasks, and datasets."
    )
    input_model = PapersWithCodeInput

    def run(self, query: str, limit: int = 5) -> str:
        url = "https://paperswithcode.com/api/v1/papers/"
        params = {
            "q": query,
            "items_per_page": limit,
        }
        headers = {"User-Agent": "StemClaw-STEM-Research-Agent/1.0"}

        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.get(url, params=params, headers=headers)
                if resp.status_code != 200:
                    return f"Papers with Code API returned status {resp.status_code}: {resp.text[:300]}"

                data = resp.json()
                count = data.get("count", 0)
                results = data.get("results", [])

                if not results:
                    return f"No Papers with Code results found for query '{query}'."

                lines = [f"=== Papers with Code Results (Total Found: {count}, Showing: {len(results)}) ==="]
                for p in results:
                    title = p.get("title", "No Title")
                    published = p.get("published", "N/A")
                    proceeding = p.get("proceeding") or "Preprint/Workshop"
                    arxiv_id = p.get("arxiv_id", "")
                    url_abs = p.get("url_abs", "")
                    tasks = p.get("tasks", [])
                    tasks_str = ", ".join(tasks[:4]) if tasks else "None listed"
                    methods = p.get("methods", [])
                    methods_str = ", ".join(methods[:4]) if methods else "None listed"

                    lines.append(f"\n- **{title}** ({published})")
                    lines.append(f"  Proceeding/Venue: {proceeding}")
                    if arxiv_id:
                        lines.append(f"  ArXiv ID: {arxiv_id}")
                    if url_abs:
                        lines.append(f"  Paper URL: {url_abs}")
                    lines.append(f"  Tasks: {tasks_str}")
                    lines.append(f"  Methods: {methods_str}")

                return "\n".join(lines)

        except Exception as e:
            return f"Error executing Papers with Code search: {e}"

