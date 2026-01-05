.PHONY: all snapshot extract normalize validate clean help

# Default target - run full pipeline
all: snapshot extract normalize validate
	@echo "✅ Pipeline complete - ready for Data Cloud ingestion"
	@echo "   Run: python upload/datacloud_ingest.py"

# Stage A: Capture JS-rendered HTML
snapshot:
	@echo "📸 Stage A: Dynamic Snapshot"
	node extract/snapshot.js

# Stage B: Extract procedures from HTML
extract:
	@echo "🔍 Stage B: Procedure Extraction"
	python extract/extract_procedures.py

# Stage C: Convert to Data Cloud-optimized Markdown
normalize:
	@echo "📝 Stage C: Markdown Normalization"
	python normalize/procedures_to_markdown.py

# Stage D: Validate before upload
validate:
	@echo "✅ Stage D: Validation"
	python validate/validate_markdown.py

# Clean all generated artifacts
clean:
	@echo "🧹 Cleaning generated files..."
	rm -rf raw/html/*
	rm -f extract/procedures.json
	rm -rf output/datacloud_markdown/*
	@echo "   Done"

# Install dependencies
setup:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt --break-system-packages
	npm install -g playwright
	npx playwright install chromium
	@echo "   Done"

# Help
help:
	@echo "Agentforce Data Cloud Doc Pipeline"
	@echo ""
	@echo "Usage:"
	@echo "  make all       - Run full pipeline (snapshot → extract → normalize → validate)"
	@echo "  make snapshot  - Capture JS-rendered HTML from source URLs"
	@echo "  make extract   - Extract procedures from HTML"
	@echo "  make normalize - Convert to Data Cloud markdown"
	@echo "  make validate  - Validate markdown files"
	@echo "  make clean     - Remove all generated files"
	@echo "  make setup     - Install dependencies"
	@echo ""
	@echo "After pipeline completes:"
	@echo "  1. cp upload/env.example upload/.env"
	@echo "  2. Edit .env with Salesforce credentials"
	@echo "  3. python upload/datacloud_ingest.py"
