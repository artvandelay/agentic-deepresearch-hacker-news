#!/usr/bin/env python3
"""
Create narrative reports from HackerNews discussions using LLM analysis.

Takes a research topic, searches HN archive, fetches full post content,
and uses Claude/GPT to synthesize a comprehensive narrative report.
"""

import os
import json
import argparse
from pathlib import Path
from datetime import datetime
import requests
from research_agent import HNDatabase


def load_api_key():
    """Load OpenRouter API key from .env or environment."""
    api_key = os.environ.get('OPENROUTER_API_KEY') or os.environ.get('OPEN_ROUTER_KEY')
    
    if not api_key:
        env_path = Path('.env')
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('OPEN_ROUTER_KEY=') or line.startswith('OPENROUTER_API_KEY='):
                        api_key = line.split('=', 1)[1].strip('"\'')
                        break
    
    return api_key


def call_llm(api_key, messages, model="anthropic/claude-3.5-sonnet", max_tokens=16000):
    """Call OpenRouter API with large context support."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/DOSAYGO-STUDIO/HackerBook",
        "X-Title": "HN Report Generator"
    }
    
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens
    }
    
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload
    )
    response.raise_for_status()
    return response.json()


def search_and_fetch(db, query, limit=100, min_score=None):
    """Search HN and fetch full content of all matching posts."""
    print(f"🔍 Searching for: {query}")
    
    # Parse query into keywords
    keywords = [kw.strip() for kw in query.split(',') if kw.strip()]
    if not keywords:
        keywords = query.split()
    
    print(f"   Keywords: {keywords}")
    
    # Search across all shards
    results = db.search_by_keywords(
        keywords=keywords,
        limit=limit,
        min_score=min_score,
        max_shards=1637  # Search all shards
    )
    
    print(f"✅ Found {len(results)} posts\n")
    
    if not results:
        return []
    
    # Fetch full content for each result
    print("📥 Fetching full post content...")
    posts = []
    
    for i, result in enumerate(results, 1):
        # Already have most of the content, just need to ensure we have full text
        item = db.get_item_by_id(result['id'], max_shards=200)
        if item:
            posts.append(item)
            if i % 10 == 0:
                print(f"   {i}/{len(results)} posts fetched")
    
    print(f"✅ Fetched {len(posts)} complete posts\n")
    
    # Sort chronologically
    posts.sort(key=lambda x: x['time'] if x['time'] else 0)
    
    return posts


def format_posts_for_llm(posts, include_full_text=True):
    """Format posts for LLM consumption."""
    formatted = []
    
    for item in posts:
        post_data = {
            'id': item['id'],
            'type': item['type'],
            'date': item.get('timestamp', 'unknown'),
            'author': item.get('by', 'unknown'),
        }
        
        if item.get('score'):
            post_data['score'] = item['score']
        
        if item.get('title'):
            post_data['title'] = item['title']
        
        if item.get('url'):
            post_data['url'] = item['url']
        
        if include_full_text and item.get('text'):
            # Clean HTML entities
            text = item['text']
            text = text.replace('&#34;', '"').replace('&#39;', "'")
            text = text.replace('&lt;', '<').replace('&gt;', '>')
            text = text.replace('&#x2F;', '/').replace('&#x27;', "'")
            text = text.replace('<p>', '\n\n')
            post_data['content'] = text
        
        formatted.append(post_data)
    
    return formatted


def create_narrative_report(api_key, query, posts, model="anthropic/claude-3.5-sonnet"):
    """Use LLM to create a narrative report from posts."""
    
    # Format posts for LLM
    formatted_posts = format_posts_for_llm(posts)
    posts_json = json.dumps(formatted_posts, indent=2)
    
    # Calculate statistics
    total_posts = len(posts)
    date_range = f"{posts[0].get('timestamp', 'unknown')[:10]} to {posts[-1].get('timestamp', 'unknown')[:10]}"
    stories = sum(1 for p in posts if p['type'] == 'story')
    comments = sum(1 for p in posts if p['type'] == 'comment')
    
    # Create prompt
    system_prompt = """You are an expert analyst creating comprehensive narrative reports from HackerNews discussions.

Your task is to:
1. Analyze all provided posts chronologically
2. Identify key themes, patterns, and evolution of ideas
3. Extract insightful quotes from community members
4. Build a compelling narrative arc showing how understanding evolved
5. Highlight technical details, debates, and consensus points
6. Create a well-structured report with:
   - Executive Summary
   - Historical narrative (organized by time periods or themes)
   - Key insights and patterns
   - Technical deep dives where relevant
   - Community consensus and disagreements
   - Resources and references mentioned
   - Timeline of key discussions
   - Conclusions

Write in an engaging, journalistic style. Use direct quotes extensively. Make it educational and insightful.
The report should tell a story, not just summarize posts."""

    user_prompt = f"""Create a comprehensive narrative report about: "{query}"

I've collected {total_posts} HackerNews posts ({stories} stories, {comments} comments) spanning {date_range}.

Here are all the posts with full content:

{posts_json}

Please analyze these posts and create a detailed narrative report that:
- Shows how the community's understanding evolved over time
- Highlights key technical insights and debates
- Uses extensive direct quotes from community members
- Identifies patterns and themes
- Provides historical context
- Concludes with synthesis of learnings

Make it thorough, insightful, and well-structured. This is for serious research, so include technical depth."""

    print("🤖 Generating narrative report with LLM...")
    print(f"   Model: {model}")
    print(f"   Posts to analyze: {total_posts}")
    print(f"   Input tokens: ~{len(posts_json) // 4}")
    print()
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    response = call_llm(api_key, messages, model=model, max_tokens=16000)
    
    report = response['choices'][0]['message']['content']
    
    # Add metadata header
    metadata = f"""# {query.title()} - HackerNews Community Analysis

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Query:** {query}  
**Posts Analyzed:** {total_posts} ({stories} stories, {comments} comments)  
**Date Range:** {date_range}  
**Model:** {model}  

---

"""
    
    return metadata + report


def main():
    parser = argparse.ArgumentParser(
        description='Generate narrative reports from HackerNews discussions',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate report on analog computers
  python3 create_report.py "analog computer" -o analog_report.md

  # High-scoring posts only
  python3 create_report.py "startup advice" --min-score 100 -o startup_advice.md
  
  # Use GPT-4 instead of Claude
  python3 create_report.py "rust programming" --model openai/gpt-4-turbo -o rust_report.md
  
  # Limit to 50 posts for faster/cheaper analysis
  python3 create_report.py "bitcoin" --limit 50 -o bitcoin_report.md
        """
    )
    
    parser.add_argument('query', help='Search query (keywords or comma-separated terms)')
    parser.add_argument('-o', '--output', required=True, help='Output markdown file')
    parser.add_argument('--limit', type=int, default=100, help='Max posts to analyze (default: 100)')
    parser.add_argument('--min-score', type=int, help='Minimum score filter')
    parser.add_argument('--model', default='anthropic/claude-3.5-sonnet',
                       help='LLM model to use (default: claude-3.5-sonnet)')
    parser.add_argument('--shards-dir', default='downloaded-site/static-shards',
                       help='Path to HN shards directory')
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("🧠 HackerNews Narrative Report Generator")
    print("=" * 80)
    print()
    
    # Load API key
    api_key = load_api_key()
    if not api_key:
        print("❌ Error: OpenRouter API key not found")
        print("\nOptions:")
        print("  1. Create .env file with: OPEN_ROUTER_KEY=\"your-key\"")
        print("  2. Or export: export OPENROUTER_API_KEY='your-key'")
        print("\nGet your API key from: https://openrouter.ai/keys")
        return 1
    
    # Initialize database
    db = HNDatabase(args.shards_dir)
    
    # Search and fetch posts
    posts = search_and_fetch(db, args.query, limit=args.limit, min_score=args.min_score)
    
    if not posts:
        print("❌ No posts found matching query")
        return 1
    
    # Generate report
    try:
        report = create_narrative_report(api_key, args.query, posts, model=args.model)
        
        # Save report
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding='utf-8')
        
        print(f"✅ Report generated successfully!")
        print(f"📄 Saved to: {args.output}")
        print(f"📊 Report length: {len(report):,} characters")
        print()
        
        # Show preview
        lines = report.split('\n')
        print("Preview (first 20 lines):")
        print("-" * 80)
        for line in lines[:20]:
            print(line)
        if len(lines) > 20:
            print(f"... ({len(lines) - 20} more lines)")
        print("-" * 80)
        
        return 0
        
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())

