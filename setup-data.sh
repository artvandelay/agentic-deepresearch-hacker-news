#!/bin/bash
# Setup script to download and extract HackerNews archive data
# Tries original source first, falls back to GitHub Releases backup

set -e

echo "🔬 Agentic Deep Research on Hacker News - Data Setup"
echo "======================================================"
echo ""
echo "This will download 8.8GB of HackerNews archive data (2006-2025)"
echo ""

# Check if data already exists
if [ -d "downloaded-site" ]; then
    echo "⚠️  Data directory already exists!"
    read -p "Do you want to re-download? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "✅ Using existing data"
        exit 0
    fi
    rm -rf downloaded-site
fi

# Try original source first
echo "📥 Attempting download from original source..."
ORIGINAL_URL="https://github.com/DOSAYGO-STUDIO/HackerBook/releases/download/v1.0/downloaded-site.tar.gz"

if curl -L --fail --silent --head "$ORIGINAL_URL" > /dev/null 2>&1; then
    echo "✅ Original source available, downloading (this may take a while)..."
    curl -L -o downloaded-site.tar.gz "$ORIGINAL_URL"
    echo ""
    echo "🔧 Extracting archive..."
    tar -xzf downloaded-site.tar.gz
    rm downloaded-site.tar.gz
    echo "✅ Downloaded from original source"
else
    echo "⚠️  Original source unavailable!"
    echo "📥 Downloading from GitHub Releases backup (archived Dec 31, 2025)..."
    echo ""
    
    REPO="artvandelay/agentic-deepresearch-hacker-news"
    
    # Create temp directory for split parts
    mkdir -p .tmp-download
    cd .tmp-download
    
    # Download all 10 split parts
    for part in aa ab ac ad ae af ag ah ai aj; do
        filename="data-archive.tar.gz.part${part}"
        echo "Downloading part ${part} (10 parts total)..."
        curl -L -o "$filename" \
            "https://github.com/${REPO}/releases/latest/download/${filename}"
    done
    
    echo ""
    echo "🔧 Merging split parts and extracting..."
    # Concatenate all parts back into single archive and extract
    cat data-archive.tar.gz.part* | tar -xzf -
    
    # Move extracted data to parent directory (the repo root)
    mv downloaded-site ../
    
    # Cleanup temp directory
    cd ..
    rm -rf .tmp-download
    
    echo "✅ Downloaded from GitHub Releases backup"
fi

echo ""
echo "======================================================"
echo "✅ Setup complete!"
echo "======================================================"
echo ""
echo "Data location: $(pwd)/downloaded-site/"
echo "Data size: $(du -sh downloaded-site/ | cut -f1)"
echo "Shards: $(ls downloaded-site/static-shards/*.sqlite.gz 2>/dev/null | wc -l | tr -d ' ') SQLite files"
echo ""
echo "You can now run:"
echo "  python3 agentic_research.py \"your query\" -o report.md"
echo ""
