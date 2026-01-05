#!/bin/bash
# GitHub Repository Setup Script
# Run this after installing GitHub CLI: brew install gh (Mac) or apt install gh (Linux)

set -e

REPO_NAME="agentforce-datacloud-doc-pipeline"

echo "🚀 Setting up GitHub repository: $REPO_NAME"
echo ""

# Check if gh is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) not installed."
    echo "   Install: https://cli.github.com/"
    exit 1
fi

# Check if logged in
if ! gh auth status &> /dev/null; then
    echo "🔐 Please authenticate with GitHub:"
    gh auth login
fi

# Create repository
echo "📦 Creating repository..."
gh repo create "$REPO_NAME" --public --description "Salesforce Data Cloud + Agentforce documentation pipeline for middle-market banking" --clone

# Navigate to repo
cd "$REPO_NAME"

echo "📄 Copying files..."
# This assumes script is run from the directory containing all pipeline files
# Adjust paths as needed
cp -r ../config .
cp -r ../extract .
cp -r ../normalize .
cp -r ../validate .
cp -r ../output .
cp -r ../upload .
cp -r ../agentforce .
cp -r ../raw .
cp ../README.md .
cp ../Makefile .
cp ../requirements.txt .
cp ../package.json .
cp ../.gitignore .

# Initialize and push
echo "📤 Pushing to GitHub..."
git add .
git commit -m "Initial commit: Data Cloud + Agentforce documentation pipeline"
git push -u origin main

echo ""
echo "✅ Repository created successfully!"
echo "   URL: https://github.com/$(gh api user --jq .login)/$REPO_NAME"
echo ""
echo "Next steps:"
echo "  1. Clone: git clone https://github.com/$(gh api user --jq .login)/$REPO_NAME"
echo "  2. Setup: make setup"
echo "  3. Configure: Edit config/source_urls.yaml with your documentation URLs"
echo "  4. Run: make all"
echo "  5. Upload: cp upload/env.example upload/.env && python upload/datacloud_ingest.py"
