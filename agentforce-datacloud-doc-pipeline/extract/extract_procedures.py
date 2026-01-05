#!/usr/bin/env python3
"""
Extract procedures from HTML snapshots.
Identifies sections with step-by-step instructions.
"""

from bs4 import BeautifulSoup
import pathlib
import json
import re

def extract_procedures():
    procedures = []
    html_dir = pathlib.Path("raw/html")
    
    if not html_dir.exists():
        print("❌ No raw/html directory found. Run snapshot first.")
        return
    
    html_files = list(html_dir.glob("*.html"))
    
    if not html_files:
        print("❌ No HTML files found in raw/html/")
        return
    
    print(f"📂 Processing {len(html_files)} HTML files...")
    
    for html_file in html_files:
        print(f"  📄 {html_file.name[:50]}...")
        
        try:
            soup = BeautifulSoup(html_file.read_text(encoding='utf-8'), "lxml")
            
            # Remove script and style elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer']):
                element.decompose()
            
            # Strategy 1: Look for section elements
            for section in soup.select("section, article, .procedure, .steps"):
                title_elem = section.find(["h1", "h2", "h3", "h4"])
                steps = section.find_all("li")
                
                if title_elem and len(steps) >= 2:
                    procedures.append({
                        "title": title_elem.get_text(strip=True),
                        "steps": [s.get_text(strip=True) for s in steps if s.get_text(strip=True)],
                        "source_file": html_file.name
                    })
            
            # Strategy 2: Look for ordered lists with preceding headings
            for ol in soup.find_all("ol"):
                prev_heading = None
                for prev in ol.find_all_previous(["h1", "h2", "h3", "h4"]):
                    prev_heading = prev
                    break
                
                steps = ol.find_all("li")
                if prev_heading and len(steps) >= 2:
                    title = prev_heading.get_text(strip=True)
                    # Avoid duplicates
                    if not any(p["title"] == title for p in procedures):
                        procedures.append({
                            "title": title,
                            "steps": [s.get_text(strip=True) for s in steps if s.get_text(strip=True)],
                            "source_file": html_file.name
                        })
                        
        except Exception as e:
            print(f"    ⚠️  Error processing {html_file.name}: {e}")
    
    # Deduplicate by title
    seen_titles = set()
    unique_procedures = []
    for p in procedures:
        if p["title"] not in seen_titles:
            seen_titles.add(p["title"])
            unique_procedures.append(p)
    
    output_path = pathlib.Path("extract/procedures.json")
    output_path.write_text(json.dumps(unique_procedures, indent=2))
    
    print(f"✅ Extracted {len(unique_procedures)} procedures to extract/procedures.json")

if __name__ == "__main__":
    extract_procedures()
