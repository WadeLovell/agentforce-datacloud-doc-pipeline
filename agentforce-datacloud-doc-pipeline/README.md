# Agentforce Data Cloud Documentation Pipeline

Purpose:
Create deterministic, procedure-level Markdown files from
JS-rendered documentation for ingestion into Salesforce Data Cloud
Unstructured Data and retrieval by Agentforce.

Target Platform:
- Salesforce Data Cloud (formerly Data 360)
- Salesforce Agentforce for Financial Services

Output:
- One Markdown file per procedure
- Chunk-ready, metadata-enriched content

This repo is POC-safe and production-scalable.

## Quick Start (POC)

```bash
# 1. Clone and setup
git clone <your-repo-url>
cd agentforce-datacloud-doc-pipeline
pip install -r requirements.txt --break-system-packages
npm install -g playwright
npx playwright install chromium

# 2. Run full pipeline
make all

# 3. Upload to Data Cloud
cp upload/env.example upload/.env
# Edit .env with your Salesforce credentials
python upload/datacloud_ingest.py
```

## Pipeline Stages

| Stage | Command | Output |
|-------|---------|--------|
| Snapshot | `make snapshot` | `raw/html/*.html` |
| Extract | `make extract` | `extract/procedures.json` |
| Normalize | `make normalize` | `output/datacloud_markdown/*.md` |
| Validate | `make validate` | Pass/fail |

## Middle-Market Banking Notes

This pipeline is designed for:
- Compliance-first documentation
- Explainable AI requirements
- Audit-ready citation trails
- FSC integration compatibility
