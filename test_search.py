#!/usr/bin/env python3
"""
Search & Retrieval Foundation Test
Validates that search and data retrieval work correctly before building agentic system.
"""

from research_agent import HNDatabase


def test_search_foundation():
    """Validate search and retrieval work correctly"""
    db = HNDatabase()
    
    print("=" * 80)
    print("SEARCH & RETRIEVAL VALIDATION")
    print("=" * 80)
    
    # Test 1: Known good query (analog computer - we know has 50+ posts)
    print("\n🔍 Test 1: Known good query (analog computer)")
    print("-" * 80)
    results = db.search_by_keywords(["analog", "computer"], limit=50)
    print(f"  ✓ Found {len(results)} posts for 'analog computer'")
    
    if len(results) < 20:
        print(f"  ⚠️  WARNING: Expected 20+ posts, found {len(results)}")
    
    # Verify full content
    if results:
        sample = db.get_item_by_id(results[0]['id'])
        if sample:
            title = sample.get('title', 'N/A')
            if title and len(title) > 60:
                title = title[:60] + "..."
            print(f"  ✓ Sample post #{sample['id']}: {title}")
            print(f"  ✓ Has title: {bool(sample.get('title'))}")
            print(f"  ✓ Has text: {bool(sample.get('text'))}")
            print(f"  ✓ Score: {sample.get('score', 0)}")
            
            if sample.get('text'):
                text_preview = sample['text'][:200].replace('\n', ' ')
                print(f"  ✓ Text preview: {text_preview}...")
        else:
            print(f"  ⚠️  Could not retrieve full item #{results[0]['id']}")
    
    # Test 2: Problematic query (mechanical keyboards - returned 0 in previous test)
    print("\n🔍 Test 2: Problematic query (mechanical keyboards)")
    print("-" * 80)
    kb_results = db.search_by_keywords(["mechanical", "keyboard"], limit=50)
    print(f"  Found {len(kb_results)} posts for 'mechanical keyboard'")
    
    # Try alternatives if few results
    if len(kb_results) < 10:
        print(f"  ℹ️  Few results found. Trying alternatives...")
        
        alt1 = db.search_by_keywords(["keyboard"], limit=50, min_score=50)
        print(f"    'keyboard' (score 50+): {len(alt1)} posts")
        
        alt2 = db.search_by_keywords(["keyboard"], limit=50)
        print(f"    'keyboard' (any score): {len(alt2)} posts")
        
        alt3 = db.search_by_keywords(["mechanical"], limit=50)
        print(f"    'mechanical' (any): {len(alt3)} posts")
        
        # Show samples from best alternative
        best_alt = alt1 if len(alt1) > 0 else (alt2 if len(alt2) > 0 else alt3)
        if best_alt and len(best_alt) > 0:
            print(f"\n  Sample from best alternative ({len(best_alt)} results):")
            for i, item in enumerate(best_alt[:3]):
                title = item.get('title', 'No title')
                if title and len(title) > 60:
                    title = title[:60] + "..."
                print(f"    {i+1}. Post #{item['id']}: {title} (score: {item.get('score', 0)})")
    else:
        print(f"  ✓ Sufficient results found!")
        for i, item in enumerate(kb_results[:3]):
            title = item.get('title', 'No title')
            if title and len(title) > 60:
                title = title[:60] + "..."
            print(f"    {i+1}. Post #{item['id']}: {title} (score: {item.get('score', 0)})")
    
    # Test 3: Different search strategies
    print("\n🔍 Test 3: Various search strategies")
    print("-" * 80)
    strategies = [
        (["rust"], "single keyword"),
        (["rust", "programming"], "two keywords"),
        (["startup", "advice"], "common topic"),
        (["ai"], "very broad"),
        (["python"], "popular language"),
    ]
    
    for keywords, desc in strategies:
        results = db.search_by_keywords(keywords, limit=20)
        print(f"  {desc:20} {str(keywords):30} → {len(results):3} posts")
        if results and len(results) > 0:
            sample = results[0]
            title = sample.get('title', 'No title')
            if title and len(title) > 50:
                title = title[:50] + "..."
            print(f"    Sample: #{sample['id']} - {title}")
    
    # Test 4: Check if search is case-sensitive
    print("\n🔍 Test 4: Case sensitivity check")
    print("-" * 80)
    lower_results = db.search_by_keywords(["rust"], limit=20)
    upper_results = db.search_by_keywords(["RUST"], limit=20)
    mixed_results = db.search_by_keywords(["Rust"], limit=20)
    
    print(f"  'rust' (lowercase): {len(lower_results)} posts")
    print(f"  'RUST' (uppercase): {len(upper_results)} posts")
    print(f"  'Rust' (mixed case): {len(mixed_results)} posts")
    
    if len(lower_results) == len(upper_results) == len(mixed_results):
        print("  ✓ Search is case-insensitive (GOOD)")
    else:
        print("  ⚠️  Search may be case-sensitive")
    
    # Test 5: Performance check
    print("\n🔍 Test 5: Performance check")
    print("-" * 80)
    import time
    
    start = time.time()
    results = db.search_by_keywords(["python"], limit=50, max_shards=100)
    elapsed = time.time() - start
    
    print(f"  Searched 100 shards for 'python': {len(results)} results in {elapsed:.2f}s")
    print(f"  Average: {elapsed/100*1000:.1f}ms per shard")
    
    if elapsed < 5.0:
        print("  ✓ Performance is acceptable")
    else:
        print(f"  ⚠️  Slow performance: {elapsed:.2f}s for 100 shards")
    
    print("\n" + "=" * 80)
    print("VALIDATION COMPLETE")
    print("=" * 80)
    
    # Summary
    print("\n📊 SUMMARY:")
    print(f"  ✓ Analog computer query: {len(db.search_by_keywords(['analog', 'computer'], limit=50))} posts")
    print(f"  ✓ Mechanical keyboard query: {len(kb_results)} posts")
    print(f"  ✓ Search is case-insensitive: {len(lower_results) == len(upper_results)}")
    print(f"  ✓ Performance: {elapsed:.2f}s for 100 shards")
    
    if len(kb_results) < 5:
        print("\n💡 RECOMMENDATION:")
        print("  - 'mechanical keyboard' returns few/no results")
        print("  - LLM should try broader terms like 'keyboard' if initial search fails")
        print("  - Implement keyword expansion in agentic system")


if __name__ == '__main__':
    test_search_foundation()

