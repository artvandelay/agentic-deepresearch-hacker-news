#!/usr/bin/env python3
"""
Minimal Tool Interface for Agentic Research
Pure data retrieval - no logic, no decisions, just execute and return data.
"""

from typing import List, Dict, Optional
from research_agent import HNDatabase


# Global database instance (reused across calls for efficiency)
_db = None


def get_db() -> HNDatabase:
    """Get or create database instance"""
    global _db
    if _db is None:
        _db = HNDatabase()
    return _db


def search_hn(keywords: List[str], limit: int = 20, min_score: Optional[int] = None, 
              max_shards: int = 1637) -> Dict:
    """
    Search HN archive - returns RAW data with full content.
    
    NO PROCESSING, NO ANALYSIS - just fetch and return.
    
    Args:
        keywords: List of keywords to search for (OR logic within, AND across)
        limit: Maximum number of posts to return
        min_score: Minimum score threshold (optional)
        max_shards: Number of shards to search (1637 = all)
    
    Returns:
        {
            "found": int,
            "posts": [list of full post dicts],
            "keywords_used": [list of keywords]
        }
    """
    db = get_db()
    
    # Search
    results = db.search_by_keywords(
        keywords=keywords,
        limit=limit,
        min_score=min_score,
        max_shards=max_shards
    )
    
    # Get full content for each result
    posts = []
    for r in results:
        item = db.get_item_by_id(r['id'], max_shards=200)
        if item:
            # Clean HTML entities (minimal processing, just readability)
            if item.get('text'):
                item['text'] = (item['text']
                    .replace('&#34;', '"')
                    .replace('&#39;', "'")
                    .replace('&quot;', '"')
                    .replace('&apos;', "'")
                    .replace('&amp;', '&')
                    .replace('&lt;', '<')
                    .replace('&gt;', '>')
                )
            if item.get('title'):
                item['title'] = (item['title']
                    .replace('&#34;', '"')
                    .replace('&#39;', "'")
                    .replace('&quot;', '"')
                    .replace('&apos;', "'")
                    .replace('&amp;', '&')
                )
            posts.append(item)
    
    return {
        "found": len(posts),
        "posts": posts,
        "keywords_used": keywords
    }


def get_post_by_id(post_id: int) -> Optional[Dict]:
    """
    Get a specific post by ID with full content.
    
    Args:
        post_id: HN post ID
    
    Returns:
        Full post dict or None if not found
    """
    db = get_db()
    return db.get_item_by_id(post_id, max_shards=200)


def get_thread(post_id: int) -> List[Dict]:
    """
    Get comment thread for a post.
    
    Args:
        post_id: HN post ID
    
    Returns:
        List of comment dicts in thread order
    """
    db = get_db()
    return db.get_thread(post_id)


def get_stats() -> Dict:
    """
    Return database statistics for LLM context.
    
    Returns:
        {
            "total_shards": int,
            "date_range": str,
            "total_items_estimate": str
        }
    """
    db = get_db()
    return {
        "total_shards": len(db.shard_files),
        "date_range": "2006-2025",
        "total_items_estimate": "~35M items"
    }


def save_report(content: str, filename: str) -> Dict:
    """
    Save final report to file.
    
    Args:
        content: Full markdown report
        filename: Output filename
    
    Returns:
        {"status": "saved", "path": str, "size": int}
    """
    from pathlib import Path
    
    path = Path(filename)
    path.write_text(content)
    
    return {
        "status": "saved",
        "path": str(path.absolute()),
        "size": len(content)
    }


# Tool registry for easy LLM access
TOOLS = {
    "search_hn": {
        "function": search_hn,
        "description": "Search HackerNews archive by keywords",
        "parameters": {
            "keywords": "List[str] - Keywords to search for",
            "limit": "int - Max results (default 20)",
            "min_score": "Optional[int] - Minimum score threshold",
            "max_shards": "int - Shards to search (default all)"
        }
    },
    "get_post_by_id": {
        "function": get_post_by_id,
        "description": "Get specific post by ID with full content",
        "parameters": {
            "post_id": "int - HN post ID"
        }
    },
    "get_thread": {
        "function": get_thread,
        "description": "Get comment thread for a post",
        "parameters": {
            "post_id": "int - HN post ID"
        }
    },
    "get_stats": {
        "function": get_stats,
        "description": "Get database statistics",
        "parameters": {}
    },
    "save_report": {
        "function": save_report,
        "description": "Save final report to file",
        "parameters": {
            "content": "str - Full markdown report",
            "filename": "str - Output filename"
        }
    }
}


if __name__ == '__main__':
    # Quick test
    print("Testing minimal tool interface...")
    
    # Test search
    result = search_hn(["analog", "computer"], limit=5)
    print(f"\n✓ search_hn: Found {result['found']} posts")
    if result['posts']:
        print(f"  Sample: {result['posts'][0].get('title', 'N/A')[:60]}")
    
    # Test stats
    stats = get_stats()
    print(f"\n✓ get_stats: {stats['total_shards']} shards, {stats['date_range']}")
    
    print("\n✓ All tools working!")

