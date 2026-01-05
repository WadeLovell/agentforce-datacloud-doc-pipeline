#!/usr/bin/env python3
"""
Extract procedures from MadCap Flare HTML snapshots.
Tailored for Springbrook documentation structure.
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
    
    html_files = list(html_dir.glob("*.html")) + list(html_dir.glob("*.htm"))
    
    if not html_files:
        print("❌ No HTML files found in raw/html/")
        return
    
    print(f"📂 Processing {len(html_files)} HTML files...")
    
    for html_file in html_files:
        print(f"  📄 {html_file.name[:50]}...")
        
        try:
            soup = BeautifulSoup(html_file.read_text(encoding='utf-8'), "lxml")
            
            # Get title from h1 or h2.TopicTitle
            title_elem = soup.select_one('h1')
            if not title_elem:
                continue
            
            title = title_elem.get_text(strip=True)
            
            # Skip index/menu pages
            if 'Index' in title or len(title) < 5:
                continue
            
            steps = []
            
            # Strategy 1: Find MCDropDown sections (Springbrook's step containers)
            dropdowns = soup.select('div.MCDropDown')
            for dropdown in dropdowns:
                # Get the step header (contains step number and title)
                header = dropdown.select_one('.MCDropDownHead, .dropDownHead')
                if header:
                    header_text = header.get_text(strip=True)
                    # Clean up the text
                    header_text = re.sub(r'\s+', ' ', header_text)
                    if len(header_text) > 5:
                        steps.append(header_text)
                
                # Get sub-steps from the dropdown body
                body = dropdown.select_one('.MCDropDownBody, .dropDownBody')
                if body:
                    for li in body.find_all('li', recursive=True):
                        text = li.get_text(strip=True)
                        text = re.sub(r'\s+', ' ', text)
                        if len(text) > 15 and not text.startswith(('Click here', 'Getting Started')):
                            steps.append(f"  • {text}")
            
            # Strategy 2: If no dropdowns, look for "Step by Step" section
            if not steps:
                step_section = soup.find('b', string=re.compile(r'Step by Step', re.I))
                if step_section:
                    # Get all following li elements
                    parent = step_section.find_parent('p')
                    if parent:
                        for sibling in parent.find_next_siblings():
                            for li in sibling.find_all('li'):
                                text = li.get_text(strip=True)
                                text = re.sub(r'\s+', ' ', text)
                                if len(text) > 15:
                                    steps.append(text)
            
            # Strategy 3: Look for numbered paragraphs
            if not steps:
                for p in soup.find_all('p'):
                    text = p.get_text(strip=True)
                    if re.match(r'^[1-9]\d?\.\s', text) and len(text) > 20:
                        steps.append(text)
            
            if len(steps) >= 2:
                procedures.append({
                    "title": title,
                    "steps": steps[:30],
                    "source_file": html_file.name
                })
                print(f"    ✓ Found {len(steps)} steps")
                
        except Exception as e:
            print(f"    ⚠️  Error: {e}")
    
    # Deduplicate by title
    seen_titles = set()
    unique_procedures = []
    for p in procedures:
        if p["title"] not in seen_titles:
            seen_titles.add(p["title"])
            unique_procedures.append(p)
    
    output_path = pathlib.Path("extract/procedures.json")
    output_path.write_text(json.dumps(unique_procedures, indent=2))
    
    print(f"\n✅ Extracted {len(unique_procedures)} procedures to extract/procedures.json")

if __name__ == "__main__":
    extract_procedures()