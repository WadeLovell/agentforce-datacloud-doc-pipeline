#!/usr/bin/env python3
"""
Convert extracted procedures to Data Cloud-optimized Markdown.
Each file includes YAML frontmatter for metadata filtering.
"""

import json
import pathlib
import yaml
import re

def normalize_to_markdown():
    config_path = pathlib.Path("config/source_urls.yaml")
    procedures_path = pathlib.Path("extract/procedures.json")
    
    if not config_path.exists():
        print("❌ config/source_urls.yaml not found")
        return
    
    if not procedures_path.exists():
        print("❌ extract/procedures.json not found. Run extraction first.")
        return
    
    config = yaml.safe_load(config_path.read_text())
    procedures = json.loads(procedures_path.read_text())
    
    if not procedures:
        print("⚠️  No procedures to normalize")
        return
    
    out = pathlib.Path("output/datacloud_markdown")
    out.mkdir(parents=True, exist_ok=True)
    
    # Clear existing files
    for existing in out.glob("*.md"):
        existing.unlink()
    
    print(f"📝 Normalizing {len(procedures)} procedures...")
    
    for p in procedures:
        # Create URL-safe slug
        slug = re.sub(r'[^a-z0-9]+', '_', p["title"].lower()).strip("_")
        slug = slug[:80]  # Limit length
        
        # Build markdown with YAML frontmatter
        md = f"""---
product: {config.get('product', 'Unknown')}
module: {config.get('module', 'Unknown')}
version: {config.get('version', 'Unknown')}
persona: {config.get('persona', 'support_agent')}
content_type: procedure
title: "{p['title']}"
---

# {p['title']}

## Procedure

"""
        # Add numbered steps
        for i, step in enumerate(p["steps"], 1):
            # Clean up step text
            step = step.strip()
            step = re.sub(r'\s+', ' ', step)  # Normalize whitespace
            md += f"{i}. {step}\n"
        
        # Write file
        output_file = out / f"{slug}.md"
        output_file.write_text(md)
        print(f"  ✅ {slug}.md")
    
    print(f"🏁 Generated {len(procedures)} markdown files in output/datacloud_markdown/")

if __name__ == "__main__":
    normalize_to_markdown()
