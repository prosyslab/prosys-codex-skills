#!/usr/bin/env python3
"""Stage 3: add metadata JSON as an item in a Zotero group library."""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import requests


DEFAULT_PUBLICATION_TITLE_RULES = Path(__file__).resolve().with_name(
    "publication_title_rules.json"
)


def read_metadata(source: str | None) -> dict[str, Any]:
    if source and source != "-":
        try:
            with Path(source).open(encoding="utf-8") as file:
                metadata = json.load(file)
        except FileNotFoundError as error:
            raise ValueError(f"metadata file not found: '{source}'") from error
        except json.JSONDecodeError as error:
            raise ValueError(f"metadata file is not valid JSON: '{source}': {error}") from error
    else:
        input_text = sys.stdin.read().strip()
        if not input_text:
            raise ValueError("no metadata supplied; pass a JSON file or pipe metadata JSON to stdin")
        try:
            metadata = json.loads(input_text)
        except json.JSONDecodeError as error:
            raise ValueError(f"stdin does not contain valid metadata JSON: {error}") from error
    if not isinstance(metadata, dict):
        raise ValueError("metadata must be a JSON object")
    return metadata


def load_publication_title_rules(rules_path: Path = DEFAULT_PUBLICATION_TITLE_RULES) -> dict[str, str]:
    try:
        with rules_path.open(encoding="utf-8") as file:
            rules = json.load(file)
    except FileNotFoundError as error:
        raise ValueError(f"publication title rules file not found: '{rules_path}'") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"publication title rules are not valid JSON: '{rules_path}': {error}") from error
    mapping = rules.get("publication_titles") if isinstance(rules, dict) else None
    if not isinstance(mapping, dict):
        raise ValueError(
            f"publication title rules must contain an object named 'publication_titles': '{rules_path}'"
        )
    if not all(isinstance(source, str) and isinstance(target, str) for source, target in mapping.items()):
        raise ValueError(f"publication title rules must map strings to strings: '{rules_path}'")
    return mapping


def normalize_publication_title(title: str, rules: dict[str, str]) -> str:
    normalized_title = " ".join(title.split())
    return rules.get(normalized_title, normalized_title)


def zotero_creator(author: Any) -> dict[str, str] | None:
    if isinstance(author, dict):
        if author.get("literal"):
            return {"creatorType": "author", "name": str(author["literal"])}
        given = str(author.get("given") or "").strip()
        family = str(author.get("family") or "").strip()
        if given or family:
            return {"creatorType": "author", "firstName": given, "lastName": family}
    elif isinstance(author, str) and author.strip():
        parts = author.split()
        return {"creatorType": "author", "firstName": " ".join(parts[:-1]), "lastName": parts[-1]}
    return None


def build_zotero_item(
    metadata: dict[str, Any],
    item_type: str | None = None,
    publication_title_rules: dict[str, str] | None = None,
) -> dict[str, Any]:
    title = str(metadata.get("title") or "").strip()
    if not title:
        raise ValueError("metadata.title is required to create a Zotero item")
    resolved_item_type = item_type or metadata.get("zotero_item_type") or "journalArticle"
    item: dict[str, Any] = {"itemType": resolved_item_type, "title": title}
    creators = [zotero_creator(author) for author in metadata.get("authors", [])]
    item["creators"] = [creator for creator in creators if creator]
    venue = str(metadata.get("venue") or "").strip()
    year = str(metadata.get("year") or "").strip()
    volume = str(metadata.get("volume") or "").strip()
    issue = str(metadata.get("issue") or "").strip()
    if venue:
        item["publicationTitle"] = normalize_publication_title(venue, publication_title_rules or {})
    if year:
        item["date"] = year
    if volume:
        item["volume"] = volume
    if issue:
        item["issue"] = issue
    return item


def add_to_zotero(item: dict[str, Any], group_id: str, api_key: str) -> dict[str, Any]:
    url = f"https://api.zotero.org/groups/{group_id}/items"
    try:
        response = requests.post(
            url,
            headers={
                "Zotero-API-Key": api_key,
                "Zotero-API-Version": "3",
                "Content-Type": "application/json",
            },
            json=[item],
            timeout=15,
        )
    except requests.RequestException as error:
        raise RuntimeError(f"Zotero request failed: {error}") from error
    if not response.ok:
        body = response.text.strip().replace("\n", " ")
        raise RuntimeError(f"Zotero rejected the request with HTTP {response.status_code}: {body[:500]}")
    try:
        result = response.json()
    except ValueError as error:
        raise RuntimeError(f"Zotero returned invalid JSON: {error}") from error
    failed = result.get("failed") or {}
    if failed:
        raise RuntimeError(f"Zotero failed to create the item: {json.dumps(failed, ensure_ascii=False)}")
    successful = result.get("successful") or {}
    created = successful.get("0") or {}
    key = created.get("key") or (result.get("success") or {}).get("0")
    if not key:
        raise RuntimeError(f"Zotero response did not contain a created item key: {result}")
    return {"status": "created", "zotero_key": key, "item": item}


def main() -> int:
    parser = argparse.ArgumentParser(description="Add metadata JSON to a Zotero group library")
    parser.add_argument("metadata", nargs="?", help="metadata JSON file, or '-' / omitted for stdin")
    parser.add_argument("--item-type", default=None, help="override inferred Zotero item type")
    args = parser.parse_args()
    group_id = os.getenv("ZOTERO_GROUP_ID")
    api_key = os.getenv("ZOTERO_API_KEY")
    if not group_id or not api_key:
        print("add_to_zotero.py failed: ZOTERO_GROUP_ID and ZOTERO_API_KEY must be set", file=sys.stderr)
        return 1
    try:
        metadata = read_metadata(args.metadata)
        item = build_zotero_item(metadata, args.item_type, load_publication_title_rules())
        result = add_to_zotero(item, group_id, api_key)
    except (RuntimeError, ValueError) as error:
        print(f"add_to_zotero.py failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
