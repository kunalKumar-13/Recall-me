"""File-type-aware text extraction.

Each parser returns plain text. Optional dependencies (python-docx,
pytesseract, Pillow) are imported lazily so the app starts even when they're
not installed — supported file types just shrink accordingly.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional

CODE_EXTS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".c", ".cpp",
    ".h", ".hpp", ".cs", ".rb", ".php", ".swift", ".kt", ".scala", ".sh",
    ".bash", ".zsh", ".ps1", ".html", ".css", ".scss", ".json", ".yaml",
    ".yml", ".toml", ".xml", ".sql", ".r", ".lua", ".dart", ".vue", ".svelte",
}
TEXT_EXTS = {
    ".txt", ".md", ".markdown", ".rst", ".log", ".csv", ".tsv", ".ini", ".cfg",
}
PDF_EXTS = {".pdf"}
DOCX_EXTS = {".docx"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff"}


def parse_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def parse_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError:
        return ""
    try:
        reader = PdfReader(str(path))
    except Exception:
        return ""
    parts = []
    for page in reader.pages:
        try:
            parts.append(page.extract_text() or "")
        except Exception:
            continue
    return "\n".join(parts)


def parse_docx(path: Path) -> str:
    try:
        import docx  # python-docx
    except ImportError:
        return ""
    try:
        document = docx.Document(str(path))
    except Exception:
        return ""
    return "\n".join(p.text for p in document.paragraphs if p.text)


def parse_image_ocr(path: Path) -> str:
    try:
        from PIL import Image
        import pytesseract
    except ImportError:
        return ""
    try:
        return pytesseract.image_to_string(Image.open(str(path)))
    except Exception:
        return ""


def get_parser(path: Path, enable_ocr: bool = False) -> Optional[Callable[[Path], str]]:
    ext = path.suffix.lower()
    if ext in PDF_EXTS:
        return parse_pdf
    if ext in DOCX_EXTS:
        return parse_docx
    if ext in TEXT_EXTS or ext in CODE_EXTS:
        return parse_text
    if enable_ocr and ext in IMAGE_EXTS:
        return parse_image_ocr
    return None


def is_supported(path: Path, enable_ocr: bool = False) -> bool:
    return get_parser(path, enable_ocr) is not None
