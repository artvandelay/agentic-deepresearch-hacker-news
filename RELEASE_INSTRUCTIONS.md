# GitHub Release Instructions

## Step 1: Push Code to GitHub

```bash
cd /Users/jigar/projects/messing-around/hn_backup/agentic-deepresearch-hacker-news

# Add remote (if not already added)
git remote add origin https://github.com/artvandelay/agentic-deepresearch-hacker-news.git

# Push code (data is ignored via .gitignore)
git push -u origin master
```

## Step 2: Create GitHub Release

1. Go to: https://github.com/artvandelay/agentic-deepresearch-hacker-news/releases/new

2. Fill in:
   - **Tag:** `v1.0.0`
   - **Release title:** `v1.0.0 - HackerNews Archive (Dec 31, 2025)`
   - **Description:**
     ```
     ## HackerNews Archive Data (Dec 31, 2025)
     
     This release includes the HackerNews archive data (8.8GB) split into 5 parts for easier downloading.
     
     **Data Contents:**
     - 42 million items (stories, comments, polls)
     - 1,637 SQLite shards
     - Coverage: 2006-2025
     - Full text content with metadata
     
     **How to Use:**
     1. Clone the repository
     2. Run `./setup-data.sh` to automatically download and extract the data
     3. Follow the README for usage instructions
     
     The setup script will automatically download these files and reconstruct the archive.
     ```

3. **Upload the 5 data files** as release assets:
   - Drag and drop from: `data-release/data-archive.tar.gz.partaa`
   - Drag and drop from: `data-release/data-archive.tar.gz.partab`
   - Drag and drop from: `data-release/data-archive.tar.gz.partac`
   - Drag and drop from: `data-release/data-archive.tar.gz.partad`
   - Drag and drop from: `data-release/data-archive.tar.gz.partae`

4. Click **"Publish release"**

## Step 3: Verify Setup Script Works

After publishing the release, test the setup:

```bash
# In a fresh clone
git clone https://github.com/artvandelay/agentic-deepresearch-hacker-news.git
cd agentic-deepresearch-hacker-news
./setup-data.sh
```

This should:
1. Download all 5 parts from GitHub Releases
2. Reconstruct the archive
3. Extract `downloaded-site/` directory
4. Clean up temporary files

## Two Flows Supported

### Flow 1: Using GitHub Releases (Recommended)
```bash
git clone https://github.com/artvandelay/agentic-deepresearch-hacker-news.git
cd agentic-deepresearch-hacker-news
./setup-data.sh  # Downloads from YOUR GitHub Releases
```

### Flow 2: Manual Download (If releases unavailable)
If GitHub Releases are unavailable, users can manually download from original source:
```bash
# Download from original source
wget https://github.com/DOSAYGO-STUDIO/HackerBook/releases/download/v1.0/downloaded-site.tar.gz
tar -xzf downloaded-site.tar.gz
rm downloaded-site.tar.gz
```

Both flows result in the same `downloaded-site/` directory structure.

## After Release

You can delete the local `data-release/` folder:
```bash
rm -rf data-release/
```

The data is now safely stored in GitHub Releases and users can download it via `setup-data.sh`.

## Repository Settings

Don't forget to update on GitHub:
- **Description:** Use the short description from REPO_DESCRIPTIONS.md
- **Topics:** Add the tags listed in REPO_DESCRIPTIONS.md
- **Website:** https://github.com/artvandelay/agentic-deepresearch-hacker-news

