"""Scientific Dataset and Sequence Inspector built-in tool."""

import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from stemclaw.config import get_settings
from stemclaw.tools.base import BaseTool


class DatasetInspectInput(BaseModel):
    file_path: str = Field(..., description="Path to tabular dataset (.csv, .tsv), JSON, or FASTA sequence file")
    preview_rows: int = Field(default=5, ge=1, le=50, description="Max sample rows to preview")


class DatasetInspectTool(BaseTool):
    name = "dataset_inspect"
    description = (
        "Inspect and profile scientific datasets (.csv, .tsv, .json, .fasta). "
        "Reports column types, missing value counts, dimensions, sequence lengths, "
        "and GC content percentages for genomic files."
    )
    input_model = DatasetInspectInput

    def run(self, file_path: str, preview_rows: int = 5) -> str:
        settings = get_settings()
        target = Path(file_path)
        if not target.is_absolute():
            target = settings.workspace_root / target

        if not target.exists():
            return f"Error: Dataset file not found at '{file_path}' (resolved: '{target}')."

        suffix = target.suffix.lower()

        try:
            if suffix in (".csv", ".tsv", ".txt"):
                return self._inspect_tabular(target, preview_rows, is_tsv=(suffix == ".tsv"))
            elif suffix in (".fasta", ".fa", ".fna", ".faa"):
                return self._inspect_fasta(target, preview_rows)
            elif suffix in (".json", ".jsonl"):
                return self._inspect_json(target, preview_rows)
            else:
                # Default text peek
                content = target.read_text(encoding="utf-8", errors="replace")
                lines = content.splitlines()
                return (
                    f"=== File Summary: {target.name} ===\n"
                    f"Size: {target.stat().st_size:,} bytes | Total Lines: {len(lines):,}\n\n"
                    f"--- Preview (First {min(preview_rows, len(lines))} lines) ---\n"
                    + "\n".join(lines[:preview_rows])
                )
        except Exception as e:
            return f"Error reading dataset '{file_path}': {e}"

    def _inspect_tabular(self, path: Path, preview_rows: int, is_tsv: bool) -> str:
        delimiter = "\t" if is_tsv else ","
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.reader(f, delimiter=delimiter)
            header = next(reader, None)
            if not header:
                return f"Tabular file '{path.name}' is empty."

            col_count = len(header)
            rows = []
            null_counts = [0] * col_count
            total_rows = 0

            for r in reader:
                total_rows += 1
                if len(rows) < preview_rows:
                    rows.append(r)
                for idx, val in enumerate(r[:col_count]):
                    if not val.strip() or val.strip().lower() in ("na", "nan", "null", "none"):
                        null_counts[idx] += 1

        lines = [
            f"=== Tabular Dataset Profile: {path.name} ===",
            f"Dimensions: {total_rows:,} rows × {col_count} columns",
            f"File Size: {path.stat().st_size:,} bytes\n",
            "Columns & Missing Values:",
        ]
        for col_idx, col_name in enumerate(header):
            null_pct = (null_counts[col_idx] / total_rows * 100) if total_rows > 0 else 0
            lines.append(f"  [{col_idx+1}] {col_name} - Missing: {null_counts[col_idx]} ({null_pct:.1f}%)")

        lines.append(f"\nSample Rows (First {len(rows)}):")
        # Format aligned preview
        header_line = " | ".join(header)
        lines.append(header_line)
        lines.append("-" * min(len(header_line), 80))
        for r in rows:
            # Pad row if fewer columns
            padded = r + [""] * (col_count - len(r))
            lines.append(" | ".join(padded[:col_count]))

        return "\n".join(lines)

    def _inspect_fasta(self, path: Path, preview_count: int) -> str:
        sequences: List[Dict[str, Any]] = []
        current_id = ""
        current_seq = []
        total_nt = 0

        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line_str = line.strip()
                if line_str.startswith(">"):
                    if current_id:
                        seq_str = "".join(current_seq)
                        sequences.append({"id": current_id, "len": len(seq_str), "seq": seq_str})
                        total_nt += len(seq_str)
                    current_id = line_str[1:]
                    current_seq = []
                else:
                    current_seq.append(line_str)

            if current_id:
                seq_str = "".join(current_seq)
                sequences.append({"id": current_id, "len": len(seq_str), "seq": seq_str})
                total_nt += len(seq_str)

        if not sequences:
            return f"FASTA file '{path.name}' contains no valid sequences."

        avg_len = total_nt / len(sequences)
        lines = [
            f"=== FASTA Sequence Profile: {path.name} ===",
            f"Total Sequences: {len(sequences):,}",
            f"Total Residues/Bases: {total_nt:,}",
            f"Mean Sequence Length: {avg_len:.1f}\n",
            f"Sequence Preview (First {min(preview_count, len(sequences))}):",
        ]

        for s in sequences[:preview_count]:
            sample = s["seq"][:40] + ("..." if len(s["seq"]) > 40 else "")
            # If nucleotide, calculate GC %
            upper = s["seq"].upper()
            g_c = upper.count("G") + upper.count("C")
            a_t_g_c = g_c + upper.count("A") + upper.count("T") + upper.count("U")
            gc_str = f" | GC: {(g_c / a_t_g_c * 100):.1f}%" if a_t_g_c > 0 else ""

            lines.append(f"\n> {s['id']}")
            lines.append(f"  Length: {s['len']:,} bp/aa{gc_str}")
            lines.append(f"  Sequence: {sample}")

        return "\n".join(lines)

    def _inspect_json(self, path: Path, preview_count: int) -> str:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            data = json.load(f)

        lines = [f"=== JSON Profile: {path.name} ==="]
        if isinstance(data, list):
            lines.append(f"Root Type: List ({len(data):,} items)")
            if data and isinstance(data[0], dict):
                lines.append(f"Sample Item Keys: {', '.join(data[0].keys())}")
            preview_str = json.dumps(data[:preview_count], indent=2)
            lines.append(f"\nPreview:\n{preview_str[:600]}...")
        elif isinstance(data, dict):
            lines.append(f"Root Type: Object ({len(data)} top-level keys)")
            lines.append(f"Keys: {', '.join(list(data.keys())[:15])}")
            preview_str = json.dumps({k: data[k] for k in list(data.keys())[:preview_count]}, indent=2)
            lines.append(f"\nPreview:\n{preview_str[:600]}...")
        else:
            lines.append(f"Root Type: {type(data).__name__}")

        return "\n".join(lines)

