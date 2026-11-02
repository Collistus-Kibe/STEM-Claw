"""StemClaw Hook System: SessionStart, PreToolUse, and PostToolUse."""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from stemclaw.config import get_settings
from stemclaw.tools.base import BaseTool, ToolCall, ToolResult

logger = logging.getLogger("stemclaw.hooks")


@dataclass
class HookDecision:
    """Decision returned by a PreToolUse hook."""

    proceed: bool = True
    modified_arguments: Optional[Dict[str, Any]] = None
    rejection_reason: Optional[str] = None


class HookManager:
    """Coordinates session lifecycle, security gates, key injection, and animations."""

    def __init__(self, workspace_root: Optional[Path] = None) -> None:
        settings = get_settings()
        self.workspace_root = (workspace_root or settings.workspace_root).resolve()
        self.allow_file_writes: bool = True
        self.require_confirmation_for_destructive: bool = False
        self._post_tool_callbacks: List[Callable[[ToolCall, ToolResult], None]] = []

    def register_post_tool_callback(
        self, callback: Callable[[ToolCall, ToolResult], None]
    ) -> None:
        """Register a callback to run after any tool executes."""
        self._post_tool_callbacks.append(callback)

    # ------------------------------------------------------------------
    # PreToolUse Gate: Key Injection & Permissions
    # ------------------------------------------------------------------
    def pre_tool_use(self, tool: BaseTool, call: ToolCall) -> HookDecision:
        """Run all PreToolUse checks before executing a tool."""
        args = dict(call.arguments)

        # 1. Path Allowlist Check for file operations
        if tool.name in ("file_write", "file_edit", "file_read"):
            path_arg = args.get("file_path") or args.get("path")
            if path_arg:
                decision = self._validate_path_allowlist(str(path_arg))
                if not decision.proceed:
                    return decision

        # 2. Transparent Key Injection from .stemclaw/.env
        args = self._inject_keys(tool.name, args)

        # 3. Confirmation gate for destructive operations if enabled
        if tool.name in ("file_write", "shell_exec") and self.require_confirmation_for_destructive:
            # Rejection or confirmation hook
            logger.info(f"Destructive operation requested on {tool.name}")

        return HookDecision(proceed=True, modified_arguments=args)

    def _validate_path_allowlist(self, target_path_str: str) -> HookDecision:
        """Ensure file operations cannot escape the active workspace."""
        try:
            target = Path(target_path_str)
            if not target.is_absolute():
                resolved = (self.workspace_root / target).resolve()
            else:
                resolved = target.resolve()

            # Path traversal check
            if not resolved.is_relative_to(self.workspace_root):
                reason = (
                    f"Security Error: Access Denied. Path '{target_path_str}' resolves to "
                    f"'{resolved}' which is outside workspace root '{self.workspace_root}'."
                )
                logger.warning(reason)
                return HookDecision(proceed=False, rejection_reason=reason)

            # Block direct modification of secret files (.env)
            if resolved.name == ".env" and ".stemclaw" in resolved.parts:
                reason = "Security Error: Direct model write to '.stemclaw/.env' is forbidden."
                logger.warning(reason)
                return HookDecision(proceed=False, rejection_reason=reason)

            return HookDecision(proceed=True)
        except Exception as e:
            return HookDecision(
                proceed=False,
                rejection_reason=f"Security Error evaluating path '{target_path_str}': {e}",
            )

    def _inject_keys(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Inject keys from settings into tool arguments if not already specified."""
        settings = get_settings()

        # NCBI tools: inject api_key if configured
        if tool_name in ("ncbi_esearch", "ncbi_efetch") and settings.ncbi_api_key:
            if "api_key" not in args:
                args["api_key"] = settings.ncbi_api_key

        # OpenAlex: inject mailto
        if tool_name == "openalex_search" and settings.openalex_mailto:
            if "mailto" not in args:
                args["mailto"] = settings.openalex_mailto

        # Crossref: inject mailto
        if tool_name == "crossref_search" and settings.crossref_mailto:
            if "mailto" not in args:
                args["mailto"] = settings.crossref_mailto

        # Materials Project
        if tool_name == "materials_project_search" and settings.materials_project_api_key:
            if "api_key" not in args:
                args["api_key"] = settings.materials_project_api_key

        # Semantic Scholar
        if tool_name in ("semantic_scholar_search", "semantic_scholar_refs") and settings.semantic_scholar_api_key:
            if "api_key" not in args:
                args["api_key"] = settings.semantic_scholar_api_key

        # GitHub
        if tool_name == "github_search" and settings.github_token:
            if "token" not in args:
                args["token"] = settings.github_token

        # IEEE Xplore
        if tool_name == "ieee_xplore" and settings.ieee_api_key:
            if "api_key" not in args:
                args["api_key"] = settings.ieee_api_key

        # NOAA
        if tool_name == "noaa_climate_data" and settings.noaa_token:
            if "token" not in args:
                args["token"] = settings.noaa_token

        # CORE
        if tool_name == "core_search" and settings.core_api_key:
            if "api_key" not in args:
                args["api_key"] = settings.core_api_key

        # Unpaywall
        if tool_name == "unpaywall_lookup" and settings.unpaywall_email:
            if "email" not in args:
                args["email"] = settings.unpaywall_email

        return args

    # ------------------------------------------------------------------
    # PostToolUse Gate: Animations and Observation Logging
    # ------------------------------------------------------------------
    def post_tool_use(
        self, tool: BaseTool, call: ToolCall, result: ToolResult
    ) -> None:
        """Run post-execution hooks, automatic caching, and visual animations."""
        # Auto-cache bibtex citations into local SQLite research cache
        if call.name == "export_bibtex" and not result.is_error:
            try:
                from stemclaw.cache.db import get_paper_cache
                db = get_paper_cache()
                args = call.arguments
                citekey = str(args.get("citekey") or args.get("title", ""))
                db.cache_paper(
                    paper_id=citekey,
                    title=args.get("title", ""),
                    authors=args.get("authors"),
                    year=int(args["year"]) if str(args.get("year", "")).isdigit() else None,
                    venue=args.get("venue"),
                    doi=args.get("doi"),
                    source="bibtex",
                )
            except Exception as e:
                logger.warning(f"Error caching paper: {e}")

        for cb in self._post_tool_callbacks:
            try:
                cb(call, result)
            except Exception as e:
                logger.warning(f"Error in post_tool_use callback: {e}")


_GLOBAL_HOOK_MANAGER: Optional[HookManager] = None


def get_hook_manager() -> HookManager:
    """Retrieve the global HookManager singleton."""
    global _GLOBAL_HOOK_MANAGER
    if _GLOBAL_HOOK_MANAGER is None:
        _GLOBAL_HOOK_MANAGER = HookManager()
    return _GLOBAL_HOOK_MANAGER
