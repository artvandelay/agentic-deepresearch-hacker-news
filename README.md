# 🔬 Agentic Deep Research on Hacker News

**AI-Powered Deep Research on 19 Years of HackerNews Discussions (2006-2025)**

Fully agentic research system where the LLM controls everything. Analyze the complete HackerNews archive with true AI agency - the LLM decides what to search, when to synthesize, and when it's done. Python just provides tools.

---

## 🚀 Quick Start

```bash
# 1. Download the HackerNews archive data (8.8GB, one-time setup)
./setup-data.sh

# 2. Set your API key in .env file
echo "OPENROUTER_API_KEY=sk-or-v1-..." > .env

# 3. Run agentic research
python3 agentic_research.py "rust programming language" -o report.md --calls 20

# 4. Read your report
open report.md
```

**That's it!** The LLM will decide what to search, when to synthesize, and when it's done.

### Data Setup

The system requires the HackerNews archive (8.8GB, 42M items, 2006-2025). 

**Option 1: Automatic (Recommended)**
```bash
./setup-data.sh  # Downloads from GitHub Releases
```

**Option 2: Manual (If releases unavailable)**
```bash
wget https://github.com/DOSAYGO-STUDIO/HackerBook/releases/download/v1.0/downloaded-site.tar.gz
tar -xzf downloaded-site.tar.gz && rm downloaded-site.tar.gz
```

The data is archived as of December 31, 2025, and split into 5 parts (~2GB each) in GitHub Releases for easier downloading.

---

## 📊 Data

- **8.8 GB** of HackerNews archive
- **~42 million items** (stories, comments, polls)
- **1,637 SQLite shards** covering 2006-2025
- **Full text content** with metadata
- **Already downloaded and ready** (`downloaded-site/`)

---

## 🤖 Available Tools

### 1. ⭐ **Agentic Research** (Recommended)

**When:** You want the LLM to control the research process  
**Cost:** $0.50-2 per report (with Gemini Flash)  
**Speed:** ~1-3 minutes for 10-20 calls

```bash
# With Gemini Flash (cheap & fast)
python3 agentic_research.py "mechanical keyboards" -o report.md --calls 15 --model "google/gemini-2.5-flash"

# With Claude Sonnet (higher quality)
python3 agentic_research.py "analog computers" -o report.md --calls 20 --model "anthropic/claude-3.5-sonnet"
```

**How it works:**
- LLM decides what to search, when to synthesize, when done
- Python just executes tools (<2% overhead)
- Recursive refinement (LLM controls depth)
- Self-correcting (adapts to data availability)

**Options:**
```bash
--calls N          # Maximum LLM calls (default: 20)
--model MODEL      # Model to use (default: anthropic/claude-3.5-sonnet)
-o FILE            # Output file (prints to stdout if not specified)
```

### 2. **Simple Report Generator** (Fast & Cheap)

**When:** Quick overview or exploration  
**Cost:** ~$0.50 per report  
**Speed:** 30 seconds

```bash
python3 create_report.py "rust programming" -o rust.md
```

Single-pass generation, good for discovery.

### 3. **Interactive Research Agent** (Exploratory)

**When:** You don't know what you're looking for  
**Cost:** $0.50-2 per session

```bash
python3 research_agent.py
```

Conversational interface for multi-step exploration.

### 4. **Editor Agent** (Legacy - Python-Controlled)

**When:** You want Python to control quality gates  
**Cost:** $5-10 per report  
**Speed:** 3-4 minutes

```bash
export OPEN_ROUTER_KEY="sk-or-v1-..."
python3 editor_agent.py "analog computers" -o report.md --calls 25
```

Original system with hard-coded workflow phases. Still works but less flexible than agentic system.

---

## 🏗️ Architecture

### Agentic Research System (Recommended)

**Design Philosophy:** LLM controls everything, Python is just glue.

```
User Question → LLM (decides action) → Python (executes) → 
LLM (analyzes result) → LLM (decides next action) → ... → 
LLM (decides DONE) → Final Report
```

**Components:**
- `agentic_research.py` - Self-conversation loop (375 lines)
- `tools.py` - Minimal data retrieval functions (150 lines)
- `prompts.py` - System prompts with all logic (100 lines)

**Performance:**
- Python logic: <2% of total time ✅
- Search I/O: Variable (depends on data)
- LLM calls: Majority of time (as it should be)

**Example Run (Gemini Flash, 10 calls):**
```
Total time:    46s
LLM time:      46s (99%)
Search I/O:    0.5s (1%)
Python logic:  <0.1s (<1%)
```

---

## 🎯 How Agentic Research Works

### Real Example: "mechanical keyboards"

**Call 1:** LLM decides to search
```
THINKING: Start with broad search to understand landscape
ACTION: SEARCH
Keywords: [mechanical keyboard, keyboard, custom keyboard]
→ Found 50 posts
```

**Call 2:** LLM refines search
```
THINKING: Good overview. Now dive into customization aspects
ACTION: SEARCH
Keywords: [custom mechanical keyboard, keycaps, switches]
→ Found 50 posts
```

**Call 3-4:** LLM continues exploring
```
→ More searches for specific topics
→ 152 posts found total
```

**Call 5-7:** LLM synthesizes
```
ACTION: SYNTHESIZE
Section: [Motivations and Benefits]
Content: [Full markdown with quotes]
```

**Call 8:** LLM searches for challenges
```
THINKING: Need to cover downsides too
ACTION: SEARCH
Keywords: [mechanical keyboard problems, expensive, noise]
→ Found 3 posts
```

**Call 9:** LLM synthesizes challenges section

**Call 10:** LLM decides done
```
THINKING: Have comprehensive coverage. Time to finalize.
ACTION: DONE
Report: [Full 15KB markdown report with 10+ quotes]
```

**Result:** 15KB report with proper structure, quotes, and analysis in 46 seconds.

---

## 💡 Key Features

### ✅ Truly Agentic
- LLM decides workflow (not Python)
- Recursive refinement (LLM controls depth)
- Self-correcting (adapts to data)

### ✅ Minimal Python Overhead
- <2% Python logic time
- Just tool execution
- Search I/O tracked separately

### ✅ Flexible & Extensible
- Add new tools easily
- Modify behavior via prompts (not code)
- Works with any OpenRouter model

### ✅ No Hallucinations
- Search validated (1,637 shards work correctly)
- LLM only uses actual posts
- Adapts when data sparse

---

## 📁 Project Structure

```
hn-sentinel/
├── agentic_research.py    # Main agentic system (recommended)
├── tools.py               # Minimal tool interface
├── prompts.py             # System prompts with logic
├── test_search.py         # Foundation validation
├── create_report.py       # Simple single-pass generator
├── research_agent.py      # Interactive agent
├── editor_agent.py        # Legacy Python-controlled system
├── requirements.txt       # Python dependencies
├── .env                   # API key (create this)
├── downloaded-site/       # 8.8GB HN archive (1,637 shards)
└── examples/              # Example reports
```

---

## 🔧 Installation

```bash
# Clone or navigate to directory
cd hn-sentinel

# Install dependencies
pip3 install -r requirements.txt

# Set API key
echo "OPENROUTER_API_KEY=sk-or-v1-your-key" > .env

# Test it works
python3 test_search.py
```

---

## 📖 Usage Examples

### Quick Research (10 calls, ~1 min, ~$0.50)
```bash
python3 agentic_research.py "rust programming" --calls 10 --model "google/gemini-2.5-flash"
```

### Standard Research (20 calls, ~2 min, ~$1-2)
```bash
python3 agentic_research.py "startup advice" -o startup.md --calls 20 --model "google/gemini-2.5-flash"
```

### Deep Research (30 calls, ~3 min, ~$3-5)
```bash
python3 agentic_research.py "analog computers" -o analog.md --calls 30 --model "anthropic/claude-3.5-sonnet"
```

### Test Search Foundation
```bash
python3 test_search.py
```

---

## 🎨 Extending the System

### Add New Tools

Edit `tools.py`:

```python
def get_user_posts(username: str, limit: int = 20) -> Dict:
    """Get all posts by a specific user"""
    db = get_db()
    # Implementation here
    return {"posts": [...]}

# Add to TOOLS registry
TOOLS["get_user_posts"] = {
    "function": get_user_posts,
    "description": "Get posts by specific user",
    "parameters": {"username": "str", "limit": "int"}
}
```

### Modify LLM Behavior

Edit `prompts.py`:

```python
AGENTIC_SYSTEM_PROMPT = """
[Add new instructions here]

NEW ACTION TYPE:
4. ANALYZE_USER - Analyze a specific user's contributions
   Format:
   ACTION: ANALYZE_USER
   Username: [username]
   Reasoning: Why analyze this user?
"""
```

No code changes needed - just update the prompt!

---

## 🐛 Troubleshooting

### "OPENROUTER_API_KEY not found"
```bash
echo "OPENROUTER_API_KEY=sk-or-v1-your-key" > .env
```

### "Payment Required" Error
Top up your OpenRouter account at https://openrouter.ai/credits

### Search Returns 0 Results
The search works correctly (validated). If 0 results:
- Topic may not be discussed on HN
- LLM should automatically try broader terms
- Try different keywords manually

### Slow Performance
- Gemini Flash: ~1-2s per call (fast)
- Claude Sonnet: ~8-9s per call (higher quality)
- Search I/O: 0.05-30s depending on query
- This is normal and expected

---

## 📊 Model Recommendations

### Gemini 2.5 Flash (Recommended for most uses)
- **Cost:** ~$0.05 per report
- **Speed:** 1-2s per call
- **Quality:** Good (7-8/10)
- **Best for:** Quick research, exploration, iteration

### Claude 3.5 Sonnet (Best quality)
- **Cost:** ~$3-5 per report
- **Speed:** 8-9s per call
- **Quality:** Excellent (8-9/10)
- **Best for:** Publication-quality reports, complex topics

### GPT-4 Turbo
- **Cost:** ~$1-2 per report
- **Speed:** 3-5s per call
- **Quality:** Very good (8/10)
- **Best for:** Balanced cost/quality

---

## 🎯 Design Philosophy

> **"Intelligence in the model, not in the code."**

We don't build Python to control the LLM.  
We build the LLM to control itself.  
Python is just glue.

This is agentic AI.

---

## 📝 License

MIT License - See repository for details

---

## 🙏 Credits

- **HackerNews Archive:** DOSAYGO-STUDIO/HackerBook
- **Data Source:** BigQuery HN dataset
- **Models:** OpenRouter.ai

---

## 🔗 Links

- **OpenRouter:** https://openrouter.ai/
- **HackerBook:** https://github.com/DOSAYGO-STUDIO/HackerBook
- **HN Archive:** https://news.ycombinator.com/
