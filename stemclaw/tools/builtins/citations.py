"""BibTeX Exporter and Citation Formatter built-in tools."""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from stemclaw.config import get_settings
from stemclaw.tools.base import BaseTool


def generate_citekey(authors: str, year: Any, title: str) -> str:
    """Generate a clean citation key like 'vaswani2017attention'."""
    # First author's last name
    first_author = "author"
    if authors:
        # Split by comma or 'and'
        parts = re.split(r",|\sand\s", authors.strip())
        if parts:
            name_token = parts[0].strip().split()
            if name_token:
                first_author = name_token[-1].lower()

    # Clean author name (alphanumeric only)
    clean_author = re.sub(r"[^a-z0-9]", "", first_author.lower()) or "author"

    # Year
    year_str = str(year).strip() if year else "nodate"
    clean_year = re.search(r"\d{4}", year_str)
    year_token = clean_year.group(0) if clean_year else "nodate"

    # First significant word from title
    stopwords = {"a", "an", "the", "on", "in", "for", "of", "and", "to", "with", "is", "at"}
    title_words = re.findall(r"[a-z0-9]+", title.lower())
    title_token = "paper"
    for w in title_words:
        if w not in stopwords:
            title_token = w
            break

    return f"{clean_author}{year_token}{title_token}"


class BibtexExportInput(BaseModel):
    title: str = Field(..., description="Paper or article title")
    authors: str = Field(..., description="Authors formatted as 'First Last, First Last' or 'Author A and Author B'")
    year: Any = Field(default="2024", description="Publication year")
    venue: Optional[str] = Field(default=None, description="Journal, conference proceeding, or repository (e.g. Nature, arXiv, bioRxiv)")
    doi: Optional[str] = Field(default=None, description="Digital Object Identifier")
    arxiv_id: Optional[str] = Field(default=None, description="ArXiv ID (e.g. 1706.03762)")
    citekey: Optional[str] = Field(default=None, description="Optional custom citekey (auto-generated if omitted)")
    file_path: str = Field(default="references.bib", description="Relative path in workspace to save BibTeX entries")


class BibtexExportTool(BaseTool):
    name = "export_bibtex"
    description = (
        "Generate a standardized BibTeX entry for a scientific paper and append or save it "
        "directly into 'references.bib' in the project workspace."
    )
    input_model = BibtexExportInput

    def run(
        self,
        title: str,
        authors: str,
        year: Any = "2024",
        venue: Optional[str] = None,
        doi: Optional[str] = None,
        arxiv_id: Optional[str] = None,
        citekey: Optional[str] = None,
        file_path: str = "references.bib",
    ) -> str:
        key = citekey or generate_citekey(authors, year, title)

        # Decide entry type
        entry_type = "article"
        if venue and any(k in venue.lower() for k in ("conference", "proceedings", "symposium", "workshop")):
            entry_type = "inproceedings"

        # Format authors for BibTeX ('and' separated)
        author_list = re.split(r",\s*|\sand\s+", authors)
        bibtex_authors = " and ".join([a.strip() for a in author_list if a.strip()])

        lines = [f"@{entry_type}{{{key},"]
        lines.append(f"  title = {{{title}}},")
        lines.append(f"  author = {{{bibtex_authors}}},")
        lines.append(f"  year = {{{year}}},")
        if venue:
            field = "booktitle" if entry_type == "inproceedings" else "journal"
            lines.append(f"  {field} = {{{venue}}},")
        if doi:
            clean_doi = doi.replace("https://doi.org/", "")
            lines.append(f"  doi = {{{clean_doi}}},")
        if arxiv_id:
            lines.append(f"  eprint = {{{arxiv_id}}},")
            lines.append("  archiveprefix = {arXiv},")
        lines.append("}")
        bibtex_entry = "\n".join(lines) + "\n\n"

        # Write/append to workspace file
        settings = get_settings()
        target_path = Path(file_path)
        if not target_path.is_absolute():
            target_path = settings.workspace_root / target_path

        target_path.parent.mkdir(parents=True, exist_ok=True)

        existing_content = ""
        if target_path.exists():
            existing_content = target_path.read_text(encoding="utf-8")

        # Avoid exact duplicate citekey appending
        if f"{{{key}," in existing_content:
            return (
                f"Notice: Citekey '{key}' already exists in {file_path}.\n"
                f"Generated BibTeX entry:\n```bibtex\n{bibtex_entry.strip()}\n```"
            )

        with open(target_path, "a", encoding="utf-8") as f:
            f.write(bibtex_entry)

        return (
            f"Successfully added citation [@{key}] to {file_path}!\n\n"
            f"```bibtex\n{bibtex_entry.strip()}\n```"
        )


class FormatCitationInput(BaseModel):
    title: str = Field(..., description="Paper or article title")
    authors: str = Field(..., description="Authors string")
    year: Any = Field(default="2024", description="Publication year")
    venue: Optional[str] = Field(default=None, description="Journal, conference, or publisher")
    doi: Optional[str] = Field(default=None, description="DOI string or URL")
    style: str = Field(default="apa", description="Citation style: 'apa', 'ieee', 'nature', or 'chicago'")


class FormatCitationTool(BaseTool):
    name = "format_citation"
    description = (
        "Format a paper citation into APA 7th, IEEE, Nature, or Chicago scientific citation style "
        "for instant inclusion in manuscripts and research bibliographies."
    )
    input_model = FormatCitationInput

    def run(
        self,
        title: str,
        authors: str,
        year: Any = "2024",
        venue: Optional[str] = None,
        doi: Optional[str] = None,
        style: str = "apa",
    ) -> str:
        clean_style = style.lower().strip()
        author_list = [a.strip() for a in re.split(r",\s*|\sand\s+", authors) if a.strip()]

        doi_str = f" https://doi.org/{doi.replace('https://doi.org/', '')}" if doi else ""
        venue_str = f"{venue}. " if venue else ""

        if clean_style == "ieee":
            # IEEE format: [1] J. K. Author, "Title," Journal, year.
            abbr_authors = []
            for a in author_list[:3]:
                toks = a.split()
                if len(toks) > 1:
                    initials = " ".join(f"{t[0]}." for t in toks[:-1])
                    abbr_authors.append(f"{initials} {toks[-1]}")
                else:
                    abbr_authors.append(a)
            auth_str = ", ".join(abbr_authors) + (", et al." if len(author_list) > 3 else "")
            citation = f'{auth_str}, "{title.rstrip(".")}," {venue_str}{year}.{doi_str}'

        elif clean_style == "nature":
            # Nature: Author, A. et al. Title. Journal (Year).
            first_author = author_list[0] if author_list else "Author"
            toks = first_author.split()
            first_fmt = f"{toks[-1]}, {toks[0][0]}." if len(toks) > 1 else first_author
            auth_str = f"{first_fmt} et al." if len(author_list) > 1 else first_fmt
            citation = f"{auth_str} {title.rstrip('.')}. {venue_str}({year}).{doi_str}"

        elif clean_style == "chicago":
            # Chicago: Author, First. Year. "Title." Journal.
            auth_str = ", and ".join(author_list[:2]) + (", et al." if len(author_list) > 2 else "")
            citation = f'{auth_str}. {year}. "{title.rstrip(".")}." {venue_str}{doi_str}'

        else:
            # Default APA 7th: Author, A. A., & Author, B. B. (Year). Title. Journal. https://doi.org/...
            auth_str = ", ".join(author_list[:3]) + (" et al." if len(author_list) > 3 else "")
            citation = f"{auth_str} ({year}). {title.rstrip('.')}. {venue_str}{doi_str}"

        return f"**[{clean_style.upper()} Citation]**\n{citation.strip()}"

