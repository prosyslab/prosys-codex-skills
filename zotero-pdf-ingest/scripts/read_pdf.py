#!/usr/bin/env python3
"""Stage 1: extract a DOI from a PDF."""

import argparse
import json
import os
import re
import sys
from pathlib import Path


local_python = Path(__file__).resolve().parent / ".venv" / "bin" / "python"
if local_python.exists() and sys.prefix == sys.base_prefix:
    os.execv(str(local_python), [str(local_python), *sys.argv])

try:
    import pymupdf
except ImportError:
    try:
        import fitz as pymupdf
    except ImportError as error:
        raise ImportError("PyMuPDF is required; install it with 'pip install pymupdf'") from error


DOI_PATTERN = re.compile(
    r"(?i)(?:https?://(?:dx\.)?doi\.org/)?"
    r"10\.\d{4,9}/[-._;()/:a-z0-9]+"
)
DOI_TRAILING_PUNCTUATION = ".,;:!?)]}>\"'"


def find_doi(text: str) -> str | None:
    match = DOI_PATTERN.search(text)
    if not match:
        return None
    doi = re.sub(r"(?i)^https?://(?:dx\.)?doi\.org/", "", match.group(0))
    return doi.rstrip(DOI_TRAILING_PUNCTUATION)


def extract_doi(pdf_path: str) -> str:
    try:
        with pymupdf.open(pdf_path) as document:
            text = "\n".join(page.get_text() for page in document)
    except (OSError, RuntimeError) as error:
        raise RuntimeError(f"could not read PDF '{pdf_path}': {error}") from error

    doi = find_doi(text)
    if not doi:
        raise ValueError(f"no DOI found in PDF '{pdf_path}'")
    return doi


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract a DOI from a PDF")
    parser.add_argument("pdf", nargs="?", default="paper.pdf", help="path to the PDF")
    args = parser.parse_args()
    try:
        doi = extract_doi(args.pdf)
    except (RuntimeError, ValueError) as error:
        print(f"read_pdf.py failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps({"doi": doi}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
