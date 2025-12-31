#!/usr/bin/env python3
"""
HackerNews Deep Research Agent
Uses OpenRouter AI to perform intelligent, multi-step research on HN archive.
"""

import os
import json
import sqlite3
import gzip
import tempfile
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import requests


class HNDatabase:
    """Interface to query HackerNews SQLite shards."""
    
    def __init__(self, shards_dir: str = "downloaded-site/static-shards"):
        self.shards_dir = Path(shards_dir)
        self.shard_files = sorted(self.shards_dir.glob("shard_*.sqlite.gz"))
        print(f"📚 Loaded {len(self.shard_files)} shards")
    
    def _query_shard(self, shard_path: Path, query: str, params: tuple = ()) -> List[Dict]:
        """Query a single shard and return results."""
        try:
            # Decompress to temp file
            with gzip.open(shard_path, 'rb') as f_in:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f_out:
                    f_out.write(f_in.read())
                    temp_db = f_out.name
            
            # Query
            conn = sqlite3.connect(temp_db)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            results = [dict(row) for row in cursor.execute(query, params)]
            conn.close()
            
            # Cleanup
            os.unlink(temp_db)
            
            return results
        except Exception as e:
            print(f"⚠️  Error querying {shard_path.name}: {e}")
            return []
    
    def search_by_keywords(self, keywords: List[str], limit: int = 50, 
                          item_type: Optional[str] = None,
                          min_score: Optional[int] = None,
                          max_shards: int = 100) -> List[Dict]:
        """Search for items containing keywords."""
        # Build WHERE clause
        conditions = []
        params = []
        
        # Keyword search (case-insensitive)
        keyword_conditions = []
        for kw in keywords:
            keyword_conditions.append("(title LIKE ? OR text LIKE ?)")
            params.extend([f"%{kw}%", f"%{kw}%"])
        conditions.append(f"({' OR '.join(keyword_conditions)})")
        
        if item_type:
            conditions.append("type = ?")
            params.append(item_type)
        
        if min_score is not None:
            conditions.append("score >= ?")
            params.append(min_score)
        
        where_clause = " AND ".join(conditions)
        
        query = f"""
            SELECT id, type, time, by, title, text, url, score, parent
            FROM items
            WHERE {where_clause}
            ORDER BY score DESC, time DESC
            LIMIT ?
        """
        params.append(limit)
        
        # Search across shards (reverse order = newer first)
        results = []
        shards_to_search = list(reversed(self.shard_files[-max_shards:]))
        
        for shard_path in shards_to_search:
            shard_results = self._query_shard(shard_path, query, tuple(params))
            results.extend(shard_results)
            if len(results) >= limit:
                break
        
        # Add readable timestamp and truncate text
        for item in results[:limit]:
            if item['time']:
                item['timestamp'] = datetime.fromtimestamp(item['time']).isoformat()
            if item['text'] and len(item['text']) > 500:
                item['text_preview'] = item['text'][:500] + "..."
            else:
                item['text_preview'] = item['text']
        
        return results[:limit]
    
    def get_item_by_id(self, item_id: int, max_shards: int = 200) -> Optional[Dict]:
        """Get a specific item by ID."""
        query = "SELECT * FROM items WHERE id = ?"
        
        # Search recent shards first (IDs are roughly chronological)
        for shard_path in reversed(self.shard_files[-max_shards:]):
            results = self._query_shard(shard_path, query, (item_id,))
            if results:
                item = results[0]
                if item['time']:
                    item['timestamp'] = datetime.fromtimestamp(item['time']).isoformat()
                return item
        
        return None
    
    def get_thread(self, item_id: int) -> List[Dict]:
        """Get comment thread for an item."""
        query = """
            SELECT items.*, edges.ord
            FROM edges
            JOIN items ON edges.child_id = items.id
            WHERE edges.parent_id = ?
            ORDER BY edges.ord
        """
        
        # Search for thread across shards
        results = []
        for shard_path in reversed(self.shard_files[-100:]):
            shard_results = self._query_shard(shard_path, query, (item_id,))
            results.extend(shard_results)
        
        return results


class ResearchAgent:
    """AI-powered research agent using OpenRouter."""
    
    def __init__(self, api_key: str, model: str = "anthropic/claude-3.5-sonnet"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.db = HNDatabase()
        self.conversation_history = []
        
    def _call_llm(self, messages: List[Dict], tools: Optional[List[Dict]] = None) -> Dict:
        """Call OpenRouter API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/DOSAYGO-STUDIO/HackerBook",
            "X-Title": "HN Research Agent"
        }
        
        payload = {
            "model": self.model,
            "messages": messages
        }
        
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        
        response = requests.post(self.base_url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    
    def _search_hn(self, keywords: List[str], item_type: str = None, 
                   min_score: int = None, limit: int = 20) -> List[Dict]:
        """Tool: Search HackerNews archive."""
        print(f"🔍 Searching HN for: {keywords} (type={item_type}, min_score={min_score})")
        results = self.db.search_by_keywords(
            keywords=keywords,
            item_type=item_type,
            min_score=min_score,
            limit=limit
        )
        print(f"   Found {len(results)} results")
        return results
    
    def _get_item(self, item_id: int) -> Optional[Dict]:
        """Tool: Get specific HN item."""
        print(f"📄 Fetching item #{item_id}")
        return self.db.get_item_by_id(item_id)
    
    def _format_results_for_llm(self, results: List[Dict]) -> str:
        """Format search results for LLM consumption."""
        if not results:
            return "No results found."
        
        formatted = []
        for i, item in enumerate(results, 1):
            parts = [f"\n[{i}] ID: {item['id']} | Type: {item['type']}"]
            
            if item.get('title'):
                parts.append(f"    Title: {item['title']}")
            
            if item.get('by'):
                parts.append(f"    Author: {item['by']}")
            
            if item.get('score'):
                parts.append(f"    Score: {item['score']} points")
            
            if item.get('timestamp'):
                parts.append(f"    Date: {item['timestamp']}")
            
            if item.get('url'):
                parts.append(f"    URL: {item['url']}")
            
            # Use preview if available, otherwise full text (truncated)
            text = item.get('text_preview') or item.get('text')
            if text:
                # Clean HTML entities
                text = text.replace('&#34;', '"').replace('&#39;', "'")
                text = text.replace('&lt;', '<').replace('&gt;', '>')
                parts.append(f"    Content: {text}")
            
            formatted.append('\n'.join(parts))
        
        return '\n'.join(formatted)
    
    def research(self, question: str, max_iterations: int = 5) -> str:
        """Conduct deep research on a question."""
        print(f"\n🔬 Research Question: {question}\n")
        print("=" * 80)
        
        system_prompt = """You are a deep research agent with access to the complete HackerNews archive (2006-2025).
Your goal is to conduct thorough research by:
1. Breaking down the research question into specific searchable queries
2. Searching the HN archive systematically
3. Analyzing the results and identifying patterns
4. Conducting follow-up searches to fill gaps
5. Synthesizing findings into a comprehensive answer

When searching:
- Use specific, relevant keywords
- Try different keyword combinations
- Filter by item type (story/comment) when appropriate
- Consider searching for high-scoring items (min_score) for quality
- Look at both stories and discussions

Available tools:
- search_hn(keywords, item_type, min_score, limit): Search for items matching keywords
  - keywords: list of search terms
  - item_type: "story" or "comment" (optional)
  - min_score: minimum score threshold (optional)
  - limit: max results (default 20)

Be systematic, thorough, and cite specific HN posts in your findings."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]
        
        iteration = 0
        search_count = 0
        
        while iteration < max_iterations:
            iteration += 1
            print(f"\n🤖 Iteration {iteration}/{max_iterations}")
            print("-" * 80)
            
            # Agent decides what to do next
            response = self._call_llm(messages)
            
            assistant_message = response['choices'][0]['message']
            content = assistant_message.get('content', '')
            
            # Check if agent wants to search
            if 'search_hn(' in content.lower() or iteration == 1:
                # Extract search parameters from agent's response
                # Simple heuristic: look for key terms in the response
                
                if iteration == 1:
                    # First iteration: create initial search strategy
                    planning_prompt = f"""Based on the research question: "{question}"

What are the most important keywords to search for in HackerNews? 
List 3-5 specific search queries you'd make, one per line.
Format: keyword1, keyword2, keyword3"""
                    
                    plan_response = self._call_llm(messages + [
                        {"role": "assistant", "content": "Let me plan my search strategy..."},
                        {"role": "user", "content": planning_prompt}
                    ])
                    
                    plan_content = plan_response['choices'][0]['message']['content']
                    print(f"\n📋 Search Strategy:\n{plan_content}\n")
                    
                    # Extract keywords (simple parsing)
                    lines = plan_content.strip().split('\n')
                    searches = []
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Remove numbering, split by commas
                            keywords = [kw.strip() for kw in line.split(',')]
                            keywords = [kw for kw in keywords if kw and not kw[0].isdigit()]
                            if keywords:
                                searches.append(keywords)
                    
                    # Perform searches
                    all_results = []
                    for keywords in searches[:3]:  # Limit to 3 initial searches
                        results = self._search_hn(keywords, limit=15)
                        all_results.extend(results)
                        search_count += 1
                    
                    # Deduplicate by ID
                    seen_ids = set()
                    unique_results = []
                    for r in all_results:
                        if r['id'] not in seen_ids:
                            seen_ids.add(r['id'])
                            unique_results.append(r)
                    
                    formatted_results = self._format_results_for_llm(unique_results[:30])
                    
                    messages.append({
                        "role": "assistant",
                        "content": f"I'll search for: {searches}"
                    })
                    messages.append({
                        "role": "user",
                        "content": f"Search results ({len(unique_results)} unique items):\n\n{formatted_results}\n\nAnalyze these results. What patterns do you see? Do you need more information on specific aspects?"
                    })
                
                else:
                    # Follow-up searches based on agent's request
                    print(f"\n💭 Agent thinking:\n{content}\n")
                    
                    # Ask agent for specific search
                    search_prompt = """Based on your analysis, what specific search should we run next?
Provide:
1. Keywords (comma-separated)
2. Item type (story/comment/both)
3. Minimum score (number or 'any')

Format:
Keywords: term1, term2, term3
Type: story
Min Score: 50"""
                    
                    search_response = self._call_llm(messages + [
                        {"role": "assistant", "content": content},
                        {"role": "user", "content": search_prompt}
                    ])
                    
                    search_content = search_response['choices'][0]['message']['content']
                    print(f"\n🎯 Next Search:\n{search_content}\n")
                    
                    # Parse search parameters
                    keywords = []
                    item_type = None
                    min_score = None
                    
                    for line in search_content.split('\n'):
                        line = line.strip()
                        if line.startswith('Keywords:'):
                            keywords = [k.strip() for k in line.split(':', 1)[1].split(',')]
                        elif line.startswith('Type:'):
                            type_val = line.split(':', 1)[1].strip().lower()
                            if type_val in ['story', 'comment']:
                                item_type = type_val
                        elif line.startswith('Min Score:'):
                            score_val = line.split(':', 1)[1].strip()
                            if score_val.isdigit():
                                min_score = int(score_val)
                    
                    if keywords:
                        results = self._search_hn(keywords, item_type=item_type, 
                                                 min_score=min_score, limit=20)
                        formatted_results = self._format_results_for_llm(results)
                        
                        messages.append({"role": "assistant", "content": content})
                        messages.append({
                            "role": "user",
                            "content": f"Additional search results:\n\n{formatted_results}\n\nContinue your analysis."
                        })
                        search_count += 1
                    else:
                        # Agent is done searching
                        break
            else:
                # Agent is providing final answer
                print(f"\n📊 Final Analysis:\n")
                print(content)
                return content
            
            if search_count >= 6:  # Limit total searches
                print("\n⚠️  Search limit reached, generating final report...")
                final_prompt = """Based on all the search results you've reviewed, provide a comprehensive final report answering the original research question. Include:
1. Summary of findings
2. Key insights from HN discussions
3. Notable posts/comments with IDs
4. Trends or patterns observed
5. Conclusion"""
                
                messages.append({"role": "user", "content": final_prompt})
                final_response = self._call_llm(messages)
                final_content = final_response['choices'][0]['message']['content']
                print(f"\n📊 Final Report:\n{final_content}")
                return final_content
        
        # Max iterations reached
        print("\n⚠️  Max iterations reached, generating summary...")
        return "Research incomplete - max iterations reached."


def main():
    """Run the research agent."""
    print("=" * 80)
    print("🧠 HackerNews Deep Research Agent")
    print("=" * 80)
    
    # Get API key from environment or .env file
    api_key = os.environ.get('OPENROUTER_API_KEY') or os.environ.get('OPEN_ROUTER_KEY')
    
    # Try loading from .env file if not in environment
    if not api_key:
        env_path = Path('.env')
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('OPEN_ROUTER_KEY=') or line.startswith('OPENROUTER_API_KEY='):
                        api_key = line.split('=', 1)[1].strip('"\'')
                        break
    
    if not api_key:
        print("\n❌ Error: OpenRouter API key not found")
        print("\nOptions:")
        print("  1. Create .env file with: OPEN_ROUTER_KEY=\"your-key\"")
        print("  2. Or export: export OPENROUTER_API_KEY='your-key'")
        print("\nGet your API key from: https://openrouter.ai/keys")
        return
    
    # Choose model
    model = os.environ.get('OPENROUTER_MODEL', 'anthropic/claude-3.5-sonnet')
    print(f"\n🤖 Using model: {model}")
    print("   (Change with: export OPENROUTER_MODEL='model-name')\n")
    
    # Initialize agent
    agent = ResearchAgent(api_key, model)
    
    # Example research questions
    examples = [
        "How has the HN community's perception of AI/ML evolved from 2010 to 2025?",
        "What were the most influential startup advice discussions on HN?",
        "How did HN discuss cryptocurrencies before Bitcoin became mainstream?",
        "What are the best HN threads about scaling web applications?",
        "What did early HN users say about AWS when it launched?"
    ]
    
    print("Example research questions:")
    for i, ex in enumerate(examples, 1):
        print(f"  {i}. {ex}")
    
    print("\nEnter your research question (or 'quit' to exit):")
    
    while True:
        question = input("\n📝 Research question: ").strip()
        
        if not question or question.lower() == 'quit':
            break
        
        try:
            result = agent.research(question)
            print("\n" + "=" * 80)
            print("✅ Research Complete!")
            print("=" * 80)
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n👋 Goodbye!")


if __name__ == '__main__':
    main()

