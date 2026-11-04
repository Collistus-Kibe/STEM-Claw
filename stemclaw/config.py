"""StemClaw configuration management."""

from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_default_workspace() -> Path:
    return Path.cwd()


class StemClawSettings(BaseSettings):
    """Runtime settings loaded from environment and .stemclaw/.env."""

    model_config = SettingsConfigDict(
        env_file=Path.cwd() / ".stemclaw" / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Core workspace paths
    workspace_root: Path = Field(default_factory=get_default_workspace)
    stemclaw_dir_name: str = ".stemclaw"
    session_file_name: str = "session.json"

    # Meta Model API configuration (dev.meta.ai / api.meta.ai)
    meta_api_key: Optional[str] = Field(default=None, alias="META_API_KEY")
    llama_api_key: Optional[str] = Field(default=None, alias="LLAMA_API_KEY")
    meta_model: str = Field(
        default="muse-wonder-1.0",
        alias="META_MODEL",
    )
    llama_model: str = Field(
        default="muse-wonder-1.0",
        alias="LLAMA_MODEL",
    )
    llama_fallback_model: str = Field(
        default="muse-spark-1.3",
        alias="LLAMA_FALLBACK_MODEL",
    )
    meta_api_base: str = Field(
        default="https://api.meta.ai/v1",
        alias="META_API_BASE",
    )
    llama_api_base: str = Field(
        default="https://api.meta.ai/v1",
        alias="LLAMA_API_BASE",
    )

    @property
    def effective_api_key(self) -> Optional[str]:
        return self.meta_api_key or self.llama_api_key

    @property
    def effective_model(self) -> str:
        raw = self.meta_model or self.llama_model or "muse-wonder-1.0"
        aliases = {
            "muse-wonder": "muse-wonder-1.0",
            "muse-spark": "muse-spark-1.3",
            "muse-spark-contributor": "muse-spark-1.3-contributor",
        }
        return aliases.get(raw.strip().lower(), raw.strip())

    @property
    def effective_api_base(self) -> str:
        if self.meta_api_key:
            return self.meta_api_base
        return self.meta_api_base or self.llama_api_base

    # Optional endpoint keys (higher rate limits / access)
    ncbi_api_key: Optional[str] = Field(default=None, alias="NCBI_API_KEY")
    materials_project_api_key: Optional[str] = Field(
        default=None, alias="MATERIALS_PROJECT_API_KEY"
    )
    openalex_mailto: Optional[str] = Field(default=None, alias="OPENALEX_MAILTO")
    crossref_mailto: Optional[str] = Field(default=None, alias="CROSSREF_MAILTO")
    semantic_scholar_api_key: Optional[str] = Field(
        default=None, alias="SEMANTIC_SCHOLAR_API_KEY"
    )
    github_token: Optional[str] = Field(default=None, alias="GITHUB_TOKEN")
    ieee_api_key: Optional[str] = Field(default=None, alias="IEEE_API_KEY")
    nasa_api_key: Optional[str] = Field(default=None, alias="NASA_API_KEY")
    noaa_token: Optional[str] = Field(default=None, alias="NOAA_TOKEN")
    data_gov_key: Optional[str] = Field(default=None, alias="DATA_GOV_KEY")
    core_api_key: Optional[str] = Field(default=None, alias="CORE_API_KEY")
    unpaywall_email: Optional[str] = Field(default=None, alias="UNPAYWALL_EMAIL")

    @property
    def stemclaw_dir(self) -> Path:
        return Path.cwd() / self.stemclaw_dir_name

    @property
    def session_file(self) -> Path:
        return self.stemclaw_dir / self.session_file_name

    @property
    def env_file(self) -> Path:
        return self.stemclaw_dir / ".env"

    def ensure_directories(self) -> None:
        """Ensure runtime directories exist."""
        self.stemclaw_dir.mkdir(parents=True, exist_ok=True)


# Global settings singleton helper
_settings_instance: Optional[StemClawSettings] = None
_last_cwd: Optional[Path] = None


def get_settings(reload: bool = False) -> StemClawSettings:
    """Retrieve the cached or reloaded settings, auto-reloading if cwd changed."""
    global _settings_instance, _last_cwd
    current_cwd = Path.cwd()
    if _settings_instance is None or reload or _last_cwd != current_cwd:
        _settings_instance = StemClawSettings(workspace_root=current_cwd)
        _last_cwd = current_cwd
    return _settings_instance
