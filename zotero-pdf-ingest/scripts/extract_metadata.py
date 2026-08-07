#!/usr/bin/env python3
"""Stage 2: retrieve bibliographic metadata from a DOI using Crossref."""

import argparse
import json
import re
import sys
from typing import Any
from urllib.parse import quote

import requests


DOI_PATTERN = re.compile(r"(?i)^10\.\d{4,9}/[-._;()/:a-z0-9]+$")
DOI_TRAILING_PUNCTUATION = ".,;:!?)]}>\"'"
CROSSREF_TO_ZOTERO_TYPE = {
    "journal-article": "journalArticle",
    "proceedings-article": "conferencePaper",
}


def normalize_doi(value: str) -> str:
    doi = value.strip()
    doi = re.sub(r"(?i)^doi:\s*", "", doi)
    doi = re.sub(r"(?i)^https?://(?:dx\.)?doi\.org/", "", doi)
    doi = doi.rstrip(DOI_TRAILING_PUNCTUATION)
    if not DOI_PATTERN.fullmatch(doi):
        raise ValueError(f"invalid DOI: '{value.strip()}'")
    return doi


def read_doi(argument: str | None) -> str:
    if argument:
        return normalize_doi(argument)
    input_text = sys.stdin.read().strip()
    if not input_text:
        raise ValueError("no DOI supplied; pass a DOI argument or pipe DOI JSON to stdin")
    try:
        input_data = json.loads(input_text)
    except json.JSONDecodeError:
        input_data = input_text
    if isinstance(input_data, dict):
        input_data = input_data.get("doi")
    if not isinstance(input_data, str) or not input_data.strip():
        raise ValueError("stdin JSON must contain a non-empty string field named 'doi'")
    return normalize_doi(input_data)


def publication_year(message: dict[str, Any]) -> str | None:
    for field in ("published-print", "published-online", "published", "issued", "created"):
        date_parts = (message.get(field) or {}).get("date-parts", [])
        if date_parts and date_parts[0]:
            return str(date_parts[0][0])
    return None


def publication_type(crossref_type: str | None) -> str | None:
    if crossref_type == "journal-article":
        return "journal"
    if crossref_type == "proceedings-article":
        return "conference"
    return None


def fetch_metadata(doi: str) -> dict[str, Any]:
    url = f"https://api.crossref.org/works/{quote(doi, safe='/')}"
    try:
        response = requests.get(
            url,
            headers={"User-Agent": "zotero-bot/1.0"},
            timeout=15,
        )
        response.raise_for_status()
        message = response.json()["message"]
    except requests.RequestException as error:
        raise RuntimeError(f"Crossref request failed for DOI '{doi}': {error}") from error
    except (KeyError, TypeError, ValueError) as error:
        raise RuntimeError(f"Crossref returned invalid metadata for DOI '{doi}': {error}") from error

    authors = []
    for author in message.get("author", []):
        given = (author.get("given") or "").strip()
        family = (author.get("family") or "").strip()
        literal = (author.get("name") or "").strip()
        if given or family:
            authors.append({"given": given, "family": family})
        elif literal:
            authors.append({"literal": literal})

    event_name = (message.get("event") or {}).get("name")
    container_titles = message.get("container-title") or []
    title_values = message.get("title") or []
    crossref_type = message.get("type")
    metadata = {
        "doi": doi,
        "title": title_values[0] if title_values else None,
        "authors": authors,
        "venue": event_name or (container_titles[0] if container_titles else None),
        "year": publication_year(message),
        "volume": message.get("volume"),
        "issue": message.get("issue"),
        "publication_type": publication_type(crossref_type),
        "crossref_type": crossref_type,
        "zotero_item_type": CROSSREF_TO_ZOTERO_TYPE.get(crossref_type),
    }
    if not metadata["title"]:
        raise RuntimeError(f"Crossref metadata for DOI '{doi}' has no title")
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser(description="Get paper metadata from a DOI")
    parser.add_argument("doi", nargs="?", help="DOI, or omit it to read DOI JSON from stdin")
    args = parser.parse_args()
    try:
        metadata = fetch_metadata(read_doi(args.doi))
    except (RuntimeError, ValueError) as error:
        print(f"extract_metadata.py failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps(metadata, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
