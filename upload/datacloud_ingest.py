#!/usr/bin/env python3
"""
Ingest procedure markdown files into Salesforce Data Cloud.
POC version using username/password auth.
For production, implement JWT OAuth flow.
"""

import os
import sys
import requests
import pathlib
import frontmatter
from dotenv import load_dotenv

# Load environment variables
load_dotenv('upload/.env')

def salesforce_auth():
    """Authenticate to Salesforce and return access token."""
    url = f"{os.environ['SF_LOGIN_URL']}/services/oauth2/token"
    
    data = {
        "grant_type": "password",
        "client_id": os.environ["SF_CLIENT_ID"],
        "client_secret": os.environ["SF_CLIENT_SECRET"],
        "username": os.environ["SF_USERNAME"],
        "password": os.environ["SF_PASSWORD"] + os.environ.get("SF_SECURITY_TOKEN", "")
    }
    
    print("🔐 Authenticating to Salesforce...")
    
    r = requests.post(url, data=data)
    
    if r.status_code != 200:
        print(f"❌ Authentication failed: {r.status_code}")
        print(r.text)
        sys.exit(1)
    
    response = r.json()
    print("✅ Authentication successful")
    
    return response["access_token"], response["instance_url"]

def ingest_file(token, instance_url, md_file, dataset_name):
    """Ingest a single markdown file into Data Cloud."""
    
    # Parse markdown with frontmatter
    post = frontmatter.load(md_file)
    
    payload = {
        "content": post.content,
        "product": post.metadata.get("product"),
        "module": post.metadata.get("module"),
        "version": post.metadata.get("version"),
        "persona": post.metadata.get("persona"),
        "content_type": post.metadata.get("content_type"),
        "title": post.metadata.get("title"),
        "source_file": md_file.name
    }
    
    # Data Cloud ingestion endpoint
    url = f"{instance_url}/services/data/v60.0/sobjects/{dataset_name}"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    r = requests.post(url, json=payload, headers=headers)
    
    if r.status_code not in [200, 201]:
        print(f"  ⚠️  Failed to ingest {md_file.name}: {r.status_code}")
        print(f"      {r.text[:200]}")
        return False
    
    return True

def main():
    # Verify environment
    required_vars = ["SF_CLIENT_ID", "SF_CLIENT_SECRET", "SF_LOGIN_URL", 
                     "SF_USERNAME", "SF_PASSWORD"]
    
    missing = [v for v in required_vars if not os.environ.get(v)]
    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        print("   Copy upload/env.example to upload/.env and fill in values")
        sys.exit(1)
    
    # Authenticate
    token, instance = salesforce_auth()
    
    # Get dataset name
    dataset_name = os.environ.get("DATACLOUD_DATASET_NAME", "Agentforce_Support_Procedures")
    
    # Find markdown files
    md_dir = pathlib.Path("output/datacloud_markdown")
    md_files = list(md_dir.glob("*.md"))
    
    if not md_files:
        print("❌ No markdown files found in output/datacloud_markdown/")
        sys.exit(1)
    
    print(f"📤 Ingesting {len(md_files)} files to Data Cloud...")
    
    success = 0
    failed = 0
    
    for md in md_files:
        print(f"  📄 {md.name}...", end=" ")
        if ingest_file(token, instance, md, dataset_name):
            print("✅")
            success += 1
        else:
            failed += 1
    
    print("")
    print(f"🏁 Ingestion complete: {success} succeeded, {failed} failed")
    
    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
