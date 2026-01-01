#!/bin/bash
# Setup script to download and extract HackerNews archive data
# This downloads 8.8GB of data split into 5 parts from GitHub Releases

set -e  # Exit on error

echo "🔬 Agentic Deep Research on Hacker News - Data Setup"
echo "======================================================"
echo ""
echo "This will download 8.8GB of HackerNews archive data (2006-2025)"
echo "Data is split into 5 parts (~2GB each)"
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

# Get the latest release tag
REPO="artvandelay/agentic-deepresearch-hacker-news"
echo "📥 Downloading data from GitHub Releases..."
echo ""

# Create temp directory
mkdir -p .tmp-download
cd .tmp-download

# Download all parts
for part in aa ab ac ad ae; do
    filename="data-archive.tar.gz.part${part}"
    echo "Downloading part ${part}..."
    curl -L -o "$filename" \
        "https://github.com/${REPO}/releases/latest/download/${filename}"
done

echo ""
echo "🔧 Reconstructing and extracting archive..."
cat data-archive.tar.gz.part* | tar -xzf -

# Move extracted data to parent directory
mv downloaded-site ../

# Go back and cleanup
cd ..
rm -rf .tmp-download

echo ""
echo "✅ Setup complete!"
echo ""
echo "Data location: $(pwd)/downloaded-site/"
echo "Data size: $(du -sh downloaded-site/ | cut -f1)"
echo ""
echo "You can now run: python3 agentic_research.py \"your query\" -o report.md"

