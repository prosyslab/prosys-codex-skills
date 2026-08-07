# Zotero PDF Ingest

Extract a paper DOI from a PDF, retrieve its metadata from Crossref, and add
the normalized item to a Zotero group library.

## Required environment variables

Set these variables before running `scripts/add_to_zotero.py`:

| Variable | Description |
| --- | --- |
| `ZOTERO_GROUP_ID` | Public numeric ID of the Zotero group library |
| `ZOTERO_API_KEY` | Zotero API key with permission to create items in that group |

Example:

```bash
export ZOTERO_GROUP_ID="5047220"  # Prosys Lab
export ZOTERO_API_KEY="your-zotero-api-key"
```

The scripts read the variables from the process environment and do not load a
`.env` file. `ZOTERO_GROUP_ID` is a public group identifier; keep
`ZOTERO_API_KEY` private and do not commit it, print it, or put it in
`SKILL.md`.

## Usage

Create the Python environment once. Reuse it for later runs instead of
reinstalling dependencies:

```bash
if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
  .venv/bin/python -m pip install PyMuPDF requests
fi
```

Run the three stages in order:

```bash
.venv/bin/python scripts/read_pdf.py path/to/paper.pdf > doi.json
.venv/bin/python scripts/extract_metadata.py < doi.json > metadata.json
.venv/bin/python scripts/add_to_zotero.py < metadata.json
```

See [SKILL.md](SKILL.md) for the complete workflow and publication-title
normalization rules.
