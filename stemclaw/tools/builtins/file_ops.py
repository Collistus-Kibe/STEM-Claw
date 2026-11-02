"""File operation tools allowing the agent to read and write in workspace."""

from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field
from stemclaw.config import get_settings
from stemclaw.tools.base import BaseTool


class FileReadInput(BaseModel):
    file_path: str = Field(..., description="Relative path of file in workspace to read")


class FileReadTool(BaseTool):
    name = "file_read"
    description = "Read file contents from the current workspace."
    input_model = FileReadInput

    def run(self, file_path: str) -> str:
        settings = get_settings()
        target = (settings.workspace_root / file_path).resolve()
        if not target.exists():
            return f"Error: File not found at '{file_path}'"
        if not target.is_file():
            return f"Error: Path '{file_path}' is not a regular file"
        try:
            return target.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            return f"Error reading file '{file_path}': {e}"


class FileWriteInput(BaseModel):
    file_path: str = Field(..., description="Relative path of file in workspace to write")
    content: str = Field(..., description="Text content to write into the file")


class FileWriteTool(BaseTool):
    name = "file_write"
    description = "Write or overwrite text content to a file in the workspace."
    input_model = FileWriteInput

    def run(self, file_path: str, content: str) -> str:
        settings = get_settings()
        target = (settings.workspace_root / file_path).resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            target.write_text(content, encoding="utf-8")
            return f"Successfully wrote {len(content)} characters to '{file_path}'"
        except Exception as e:
            return f"Error writing file '{file_path}': {e}"


class ListDirectoryInput(BaseModel):
    directory_path: str = Field(
        default=".", description="Relative directory path to inspect"
    )


class ListDirectoryTool(BaseTool):
    name = "list_directory"
    description = "List files and subdirectories in a workspace path."
    input_model = ListDirectoryInput

    def run(self, directory_path: str = ".") -> str:
        settings = get_settings()
        target = (settings.workspace_root / directory_path).resolve()
        if not target.exists():
            return f"Error: Directory '{directory_path}' does not exist."
        if not target.is_dir():
            return f"Error: Path '{directory_path}' is not a directory."

        entries = []
        for p in sorted(target.iterdir()):
            kind = "[DIR]" if p.is_dir() else "[FILE]"
            entries.append(f"{kind} {p.name}")
        return "\n".join(entries) if entries else "(Empty directory)"

