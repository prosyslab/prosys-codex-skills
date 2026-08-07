---
name: zotero-pdf-ingest
description: "Extract a paper DOI from a PDF, fetch title/authors/publication venue/year/volume/issue and journal-versus-conference type from Crossref, then add the normalized metadata to a Zotero group library. Use one persistent Python virtual environment: create and install dependencies only on the first use, then reuse that environment on every later use."
---

# Zotero PDF Ingest

Use the bundled three executable stages in `scripts/` as a JSON pipeline. Keep
the stages separate so an agent can inspect, retry, or replace one stage
without repeating the others. Before running them, check for the repository's
persistent `.venv`. If it does not exist, create it once and install PyMuPDF
and `requests`; if it already exists, reuse it and do not recreate the virtual
environment or reinstall its dependencies on later skill invocations.

Run every stage with the same persistent virtual-environment interpreter. If a
dependency is missing from an existing environment, diagnose or repair that
environment instead of deleting and rebuilding it.

Initialize the environment once before the first stage:

```bash
if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi
if ! .venv/bin/python -c 'import pymupdf, requests' >/dev/null 2>&1; then
  .venv/bin/python -m pip install PyMuPDF requests
fi
```

The existence and import checks make subsequent invocations reuse the same
environment without reinstalling dependencies.

## Workflow

1. Extract the DOI from the PDF:

   ```bash
   .venv/bin/python scripts/read_pdf.py path/to/paper.pdf > doi.json
   ```

2. Resolve the DOI through Crossref:

   ```bash
   .venv/bin/python scripts/extract_metadata.py < doi.json > metadata.json
   ```

3. Add the metadata to Zotero:

   ```bash
   .venv/bin/python scripts/add_to_zotero.py < metadata.json
   ```

The stages can also be piped directly:

```bash
.venv/bin/python scripts/read_pdf.py path/to/paper.pdf \
  | .venv/bin/python scripts/extract_metadata.py \
  | .venv/bin/python scripts/add_to_zotero.py
```

Require `ZOTERO_GROUP_ID` and `ZOTERO_API_KEY` in the process environment
before running the final stage. The programs read these values directly with
environment-variable lookups and do not load a `.env` file. Do not print or
expose the API key.

## Data and classification

Expect each successful stage to write JSON to stdout and each failure to write
a stage-specific message to stderr with a non-zero exit code. Preserve these
streams when invoking a stage so failures are not mistaken for successful JSON.

`extract_metadata.py` emits:

- `title`, `authors`, `venue`, `year`
- `volume` and `issue` when Crossref provides them
- `publication_type`: `journal` or `conference` when recognized
- `crossref_type` and `zotero_item_type`

Map Crossref types as follows:

- `journal-article` → `journalArticle`
- `proceedings-article` → `conferencePaper`

The final Zotero item uses the inferred `itemType`; an explicit
`--item-type` overrides it. Do not add DOI or URL fields to the Zotero item.

## Publication-title normalization

Publication titles written to Zotero must use the `full name (acronym)` format
for both journals and conferences. DOI metadata and paper PDFs often contain
full names, abbreviations, or other non-standard variants, so do not copy an
unstandardized venue name directly into Zotero.

Always let the bundled `scripts/add_to_zotero.py` load the adjacent
`scripts/publication_title_rules.json` at runtime. Apply the exact
source-to-target mappings in that file. If no rule exists for a venue, determine
its conventional full name and acronym from the DOI metadata, paper, or the
official publication page, add the exact mapping to
`publication_title_rules.json`, and then run the script so the normalized value
is used in Zotero. Do not leave an unknown or non-standard venue unchanged.

Examples of the required format:

- `Proceedings of the ACM on Programming Languages (PACMPL)`
- `ACM International Conference on the Foundations of Software Engineering (FSE)`
- `International Conference on Software Engineering (ICSE)`

For example:

```json
"Proc. ACM Program. Lang.":
  "Proceedings of the ACM on Programming Languages (PACMPL)"
```

Do not hard-code publication-title aliases in the Python script. If the rules
file is missing or malformed, report that as a configuration failure and do not
call Zotero.

## Failure handling

Run stages independently when diagnosing a failure. Check, in order:

- DOI extraction: PDF exists, is readable, and contains searchable DOI text.
- Crossref lookup: DOI is valid and network/API access is available.
- Zotero insertion: credentials are present, metadata has a title, and the API
  response contains a created item key.

Never retry Zotero insertion blindly after an ambiguous network error; first
check whether the item was created to avoid duplicates.
