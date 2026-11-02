"""GitHub repository search tool for open-source scientific software and ML implementations."""

from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel, Field
from stemclaw.tools.base import BaseTool


class GithubSearchInput(BaseModel):
    query: str = Field(..., description="Software keywords, algorithm name, or library search")
    limit: int = Field(default=5, ge=1, le=20, description="Max repositories to return")
    token: Optional[str] = Field(default=None, description="Optional GitHub Personal Access Token")


class GithubSearchTool(BaseTool):
    name = "github_search"
    description = (
        "Search GitHub for open-source research implementations, scientific code libraries, "
        "reproducibility packages, and star metrics."
    )
    input_model = GithubSearchInput

    def run(self, query: str, limit: int = 5, token: Optional[str] = None) -> str:
        url = "https://api.github.com/search/repositories"
        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": limit,
        }
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "StemClaw-STEM-Research-Agent/1.0",
        }
        if token:
            headers["Authorization"] = f"token {token}"

        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.get(url, params=params, headers=headers)
                if resp.status_code != 200:
                    return f"GitHub API returned status {resp.status_code}: {resp.text[:300]}"

                data = resp.json()
                total = data.get("total_count", 0)
                items = data.get("items", [])

                if not items:
                    return f"No GitHub repositories found for query '{query}'."

                lines = [f"=== GitHub Research Repositories (Total: {total}, Showing: {len(items)}) ==="]
                for repo in items:
                    name = repo.get("full_name", "")
                    stars = repo.get("stargazers_count", 0)
                    forks = repo.get("forks_count", 0)
                    language = repo.get("language") or "N/A"
                    desc = repo.get("description") or "No description provided."
                    html_url = repo.get("html_url", "")
                    topics = repo.get("topics", [])
                    topics_str = ", ".join(topics[:5]) if topics else "None"

                    lines.append(f"\n- **{name}** [⭐ {stars:,} | 🍴 {forks:,} | Lang: {language}]")
                    lines.append(f"  Description: {desc}")
                    lines.append(f"  Topics: {topics_str}")
                    lines.append(f"  URL: {html_url}")

                return "\n".join(lines)

        except Exception as e:
            return f"Error executing GitHub search: {e}"

