#!/usr/bin/env python3
"""
Validate markdown files before Data Cloud ingestion.
Fail-fast approach to catch issues early.
"""

import pathlib
import sys
import yaml

def validate_markdown():
    md_dir = pathlib.Path("output/datacloud_markdown")
    
    if not md_dir.exists():
        print("❌ output/datacloud_markdown/ not found. Run normalization first.")
        sys.exit(1)
    
    md_files = list(md_dir.glob("*.md"))
    
    if not md_files:
        print("❌ No markdown files found to validate")
        sys.exit(1)
    
    print(f"🔍 Validating {len(md_files)} markdown files...")
    
    errors = 0
    warnings = 0
    
    for md in md_files:
        text = md.read_text()
        file_errors = []
        file_warnings = []
        
        # Check 1: Has frontmatter
        if not text.startswith("---"):
            file_errors.append("Missing YAML frontmatter")
        else:
            # Parse frontmatter
            try:
                parts = text.split("---", 2)
                if len(parts) >= 3:
                    frontmatter = yaml.safe_load(parts[1])
                    
                    # Check required fields
                    required = ['product', 'module', 'version', 'persona', 'content_type']
                    for field in required:
                        if field not in frontmatter:
                            file_errors.append(f"Missing required field: {field}")
            except yaml.YAMLError as e:
                file_errors.append(f"Invalid YAML frontmatter: {e}")
        
        # Check 2: Has procedure section
        if "## Procedure" not in text:
            file_errors.append("Missing '## Procedure' section")
        
        # Check 3: Has numbered steps
        if "\n1." not in text:
            file_errors.append("Missing numbered steps (no '1.' found)")
        
        # Check 4: Step count
        step_count = text.count("\n1.")
        if step_count > 1:
            file_warnings.append(f"Multiple step sequences found ({step_count})")
        
        # Check 5: Has title heading
        if "\n# " not in text and not text.startswith("# "):
            file_errors.append("Missing title heading")
        
        # Check 6: Token estimate (rough)
        token_estimate = len(text.split())
        if token_estimate > 1000:
            file_warnings.append(f"Large file ({token_estimate} words) - may need chunking")
        elif token_estimate < 50:
            file_warnings.append(f"Small file ({token_estimate} words) - verify content")
        
        # Report issues
        if file_errors:
            print(f"❌ {md.name}")
            for err in file_errors:
                print(f"   ERROR: {err}")
            errors += len(file_errors)
        
        if file_warnings:
            if not file_errors:
                print(f"⚠️  {md.name}")
            for warn in file_warnings:
                print(f"   WARNING: {warn}")
            warnings += len(file_warnings)
    
    # Summary
    print("")
    if errors:
        print(f"❌ Validation FAILED: {errors} error(s), {warnings} warning(s)")
        sys.exit(1)
    elif warnings:
        print(f"⚠️  Validation PASSED with {warnings} warning(s)")
    else:
        print("✅ Validation PASSED - all files ready for Data Cloud ingestion")

if __name__ == "__main__":
    validate_markdown()
