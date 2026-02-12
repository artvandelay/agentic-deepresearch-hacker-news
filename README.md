# 🔬 Agentic Deep Research on Hacker News

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/artvandelay/agentic-deepresearch-hacker-news)

**AI-powered research on 19 years of HackerNews discussions (2006-2025)**

Ask a question. Get a comprehensive research report. The AI decides everything—what to search, what to analyze, when it's done.

> **Data:** 8.8GB archive available in [GitHub Releases](https://github.com/artvandelay/agentic-deepresearch-hacker-news/releases)

---

## 🚀 Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/artvandelay/agentic-deepresearch-hacker-news.git
cd agentic-deepresearch-hacker-news
./setup-data.sh  # Downloads 8.8GB HN archive (one-time)

# 2. Add your API key
echo "OPENROUTER_API_KEY=sk-or-v1-..." > .env

# 3. Run research
python3 agentic_research.py "rust programming language" -o report.md

# 4. Read your report
open report.md
```

**That's it!** The AI controls the entire research process.

---

## 💡 What You Get

Ask: *"What does HackerNews think about mechanical keyboards?"*

Get: A comprehensive markdown report with:
- Multiple perspectives from actual HN discussions
- 10+ direct quotes with attribution `[Post #123, by username]`
- Historical context and trends
- Technical details and community insights
- 2000+ words of analysis

**Cost:** ~$0.50 with Gemini Flash  
**Time:** 1-2 minutes  
**Quality:** The AI refines until satisfied

---

## 🎯 How It Works

**Fully Agentic Design:**
1. AI decides what to search
2. AI analyzes results
3. AI decides to search more or synthesize
4. AI decides when research is complete
5. AI generates final report

**Python is just glue** (<2% of execution time). All intelligence lives in the LLM.

**Example conversation:**
```
AI: "I'll search for 'mechanical keyboard' to understand the landscape"
→ Finds 50 posts

AI: "Good overview. Now I'll search for customization aspects"
→ Finds 50 more posts

AI: "I'll synthesize the motivations section now"
→ Writes section with quotes

AI: "Need to cover downsides. Searching for problems"
→ Finds 3 posts

AI: "I have comprehensive coverage. Finalizing report."
→ Generates 15KB report
```

---

## 📊 Model Options

### Gemini 2.5 Flash (Recommended)
- **Cost:** ~$0.50 per report
- **Speed:** 1-2 minutes
- **Quality:** Very good
```bash
python3 agentic_research.py "your question" --model "google/gemini-2.5-flash"
```

### Claude 3.5 Sonnet (Highest Quality)
- **Cost:** ~$3-5 per report
- **Speed:** 3-5 minutes
- **Quality:** Excellent
```bash
python3 agentic_research.py "your question" --model "anthropic/claude-3.5-sonnet"
```

---

## 🔧 Options

```bash
python3 agentic_research.py "your question" [options]

Options:
  -o FILE           Output file (default: print to stdout)
  --calls N         Max AI calls/budget (default: 20)
  --model MODEL     OpenRouter model (default: claude-3.5-sonnet)
```

**Examples:**
```bash
# Quick research (10 calls, ~1 min)
python3 agentic_research.py "startup advice" --calls 10

# Standard research (20 calls, ~2 min)
python3 agentic_research.py "analog computers" -o report.md

# Deep research (30 calls, ~3 min)
python3 agentic_research.py "rust vs go" --calls 30 --model "anthropic/claude-3.5-sonnet"
```

---

## 📁 What's Inside

```
agentic-deepresearch-hacker-news/
├── agentic_research.py    # Main system (375 lines)
├── tools.py               # Data retrieval (150 lines)
├── prompts.py             # AI instructions (100 lines)
├── requirements.txt       # Dependencies
├── .env                   # Your API key (create this)
└── downloaded-site/       # 8.8GB HN archive (auto-downloaded)
```

**Total code:** ~625 lines  
**Intelligence location:** In the LLM, not the code

---

## 🏗️ Architecture

```
User Question
    ↓
AI decides action (SEARCH/SYNTHESIZE/DONE)
    ↓
Python executes (search database, save file)
    ↓
AI analyzes results
    ↓
AI decides next action
    ↓
... recursive refinement ...
    ↓
AI decides DONE
    ↓
Final Report
```

**Performance (typical run):**
- Total time: 46s
- AI thinking: 45.5s (99%)
- Database I/O: 0.5s (1%)
- Python logic: <0.1s (<1%)

✅ Python overhead: <2% (as designed)

---

## 🎨 Extending

### Add New Tools

Edit `tools.py`:
```python
def get_user_posts(username: str) -> Dict:
    """Get all posts by a user"""
    # Your implementation
    return {"posts": [...]}
```

### Modify AI Behavior

Edit `prompts.py`:
```python
def get_system_prompt() -> str:
    return """
    You are a researcher...
    
    NEW ACTION:
    4. ANALYZE_USER - Deep dive into a user's contributions
    """
```

**No code changes needed** - just update the prompt!

---

## 📖 Data

- **Size:** 8.8GB
- **Items:** ~42 million (stories, comments, polls)
- **Coverage:** 2006-2025
- **Format:** 1,637 SQLite shards
- **Source:** HackerNews BigQuery dataset

The `setup-data.sh` script:
1. Tries original source first
2. Falls back to GitHub Releases if needed
3. Automatically extracts and validates

---

## 🔑 API Key Setup

Get your key from [OpenRouter](https://openrouter.ai/keys):

```bash
echo "OPENROUTER_API_KEY=sk-or-v1-your-key-here" > .env
```

Add credits at https://openrouter.ai/credits

---

## 🐛 Troubleshooting

### "OPENROUTER_API_KEY not found"
```bash
echo "OPENROUTER_API_KEY=sk-or-v1-..." > .env
```

### "Payment Required"
Add credits at https://openrouter.ai/credits

### Search returns 0 results
The AI should automatically try broader terms. If not, try different keywords.

### Slow performance
- Gemini Flash: 1-2s per call (fast)
- Claude Sonnet: 8-9s per call (high quality)
- This is normal—most time is AI thinking

---

## 🎯 Design Philosophy

> **"Intelligence in the model, not in the code."**

Traditional approach:
```python
# Python controls everything
for phase in ["search", "analyze", "synthesize"]:
    results = llm.call(phase)
    if quality_check(results):
        continue
```

Agentic approach:
```python
# AI controls everything
while not done:
    action = llm.decide_next_action()
    result = execute(action)
    done = llm.is_satisfied(result)
```

**Python is just glue.** All intelligence lives in the LLM.

---

## 📝 Additional Tools (Legacy)

### Simple Report Generator
```bash
python3 create_report.py "rust programming" -o rust.md
```
Single-pass generation. Fast but less thorough.

### Interactive Agent
```bash
python3 research_agent.py
```
Conversational interface for exploration.

### Editor Agent (Original System)
```bash
python3 editor_agent.py "analog computers" -o report.md --calls 25
```
Python-controlled workflow. Still works but less flexible.

---

## 🙏 Credits

- **HN Archive:** [DOSAYGO-STUDIO/HackerBook](https://github.com/DOSAYGO-STUDIO/HackerBook)
- **Data Source:** BigQuery HN dataset
- **Models:** [OpenRouter.ai](https://openrouter.ai/)

---

## 📜 License

MIT License

---

## 🔗 Links

- **OpenRouter:** https://openrouter.ai/
- **Get API Key:** https://openrouter.ai/keys
- **HackerBook Project:** https://github.com/DOSAYGO-STUDIO/HackerBook
- **HackerNews:** https://news.ycombinator.com/
